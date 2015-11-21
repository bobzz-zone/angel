# Copyright (c) 2013, Korecent Solutions Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _

def execute(filters=None):
	columns, data = [], []
        columns = get_columns(filters)
        data = get_data(filters) 
	return columns, data


def get_columns(filters):
        if not filters.get("name"):
                msgprint(_("Please select Deal Number first"), raise_exception=1)


        return [
                _("Sales Order No") + ":Link/Sales Order:140",
                _("Deal Number") + ":Link/Deal Counter:140",
                _("Total Amount") + ":Link/Currency:140"
               ]

def get_data(filters):
        deal_no = filters["name"]
        data = frappe.db.sql("""SELECT `name`, `deal_number`, `total`     
             FROM 
                 `tabSales Order`
             WHERE 
                  deal_number = %s; """ , 
             deal_no, as_dict = True)
        return data
        
