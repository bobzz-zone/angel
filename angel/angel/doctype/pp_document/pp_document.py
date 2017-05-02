# -*- coding: utf-8 -*-
# Copyright (c) 2015, Korecent Solutions Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class PPDocument(Document):
	
        def validate(self):
                pass
        def on_submit(self):
                self.update_pp()

        def update_pp(self):
                tbl = self.outstanding_invoices or []
                for item in tbl:
                        voucher_no = item.against_voucher_no
                        name = self.name
                        if voucher_no:
                                frappe.db.sql(""" UPDATE `tabPurchase Invoice` SET pp_reference_number=%(val)s\
                                                        WHERE name=%(flag)s""" , {"flag":voucher_no, "val":name})
