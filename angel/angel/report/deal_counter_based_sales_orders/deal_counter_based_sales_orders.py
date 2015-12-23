# Copyright (c) 2013, Korecent Solutions Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _

def execute(filters=None):
	columns, data = [], []
        columns = get_columns(filters)
        entries = get_data(filters) 
        for d in entries:
		data.append([d.name, d.deal_number, d.total])
	return columns, data


def get_columns(filters):
        return [
                _("Sales Order No") + "::140",
                _("Deal Number") + "::140",
                _("Total Amount") + ":Currency:140"
               ]

def get_data(filters):
        deal_no = filters["name"]
        data = frappe.db.sql("""SELECT `name`, `deal_number`, `total`     
             FROM 
                 `tabSales Order`
             WHERE 
                  deal_number = %s """ , 
             deal_no, as_dict = 1)
        return data
        
