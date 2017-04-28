// Copyright (c) 2013, Korecent Solutions Pvt Ltd and contributors
// For license information, please see license.txt

frappe.query_reports["TT Report"] = {
	"filters": [
	        {
                        "fieldname":"from_date",
                        "label": __("From Date"),
                        "fieldtype": "Date",
                        "default": frappe.defaults.get_default("year_start_date"),
                        "width": "80"
                },
                {
                        "fieldname":"to_date",
                        "label": __("To Date"),
                        "fieldtype": "Date",
                        "default": get_today()
                },
                {
                        "fieldname":"customer",
                        "label": __("Customer"),
                        "fieldtype": "Link",
                        "options": "Customer"
                },
                {
                        "fieldname":"company",
                        "label": __("Company"),
                        "fieldtype": "Link",
                        "options": "Company",
                        "default": frappe.defaults.get_user_default("company")
                },
		{
			"fieldname":"brand",
			"label":"Brand",
			"fieldtype":"Link",
			"options":"Brand"
		} 

	]
}
