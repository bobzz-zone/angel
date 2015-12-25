# -*- coding: utf-8 -*-
# Copyright (c) 2015, Korecent Solutions Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class TTDocument(Document):

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
			
