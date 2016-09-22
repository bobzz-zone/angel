# -*- coding: utf-8 -*-
# Copyright (c) 2015, Korecent Solutions Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _, msgprint, throw

class TTDocument(Document):

	'''
	def onload(self):
		lst = []
		grand_total = 0
		tbl = self.get("outstanding_invoices")
                dest = []
		for arr in tbl:
			against_v = arr.against_voucher_no
			val = frappe.db.get_value("Sales Invoice",{"name":against_v},"outstanding_amount")
                        grand_total += arr.total_amount
			arr.outstanding_amount = val
                        dest.append(arr)
	        self.set("outstanding_invoices", dest)
		self.set("grand_total", grand_total)
	'''		
	def validate(self):
		pass
	def on_submit(self):
		self.update_si()

	def update_si(self):
		table = self.outstanding_invoices or []
		for item in table:
			voucher_no = item.against_voucher_no
			name = self.name
			#frappe.msgprint(_("name = {0}").format(name))
			if voucher_no:
				frappe.db.sql(""" UPDATE `tabSales Invoice` SET tt_reference_number=%(number)s
							WHERE name=%(tt_name)s""" , {"number":name, "tt_name":voucher_no}) 
