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
					var records = r.message || {"result_table":[], "result_table_item_wise":[]};
					var data = records['result_table']
					var item_wise_data = records['result_table_item_wise']
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
					for(var i=0; i<item_wise_data.length; i++){
						var child_doc = frappe.model.get_new_doc("CombineDelivery Itemwise", parent_doc, "item_wise_quantities");
						var item = item_wise_data[i];
						console.log(item);
						$.extend(child_doc,{
							"item_code": item.item_code,
							"item_qty_for_delivery": item.qty_for_delivery
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
					me.frm.clear_table("item_wise_quantities");
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
			
		

	},
"get_result_table_list": function(doc, cdt, cdn){
				var result_table = doc.result_table || [];
				var item_list = [];
				var item_name = "";
				var temp_item_name = "";
				var qty = 0;
				var temp_list = [];
				var element_tobe_remove = [];
				console.log("List Before", result_table);
				if(result_table.length > 0){
					for(var i=0; i<result_table.length-1; i++){
						if(i == 0){
							item_name = result_table[i].item_name;
							qty += flt(result_table[i].qty_for_delivery)
							element_tobe_remove = element_tobe_remove.concat(i);
							continue;
						}
							temp_item_name = result_table[i].item_name;
							if(temp_item_name == item_name){
								qty += flt(result_table[i].qty_for_delivery)
								element_tobe_remove = element_tobe_remove.concat(i)
							}
					}
				temp_list = temp_list.concat(qty);
				console.log("Element To be Remove ", element_tobe_remove);
				result_table = result_table.splice(element_tobe_remove, element_tobe_remove.length);
				console.log("List After", result_table);
				}
	},
"get_items_wise": function(doc, cdt, cdn){

		this.get_result_table_list(doc, cdt ,cdn);
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
