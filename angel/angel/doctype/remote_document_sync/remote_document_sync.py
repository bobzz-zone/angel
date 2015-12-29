# -*- coding: utf-8 -*-
# Copyright (c) 2015, Korecent Solutions Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from angel.tasks import sync_erp2_queue

class RemoteDocumentSync(Document):
	pass

@frappe.whitelist()
def sync_erp2(doc_list):
	sync_erp2_queue(doc_list)

