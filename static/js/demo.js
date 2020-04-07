
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
            if (res.dtset_logs.length > 0 ){
                var html = "";
                for ( i = 0; i < res.dtset_logs.length; i++){
                    html += '<div class="media"><p class="media-body mb-0 small lh-125 border-bottom border-gray">';
                    html += '<a href="../' + res.dtset_logs[i] + '" class="text-warning" target="_blank">';
                    html += get_file_name(res.dtset_logs[i]) + '</a></p></div>';
                }
                $('#dtset-result-view').html(html);
                $('.result-dataset').css('display', 'block');
            }

            if (processing_status)
                setTimeout(function(){
                    get_status(timestamp)
                }, 30000);
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

            if(res.result_links.length > 0) {
                processing_status = false;
                $('.spinner').css('display', 'none');

                $('.result-video').css('display', 'block');

                // show video result
                html = "";
                for (var i = 0 ; i < res.result_links.length ; i++){
                    html += '<div class="media"><p class="media-body mb-0 small lh-125 border-bottom border-gray">';
                    html += '<a href="../' + res.result_links[i] + '" class="text-warning" target="_blank">';
                    html += get_file_name(res.result_links[i]) + '</a></p></div>';
                }

                $('#video-result-view').html(html);
            }

            if (processing_status)
                setTimeout(function(){
                    get_results(timestamp)
                }, 30000);
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