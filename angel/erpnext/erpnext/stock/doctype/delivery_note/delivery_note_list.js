frappe.listview_settings['Delivery Note'] = {
	add_fields: ["customer", "customer_name", "base_grand_total", "per_installed",
		"transporter_name", "grand_total", "is_return"],
	get_indicator: function(doc) {
		if(cint(doc.is_return)==1) {
			return [__("Return"), "darkgrey", "is_return,=,Yes"];
		} else if(doc.docstatus == 1 && doc.__onload && !doc.__onload.billing_complete) {
			return [__("Delivered but not Invoiced"), "red", "status,=,Submitted"];
		}
		 else if ((doc.docstatus == 1) && doc.__onload &&  doc.__onload.billing_complete) {
			return[__("Delivered and Invoiced"), "orange", "status,=,Submitted,billing_complete,=,True"];
		}		
	},

	onload: function(listview) {
		listview.page.add_menu_item(__("Make Combine Delivery"), function() { 
			var me = this;
			var lst = {};
			var name = [];
			var select = listview.get_checked_items() || [];
			if (!select.length) {
				msgprint(__("Please select Delivery Note"));
				return;
			}
			else {
				var count = 0;
				var tbl = select.length;
				doc_p = frappe.model.get_new_doc("Combine Deliveries");
				var  delivery_note = [];
				for(var i=0; i<select.length; i++){
					var doc_s = select[i].docstatus;
					if(doc_s != 0) {
						delivery_note.push(select[i].name)
					}
					count ++;
					if(count == tbl){
						frappe.call({
							"method":"angel.utils.get_delivery_items",
							"args": {"delivery_note":delivery_note},
							"async":false,
							"callback":function(r){
								console.log(r);
								if(r && r.message){
								$.each(r.message[0], function(k, v){	
								var doc_c = frappe.model.get_new_doc("Combine Delivery Item",  doc_p, "result_table");
                                                			$.extend(doc_c, {
                                                        	 	"delivery_note_number":v.parent,
									"item_name": v.item_code,
									"qty_for_delivery":v.qty,
									"price_of_item_as_per_qty":v.price_list_rate,
	                                                		});
								});
								var item_wise_qty = r.message[1] || {}
								for(var item in r.message[1]){
									item_detail = item_wise_qty[item]
									var doc = frappe.model.get_new_doc("CombineDelivery Itemwise", doc_p, "item_wise_quantities");
									$.extend(doc, {
										"item_code":item_detail.item_name,
										"item_qty_for_delivery":item_detail.qty
									});
								}
							}
							frappe.set_route("Form", "Combine Deliveries", doc_p.name);
						}
						});
						//frappe.set_route("Form", "Combine Deliveries", doc_p.name);
					}
				}
				
			}
		});
	}
};
