// truncate text
function truncate(n, len) {

    if(n.length <= len) {
        return n;
    }

    var ext = n.substring(n.length - 8, n.length);
    var filename = n.replace(ext,'');

    filename = filename.substr(0, len-8) + (n.length > len ? '...' : '');
    return filename + ext;
};

// Insert path into directory tree structure:
function insert(children = [], [head, ...tail]) {
    let child = children.find(child => child.text === head);
    if (!child) {
        var text = truncate(head, 34);
        head.includes('.') ?
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
    if (tail.length > 0) insert(child.children, tail);
    return children;
}

// get JSON from files path array
function get_json_from_array(arr){
    let objectArray = arr
        .map(path => path.split('/').slice(1))
        .reduce((children, path) => insert(children, path), []);
    return objectArray;
}

// Get appropriate item by path
function get_item(path){
    var _item = null;
    [...dtset_logs, ...results_links].forEach(function(item){
        if (item.path === path)
            _item = item
    })
    return _item;
}

function create_jstree_for_results(paths){
    $('#hierarchy').remove();
    $("#hierarchy_div").append('<div id="hierarchy"></div>');
    $('#hierarchy')
        .on("changed.jstree", function (e, data) {
            if(data.selected.length) {
                if (data.node.li_attr.type === 'folder') return;
                var full_path = data.instance.get_path(data.node,'/').replace(data.node.text, data.node.li_attr.title).replace("results/", '');
                var item = get_item(full_path);
                if (item !== null){
                    window.open( '../' + item.link, "_blank");
                }
            }
        })
        .jstree({
            'plugins':["wholerow", "contextmenu"],
            contextmenu: {
                items: function(node){
                    // The default set of all items
                    var items = {
                        downItem: { // The "delete" menu item
                            label: "Donwload",
                            action: function () {
                                var path = "/static/downloads/" + timestamp + "/" + node.li_attr.title;
                                document.getElementById('_iframe').href = path;
                                document.getElementById('_iframe').click();
                            }
                        }
                    };

                    // Delete the "delete" menu item if selected node is folder
                    if (node.li_attr.type === 'folder') {
                        delete items.downItem;
                    }

                    return items;
                },
                select_node: false,
                icon: true,
            },
            'core' : {
                'data' : get_json_from_array(paths)
            }
        });
}


// get selected node by tree_id and prefix
function get_selected_nodes(tree_id, prefix){
    var files = [];
    var selectedNodes = $('#' + tree_id).jstree(true).get_selected();
    console.log(selectedNodes);
    for(var i = 0; i < selectedNodes.length; i++) {
        var full_node = $('#' + tree_id).jstree(true).get_node(selectedNodes[i]);

        var path = $('#' + tree_id).jstree(true).get_path(full_node,"/").replace(full_node.text, full_node.li_attr.title);
        var ext = (/[.]/.exec(path)) ? /[^.]+$/.exec(path) : undefined;
        if (ext) {
            path = path.replace(prefix, '');
            console.log(path);
            files.push(path);
        }
    }
    return files;
}


// update JSTree
function update_jstree(){
    var paths = [];

    [...dtset_logs, ...results_links].forEach(function(item){
        paths.push('/results/' + item.path);
    });
    create_jstree_for_results(paths);
}


// delete Action
function delete_action(node, type, tree){
    var path = tree.get_path(node,"/").replace(node.text, node.li_attr.title).replace(type + "/", '');

    $.ajax({
        url: '/get_user_files/',
        method: 'DELETE',
        data: {
            file_name: path,
            type: type
        },
        success: function(res){
            tree.delete_node(node);
            // refresh_databucket_list();
        },
        error: function(err){
            console.log(err);
        }
    })
}


// download Action
function down_action(node, type, tree){
    var path = tree.get_path(node,"/").replace(node.text, node.li_attr.title).replace(type + "/", '');
    $.ajax({
        url: '/get_user_files/',
        method: 'PUT',
        data: {
            file_name: path,
            type: type
        },
        success: function(res){
            if (res.message !== null){
                document.getElementById('_iframe').href = "/" + res.message;
                document.getElementById('_iframe').click();
            } else {
                window.location.reload();
            }
        },
        error: function(err){
            console.log(err);
        }
    })
}


// create jstrees for datasets
function create_dataset_jstree(paths){
    $('#dataset_folder').remove();
    $("#dataset_div").append('<div id="dataset_folder"></div>');

    $('#dataset_folder')
        .on("changed.jstree", function (e, data) {
            if (data.node.li_attr.type === 'folder') return;
            var filename = data.instance.get_path(data.node,'/').replace(data.node.text, data.node.li_attr.title).replace("inputs/", '');
            for ( var i=0; i< datasets.length; i++ ){
                if (datasets[i].name === filename) show_detail(i, 0);
            }
        })
        .jstree({
            'plugins':["wholerow", "checkbox", "contextmenu"],
            contextmenu: {
                items: function(node){
                    // The default set of all items
                    var items = {
                        deleteItem: { // The "delete" menu item
                            label: "Delete",
                            action: function () {
                                var tree = $('#dataset_folder').jstree(true);
                                if (confirm("Are you sure to delete item, " + node.li_attr.title + "?"))
                                    delete_action(node, 'inputs', tree);
                            }
                        }
                    };

                    // Delete the "delete" menu item if selected node is folder
                    if (node.li_attr.type === 'folder') {
                        delete items.deleteItem;
                        delete items.downItem;
                    }

                    return items;
                },
                select_node: false,
                icon: true,
            },
            'core' : {
                'data' : get_json_from_array(paths),
                "check_callback" : true,
                'themes': {
                    'responsive': false,
                    'variant': 'medium',
                }
            }
        });
}


// create jstree for configs
function create_config_jstree(paths){
    $('#config_folder').remove();
    $("#config_div").append('<div id="config_folder"></div>');

    $('#config_folder')
        .on("changed.jstree", function (e, data) {
            var filename = data.node.li_attr.title;
            console.log(filename);
            if (data.node.li_attr.type === 'folder') return;

            for ( var i=0; i< configs.length; i++ ){
                if (configs[i].name === filename) show_detail(i, 1);
            }
        })
        .jstree({
            'plugins':["wholerow","conditionalselect", "contextmenu"],
            contextmenu: {
                items: function(node){
                    // The default set of all items
                    var items = {
                        deleteItem: { // The "delete" menu item
                            label: "Delete",
                            action: function () {
                                var tree = $('#config_folder').jstree(true);
                                if (node.li_attr.type === 'folder') return;
                                if (confirm("Are you sure to delete item, " + node.li_attr.title + "?")) delete_action(node, 'configs', tree);
                            }
                        },
                        downItem: { // The "delete" menu item
                            label: "Donwload",
                            action: function () {
                                var tree = $('#config_folder').jstree(true);
                                down_action(node, 'configs', tree);
                            }
                        }
                    };

                    // Delete the "delete" menu item if selected node is folder
                    if (node.li_attr.type === 'folder') {
                        delete items.deleteItem;
                        delete items.downItem;
                    }

                    return items;
                },
                select_node: false,
                icon: true,
            },
            'core' : {
                'data' : get_json_from_array(paths),
                "check_callback" : true,
                'themes': {
                    'responsive': false,
                    'variant': 'medium',
                }
            }
        });
}


// create dataset and config jstrees
function refresh_data_jstrees(){
    console.log(datasets);
    console.log(configs);

    // create dataset jstree
    data = [];
    for ( var i = 0; i < datasets.length; i++){
        data.push("/inputs/" + datasets[i].name);
    }
    if (data.length > 0) create_dataset_jstree(data);

    // create config jstree
    data = [];
    for ( var i = 0; i < configs.length; i++){
        data.push("/configs/" + configs[i].name);
    }
    if (data.length > 0) create_config_jstree(data);
}