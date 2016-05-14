// Copyright (c) 2013, Korecent Solutions Pvt Ltd and contributors
// For license information, please see license.txt

frappe.query_reports["Deal Counter based Sales Orders"] = {
	"filters": [
                {
                        "fieldname":"name",
                        "label": __("Deal Number"),
                        "fieldtype": "Link",
                        "options" : "Deal Counter",
                        "width": "80",
                        "reqd" : 1
                },
		{
			"fieldname" :"type",
			"label": __("Type"),
			"fieldtype": "Select",
			"options": "Sales Invoice\nSales Order",
			"default": "Sales Invoice",
			"width": "100"
		}
	]
}
