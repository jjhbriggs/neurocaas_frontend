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

var paths = [
    '/results/process_results/main_result.txt',
    '/results/process_results/supp_results/supp_analysis_overall.txt',
    '/results/process_results/supp_results/supp_diagnostic.txt',
    '/logs/log1.txt',
    '/logs/log2.txt',
]

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