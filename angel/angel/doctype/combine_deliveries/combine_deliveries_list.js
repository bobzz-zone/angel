frappe.listview_settings['Combine Deliveries'] = {
	add_fields: ["company", "status", "date", "branch", "employee_handling"],
	selectable: true,
	get_indicator: function(doc){
		if(doc.status == "Delivered"){
			return [__("Delivered"), "green", "status,=,Delivered"]
		}
		else if(doc.status == "Partially Shipped"){
			return [__("Partially Shipped"), "orange", "status,=,Partially Shipped"]
		}
		
	}
};
