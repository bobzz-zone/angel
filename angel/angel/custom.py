from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class custom(Document):
	pass
@frappe.whitelist()
def overdue_invoice_check(doc,method):
	inv = frappe.db.sql("""select group_concat(name) from `tabSales Invoice` where outstanding_amount>0 and due_date<NOW() and customer="{}" group by customer""".format(doc.customer),as_list=1)
	for data in inv:
		frappe.throw("Ada Invoice yang belum lunas dan telah Overdue {}".format(data[0]))