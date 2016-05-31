# -*- coding: utf-8 -*-
# Copyright (c) 2015, Korecent Solutions Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint, flt
from frappe.model.document import Document

class DealCounter(Document):
	def validate(self):
		amt = flt(self.credit_limit)
		if(amt < 0.0):
			frappe.throw("Please Select Different Customer having  more Zero credit Limit")

@frappe.whitelist()
def get_customer_deal(customer_name = None):
	data = []
	if not customer_name:
		return data
	deals = frappe.db.get_values("Deal Counter", filters= {"customer_name": customer_name, "docstatus":1}, fieldname ="*", as_dict = True)
	if not deals:
		return data
	for item in deals:
		d = {}
		d['name'] = item['name']
		d['deal_amount'] = item['new_deal_amt']
		data.append(d)
	return data

def update_balance_amt(sales_order_name=None):
	if not sales_order_name:
		return
	bal = 0.0
	DN = ""
	SO = frappe.db.get_value("Sales Order", filters={"name":sales_order_name, "docstatus":1}, fieldname="*", as_dict = True)
	if SO:
		bal = flt(SO['base_rounded_total'])
		DN = SO['deal_number']
		if not DN:
			return
		DN_amt = frappe.db.get_value("Deal Counter", filters ={"name":DN},fieldname="*", as_dict = True);
		if not DN_amt:
			return
		DN_bal = flt(DN_amt['balance_amt'])
		val = DN_bal - bal
		frappe.db.sql("""UPDATE `tabDeal Counter` SET balance_amt = %s WHERE name = '%s'"""%(val, DN))
		frappe.db.commit()

def update_dn_bal(sales_invoice_name = None, cancel=False):
	if not sales_invoice_name:
		return
	items = []
	if cancel:
		items  = frappe.db.get_values("Sales Invoice Item", filters= {"parent":sales_invoice_name, "docstatus":2}, fieldname ="*", as_dict = True)
	if not cancel:
		items  = frappe.db.get_values("Sales Invoice Item", filters= {"parent":sales_invoice_name, "docstatus":1}, fieldname ="*", as_dict = True)
	if not items:
		return
	sales_order = None
	for item in items:
		if not item['sales_order']:
			continue
		else:
			sales_order = item['sales_order']
	if not sales_order:
		return
	sales_data = frappe.db.get_value("Sales Order", filters={"name":sales_order, "docstatus":1}, fieldname="*", as_dict= True)
	if not sales_data:
		return
	if not sales_data['deal_number']:
		return
	amt = flt(sales_data['base_rounded_total'])
	dn = sales_data['deal_number']
	dn_amt = frappe.db.get_value("Deal Counter", filters = {"name":dn, "docstatus":1}, fieldname ="*", as_dict = True)
	if not dn_amt:
		return
	if cancel:
		dn_bal = flt(dn_amt['balance_amt']) + amt
		frappe.db.sql("""UPDATE  `tabDeal Counter` SET balance_amt = %s WHERE name = '%s'"""%(dn_bal, dn))
	if not cancel:
		dn_bal = flt(dn_amt['balance_amt']) - amt
		frappe.db.sql("""UPDATE `tabDeal Counter` SET balance_amt = %s WHERE name = '%s'"""%(dn_bal, dn))
	
		
