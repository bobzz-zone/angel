'''
ALL Whitelisted functions will be written here in common file
'''

import frappe
from frappe import msgprint,  _
from frappe.utils import flt


'''
Function to get by Applying filters of Product Bundle
Callled from Combine Deliveries Doctype Custom Script
'''

@frappe.whitelist()
def get_bundle_items(name=False):
	data_dict = {'items':[]}
	if not name :
		return data_dict

	items = frappe.db.get_values("Product Bundle Item", filters={"parent":name, "docstatus":0}, fieldname="*", as_dict=True)
	if items:
		data_dict['items'] = items

	return data_dict
