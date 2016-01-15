from frappe.utils import flt, cint, cstr
import frappe
from frappe import _

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
