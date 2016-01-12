
frappe.ui.form.on("Petty Cash", { refresh: function(frm){
	var pay_for = frm.doc.pay_for;
	var amount =frm.doc.amount;
	var status = cint(frm.doc.docstatus);
	if(status == 1){
		frm.add_custom_button(__("Post To Journal"),function(frm){
			var JE = frappe.model.get_new_doc("Journal Entry");
			frappe.model.with_doctype("Journal Entry",function(){
			for(var i = 0; i < 2 ; i++){
			var child_doc_type = frappe.model.get_new_doc("Journal Entry Account", JE, "accounts"); 
				console.log(frm);
				if(i ==0){
				$.extend(child_doc_type,{
				"account": "Petty Cash A/C - BC",
				"debit_in_account_currency":amount
	});
}			else {
			$.extend(child_doc_type,{
				"account": pay_for,
				"credit_in_account_currency":amount
});
			}
		
}	
			frappe.set_route("Form", "Journal Entry", JE.name);
		
	})

}
 ).addClass("btn-primary");
		
	}


}});

