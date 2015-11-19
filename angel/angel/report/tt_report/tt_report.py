# Copyright (c) 2013, Korecent Solutions Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
from erpnext.accounts.utils import get_account_currency
import json

def execute(filters=None):
	columns, data = [], []
        ret_data = get_outstanding_vouchers(filters)
        print ret_data
	return columns, data

def get_columns(filters):
        if not filters.get("party") and filters.get("party_account"):
                msgprint(_("Please select party and party account"), raise_exception=1)


        return [_("Sales Invoice No") + ":Link/Sales Invoice:140",
                _("Date") + ":Date:100",
                _("Amount") + ":Currency:140"
               ]


def get_orders_to_be_billed(party_type, party, party_account_currency, company_currency):
        voucher_type = 'Sales Order' if party_type == "Customer" else 'Purchase Order'

        ref_field = "base_grand_total" if party_account_currency == company_currency else "grand_total"

        orders = frappe.db.sql("""
                select
                        name as voucher_no,
                        ifnull({ref_field}, 0) as invoice_amount,
                        (ifnull({ref_field}, 0) - ifnull(advance_paid, 0)) as outstanding_amount,
                        transaction_date as posting_date
                from
                        `tab{voucher_type}`
                where
                        {party_type} = %s
                        and docstatus = 1
                        and ifnull(status, "") != "Stopped"
                        and ifnull({ref_field}, 0) > ifnull(advance_paid, 0)
                        and abs(100 - ifnull(per_billed, 0)) > 0.01
                """.format(**{
                        "ref_field": ref_field,
                        "voucher_type": voucher_type,
                        "party_type": scrub(party_type)
                }), party, as_dict = True)

        order_list = []
        for d in orders:
                d["voucher_type"] = voucher_type
                order_list.append(d)

        return order_list

def get_outstanding_vouchers(filters):
        from erpnext.accounts.utils import get_outstanding_invoices
        
        amount_query = ""
        args = filters
        amt_date = ""
        party_account_currency = get_account_currency(args.get("party_account"))
        company_currency = frappe.db.get_value("Company", args.get("company"), "default_currency")
        if not args.get("start_sales_invoice"):
                amt_date += "posting_date >= '" + str(args.get("start_sales_invoice")) + "' and "
        if not args.get("end_sales_invoice"):
                amt_date += "posting_date <= '" +  str(args.get("end_sales_invoice")) + "' and" 

        if args.get("party_type") == "Customer":
                amount_query += "ifnull(debit_in_account_currency, 0) - ifnull(credit_in_account_currency, 0)"
        elif args.get("party_type") == "Supplier":
                amount_query += "ifnull(credit_in_account_currency, 0) - ifnull(debit_in_account_currency, 0)"
        else:
                frappe.throw(_("Please enter the Against Vouchers manually"))

        # Get all outstanding sales /purchase invoices
        all_outstanding_vouchers = []
        outstanding_voucher_list = frappe.db.sql("""
                select
                        voucher_no, voucher_type, posting_date,
                        ifnull(sum({amount_query}), 0) as invoice_amount
                from
                        `tabGL Entry`
                where
                        %s account = %s and party_type=%s and party=%s and {amount_query} > 0
                        and (CASE
                                        WHEN voucher_type = 'Journal Entry'
                                        THEN ifnull(against_voucher, '') = ''
                                        ELSE 1=1
                                END)
                group by voucher_type, voucher_no
                """.format(amount_query = amount_query), (amt_date, args.get("party_account"),
                args.get("party_type"), args.get("party")), as_dict = True)

        for d in outstanding_voucher_list:
                payment_amount = frappe.db.sql("""
                        select ifnull(sum({amount_query}), 0)
                        from
                                `tabGL Entry`
                        where
                                %s account = %s and party_type=%s and party=%s and {amount_query} < 0
                                and against_voucher_type = %s and ifnull(against_voucher, '') = %s
                        """.format(**{
                        "amount_query": amount_query
                        }), (amt_date, account, party_type, party, d.voucher_type, d.voucher_no))
                payment_amount = -1*payment_amount[0][0] if payment_amount else 0
                precision = frappe.get_precision("Sales Invoice", "outstanding_amount")

                if d.invoice_amount > payment_amount:

                        all_outstanding_vouchers.append({
                                'voucher_no': d.voucher_no,
                                'voucher_type': d.voucher_type,
                                'posting_date': d.posting_date,
                                'invoice_amount': flt(d.invoice_amount, precision),
                                'outstanding_amount': flt(d.invoice_amount - payment_amount, precision)
                        })




        #outstanding_invoices = get_outstanding_invoices(amount_query, args.get("party_account"),
        #        args.get("party_type"), args.get("party"))

        # Get all SO / PO which are not fully billed or aginst which full advance not paid
        orders_to_be_billed = get_orders_to_be_billed(args.get("party_type"), args.get("party"),
                party_account_currency, company_currency)
        return all_outstanding_vouchers + orders_to_be_billed

