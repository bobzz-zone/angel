/*frappe.ui.form.on("Delivery Note Item", "price_list_rate", function(doc, cdt, cdn){
  var d = locals[cdt][cdn];
//  debugger;

  //var price_list_rate = frappe.model.get_value("Delivery Note Item", cdn, "price_list_rate");
   
  var price_list = frappe.model.get_value("Delivery Note Item", cdn, "price_list");
  if (price_list == "" || ! price_list){
     return;
  }
  var item_code = frappe.model.get_value("Delivery Note Item", cdn, "item_code");
  frappe.model.get_value("Item Price", {
                     "item_code": item_code,
                     "price_list": price_list
                    }, 'price_list_rate', 
                    function(r){
                         frappe.model.set_value("Delivery Note Item", cdn, "price_list_rate", r.price_list_rate);
                    }
   };
 // set_value: ,

  frappe.call({
    method: 'frappe.client.get_value',
    args: {
        'doctype': 'Item Price',
        'fieldname': 'price_list_rate',
        'filters': {
                     "item_code": item_code,
                     "price_list": price_list
                    }
                   
    },
   callback: function(res){
    console.log(res);
    if ( res.message){ 
      if (res.message.price_list_rate) {
     
             //cur_frm.fields_dict.items.grid.grid_rows_by_docname[cdn].refresh_field('price_list_rate');
      }    
    } 
   }
  });

  frappe.model.get_value("Item Price", 
  //cur_frm.fields_dict.items.grid.grid_rows_by_docname[cdn].refresh_field('price_list_rate');
});

*/

frappe.ui.form.on("Delivery Note Item", "price_list_rate", function(doc, cdt, cdn){
  var d = locals[cdt][cdn];

  var price_list = frappe.model.get_value("Delivery Note Item", cdn, "price_list");
  if ( price_list == "" || ! price_list){
     frappe.model.set_value("Delivery Note Item", cdn, "price_list_rate", 0.0);
     return;
  }
  var item_code = frappe.model.get_value("Delivery Note Item", cdn, "item_code");
  frappe.model.get_value("Item Price", {
                     "item_code": item_code,
                     "price_list": price_list
                    }, 'price_list_rate', 
                    function(r){
                         frappe.model.set_value("Delivery Note Item", cdn, "price_list_rate", r.price_list_rate);
                    });
   
 
  
  //cur_frm.fields_dict.items.grid.grid_rows_by_docname[cdn].refresh_field('price_list_rate');
});

frappe.ui.form.on("Delivery Note Item", "price_list", function(doc, cdt, cdn){
       var d = locals[cdt][cdn];

       frappe.model.trigger("price_list_rate", 
                      frappe.model.get_value("Delivery Note Item", cdn, "price_list_rate"), d);
 });
