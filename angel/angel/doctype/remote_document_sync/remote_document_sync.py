# -*- coding: utf-8 -*-
# Copyright (c) 2015, Korecent Solutions Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
#from angel.tasks import sync_erp2_queue

class RemoteDocumentSync(Document):
	#def autoname(self):
	#	self.name = self.doctype_name + "-" + self.source_document_name
	pass

@frappe.whitelist()
def sync_erp2(doc_list):
	pass
	#sync_erp2_queue(doc_list)

