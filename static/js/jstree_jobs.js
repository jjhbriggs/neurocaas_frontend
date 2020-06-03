function truncate(n, len) {
/*
    truncate text

    @params:
            n: string,
            len: int
    @return:
            truncated string
*/

    if(n.length <= len) {
        return n;
    }

    var ext = n.substring(n.length - 8, n.length);
    var filename = n.replace(ext,'');

    filename = filename.substr(0, len-11) + (n.length > len ? '...' : '');
    return filename + ext;
};


function insert(children = [], [head, ...tail], text_length) {
    /*
        Insert path into directory tree structure:

        @params:
                children: array,
                text_length: int
        @return:
                array
    */
    let child = children.find(child => child.text === head);
    if (!child) {
        var text = truncate(head, text_length);
        tail.length === 0 ?
        children.push(child = {
            text: text, children: [],
            icon: 'jstree-file',
            li_attr: {
                title: head,
                type: 'file'
            }
        }) :
        children.push(child = {
            text: head,
            children: [],
            state : { 'opened' : true },
            li_attr: {
                title: head,
                type: 'folder'
            }
        })
    }

    if (tail.length > 0) insert(child.children, tail, text_length);
    return children;
}


function get_json_from_array(arr, text_length=34){
    /*
        get JSON from files path array

        @params:
                arr: array,
                text_length: int
        @return:
                json
    */
    let objectArray = arr
        .map(path => path.split('/').slice(1))
        .reduce((children, path) => insert(children, path, text_length), []);
    return objectArray;
}

// Async Ajax Request
function AjaxRequest(url, method='GET', data=null){
    show_spinner();
    return new Promise((resolve, reject) => {
       $.ajax({
            url : url,
            method : method,
            data : data,
            success :  function(res){
                hide_spinner();
                resolve(res);
            },
            error: function(err){
                hide_spinner();
                reject();
            }
       });
    });
}


function get_full_path_of_node(node, tree){
    return tree.get_path(node,"/").replace(node.text, node.li_attr.title) + "/";
}


// download Action
function down_action(node, key){
    if (node.li_attr.type === 'folder')
        download_folder(key, ana_id);
    else
        download_file(key, ana_id);
}

async function download_file(file_key, ana_id){
    var url = '/files/' + ana_id + '/?key=' + encodeURIComponent(file_key);
    var res = await AjaxRequest(url);

    if (res.status == 200){
        document.getElementById('_iframe').href = "/" + res.message;
        document.getElementById('_iframe').click();
    }
}


async function download_folder(folder_key, ana_id){
    var url = '/files/' + ana_id + '/';

    var params = {
        'key': folder_key
    }

    var res = await AjaxRequest(url, 'POST', params);

    if (res.status === 200){
        document.getElementById('_iframe').href = "/" + res.message;
        document.getElementById('_iframe').click();
    }
}


async function show_file_content(file_key, ana_id){
    var url = '/files/' + ana_id + '/?key=' + encodeURIComponent(file_key);
    var res = await AjaxRequest(url);

    if (res.status == 200)
        window.open("/" + res.message, '_blank');
}


function create_job_tree(paths){
    // console.log(paths);
    $('#job_detail_view')
        .on("changed.jstree", function (e, data) {
            if(data.selected.length) {
                if (data.node.li_attr.type === 'folder') return;
                var full_path = data.instance.get_path(data.node,'/').replace(data.node.text, data.node.li_attr.title).replace("results/", '');
                full_path = 'results/' + ana_prefix + timestamp + '/' + full_path;
                console.log( "selected node path", full_path);
                show_file_content(full_path, ana_id);
            }
        })
        .jstree({
            'plugins':["wholerow", "contextmenu"],
            contextmenu: {
                items: function(node){
                    // The default set of all items
                    var items = {
                        downItem: { // The "delete" menu item
                            label: "Download",
                            action: function () {
                                var tree = $('#job_detail_view').jstree(true);
                                var path = get_full_path_of_node(node, tree);
                                path = path.replace("results/", '');
                                var key =  'results/' + ana_prefix + timestamp + "/" + path;
                                down_action(node, key.slice(0, -1));
                            }
                        }
                    };

                    return items;
                },
                select_node: false,
                icon: true,
            },
            'core' : {
                'data' : get_json_from_array(paths, 50)
            }
        });
}