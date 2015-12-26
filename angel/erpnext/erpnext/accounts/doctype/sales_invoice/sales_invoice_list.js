// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// render
frappe.listview_settings['Sales Invoice'] = {
	add_fields: ["customer", "customer_name", "base_grand_total", "outstanding_amount", "due_date", "company",
		"currency","sales_person", "is_return"],
	selectable: true,
	get_indicator: function(doc) {
		if(cint(doc.is_return)==1) {

			return [__("Return"), "darkgrey", "is_return,=,Yes"];
		} else if(flt(doc.outstanding_amount)==0) {
			return [__("Paid"), "green", "outstanding_amount,=,0"]
		} else if (flt(doc.outstanding_amount) > 0 && doc.due_date > frappe.datetime.get_today()) {
			return [__("Unpaid"), "orange", "outstanding_amount,>,0|due_date,>,Today"]
		} else if (flt(doc.outstanding_amount) > 0 && doc.due_date <= frappe.datetime.get_today()) {
			return [__("Overdue"), "red", "outstanding_amount,>,0|due_date,<=,Today"]
		}
	
	},
        onload: function(me){
		me.page.add_menu_item(__("Make TT Document"), function(){
		var selected = me.get_checked_items() || [];
			if(!selected.length) {
				msgprint(__("Please select Sales Invoice"));
				return;
			}
			else{
				var count = 0;
				var table_length = selected.length;
				var total_amount = 0;
				for(var i =0; i<selected.length;i++){
							var outstanding_amount = selected[i].outstanding_amount;
							var due_date = selected[i].due_date;
							var doc_status = selected[i].docstatus;
							var customer = selected[i].customer;
							var today = frappe.datetime.get_today();
							if((due_date > today && outstanding_amount > 0) || (due_date <= today && outstanding_amount > 0) && (doc_status != 0)){
							frappe.model.with_doctype("TT Document", function(){
								total_amount += outstanding_amount;
								var tbl = frappe.model.get_new_doc("TT Document");
								$.extend(tbl, {
                                                                        "customer":customer
                                                                });
								$.each(selected, function(i,d){
									var detail = frappe.model.get_new_doc("TT Document Detail", tbl, "outstanding_invoices");
									$.extend(detail, {
										//"against_voucher_type":"Sales Invoice",
										"against_voucher_no":d.name,
										"outstanding_amount":d.outstanding_amount,
										"total_amount":d.grand_total,
										"sales_person":d.sales_person
								});
							
							})
							count ++;
							if(count == table_length){
							frappe.set_route("Form", "TT Document", tbl.name);	
							}							
							})
							}
							else {
								msgprint(__("TT Document Can be Created for only Overdue and Unpaid Invoices"));
								break;
								return;
				
								}		
		}
		
			}	
			 	}, "icon-file-alt");
}
};



