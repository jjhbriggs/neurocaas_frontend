// Insert path into directory tree structure:
function insert(children = [], [head, ...tail]) {
    let child = children.find(child => child.text === head);
    if (!child) {
        head.includes('.') ? children.push(child = {text: head, children: [], icon: 'jstree-file'}) : children.push(child = {text: head, children: [], state : { 'opened' : true }})
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
                var full_path = data.instance.get_path(data.selected[0]).join('/').replace('results/', '');
                if (!full_path.includes('.')) return;
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
                                console.log(node);
                                var path = "/static/downloads/" + timestamp + "/" + node.text;
                                console.log(path);
                                /*var full_path = data.instance.get_path(data.selected[0]).join('/').replace('results/', '');
                                if (!full_path.includes('.')) return;
                                var item = get_item(full_path);
                                */

                                document.getElementById('_iframe').href = path;
                                document.getElementById('_iframe').click();
                            }
                        }
                    };

                    // Delete the "delete" menu item if selected node is folder
                    if (!node.text.includes(".")) {
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

// update JSTree
function update_jstree(){
    var paths = [];

    [...dtset_logs, ...results_links].forEach(function(item){
        paths.push('/results/' + item.path);
    })
    create_jstree_for_results(paths);
}


// delete Action
function delete_action(node, type, tree){
    $.ajax({
        url: '/get_user_files/',
        method: 'DELETE',
        data: {
            file_name: node.text,
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
function down_action(file_name, type){
    $.ajax({
        url: '/get_user_files/',
        method: 'PUT',
        data: {
            file_name: file_name,
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
            console.log(data);
            if (data.action === "delete_node" && !data.node.text.includes('.')) return;
            var filename = data.node.text;
            if (!filename.includes('.')) return;
            for ( var i=0; i< datasets.length; i++ ){
                if (datasets[i].name === filename) show_detail(i, 0);
            }
        })
        .jstree({
            'plugins':["wholerow","checkbox", "contextmenu"],
            contextmenu: {
                items: function(node){
                    // The default set of all items
                    var items = {
                        deleteItem: { // The "delete" menu item
                            label: "Delete",
                            action: function () {
                                var tree = $('#dataset_folder').jstree(true);
                                if (confirm("Are you sure to delete item, " + node.text + "?")) delete_action(node, 'inputs', tree);
                            }
                        }
                        /*,downItem: { // The "delete" menu item
                            label: "Donwload",
                            action: function () {
                                down_action(node.text, 'inputs');
                            }
                        }*/
                    };

                    // Delete the "delete" menu item if selected node is folder
                    if (!node.text.includes(".")) {
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
            // console.log(data.node.text);
            var filename = data.node.text;
            if (!filename.includes('.')) return;
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
                                if (confirm("Are you sure to delete item, " + node.text + "?")) delete_action(node, 'configs', tree);
                            }
                        },
                        downItem: { // The "delete" menu item
                            label: "Donwload",
                            action: function () {
                                down_action(node.text, 'configs');
                            }
                        }
                    };

                    // Delete the "delete" menu item if selected node is folder
                    if (!node.text.includes(".")) {
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
        data.push("/config/" + configs[i].name);
    }
    if (data.length > 0) create_config_jstree(data);
}