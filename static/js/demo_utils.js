// show dataset and config file list
function refresh_databucket_list(){
	$.ajax({
		url: '/demo_bucket/',
		success: function(res){
			console.log(res);
		}
	})
}