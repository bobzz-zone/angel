# -*- coding: utf-8 -*-
# Copyright (c) 2015, Korecent Solutions Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import ast
from frappe import _, msgprint, throw
import datetime

class GiroTracker(Document):
	pass

@frappe.whitelist()
def check_duplicate_entry(data):
        item = ast.literal_eval(data)
        active = item['active_giro']
        from_number = item['starting_giro_number']
        to_number = item['no_of_giros']
        if(from_number and to_number):
                filters = {}
                filters['from_number'] = from_number
                #filters['to_number'] = to_number
                flag = frappe.db.sql("""SELECT name, giro_number, status 
                                                FROM `tabGiro Series` 
                                        WHERE giro_number = %(from_number)s""", filters, as_dict=True)

                return (flag)

def update_giro_number_status(giro_name, series_name, giro_no, giro_date):
        if giro_name and series_name and giro_no:
                frappe.db.sql("""UPDATE `tabGiro Series` SET status = '%s' WHERE parent = '%s' AND name = '%s' """%("Processed", giro_name, series_name))

        if giro_date:
                days = frappe.db.get_value("Giro Tracker", {"name":giro_name}, "giro_validity")
                timeNow = datetime.datetime.now()
                anotherTime = timeNow + datetime.timedelta(days)
                expiry = anotherTime.strftime("%Y-%m-%d")
                frappe.db.sql("""UPDATE `tabGiro Series` SET giro_expire = '%s' WHERE parent = '%s' AND name = '%s' """%(expiry, giro_name, series_name))
