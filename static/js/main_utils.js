/* get file name from url */
function get_file_name(url){
    return url === null ? "" : url.split("/").slice(-1)[0]
}

function hide_spinner(){
    $('#spinner').css('display', 'none');
}

function show_spinner(){
    $('#spinner').css('display', 'block');
}

// Async Ajax Request
function AjaxRequest(url, method='GET', data=null){
    /*
        Async Ajax Module

        @params:
                url: endpoint,
                data: array,
                method: request method
        @return:
                array
    */
    show_spinner();
    return new Promise((resolve, reject) => {
       $.ajax({
            url : url,
            method : method,
            data : data,
            success :  function(res){
                hide_spinner();
                resolve(res);
            },
            error: function(err){
                hide_spinner();
                reject();
            }
       });
    });
}


function download_cert(){
    if (!processing_status){
        alert('Please start process first.');
        return;
    }
    
    var path = 'results/' + ana_prefix + timestamp + "/logs/certificate.txt";
    download_file(path, ana_id);
}


function show_detail(ind, type){
    if (!detail_flag) return;
    var content = "";
    if (type === 0){
        content += 'Name: ' + data_sets[ind].name + '\n\n';
        content += 'Size: ' + data_sets[ind].size + '\n\n';
        content += 'Date modified: ' + data_sets[ind].date_modified + '\n';
    } else {
        content += 'Name: ' + configs[ind].name + '\n\n';
        content += 'Date modified: ' + configs[ind].date_modified + '\n\n';
        content += configs[ind].content + '\n';
    }
    $('#status-text').html(content)
}

async function refresh_bucket(){
    var loading_template = "<tr><td>loading ...</td></tr>";
    var empty_template = "<tr><td> No files found. </td></tr>";

    $('#data_set_folder').html(loading_template);
    $('#config_folder').html(loading_template);

    var url = '/user_files/' + ana_id;
    var res = await AjaxRequest(url);
    console.log(res);

    if (res.status == 200){
        configs = res.configs;
        data_sets = res.data_sets;


        refresh_data_jstrees();

        data_sets.length == 0 ? $('#data_set_folder').html(empty_template): null;
        configs.length == 0 ? $('#config_folder').html(empty_template): null;
    }
}

