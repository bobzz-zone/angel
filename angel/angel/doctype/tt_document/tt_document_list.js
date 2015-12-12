frappe.listview_settings['TT Document'] = {
	add_fields: ["status", "total_amount", "sales_person"],
	selectable: true,
	get_indicator: function(doc) {
		if(doc.status=="Due for Payment") {
			return[__("Due for Payment"), "orange", "status,=,Due for Payment"];
		}
		else if((flt(doc.total_amount == 0))) {
			return[__("Settled"), "green", "status,=,Settled"];
		}
	},
	onload:function(doc){
//	//	console.log(doc);
//		 $(".primary-action").hide();
		 $(".btn-danger").show();	 
	}
	

};
