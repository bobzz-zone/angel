# Copyright (c) 2013, Korecent Solutions Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
        data  = [
  {
    u'account': u'Application of Funds (Assets) - OCF',
    u'indent': 0.0,
    u'parent_account': None,
    u'from_date': '2015-01-01',
    u'to_date': '2015-12-31',
    u'dec_2015': u'',
    u'account_name': u'Application of Funds (Assets)'
  },
  {
    u'account': u'Current Assets - OCF',
    u'indent': 1.0,
    u'parent_account': u'Application of Funds (Assets) - OCF',
    u'from_date': '2015-01-01',
    u'to_date': '2015-12-31',
    u'dec_2015': 150.0,
    u'account_name': u'Current Assets'
  },
  {
    u'account': u'Accounts Receivable - OCF',
    u'indent': 2.0,
    u'parent_account': u'Current Assets - OCF',
    u'from_date': '2015-01-01',
    u'to_date': '2015-12-31',
    u'dec_2015': 150.0,
    u'account_name': u'Accounts Receivable'
  },
  {
    u'account': u'Debtors - OCF',
    u'indent': 3.0,
    u'parent_account': u'Accounts Receivable - OCF',
    u'from_date': '2015-01-01',
    u'to_date': '2015-12-31',
    u'dec_2015': 150.0,
    u'account_name': u'Debtors'
  },
  {
    u'account': None,
    u'account_name': u"'Total (Debit)'",
    u'dec_2015': 150.0
  },
  {
    
  }
]

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
	workstations = frappe.db.sql("""select DISTINCT bi.item_workstation 
                                        from `tabBOM Item` bi""")
	#workstations = frappe.db.sql("""select DISTINCT bi.item_workstation, bi.parent, po.name from `tabBOM Item` bi, `tabProduction Order` po where po.bom_no = bi.parent""")
        data = []
        if not workstations:
		return []
	
	for workstation in workstations:
                if not len(workstation):
                	continue
                workstation = workstation[0]
		data.append( {
                                 'indent': 0.0,
                                 'parent_account': None,
                                 'dec_2015': 0,
                                 'account': workstation,
                                 'account_name': workstation
                             })

                prod_orders = frappe.db.sql("""select DISTINCT po.name 
                                               from `tabProduction Order` po, `tabBOM Item` bi
                                               where po.bom_no = bi.parent AND
                                                     bi.item_workstation = '%s'""" %(workstation))
                if not len(prod_orders):
			continue
		for prod_order in prod_orders:
			if not len(prod_order):
				continue
			prod_order = prod_order[0]
			data.append( {
                                 'indent': 1.0,
                                 'parent_account': workstation,
                                 'dec_2015': 0,
                                 'account': prod_order,
                                 'account_name': prod_order
                             })
                        #items = frappe.db.sql("""select DISTINCT operation from `tabProduction Order Operation` where parent= '%s'""" %(prod_order))
                        items = frappe.db.sql("""select DISTINCT bi.item_code, bi.qty 
                                                 from `tabBOM Item` bi, `tabProduction Order` po 
                                                 where po.bom_no = bi.parent AND
                                                       bi.item_workstation = '%s' AND
                                                       po.name = '%s' """ %(workstation, prod_order))

 			if not len(items):
				continue
                        for item in items:
				if not len(item):
					continue
				item, qty = item
				data.append({
					'indent': 2.0,
					'parent_account': prod_order,
					'dec_2015': qty,
					'account': item,
					'account_name': item
                                   })
	#frappe.msgprint((data))
	return data
