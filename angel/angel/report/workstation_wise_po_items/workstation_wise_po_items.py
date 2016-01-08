# Copyright (c) 2013, Korecent Solutions Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
        columns = [
  {
    u'width': 300,
    u'fieldname': u'account',
    u'fieldtype': u'Data',
    u'label': u'Item'
  },
  {
    u'width': 150,
    u'fieldname': u'dec_2015',
    u'fieldtype': u'Decimal',
    u'label': u'Quantity'
  }
]
	data = get_data(filters)
	
	return columns, data

def get_data(filters):
	prod_orders = frappe.db.sql("""select DISTINCT po.name from `tabProduction Order` po where po.bom_no IS NOT NULL""")  if filters.get("prod_order") is None  else ((filters.get("prod_order"),),)

        data = []
	if not len(prod_orders):
		return []

	for prod_order in prod_orders:
		if not len(prod_order):
			continue
		prod_order = prod_order[0]
		data.append( {
			 'indent': 0.0,
			 'parent_account': None,
			 'dec_2015': 0,
			 'account': prod_order,
			 'account_name': prod_order
		     })

		items = frappe.db.sql("""select bi.item_workstation, bi.item_code, bi.qty
					 from `tabBOM Item` bi, `tabProduction Order` po
					 where po.bom_no = bi.parent AND
					       po.name = '%s' """ %(prod_order))

		if not len(items):
			continue

		workstations = {}
		for item in items:
			if not len(item):
				continue

			workstation, item, qty = item
			# require this hash for uniqueness of no
 			#it will generate a hash order of 10
			work_hash = frappe.generate_hash(workstation, 10)
			if workstations.has_key(workstation):
				work_hash = workstations[workstation]
                        else:
				workstations[workstation] = work_hash
				data.append({
					'indent': 1.0,
					'parent_account': prod_order,
					'dec_2015': 0,
					'account': work_hash,
					'account_name': workstation
				})
			data.append({
				'indent': 2.0,
				'parent_account': work_hash,
				'dec_2015': qty,
				'account': item,
				'account_name': item
			   })
	#frappe.msgprint((data))
	return data
