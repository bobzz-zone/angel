# -*- coding: utf-8 -*-
# Copyright (c) 2015, Korecent Solutions Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class PrintDocumentSetting(Document):
	pass

def new_print_document_setting(dtype, dname, cur_val, max_val):
        doc = frappe.new_doc("Print Document Setting")
        doc.doctype = "Print Document Settting"
        doc.doctype_name = dtype
        doc.docname_name = dname
        doc.current_value = cur_val
        doc.max_value = max_val
        return doc
        
@frappe.whitelist()
def update_print_counter(dtype, name):
        frappe.msgprint(("chetan inside update_print_counter"))
        if not frappe.db.get_value("Print Doctype Setting", {'doctype_name': dtype}, "max_value"):
                frappe.throw(("This Doctype is not present in print Doctype Setting"))
                return
        max_val = frappe.db.get_value("Print Doctype Setting", {'doctype_name': dtype}, "max_value")
        doc = ''
        cur_val = 0
        try:
                cur_val = frappe.db.get_value("Print Document Setting", {'docname_name': name, 'doctype_name': dtype}, "current_value")
                if not cur_val:
                	raise 
	        doc = frappe.get_doc("Print Document Setting", {'docname_name': name, 'doctype_name': dtype})
                frappe.msgprint(frappe._("{0} chetan".format(doc)))
                doc.current_value = doc.current_value + 1
        except:
                doc = new_print_document_setting(dtype, name, 1, max_val)
        doc.save()
        frappe.db.commit()
        return doc.current_value
