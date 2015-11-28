# -*- coding: utf-8 -*-
# Copyright (c) 2015, Korecent Solutions Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

#frappe.require("assets/erpnext/js/utils.js");

class DealCounter(Document):
	 def validate(self):
         #add validation on carry_fwd table to not have more than 4 items of ref deal counter numbers
                 lst = self.get("carry_fwd")
                 if(len(lst) > 4):
			 frappe.throw(("You can only insert 4 rows"))
	
#create 'View Usage' custom button to view related Sales orders with the current Deal Counter

#frappe.ui.form.on("Deal Counter", {
#	refresh: function(frm) {
#		if(frm.doc.docstatus==1) {
#			frm.add_custom_button(_('View Usage'), function() {
#				frappe.route_options = {
#					"deal_num": frm.doc.name,
#					"date": frm.doc.date,
#					"company": frm.doc.company
#				};
#				frappe.set_route("query-report", "Sales order by DealNum");
#				}, "icon-table");
#			}
#	}
#});
