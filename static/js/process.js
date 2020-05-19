/* get file name from url */
function get_file_name(url){
    return url === null ? "" : url.split("/").slice(-1)[0]
}

/* function to show processing status from certificate.txt */
function get_status(timestamp){
    url = "/get_results/?timestamp=" + timestamp;
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
    url = "/get_results/";
    $.ajax({
        url: url,
        method: "POST",
        data: {
            timestamp: timestamp
        },
        success: function(res){
            console.log(res);

            if (res.data_set_logs.length > 0 ){
                dtset_logs = res.data_set_logs;
                $('.result-dataset').css('display', 'block');
                update_jstree();
            }

            if(res.result_links.length > 0) {
                results_links = res.result_links;

                if (res.end){
                    // set the processing status to FALSE
                    processing_status = false;
                    $('.spinner').css('display', 'none');

                    $('.result-video').css('display', 'block');
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
        refresh_databucket_list();
        dataset_area.clear_status();
        config_area.clear_status();
    }, 700);
}

function download_cert(){
    var path = '/static/downloads/' + timestamp + "/certificate.txt";
    document.getElementById('_iframe').href = path;
    document.getElementById('_iframe').click();
}