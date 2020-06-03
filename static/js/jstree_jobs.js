function create_job_tree(paths){
    /*
        Create Jstree with paths

        @params:
                paths: array of keys,
        @return:
                None
    */

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