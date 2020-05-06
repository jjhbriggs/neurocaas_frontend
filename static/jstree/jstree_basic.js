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
//            'plugins':["wholerow","checkbox"],
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

// create jstrees by data
function create_jstree(id, parent_id, paths){
    $('#' + id).remove();
    $("#" + parent_id).append('<div id="' + id + '"></div>');

    $('#' + id)
    .on("changed.jstree", function (e, data) {
        console.log(data);
        if(data.selected.length) {
            var full_path = data.instance.get_path(data.selected[0]).join('/').replace('results/', '');
            if (!full_path.includes('.')) return;
            console.log(full_path);
        }
    })
    .jstree({
        //'plugins':["wholerow","checkbox"],
        'plugins':["wholerow","checkbox"],
        'core' : {
            'data' : get_json_from_array(paths)
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
        data.push("/dataset/" + datasets[i].name);
    }
    create_jstree('dataset_folder', 'dataset_div', data);
}