# Copyright (c) 2013, Korecent Solutions Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint

def execute(filters=None):
        columns, data = [], []
        columns = get_columns(filters)
        enteries  = get_data(filters)
        for d in enteries:
                data.append([d.name, d.territory])

        return columns, data
def get_columns(filters):
        if not filters.get("territory"):
                msgprint(_("Please select the territory first"), raise_exception=1)


        return [
                _("Sales Order No") + ":Link/Sales Order:140",
                _("territory") + ":Link/Territory:140"]




def  get_data(filters):
     territory = filters["territory"]
     #frappe.msgprint( _("{0}".format( territory)))
     data = frappe.db.sql('''SELECT `name`, `territory`, `delivery_status`     
             FROM 
                 `tabSales Order`
             WHERE 
                  territory = "India" AND delivery_status = "Not Delivered"; ''' ,
             #filters["territory"],  
              as_dict = True)
     return data

