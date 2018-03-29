# -*- coding: utf-8 -*-
# Copyright (c) 2015, Korecent Solutions Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _, msgprint, throw
from frappe.utils import  flt
class TTDocument(Document):

	
	def onload(self):
		lst = []
		grand_total = 0
		tbl = self.get("outstanding_invoices")
                dest = []
		om=0
		for arr in tbl:
			against_v = arr.against_voucher_no
			val = frappe.db.get_value("Sales Invoice",{"name":against_v},"outstanding_amount")
			grand_total += flt(arr.total_amount)
			arr.outstanding_amount = val
			dest.append(arr)
			om+=val
	        self.set("outstanding_invoices", dest)
		self.set("grand_total", grand_total)
		self.set("total_amount",om)
	def validate(self):
		found=0
		for row in self.outstanding_invoices:
			invoice = frappe.get_doc("Sales Invoice", row.against_voucher_no)
			row.invoice_due_date=invoice.due_date
			row.invoice_date = invoice.posting_date
			row.customer = invoice.customer
			row.sales_person = invoice.sales_team[0].sales_person
			if invoice.tt_reference_number and invoice.tt_reference_number!="":
				frappe.throw("Invoice {} sudah ada di TT Document {}".format(row.against_voucher_no,invoice.tt_reference_number))
			if self.sales_person!=row.sales_person:
				found=1
		if found==1:
			frappe.throw("Sales Person Tidak Sama")
	def on_submit(self):
		self.update_si()

	def on_cancel(self):
		frappe.db.sql(""" UPDATE `tabSales Invoice` SET tt_reference_number=""
							WHERE tt_reference_number=%(tt_name)s""" , {"tt_name":self.name})
	def update_si(self):
		table = self.outstanding_invoices or []
		for item in table:
			voucher_no = item.against_voucher_no
			name = self.name
			#frappe.msgprint(_("name = {0}").format(name))
			if voucher_no:
				frappe.db.sql(""" UPDATE `tabSales Invoice` SET tt_reference_number=%(number)s
							WHERE name=%(tt_name)s""" , {"number":name, "tt_name":voucher_no}) 
