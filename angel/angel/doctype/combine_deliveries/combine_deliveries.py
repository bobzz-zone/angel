# -*- coding: utf-8 -*-
# Copyright (c) 2015, Korecent Solutions Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.utils import flt
from frappe import _
from frappe.model.document import Document

class CombineDeliveries(Document):
	def validate(self):
		flag = self.check_status()
		if(flag):
			self.status ="Delivered"
		else:
			self.status = "Partially Shipped"
	def check_status(self):
		flag = True;
		result_table = self.result_table  or []
		for result in result_table:
			qty = flt(result.qty_pending_delivery)
			if(qty):
				flag = False
				break
			else:
				flag = True
		return flag

@frappe.whitelist()
def get_delivery_note(data=None):
	new_data = []
	record_list = []
	filtered_list= []
	customer_list = []
	territory_list = []
	if not data:
		return new_data
	else:
		data = json.loads(data)
		customer_list = data['customer']
		territory_list = data['territory']
	customers = frappe.db.sql("""SELECT name from `tabDelivery Note` WHERE customer IN (%s) AND docstatus = 1""" \
				%', '.join(['%s']*len(customer_list)),tuple([name for name in customer_list]), as_list = True)

	territory = frappe.db.sql("""SELECT  name from `tabDelivery Note` WHERE  territory IN (%s) AND docstatus = 1""" \
				%', '.join(['%s']*len(territory_list)), tuple([name for name in territory_list]), as_list = True)
	new_data = customers + territory
	for record in new_data:
		for dn in record:
			record_list.append(dn)
	filtered_list = set(record_list)
	filtered_list = list(filtered_list)
	new_data = []
	for item in filtered_list:
		item_list = get_items(item)
		if item_list:
			for data in item_list:
				new_data.append(data)
	new_data.sort()
	return new_data	

def get_items(delivery_number):
	item_list = []
	if delivery_number:
		items = frappe.db.get_values("Delivery Note Item", filters = {"parent":delivery_number, "docstatus":1}, fieldname="*", as_dict =True)
		if items:
			for item in items:
				temp_item = {}
				if item['qty'] < 0:
					continue
				temp_item['delivery_note_number'] = item['parent']
				temp_item['item_name'] = item['item_name']
				temp_item['qty_for_delivery'] = item['qty']
				temp_item['item_code'] = item['item_code']
				temp_item['price_list_rate'] = item['price_list_rate']
				item_list.append(temp_item)
	return item_list

@frappe.whitelist()
def make_return_deliveries(source_name_list, target_doc = None):
	if "erpnext" in frappe.get_installed_apps():
		from erpnext.controllers.sales_and_purchase_return import make_return_doc
		import json
		source_name_list = json.loads(source_name_list)
		lst = set(source_name_list)
		lst = list(lst)
		if source_name_list:
			for name in lst:
				doc  = make_return_doc("Delivery Note", name, target_doc)
				try:
					doc.save()
					frappe.db.commit()
				except:
					print frappe.get_traceback()		
