// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// render

frappe.listview_settings['Deal Counter'] = {
	add_fields: ["name",  "customer_name", "validity_dateline", "expiry_date"],
        selectable: true,
	get_indicator: function(doc) {
		if((doc.validity_dateline) < frappe.datetime.get_today() && ((doc.expiry_date) >= frappe.datetime.get_today())) {
			return [__("Active"), "green", "validity_dateline,<,Today|expiry_date,>=,Today"]
                } else if ((doc.validity_dateline) >= frappe.datetime.get_today() && ((doc.expiry_date) >= frappe.datetime.get_today())) {
			return [__("Follow Up"), "orange", "validity_dateline,>=,Today|expiry_date,>=,Today"]
		} else if ((doc.validity_dateline) < frappe.datetime.get_today() && ((doc.expiry_date) < frappe.datetime.get_today())) {
			return [__("Alert"), "red", "validity_date,<,Today|expiry_date,<,Today"]
                } else if ((doc.expiry_date) < frappe.datetime.get_today()) {
			return [__("Expired"), "red", "expiry_date,<,Today"]
		}
	}	
};
