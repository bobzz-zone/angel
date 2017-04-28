# Copyright (c) 2013, Korecent Solutions Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt , cint , cstr

def execute(filters=None):
	columns, data = [], []
	if not filters:
		filters = {}

	columns = get_columns()
	items = get_data(filters)
	
	for d in items:
		data.append([d.giro_number, d.customer_name, d.account, d.date_of_issue, d.expiry_date, d.giro_amount])

	return columns, data

def get_condition(filters):
	condition = ""
	if filters.get("customer_name"):
		condition += "and customer_name=%(customer_name)s"
	if filters.get("from_date") and filters.get("to_date"):
		condition += "and date_of_issue BETWEEN %(from_date)s AND %(to_date)s"
	return condition

def get_columns():
	columns = [
		_("Giro Number")+":Data:150", _("Customer Name")+":Data:150", _("Bank Name")+":Data:150", _("Date Of Issue")+":Data:150",
			_("Expiry Date")+":Data:150", _("Amount")+":Data:150"
	]
	return columns

def get_data(filters):
	condition = get_condition(filters)
	data_list = frappe.db.sql(""" SELECT IGT.giro_number, IGT.customer_name, IGT.account, IGT.date_of_issue, IGT.expiry_date, IGT.giro_amount
					FROM `tabIncoming Giro Tracker` IGT
					WHERE IGT.docstatus = 0 %s """%condition, filters, as_dict = 1)
	return data_list
