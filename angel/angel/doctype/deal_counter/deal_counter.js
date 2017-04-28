$.extend(cur_frm.cscript,{
	onload: function(doc, cdt, cdn){
		var me = this;
		cur_frm.add_fetch("tc_name", "terms", "terms");
		cur_frm.add_fetch("deal_num", "new_deal_amt", "deal_amt");
		var table_field = me.frm.get_field("carry_forward");
	}, 
	refresh:function(doc, cdt, cdn){
		var me = this;
		if(me.frm.doc.docstatus == 1){
			me.frm.add_custom_button("View Usage", function(){
			frappe.route_options = {
				"name":me.frm.doc.name
				};
				frappe.set_route("query-report", "Deal Counter based Sales Orders");
			}).addClass("btn-primary");
		}
		if(cint(doc.docstatus) == 1){
      			if ((cint(doc.balance_amt) > 0) && (date.nowdate() <= doc.validity_dateline)) {     
              			me.frm.page.add_inner_button("Create New Sales Order",function(){
                   		var doc = frappe.model.get_new_doc("Sales Order");
                    		$.extend(doc,{
                              		"customer": doc.customer_name,
                              		"deal_number": doc.docname
        			});
           			frappe.set_route("Form","Sales Order",doc.name);
				}).addClass("btn-primary");
      			}
		}
		flag = doc.__islocal == undefined?false:true;
		if(flag || doc.docstatus == 0){
			this.calculate_amount(doc, me.frm);	
		}
	},
	customer_name: function(doc, cdt, cdn){
		var me = this;
		var flag = false;
		var credit_limit = doc.credit_limit || 0;
		if(credit_limit < 0){
			frappe.msgprint(frappe._("Please Select Different customer  having  credit limit"));
			me.frm.set_value('customer_name', '');
		}
		else{
			var parent_doc = frappe.model.get_doc("Deal Counter", cdn);
			me.frm.clear_table("carry_forward");
			frappe.call({
				async : true,
				method: "angel.angel.doctype.deal_counter.deal_counter.get_customer_deal",
				args: {"customer_name":me.frm.doc.customer_name},
				callback: function(r){
					if(r.message){
						var deals = r.message || [];
						for(var i =0; i<deals.length; i++){
							doc = frappe.model.get_new_doc("Deal Counter Item", parent_doc, "carry_forward");
							doc.deal_num = deals[i].name;
							doc.deal_amt = deals[i].deal_amount;
						}
						cur_frm.refresh()
					
					}

				}
			});
		}
		
		
	},
	"carry_forward_add": function(doc, cdt, cdn){
			frappe.msgprint(frappe._("You cannot add row manually"));
			return;
	},
	"new_deal_amt": function(doc){

        	var credit_limit = cint(doc.credit_limit);
		var temp = cint(doc.new_deal_amt);
        	var new_deal_amt = flt(doc.new_deal_amt);
        	if(credit_limit < temp){
       			frappe.msgprint(frappe._("Credit Limit Can't be Less than New Deal Amount"));
       			cur_frm.set_value("new_deal_amt", 0.0);
			return;
        	}
		var used_deal_amt = flt(doc.used_deal_amt);
		var bal = new_deal_amt - used_deal_amt;
		cur_frm.set_value("balance_amt", bal);
	},
	"carry_forward_remove": function(doc){
		var me = this;
		this.calculate_amount(doc, me.frm);
	},
	"calculate_amount": function calculate(doc, frm){
		var table = doc.carry_forward || [];
		var total_amount = 0;
		for(var i = 0; i<table.length; i++){
			total_amount += table[i].deal_amt;
    		}
		if(table.length == 0){
			return;
		}
		frm.set_value("used_deal_amt", total_amount);
		var new_deal_amt = doc.new_deal_amt;
  		var used_amt = doc.used_deal_amt;
  		var balance_amt = cint(new_deal_amt - used_amt);
  		frm.set_value("balance_amt", balance_amt);
	}

});
