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

	def on_update(self):
		self.update_delivery_note()

	def update_delivery_note(self):
		tbl = self.result_table
		for item in tbl:
			dn_name = item.delivery_note_number
			name = self.name
			if dn_name:
				frappe.db.sql("""UPDATE `tabDelivery Note` SET combined_reference_number = %(val)s
						WHERE name = %(flag)s """, {"flag":dn_name, "val":name})

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
	item_name_list = []
	for item in filtered_list:
		temp = get_items(item)
		item_list = temp[1]
		item_name_list = temp[0]
		if temp:
			if item_list:
				for data in item_list:
					new_data.append(data)
	new_data.sort()
	items = get_result_table_item(item_name_list, new_data)
	data = {}
	data["result_table"] = new_data
	data['result_table_item_wise'] = items
	return data

def get_items(delivery_number):
	records = []
	item_list = []
	item_name_list = []
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
				item_name_list.append(item['item_name'])
				item_list.append(temp_item)
	records.append(item_name_list)
	records.append(item_list)
	return records

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

def get_result_table_item(item_name_list, result_table_list):
	temp_list = []
	items = {}
	item_temp = {}
	if result_table_list:
		temp_list = list(set(item_name_list))
		for result in result_table_list:
			flag = items.has_key(result['item_name'])
			if flag:
				items[result['item_code']] += flt(result['qty_for_delivery'])
			if not flag:
				items[result['item_code']] = flt(result['qty_for_delivery'])
	items = [{"item_code":key, "qty_for_delivery":value} for key, value in items.iteritems()]
	return items
