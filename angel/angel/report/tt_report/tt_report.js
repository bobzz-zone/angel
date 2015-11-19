// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["TT Report"] = {
	"filters": [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
                        default: frappe.defaults.get_global_default('company')
		},
		{
			fieldname: "party",
			label: __("Party"),
			fieldtype: "Link",
			options: "Customer",
		},
		{
			fieldname: "party_account",
			label: __("Party Account"),
			fieldtype: "Link",
			options: "Account",
                        reqd: 1
		},
                {
			fieldname: "start_sales_invoice",
			label: __("Start SI No"),
			fieldtype: "Link",
			options: "Sales Invoice"
                },
                {
			fieldname: "end_sales_invoice",
			label: __("End SI No"),
			fieldtype: "Link",
			options: "Sales Invoice"
                },
	]
}
