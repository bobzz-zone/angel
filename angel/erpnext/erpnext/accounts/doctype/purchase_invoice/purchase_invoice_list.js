// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// render
frappe.listview_settings['Purchase Invoice'] = {
	add_fields: ["supplier", "supplier_name", "base_grand_total", "outstanding_amount", "due_date", "company",
		"currency", "is_return"],
	get_indicator: function(doc) {
		if(cint(doc.is_return)==1) {
			return [__("Return"), "darkgrey", "is_return,=,Yes"];
		} else if(flt(doc.outstanding_amount) > 0 && doc.docstatus==1) {
			if(frappe.datetime.get_diff(doc.due_date) < 0) {
				return [__("Overdue"), "red", "outstanding_amount,>,0|due_date,<,Today"];
			} else {
				return [__("Unpaid"), "orange", "outstanding_amount,>,0|due,>=,Today"];
			}
		} else if(flt(doc.outstanding_amount)==0 && doc.docstatus==1) {
			return [__("Paid"), "green", "outstanding_amount,=,0"];
		}
	},
	onload: function(me){
		me.page.add_menu_item(__("Make PP Document"), function(){
			var selected = me.get_checked_items() || {};
			if(!selected.length){
				msgprint(__("Please select Purchase Invoice"));
				return;
			}
			else{
				var count = 0;
				var table_length = selected.length;
				console.log(table_length);
				var total_amount = 0;
                                var flag = get_supplier(me);
				if(flag == false){
					msgprint(__("You Cannot Create PP Document for Different Supplier"));
					return;
				}
				else if(flag == true) {
					for(var i=0; i<selected.length; i++){
						console.log(selected);
						var outstanding_amount = selected[i].outstanding_amount;
						var posting_date = selected[i].due_date; console.log(posting_date);
						var doc_status = selected[i].docstatus;
						var supplier = selected[i].supplier;
						var comp = selected[i].company; console.log(comp);
						var today = frappe.datetime.get_today();
						if((posting_date > today && outstanding_amount > 0) || (posting_date <= today && outstanding_amount > 0) && (doc_status != 0)){
							frappe.model.with_doctype("PP Document", function(){	
								//total_amount += outstanding_amount;
								//console.log(posting_date);
								var tbl = frappe.model.get_new_doc("PP Document");
								$.extend(tbl, {
									"supplier":supplier,
									"company":comp,
									"posting_date":posting_date
								});
								$.each(selected, function(i,d){
									var detail = frappe.model.get_new_doc("PP Document Detail", tbl, "outstanding_invoices");
									$.extend(detail, {
										"against_voucher_no":d.name,
										"outstanding_amount":d.outstanding_amount,
										"total_amount":d.grand_total
									});
								})
								count = count +1;
								if(count == table_length){
									frappe.set_route("Form", "PP Document", tbl.name);
								}
							})
						}
						else {
							msgprint(__("PP Document Can be Created for only Overdue and Unpaid Invoices"));
							break;
							return;
						}
					}
				}
			}
		}, "icon-file-alt");	
	}
};

function get_supplier(list){
	var selected = list.get_checked_items() || [];
	var arr = new Array(selected.length);
	var count = 1;
	for(var i=0; i<selected.length; i++){
		arr[i] = selected[i].supplier;
	}
	if(arr.length == 1){
		return true;
	}
	else if(arr.length > 1) {
		for(var i=0; i<arr.length - 1; i++) {
			if(arr[i] == arr[i+1]) {
				count = count +1;
			}
		if(count == selected.length) {
			return true;
		}
		else{
			return false;
		}	
		}	
	}
}
