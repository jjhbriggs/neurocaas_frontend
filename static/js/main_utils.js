// show dataset and config file list

function get_tr_template(file, type, name, ind, flag=0){
	return '<tr onclick="show_detail(' + ind + ', ' + flag + ')"><td class="value">' + file + '</td><td><input type="' + type + '" name="' + name + '"></td>';
}

/* get file name from url */
function get_file_name(url){
    return url === null ? "" : url.split("/").slice(-1)[0]
}

function download_cert(){
    var path = '/static/downloads/' + timestamp + "/certificate.txt";
    document.getElementById('_iframe').href = path;
    document.getElementById('_iframe').click();
}

function show_detail(ind, type){
    if (!detail_flag) return;
    var content = "";
    if (type === 0){
        content += 'Name: ' + datasets[ind].name + '\n\n';
        content += 'Size: ' + datasets[ind].size + '\n\n';
        content += 'Date modified: ' + datasets[ind].date_modified + '\n';
    } else {
        content += 'Name: ' + configs[ind].name + '\n\n';
        content += 'Date modified: ' + configs[ind].date_modified + '\n\n';
        content += configs[ind].content + '\n';
    }
    $('#status-text').html(content)
}

function refresh_databucket_list(){
    var loading_template = "<tr><td>loading ...</td></tr>";
    var empty_template = "<tr><td> No files found. </td></tr>";

    $('#dataset_folder').html(loading_template);
    $('#config_folder').html(loading_template);

	$.ajax({
		url: '/get_user_files/',
		success: function(res){
			console.log(res);
			if (res.status == 200){
			    configs = res.configs;
			    datasets = res.data_sets;

				var dataset_html = '';
				for ( var i = 0 ; i < datasets.length ; i++)
					dataset_html += get_tr_template(datasets[i].name, "checkbox", "dataset_file", i, 0)

				dataset_html === '' ? $('#dataset_table tbody').html(empty_template) : $('#dataset_table tbody').html(dataset_html);

				var config_html = '';
				for ( var i = 0 ; i < configs.length ; i++)
					config_html += get_tr_template(configs[i].name, "radio", "config_file", i, 1)

                 config_html === '' ? $('#config_table tbody').html(empty_template) : $('#config_table tbody').html(config_html);

				// add eventlistener for each tr
				$('tr').click(function(event){
					if (event.target.type !== 'checkbox') {
                        $(':checkbox', this).trigger('click');                        
                    }

                    if (event.target.type !== 'radio') {
                        $(':radio', this).trigger('click');                        
                    }                    

                    if ($(this).find('input').is(":checked") === true){
                    	$(this).addClass('active');
                    }
                    else
                    	$(this).removeClass('active');

                    if ($(this).find('input[type="radio"]').val() === 'on'){
                        $('input[type="radio"]').parent().parent().removeClass('active');
                        $(this).addClass('active');
                    }
				})

				refresh_data_jstrees();

				datasets.length == 0 ? $('#dataset_folder').html(empty_template): null;
                configs.length == 0 ? $('#config_folder').html(empty_template): null;
			}
		}
	})
}

