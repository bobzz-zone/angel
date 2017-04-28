// Copyright (c) 2013, Korecent Solutions Pvt Ltd and contributors
// For license information, please see license.txt

frappe.query_reports["Territory Based Undelivered Sales Order"] = {
        "filters": [
                {
                        "fieldname":"territory",
                        "label": __("Territory"),
                        "fieldtype": "Link",
                        "width": "80",
                        "options" : "Territory",
                        "reqd" : 1
                },

           ]
}

