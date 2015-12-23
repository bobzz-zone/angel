frappe.ui.form.on("Deal Counter", { refresh:function(frm){

	if(frm.doc.docstatus == 1){
		frm.add_custom_button("View Usage", function(){
		frappe.route_options = {
			"name":frm.doc.name
			};
			frappe.set_route("query-report", "Deal Counter based Sales Orders");
		}).addClass("btn-primary");
	}	
}

});
