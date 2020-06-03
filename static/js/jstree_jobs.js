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
    return new Promise((resolve, reject) => {
       $.ajax({
            url : url,
            method : method,
            data : data,
            success :  function(res){
                resolve(res);
            },
            error: function(err){
                reject();
            }
       });
    });
}

// download Action
function down_action(node, type, tree, job_history=false){

    var path = tree.get_path(node,"/").replace(node.text, node.li_attr.title)
    path =  node.li_attr.type === 'folder' ?  path + "/" : path;
    path = path.replace(type + "/", '');
    $.ajax({
        url: '/get_user_files/',
        method: 'PUT',
        data: {
            file_name: path,
            type: type,
            choice: node.li_attr.type,
            timestamp: timestamp,
            ana_id: ana_id,
            job_history: job_history
        },
        success: function(res){
            if (res.message !== null){
                document.getElementById('_iframe').href = "/" + res.message;
                document.getElementById('_iframe').click();
            } else {
                // window.location.reload();
            }
        },
        error: function(err){
            console.log(err);
        }
    })
}


async function show_file_content(file_key, ana_id){
    var url = '/files/' + ana_id + '/?key=' + file_key;
    var res = await AjaxRequest(url);

    if (res.status == 200)
        window.open("/" + res.path, '_blank');

    console.log(res);
}


function create_job_tree(paths){
    // console.log(paths);
    $('#job_detail_view')
        .on("changed.jstree", function (e, data) {
            if(data.selected.length) {
                if (data.node.li_attr.type === 'folder') return;
                var full_path = data.instance.get_path(data.node,'/').replace(data.node.text, data.node.li_attr.title).replace("results/", '');
                console.log( "selected node path", full_path);
                full_path = 'results/' + ana_prefix + timestamp + '/' + full_path;
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
                                if (node.li_attr.type === 'folder'){
                                    var tree = $('#job_detail_view').jstree(true);
                                    down_action(node, 'results', tree);
                                }
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


// get selected node by tree_id and prefix
function get_selected_nodes(tree_id, prefix){
    var files = [];
    var selectedNodes = $('#' + tree_id).jstree(true).get_selected();
    for(var i = 0; i < selectedNodes.length; i++) {
        var full_node = $('#' + tree_id).jstree(true).get_node(selectedNodes[i]);

        var path = $('#' + tree_id).jstree(true).get_path(full_node,"/").replace(full_node.text, full_node.li_attr.title);
        var ext = (/[.]/.exec(path)) ? /[^.]+$/.exec(path) : undefined;
        if (ext) {
            path = path.replace(prefix, '');
            files.push(path);
        }
    }
    return files;
}