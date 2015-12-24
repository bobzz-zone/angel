frappe.listview_settings['Sales Order'] = {
	add_fields: ["base_grand_total", "customer_name", "currency", "delivery_date", "per_delivered", "per_billed",
		"status", "order_type"],
	get_indicator: function(doc) {
        if(doc.status==="Stopped") {
			return [__("Stopped"), "darkgrey", "status,=,Stopped"];

        } else if (doc.order_type !== "Maintenance"
			&& flt(doc.per_delivered, 2) < 100 && frappe.datetime.get_diff(doc.delivery_date) < 0) {
			// to bill & overdue
			return [__("Overdue"), "red", "per_delivered,<,100|delivery_date,<,Today|status,!=,Stopped"];

		} else if (doc.order_type !== "Maintenance"
			&& flt(doc.per_delivered, 2) < 100 && doc.status!=="Stopped") {
			// not delivered

			if(flt(doc.per_billed, 2) < 100) {
				// not delivered & not billed

				return [__("To Deliver and Bill"), "orange",
					"per_delivered,<,100|per_billed,<,100|status,!=,Stopped"];
			} else {
				// not billed

				return [__("To Deliver"), "orange",
					"per_delivered,<,100|per_billed,=,100|status,!=,Stopped"];
			}

		} else if ((doc.order_type === "Maintenance" || flt(doc.per_delivered, 2) == 100)
			&& flt(doc.per_billed, 2) < 100 && doc.status!=="Stopped") {

			// to bill
			return [__("To Bill"), "orange", "per_delivered,=,100|per_billed,<,100|status,!=,Stopped"];

		} else if((doc.order_type === "Maintenance" || flt(doc.per_delivered, 2) == 100)
			&& flt(doc.per_billed, 2) == 100 && doc.status!=="Stopped") {

			return [__("Completed"), "green", "per_delivered,=,100|per_billed,=,100|status,!=,Stopped"];
		}
	},
	onload: function(listview) {
		var method = "erpnext.selling.doctype.sales_order.sales_order.stop_or_unstop_sales_orders";
		//var delmethod = "erpnext.selling.doctype.sales_order.sales_order.make_delivery_note";
		//var delmethod = "erpnext.selling.doctype.sales_order.sales_order.update_multiple_dno";

		listview.page.add_menu_item(__("Set as Stopped"), function() {
			listview.call_for_selected_items(method, {"status": "Stop"});
		});

		listview.page.add_menu_item(__("Set as Unstopped"), function() {
			listview.call_for_selected_items(method, {"status": "Unstop"});
		});
//Angel#7: Added "Submit Delivery" menu button for multiple sales orders		
		listview.page.add_menu_item(__("Submit Delivery"), function() {
	        var me = this;
        	var selected = listview.get_checked_items() || [];
              	if(!selected.length) {
                	msgprint(__("Please select Sales Order"));
                  	return;
              	}	
              	else {
		/*	for(var i = 0; i<selected.length; i++){
				
                      		item = selected[i];
				//so = frappe.get_doc(item.name);
				listview.call_for_selected_items((delmethod, {item.name}), {"status": "Overdue"});
		*/		
			
		var item;
              	names = $.map(selected, function(d) { return d.name; });
              	frappe.call({
                        method: "erpnext.selling.doctype.sales_order.sales_order.update_multiple_dno",
                        args: {'so_list': names},
                        freeze: true,
                        callback: function(r) {
                                if(!r.exc) {
                                       // me.list_header.find(".list-select-all").prop("checked", false);
                                       //  me.refresh();
                                }
                        }
                });
			}
		//}


	});
}
};
