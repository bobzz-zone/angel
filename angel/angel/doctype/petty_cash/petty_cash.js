var PETTY_CASH;
var OTHER_ACCOUNT;
frappe.ui.form.on("Petty Cash", { refresh: function(frm){
	var pay_for = frm.doc.pay_for;
	var amount =frm.doc.amount;
	var posting_date = frm.doc.transaction_date;
	var status = cint(frm.doc.docstatus);
	if(status == 1){
		frm.add_custom_button(__("Post To Journal"),function(frm){	
			var JE = frappe.model.get_new_doc("Journal Entry");
			$.extend(JE,{
				"posting_date": date,
				"company": "OCF Furniture"
				});
			frappe.model.with_doctype("Journal Entry",function(){
			for(var i = 0; i < 2 ; i++){
			var child_doc_type = frappe.model.get_new_doc("Journal Entry Account", JE, "accounts"); 
				if(i ==0){
				get_account_balance("Petty Cash - OCF", posting_date, "OCF Furniture")
				$.extend(child_doc_type,{
				"account": "Petty Cash - OCF",
				"balance": PETTY_CASH.message.balance,
				"account_currency": PETTY_CASH.message.account_currency,
				"debit_in_account_currency":amount
		});
}			else {
			get_account_balance(pay_for, posting_date, "OCF Furniture")
			$.extend(child_doc_type,{
				"account": pay_for,	
				"balance": PETTY_CASH.message.balance,
				"account_currency": PETTY_CASH.message.account_currency,
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
/*
function get_account_detail(payfor){
	frappe.call({
		async: true,
		method: "angel.angel.doctype.petty_cash.petty_cash.get_account_detail",
		args: {"payfor": payfor},
		callback: function(r){
		if(r){
		alert("Navdeep is here");
		}
		}

	});
}
*/
function get_account_balance(account, posting_date, company){
	frappe.call({
		async: false,
		method: "erpnext.accounts.doctype.journal_entry.journal_entry.get_account_balance_and_party_type",
		args: {
                                account: account,
                                date: posting_date,
                                company: company,
                      },
		callback: function(r){
		if (r.message){
			
			PETTY_CASH = r;
		}
		}

	});
}	
