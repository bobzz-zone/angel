// Copyright (c) 2013, Korecent Solutions Pvt Ltd and contributors
// For license information, please see license.txt

frappe.query_reports["PP Report"] = {
	"filters": [
		{
                   "fieldname":"company",
                   "label":__("Company"),
                   "fieldtype": "Link",
                   "options": "Company"
                },
		{
                   "fieldname":"supplier",
                   "label":__("Supplier"),
                   "fieldtype": "Link",
                   "options": "Supplier"
                },
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
                }
	]
}
