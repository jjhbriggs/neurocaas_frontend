/* function to show processing status from certificate.txt */
function get_status(timestamp){
    url = "/results/" + ana_id + "?timestamp=" + timestamp;
    $.ajax({
        url: url,
        success: function(res){
            console.log(res);
            $('#status-text').html(res.cert_file);
            if (res.cert_file !== '')
                $('#down_cert').removeClass('hidden');
            if (processing_status)
                setTimeout(function(){
                    get_status(timestamp)
                }, 10000);
        }
    })
}

/* function to show processing results from log and hp_optimum folder */
function get_results(timestamp){
    url = "/results/" + ana_id;
    $.ajax({
        url: url,
        method: "POST",
        data: {
            timestamp: timestamp
        },
        success: function(res){
            console.log(res);

            if(res.result_links.length > 0) {
                results_links = res.result_links;

                if (res.end){
                    // set the processing status to FALSE
                    processing_status = false;
                    $('.spinner').css('display', 'none');
                }
                update_jstree();
            }

            if (processing_status)
                setTimeout(function(){
                    get_results(timestamp)
                }, 20000);
        }
    })
}


function submit(){
    var data_set_files = [];
    var config_file = null;

    data_set_files = get_selected_nodes('data_set_folder', 'inputs/');

    if (data_set_files.length < 1) {
    	alert('Select dataset files');
    	return;
    }

    // get config file name
    config_files = get_selected_nodes('config_folder', 'configs/');

    if (config_files.length === 0) {
    	alert('Select config file');
    	return;
    }
    console.log(data_set_files, config_files[0]);

    $('#btn-spinner').css('display', 'inline-block');

    // set the processing status to TRUE
    processing_status = true;

    // disabled showing detail of dataset and config files
    detail_flag = false;


    $.ajax({
    	url: window.location.pathname,
    	method: 'POST',
    	data: {
    		data_set_files: data_set_files,
    		config_file: config_files[0]
    	},
    	success: function(res){
    	    $('#btn-spinner').css('display', 'none');
    		console.log(res)
    		timestamp = res.timestamp;
    		trigger_function(res.timestamp);
    	},
    	error: function(err){
    	    $('#btn-spinner').css('display', 'none');
    		console.log(err);
    		$('#submit_button').attr('disabled', false);
    	}
    })
    $('#submit_button').attr('disabled', true);
}


var trigger_function = function(timestamp){
    $('.spinner').css('display', 'block');
    setTimeout(function(){
        // timestamp = Math.floor(Date.now()/1000);
        get_status(timestamp);
        get_results(timestamp);
    }, 1000);
}

var submit_trigger = function(){
    setTimeout(function(){
        refresh_bucket();
        data_set_area.clear_status();
        config_area.clear_status();
    }, 700);
}