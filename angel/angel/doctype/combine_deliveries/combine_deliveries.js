frappe.provide('frappe.msgprint');
frappe.provide('frappe._');
$.extend(cur_frm.cscript, {
"refresh": function(doc, cdt, cdn){
		var me = this;
		var flag = doc.__islocal == undefined ? true:false;
		if(flag){
			me.frm.add_custom_button("Make Sales Return", this.make_sales_return).addClass("btn-primary");
		}
},

"get_items" : function(doc, cdt ,cdn){
		var me = this;
		var customer_terr = doc.cust_and_terr || [];
		var lst = {};
		var customer =[];
		var territory =[];
		this.validate_table(doc,cdt, cdn);
		if(customer_terr.length ==0){
			msgprint(frappe._("Please add atleast one filter"));
			return
		}
		else{
			for(var i=0; i<customer_terr.length; i++){
				customer.push(customer_terr[i].customer);
				territory.push(customer_terr[i].territory);	
			}
			lst.customer = customer;
			lst.territory = territory;
		}
		frappe.call({
			method: "angel.angel.doctype.combine_deliveries.combine_deliveries.get_delivery_note",
			args : {"data":lst},
			callback: function(r){
				if(r && r.message){
					var parent_doc = frappe.model.get_doc("Combine Deliveries", doc.name);
					var data = r.message || [];
					for(var i=0;i<data.length;i++){
						var child_doc = frappe.model.get_new_doc("Combine Delivery Item", parent_doc, "result_table");
						var item = data[i]
						$.extend(child_doc, {
							"delivery_note_number": item.delivery_note_number,
							"item_name": item.item_name,
							"qty_for_delivery": item.qty_for_delivery,
							"price_of_item_as_per_qty" : item.price_list_rate
						});
					}
					me.frm.refresh()

				}
			}
		});
	},
"validate_table": function(doc, cdt, cdn){
			var table = cur_frm.doc.result_table || [];
			if(table){
				if (table.length > 0){
					me.frm.clear_table("result_table");
					me.frm.refresh();
				}
			}
	},
"make_sales_return" : function(){
		var lst = []
		var save_doc = cur_frm.doc.result_table || [];
		if(save_doc.length > 0){
			for(var i=0; i<save_doc.length; i++){
				var flag = save_doc[i].__islocal == undefined?true:false;
				if(flag){
					var return_qty = flt(save_doc[i].qty_pending_delivery);
					if(return_qty == 0) continue;
					lst.push(save_doc[i].delivery_note_number)
				}
				else{
					frappe.throw(frappe._("Please save document its modified after you've opened it"))
					return
				}
			}
			frappe.call({
				method: "angel.angel.doctype.combine_deliveries.combine_deliveries.make_return_deliveries",
				args: {"source_name_list":lst}
			});
		}
	},

"qty_pending_delivery": function(doc, cdt, cdn){
			var me = this;
			var flag  = doc.result_table || false;
			if(flag){
				var frm = cur_frm.fields_dict['result_table']['grid']['grid_rows_by_docname'][cdn];
				var price_list_rate = frm.doc.price_of_item_as_per_qty || 0;
				var pending_qty = frm.doc.qty_pending_delivery;
				var qty = frm.doc.qty_for_delivery;
				var status_field = frm.fields_dict['individual_delivery_status']
				if(!this.validate_qty(flt(qty), flt(pending_qty),status_field)) return;
				var field = frm.fields_dict['affected_qty_rate'];
				var pending_qty_field = frm.fields_dict['qty_pending_delivery'];
				pending_qty_field.set_value(-(flt(pending_qty_field.value)));
				field.set_value(-(flt(price_list_rate)* flt(pending_qty)));
			}
			
	},
"validate_qty": function(actual_qty, return_qty, ind_field){
			if(actual_qty<return_qty){
				frappe.msgprint(frappe._("Return quantity must be less than actual quantity"));
				return false;
			}
			else if(return_qty != 0){
				ind_field.set_value("Partial Delivered")
				return true;
			}
			else if(return_qty == 0){
				ind_field.set_value("Delivered");
				return true;
			}
			
		

	}
});
/*
frappe.ui.form.on("Combine Delivery Item",{
"qty_pending_delivery": function(frm, cdt, cdn){
			var flag  = frm.doc.result_table || false;
			alert(flag);
			if(flag){
				alert();
				var frm = cur_frm.fields_dict['result_table']['grid']['grid_rows_by_docname'][cdn];
				var price_list_rate = frm.doc.price_of_item_as_per_qty || 0;
				var pending_qty = frm.doc.qty_pending_delivery;
				var field = frm.fields_dict['affected_qty_rate'];
				field.set_value(-(flt(price_list_rate)* flt(pending_qty)))
			}
			
	}
});
*/
