from frappe.utils import flt, cint, cstr
import frappe
from frappe import _
import json

DATE_FORMAT = "%Y-%m-%d"
EMP_NAME = "EMP/0001"
START_DATE = "06-01-2016"
END_DATE = "12-01-2016"
APPLY_ON = "Employee"
SALES_INVOICE = "SINV-00008"
COMMISSION_RULE = 5


def calculate_sales_commission(outstanding_amount, grand_total, allocated_percentage, commission_rule):
	if not commission_rule:
		return 0
	commission = frappe.db.get_value("Commissions Rule", {"name":commission_rule}, fieldname = "*", as_dict = True)
	if not commission:
		return 0
	commission_percentage = commission["commission_rate"]
	if outstanding_amount == 0:
		total_commission = flt((grand_total*commission_percentage/100))
		return flt((total_commission*allocated_percentage/100))
	else:
		return 0

def add_commission(emp_id, from_date , end_date):
	if not emp_id or not from_date or not end_date:
		return 0	
	sales_invoice = frappe.db.sql("""SELECT  SI.commission_rule, SI.outstanding_amount, SI.grand_total, ST.allocated_percentage from `tabSales Invoice` SI inner join
		 `tabSales Team` ST on SI.name	= ST.parent WHERE ST.emp_id = '%s' and SI.posting_date >= '%s' and SI.posting_date <= '%s' and SI.docstatus = 1 
		and SI.outstanding_amount = 0 """%(emp_id, from_date, end_date), as_dict = True)
	if not sales_invoice:
		return 0
	calculated_commission = flt(0)
	for invoice in sales_invoice:
		outstanding_amount = invoice["outstanding_amount"]
		grand_total = invoice["grand_total"]
		allocated_percentage = invoice["allocated_percentage"]
		commission_rule = invoice["commission_rule"]
		calculated_commission = (calculated_commission + calculate_sales_commission(outstanding_amount, grand_total, allocated_percentage, commission_rule))
	return calculated_commission

@frappe.whitelist()
def get_delivery_items(delivery_note= None):
	items_details = []
	delivery_note = json.loads(delivery_note)
	if not delivery_note:
		return items_details
	if isinstance(delivery_note, list):
		items_details = frappe.db.sql("""SELECT item_code, item_name, qty, parent,price_list_rate from `tabDelivery Note Item` WHERE docstatus = 1 AND parent IN (%s) """%" ,".join(['%s']*len(delivery_note)), 
					tuple(name for name in delivery_note), as_dict =True)
	

	return items_details




def map_customer(item_code, parent, item_detail):
	customer = frappe.db.get_value("Delivery Note", filters={"name":parent}, fieldname=["customer", "customer_address"], as_dict= True)
	if customer:
		item_detail[item_code]['customer'] = customer['customer']
		item_detail[item_code]['customer_address'] = customer['customer_address']
	return item_detail		

def item_wise_qty(items_details):
	pass


def dict_to_list(items):
	data = []
	if not items:
		return data
	for key, val in items.iteritems():
		data.append(val)
	return data



def validate_delivery(l_doc, name):
	if not (l_doc and name):
		return l_doc
	s_doc_list = frappe.get_list("Delivery Note", filters={"is_return":1, "return_against":name, "docstatus":1}, fields="*")
	if not s_doc_list:
		return l_doc

	for item in s_doc_list:

		items = frappe.db.sql("""SELECT name, item_code, qty, rate, price_list_rate, amount from `tabDelivery Note Item` WHERE \
					parent = '%s'"""%(item.get("name")), as_dict=True)
		l_doc = update_parent(l_doc, item)
		if not items:
			continue
	
		for item in items:
			l_doc = update_item(item, l_doc)

	l_doc  = post_delivery_validation(l_doc)
	return l_doc



def update_item(item, doc):
	for idx in range(0,len(doc.items)):
		if doc.items[idx].item_code == item.item_code:
			doc.items[idx].qty += item.qty
			doc.items[idx].amount += item.amount
	return doc	

def update_parent(l_doc, s_doc):
	l_doc.grand_total += s_doc.get("grand_total")
	l_doc.total += s_doc.get("total")
	l_doc.rounded_total += s_doc.get("rounded_total")
	l_doc.total_taxes_and_charges = s_doc.get("total_taxes_and_charges")
	return l_doc

def post_delivery_validation(l_doc):
	for idx in range(0, len(l_doc.items)):
		item = l_doc.items[idx]
		if item.qty == 0:
			del l_doc.items[idx]
	return l_doc
