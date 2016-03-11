import frappe
from frappe import _
from frappe.model.document import Document
class Test(Document):
	def validate(self):
		frappe.msgprint(_("Navdeep Here"))
		frappe.throw("Error")
