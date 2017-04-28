# Copyright (c) 2013, Korecent Solutions Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _

def execute(filters=None):
	columns, data = [], []
        columns = get_columns(filters)
	entries = []
	doctype = filters['type']
	if doctype == "Sales Order":
        	entries = get_sales_order(filters)
	else:
		entries = get_sales_invoice(filters)
        for d in entries:
		data.append([d.name, d.deal_number, d.total])
	return columns, data


def get_columns(filters):
	doctype = filters['type']
	if doctype == 'Sales Order':

	        return [
        	        _("Sales Order No") + "::140",
                	_("Deal Number") + "::140",
                	_("Total Amount") + ":Currency:140"
              	 	]
	else:
		return[
			_("Sales Invoice No") + "::140",
			_("Deal Number") + "::140",
			_("Total Amount") + ":Currency:140"
			]

def get_sales_order(filters):
	args = {}
        args['deal_number'] = filters["name"]
        SO = frappe.db.sql("""SELECT SO.`name`, SO.`deal_number`, SO.`total`
			FROM `tabSales Order` SO WHERE SO.deal_number = %(deal_number)s AND   SO.docstatus = 1""" , 
             args, as_dict = 1)
	
        return SO

def get_sales_invoice(filters):
	args = {}
	args['deal_number'] = filters['name']
	SI = frappe.db.sql("""SELECT SI.name, SI.total, SI.deal_number FROM
				`tabSales Invoice` SI WHERE SI.deal_number=%(deal_number)s AND docstatus = 1""",
				args, as_dict=True)
	
	return SI


        

def map_data(so, si):
	if not so:
		return []
	frappe.msgprint("So = {}".format(so))
	frappe.msgprint("si ={}".format(si))
	for so, si in zip(so, si):
		print so
		print si
	return []
