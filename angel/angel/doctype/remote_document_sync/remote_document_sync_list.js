frappe.listview_settings['Remote Document Sync'] = { onload: function(cur_list){
	cur_list.page.add_inner_button("Sync", function(){
	var selected = cur_list.get_checked_items();
	var len = selected.length;
	if(!len){
		alert("Please Select Atleast One Item from List");
		return
	}
	else if(len){
		var source_document_name = "source_document_name";
		var doctype_name = "doctype_name";
		var document_status = "document_status";
		var data = [];
		for(var i = 0; i < len; i++){
			var item = selected[i];
			//data[i] = {source_document_name:item.source_document_name, doctype_name:item.doctype_name, document_status:item.document_status,"args":{"name":item.name,"target_document_name":item.target_document_name}}
			data[i] = { "name": item.name,
                                    "target_document_name": item.target_document_name,
                                    "doctype_name": item.doctype_name
                                  }
		        console.log(data);
		}
		
		frappe.call({
		type:"POST",
		method:"angel.angel.doctype.remote_document_sync.remote_document_sync.sync_erp2",
		args:{"doc_list":data},
		callback:function(rec){
			
			}
		});
	}
	

}).addClass("btn-primary");



}
}
