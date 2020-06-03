// show dataset and config file list
function get_tr_template(file, type, name, ind, flag=0){
	return '<tr onclick="show_detail(' + ind + ', ' + flag + ')"><td class="value">' + file + '</td><td><input type="' + type + '" name="' + name + '"></td>';
}

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

        var data_set_html = '';
        for ( var i = 0 ; i < data_sets.length ; i++)
            data_set_html += get_tr_template(data_sets[i].name, "checkbox", "dataset_file", i, 0)

        data_set_html === '' ? $('#data_set_table tbody').html(empty_template) : $('#data_set_table tbody').html(data_set_html);

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

        data_sets.length == 0 ? $('#data_set_folder').html(empty_template): null;
        configs.length == 0 ? $('#config_folder').html(empty_template): null;
    }
}

