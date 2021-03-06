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
	def remove_dn(self):
		lists=[]
		for row in self.result_table:
			if row.delivery_note_number!=self.delivery_note:
				lists.append(row)
		self.result_table=[]
		for a in lists:
			det_item = self.append("result_table",{})
			det_item.delivery_note_number=a.delivery_note_number
			det_item.item = a.item
			det_item.item_name = a.item_name
			det_item.qty = a.qty
			det_item.rate = a.rate

	def add_delivery_note(self):
		if self.delivery_note:
			found =0
			#if self.result_table:
			#	for row in self.result_table:
			#		if row.delivery_note_number == self.delivery_note:
			#			found=1
			#			break
			if found==1:
				frappe.throw("Delivery Note Already exist.")
			else:
				data = frappe.db.sql("""select di.item_code,di.item_name,di.qty,di.rate,d.combined_reference_number from `tabDelivery Note Item` di 
					join `tabDelivery Note` d on di.parent = d.name 
					where di.parent = "{}" 
					and d.docstatus=1""".format(self.delivery_note),as_dict=1)
				for row in data:
					if row['combined_reference_number']:
						frappe.throw("Cannot add Deliery Note that already in another Combine Delivery Document.")
					det_item = self.append("result_table",{})
					det_item.delivery_note_number=self.delivery_note
					det_item.item = row['item_code']
					det_item.item_name = row['item_name']
					det_item.qty = row['qty']
					det_item.rate = row['rate']
		else:
			frappe.throw("Delivery Note cannot be empty.")
	def validate(self):
		dn=""
		for row in self.result_table:
			if dn=="":
				dn = """ "{}" """.format(row.delivery_note_number)
			elif not row.delivery_note_number in dn:
				dn = """ {},"{}" """.format(dn, row.delivery_note_number)
		data = frappe.db.sql("""select name,combined_reference_number, docstatus,workflow_state from `tabDelivery Note` where name IN ({}) """.format(dn),as_list=1)
		for row in data:
			if row[1]:
				if row[2]!=1 or row[3]!="Siap Kirim":
					frappe.throw("{} not valid".format(row[0]))
	def on_submit(self):
		done=[]
		self.delivery_note=""
		for item in self.result_table:
			if item.delivery_note_number in done:
				continue
			stat = "Terkirim"
			dn = frappe.get_doc("Delivery Note",item.delivery_note_number)
			if dn.per_billed and dn.per_billed>0:
				stat="Tertagih"
			frappe.db.sql("""UPDATE `tabDelivery Note` SET workflow_state = %(val)s
						WHERE name = %(flag)s """, {"flag":item.delivery_note_number, "val":stat})
			done.append(item.delivery_note_number)
		self.update_delivery_note()
	def on_cancel(self):
		done=[]
		for item in self.result_table:
			if item.delivery_note_number in done:
				continue
			frappe.db.sql("""UPDATE `tabDelivery Note` SET workflow_state = %(val)s , combined_reference_number=""
						WHERE name = %(flag)s """, {"flag":item.delivery_note_number, "val":"Siap Kirim"})
			done.append(item.delivery_note_number)
#	def on_update(self):
#		self.update_delivery_note()

	def update_delivery_note(self):
		frappe.db.sql("""update `tabDelivery Note` set combined_reference_number="" where combined_reference_number="{}" """.format(self.name),as_list=1)
		tbl = self.result_table
		for item in tbl:
			if item.delivery_note_number:
				frappe.db.sql("""UPDATE `tabDelivery Note` SET combined_reference_number = %(val)s
						WHERE name = %(flag)s """, {"flag":item.delivery_note_number, "val":self.name})

	def get_items(self):
		packed_item={}
		parent_list=[]
		dn_list=[]
		for row in self.result_table:
			if row.delivery_note_number in dn_list:
				continue
			items = frappe.db.get_values("Delivery Note Item", filters = {"parent":row.delivery_note_number, "docstatus":1}, fieldname="*", as_dict =True)
			packed = frappe.db.get_values("Packed Item", filters = {"parent":row.delivery_note_number, "docstatus":1}, fieldname="*", as_dict =True)
			if packed:
				for item in packed:
					temp_item = {}
					if item['qty'] < 0:
						continue
					if item['item_code'] in packed_item:
						packed_item[item['item_code']]['qty']+=flt(item['qty'])
					else:
						packed_item[item['item_code']]={}
						packed_item[item['item_code']]['item_name'] = item['item_name']
						packed_item[item['item_code']]['qty'] = flt(item['qty'])
						packed_item[item['item_code']]['item_code'] = item['item_code']
					if not item['parent_item'] in parent_list:
						parent_list.append(item['parent_item'])
			if items:
				for item in items:
					if item['qty'] < 0:
						continue
					if not item['item_code'] in parent_list:
						if item['item_code'] in packed_item:
							packed_item[item['item_code']]['qty']+=flt(item['qty'])
						else:
							packed_item[item['item_code']]={}
							packed_item[item['item_code']]['item_name'] = item['item_name']
							packed_item[item['item_code']]['qty'] = flt(item['qty'])
							packed_item[item['item_code']]['item_code'] = item['item_code']
			dn_list.append(row.delivery_note_number)
		self.item_wise_quantities=[]
		for row in packed_item:
			det_item = self.append("item_wise_quantities",{})
			det_item.item_code=packed_item[row]['item_code']
			det_item.qty=packed_item[row]['qty']
			det_item.item_name=packed_item[row]['item_name']


