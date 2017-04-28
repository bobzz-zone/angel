# -*- coding: utf-8 -*-
# Copyright (c) 2015, Korecent Solutions Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json

class IncomingGiroTracker(Document):
	
	def autoname(self):
                giro = self.giro_number

                if not giro:
                        frappe.throw(_("Please Enter Giro Number"))
 
                name = frappe.db.get_value("Incoming Giro Tracker", filters={"giro_number":giro}, fieldname="name", as_dict=True)
                if name and name['name'] != self.giro_number:
                        frappe.throw(_("Giro Number Already Exists"))

                else :
                        self.name = giro

        def validate(self):
                if not hasattr(self, "__islocal"):
                        self.autoname()


@frappe.whitelist()
def create_incoming_giro(data=None):
        if not data:
                return
        res = None
        temp_data = None
        try:
                if isinstance(data, basestring):
                        data = json.loads(data)

                doc = frappe.get_doc(data)
                res = doc.save().as_dict()
                frappe.local.response.update({"data":res})
        except:
                frappe.local.response.update({"data":res})
