# -*- coding: utf-8 -*-
# Copyright (c) 2015, Korecent Solutions Pvt Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _ 
from frappe.model.document import Document

class PettyCash(Document):

        def before_save(self):
                amount = self.get("amount")
                posting_date = self.get("posting_date")
                pay_for = self.get("pay_for")
                received_by = self.get("received_by")
		if  frappe.db.get_value("Petty Cash", {"amount":amount, "posting_date":posting_date, "pay_for":pay_for, "received_by":received_by}, "name", as_dict = True):
                        frappe.throw("You can't create duplicate doctype")
	
	def validate(self):
		  amount = self.get("amount")
                  posting_date = self.get("posting_date")
                  pay_for = self.get("pay_for")
                  received_by = self.get("received_by")
                  if  frappe.db.get_value("Petty Cash", {"amount":amount, "posting_date":posting_date, "pay_for":pay_for, "received_by":received_by, "docstatus":1}, "name", as_dict = True):
                         frappe.throw(_("You can't create duplicate doctype"))
'''
@frappe.whitelist()
def get_account_detail(payfor):
	if payfor:
		frappe.db.get_value("Account", filters = {"
	return "Navdeep"
'''
