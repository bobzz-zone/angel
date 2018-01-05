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
def validate_dn_on_invoice(doc,method):
	#for item in doc.items:
	#	if item.delivery_note:
	if doc.is_return==1:
		return
	dn=""
	for row in doc.items:
		if row.delivery_note:
			if dn=="":
				dn = """ "{}" """.format(row.delivery_note)
			elif not row.delivery_note in dn:
				dn = """ {},"{}" """.format(dn, row.delivery_note)
	if dn=="":
		return
	data = frappe.db.sql("""select name,combined_reference_number, docstatus,workflow_state from `tabDelivery Note` where name IN ({}) """.format(dn),as_list=1)
	for row in data:
		if row[1]:
			if row[2]!=1 or row[3]!="Siap Kirim":
				frappe.throw("{} not valid".format(row[0]))

@frappe.whitelist()
def update_dn_on_update(doc,method):
	valupdate="Tertagih"
	if method=="on_cancel":
		valupdate="Siap Kirim"
	for item in doc.items:
		if item.delivery_note:
			frappe.db.sql("""UPDATE `tabDelivery Note` SET workflow_state = %(val)s
						WHERE name = %(flag)s """, {"flag":item.delivery_note, "val":valupdate})

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

