function create_results_tree(paths){
    // console.log(paths);
    $('#hierarchy').remove();
    $("#hierarchy_div").append('<div id="hierarchy"></div>');
    $('#hierarchy')
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

                                var tree = $('#hierarchy').jstree(true);
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
                'data' : get_json_from_array(paths)
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


// update JSTree
function update_jstree(){
    var paths = [];

    [...dtset_logs, ...results_links].forEach(function(item){
        paths.push('/results/' + item.path);
    });
    create_results_tree(paths);
}


// download Action
function down_action(node, type, tree, job_history=false){

    var path = tree.get_path(node,"/").replace(node.text, node.li_attr.title)
    path =  node.li_attr.type === 'folder' ?  path + "/" : path;
    path = path.replace(type + "/", '');
    $.ajax({
        url: '/user_files/',
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


// create jstrees for data_sets
function create_data_set_jstree(paths){

    $('#data_set_folder').remove();
    $("#data_set_div").append('<div id="data_set_folder"></div>');
    $('#data_set_folder')
        .on("changed.jstree", function (e, data) {
            if (data.node.li_attr.type === 'folder') return;
            var filename = data.instance.get_path(data.node,'/').replace(data.node.text, data.node.li_attr.title).replace("inputs/", '');
            console.log(filename);

            for ( var i=0; i< data_sets.length; i++ ){
                if (data_sets[i].name === filename) show_detail(i, 0);
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
                                var tree = $('#data_set_folder').jstree(true);

                                if (confirm("Are you sure to delete item, " + node.li_attr.title + "?")){
                                    var key = get_full_path_of_node(node, tree);
                                    delete_action(node, key.slice(0, -1), tree);
                                }
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
                                
                                if (confirm("Are you sure to delete item, " + node.li_attr.title + "?")){
                                    var key = get_full_path_of_node(node, tree);
                                    delete_action(node, key.slice(0, -1), tree);
                                }
                            }
                        },
                        downItem: { // The "delete" menu item
                            label: "Download",
                            action: function () {
                                var tree = $('#config_folder').jstree(true);
                                down_action(node, 'configs', tree);
                            }
                        }
                    };

                    // Delete the "delete" menu item if selected node is folder
                    if (node.li_attr.type === 'folder') {
                        delete items.deleteItem;
                        //delete items.downItem;
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

    // create data_set jstree
    data = [];
    for ( var i = 0; i < data_sets.length; i++){
        data.push("/inputs/" + data_sets[i].name);
    }
    if (data.length > 0) create_data_set_jstree(data);

    // create config jstree
    data = [];
    for ( var i = 0; i < configs.length; i++){
        data.push("/configs/" + configs[i].name);
    }

    if (data.length > 0) create_config_jstree(data);
}