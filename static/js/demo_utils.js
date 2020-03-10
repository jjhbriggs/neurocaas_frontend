// show dataset and config file list

function get_tr_template(file){
	return '<tr><td>' + file + '</td><td><input type="checkbox"></td>';
}

function refresh_databucket_list(){
	$.ajax({
		url: '/demo_bucket/',
		success: function(res){
			console.log(res);
			if (res.status == 200){
				var dataset_html = '';
				for ( var i = 0 ; i < res.datasets.length ; i++)
					dataset_html += get_tr_template(res.datasets[i])
				$('#dataset_table tbody').html(dataset_html);

				var config_html = '';
				for ( var i = 0 ; i < res.configs.length ; i++)
					config_html += get_tr_template(res.configs[i])
				$('#config_table tbody').html(config_html);

				// add eventlistener for each tr
				$('tr').click(function(event){
                    if (event.target.type !== 'checkbox') {
                        $(':checkbox', this).trigger('click');
                    }
				})
			}
		}
	})
}