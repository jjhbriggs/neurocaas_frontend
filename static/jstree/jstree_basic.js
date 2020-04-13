// Insert path into directory tree structure:
function insert(children = [], [head, ...tail]) {
    let child = children.find(child => child.text === head);
    if (!child) {
        head.includes('.') ? children.push(child = {text: head, children: [], icon: 'jstree-file'}) : children.push(child = {text: head, children: []})


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

function create_jstree(paths){
    $('#hierarchy').remove();
    console.log('removed');
    $("#hierarchy_div").append('<div id="hierarchy"></div>');
    $('#hierarchy')
        .on("changed.jstree", function (e, data) {
            if(data.selected.length) {
                alert('The selected node is: ' + data.instance.get_node(data.selected[0]).text);
            }
        })
        .jstree({
            'core' : {
                'data' : get_json_from_array(paths)
            }
        });
}

function update_jstree(){
    var paths = [];

    dtset_logs.forEach(function(item){
        paths.push('/results/' + item.path);
    })

    results_links.forEach(function(item){
        paths.push('/results/' + item.path);
    })

    create_jstree(paths);
}
