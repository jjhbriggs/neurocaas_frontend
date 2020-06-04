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
function AjaxRequest(url, method='GET', data=null, spin=true){
    /*
        Async Ajax Module

        @params:
                url: endpoint,
                data: array,
                method: request method
        @return:
                array
    */

    if (spin) show_spinner();
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

