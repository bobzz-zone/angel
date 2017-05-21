from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import frappe.utils
from frappe.utils import flt

class custom(Document):
	pass
@frappe.whitelist()
def overdue_invoice_check(doc,method):
	inv = frappe.db.sql("""select group_concat(name) from `tabSales Invoice` where outstanding_amount>0 and due_date<NOW() and customer="{}" group by customer""".format(doc.customer),as_list=1)
	for data in inv:
		frappe.throw("Ada Invoice yang belum lunas dan telah Overdue {}".format(data[0]))

@frappe.whitelist()
def get_customer_outstanding(customer, company):
	# Outstanding based on GL Entries
	outstanding_based_on_gle = frappe.db.sql("""select sum(debit) - sum(credit)
		from `tabGL Entry` where party_type = 'Customer' and party = %s and company=%s""", (customer, company))

	outstanding_based_on_gle = flt(outstanding_based_on_gle[0][0]) if outstanding_based_on_gle else 0

	# Outstanding based on Sales Order
	outstanding_based_on_so = frappe.db.sql("""
		select sum(base_grand_total*(100 - per_billed)/100)
		from `tabSales Order`
		where customer=%s and docstatus = 1 and company=%s
		and per_billed < 100 and status != 'Closed'""", (customer, company))

	outstanding_based_on_so = flt(outstanding_based_on_so[0][0]) if outstanding_based_on_so else 0.0

	return {
	"outstanding_invoice":outstanding_based_on_gle,
	"outstanding_sales_order":outstanding_based_on_so
	}

