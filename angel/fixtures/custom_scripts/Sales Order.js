frappe.ui.form.on("Sales Order Item", "price_list_rate", function(doc, cdt, cdn){
  var d = locals[cdt][cdn];

  var price_list = frappe.model.get_value("Sales Order Item", cdn, "price_list");
  if ( price_list == "" || ! price_list){
     frappe.model.set_value("Sales Order Item", cdn, "price_list_rate", 0.0);
     return;
  }

  var item_code = frappe.model.get_value("Sales Order Item", cdn, "item_code");
  frappe.model.get_value("Item Price", {
                     "item_code": item_code,
                     "price_list": price_list
                    }, 'price_list_rate', 
                    function(r){
                         frappe.model.set_value("Sales Order Item", cdn, "price_list_rate", r.price_list_rate);
                    });
   
 
  
  //cur_frm.fields_dict.items.grid.grid_rows_by_docname[cdn].refresh_field('price_list_rate');
});

frappe.ui.form.on("Sales Order Item", "price_list", function(doc, cdt, cdn){
       var d = locals[cdt][cdn];
       frappe.model.trigger("price_list_rate", 
                      frappe.model.get_value("Sales Order Item", cdn, "price_list_rate"), d);
 });