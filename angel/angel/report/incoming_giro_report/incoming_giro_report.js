// Copyright (c) 2013, Korecent Solutions Pvt Ltd and contributors
// For license information, please see license.txt

frappe.query_reports["Incoming Giro Report"] = {
	"filters": [
                {
                        "fieldname":"customer_name",
                        "label":__("Customer"),
                        "fieldtype":"Link",
                        "options":"Supplier"
                },
                {
                        "fieldname": "from_date",
                        "label":__("From Date"),
                        "fieldtype": "Date",
			"width": "80"
                },
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80"
		}
	]
}
