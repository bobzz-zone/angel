# Copyright (c) 2013, Korecent Solutions Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt , cint , cstr

def execute(filters=None):
	columns, data = [], []
	if not filters: filters = {}
	columns = get_columns()
	items = get_data(filters)
	purchase_invoices = get_purchase_invoices(filters)

	for d in items:
		data.append([d.against_voucher_no, d.posting_date, d.supplier, d.supplier_type, "", "PP Document"])
	
	for d in purchase_invoices:
		data.append([d.name, d.posting_date, d.supplier, d.supplier_type, d.remarks, "Purchase Invoice"])
		
	return columns, data

def get_condition(filters):
        condition = ""
        if filters.get("company"): condition += "  and company=%(company)s"
        if filters.get("supplier"): condition += " and supplier=%(supplier)s"
	if filters.get("from_date") and filters.get("to_date"): condition += " and posting_date BETWEEN %(from_date)s AND %(to_date)s"
	return condition 

def get_columns():
        "Return columns based on filters"
        columns  = [
                _("Invoice")+":Link/Purchase Invoice:120", _("Posting Date")+":Data:150",_("Supplier Name")+":Data:120", _("Supplier Type")+":Data:150",
		_("Remarks")+":Data:200", _("Type")+":Data:200"
        ]
        return columns

def get_data(filters):
	condition = get_condition(filters)
	data_list = frappe.db.sql(""" SELECT PP.supplier, PP.supplier_type, PP.posting_date, PPD.against_voucher_no
				FROM `tabPP Document` PP, `tabPP Document Detail` PPD
				WHERE PP.name = PPD.parent AND PP.docstatus = 1 AND PPD.docstatus = 1 %s """%condition, filters, as_dict = 1)
	return data_list

def get_purchase_invoices(filters):
	condition = get_condition(filters)
	purchase_invoice = frappe.db.sql("""SELECT PI.supplier, PI.supplier_type, PI.posting_date, PI.name, PI.remarks
					FROM `tabPurchase Invoice` PI
					WHERE PI.docstatus = 1 %s """%condition, filters, as_dict = 1)
	return purchase_invoice
