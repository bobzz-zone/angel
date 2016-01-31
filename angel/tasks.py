# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.celery_app import celery_task, task_logger
from frappe.frappeclient import FrappeClient
from frappe.tasks import run_async_task
import json


from frappe.celery_app import get_queue 

RSYNC_TASK_PREFIX = "rsync@" 
default_columns = ['name', 'creation', 'modified', 'modified_by', 'owner',
        'docstatus', 'parent', 'parentfield', 'parenttype', 'idx']
'''
MASTER_TABLE = ["Account", "Activity Cost", "Activity type", "Address", "Appraisal Template","Attendance", "Authorization Rule", "Batch", "Blog Category",
		"Blog Post", "Blogger", "BOM", "Branch", "Brand", "Campaign", "C-Form", "Comment", "Commissions Role", "Communication", "Company", "Contact",
		"Cost Center", "Country", "Currency Exchange", "Custom Field", "Custom Script", "Customer", "Customer Group", "Deduction Type", "Delivery Note",
		"Department", "Designation", "DocShare", "Earning Type", "Employee", "Employment Type", "Expense Claim Type", "File", "Fiscal Year", "Holiday List",
		"Industry Type", "Item", "Item Attribute", "Item Attribute Value", "Item Group", "Item Price", "Item Variant", "Item Variant Attribute", "Journal Entry",
		"Lead", "Leave Allocation", "Leave Block List", "Leave Type", "Material Request", "Mode of Payment", "Newsletter List", "Newsletter List Subscriber",
		"Offer Letter", "Offer Term", "Operation", "Opportunity", "Petty Cash", "Price List", "Pricing Rule", "Print Heading", "Product Bundle", "Production Order",
		"Project", "Purchase Invoice", "Purchase Order", "Purchase Taxes and Charges Template", "Quotation", "Quotation Lost Reason", "Salary Structure","Sales Invoice",
		"Sales Order", "Sales Partner", "Sales Person", "Sales Taxes and Charges Template", "Serial No", "Standard Reply", "Stock Entry", "Supplier", "Supplier Quotation",
		"Supplier Type", "Task", "Tax Rule", "Terms and Conditions", "Territory", "Time Log", "UOM", "User", "Warehouse", "Warranty Claim", "Website Theme", 
		"Workflow Document State", "Workflow State", "Workstation", "DocShare", "DocField", "DocType", "DocPerm", "Role"]
'''

MASTER_TABLE = ["Account", "Activity Type", "Address", "Appraisal Template", "Branch", "Brand", "Comment", "Communication", "Company",
                "Contact", "Country", "Customer", "Customer Group", "Deduction Type", "Designation", "Earning Type", "Employee",
                "Employment Type", "Expense Claim Type", "Fiscal Year", "Industry Type", "Item", "Item Attribute", "Item Group",
		"Item Price", "Leave Type", "Mode of Payment", "Offer Term", "Operation list", "Price List", "Sales Person", "Supplier",
                "Supplier Type", "Territory", "UOM", "User", "Warehouse", "Website Theme", "Workflow Document State",
                "Workflow State", "Workstation"]

EXTRA_TABLE = ["Time Log", "Task", "Comment", "GL Entry", "DocShare", "User", "Bin", "Role", "File", "Custom Script", "Custom Field", "DocPerm", "Property Setter", "Customize Form", "DocField", "DocType" ]

ITEM_TABLE = ["About Us Team Member", "Appraisal Goal", "Appraisal Template Goal", "Bank Reconciliation Detail", "Block Module", "BOM Explosion Item", "BOM Item", "BOM Operation",
		"Budget Detail", "C-Form Invoice Detail", "Company History", "Customize Form Field", "Deal Counter Item", "DefaultValue", "Delivery Note Item", "Dependent Task",
		 "DocField", "DocPerm", "Email Alert Recipient", "Employee Education", "Employee External Work History", "Employee Internal Work History", "Employee Leave Approver",
		 "Event Role", "Expense Claim Detail", "Fiscal Year Company", "Holiday", "Installation Note Item", "Item Attribute Value", "Item Customer Detail",
		 "Item Quality Inspection Parameter", "Item Reorder", "Item Supplier", "Item Tax", "Item Variant", "Item Variant Attribute", "Item Website Specification", 
		 "Journal Entry Account", "Landed Cost Item", "Landed Cost Purchase Receipt", "Landed Cost Taxes and Charges", "Leave Block List Allow", "Leave Block List Date", 
		 "Maintenance Schedule Detail", "Maintenance Schedule Item", "Maintenance Visit Purpose", "Material Request Item", "Mode of Payment Account", 
		 "Monthly Distribution Percentage", "Offer Letter Term", "Opportunity Item", "Packed Item", "Packing Slip Item", "Page Role", "Party Account",
		 "Payment Reconciliation Invoice", "Payment Reconciliation Payment", "Payment Tool Detail", "Price List Country", "Product Bundle Item", "Production Order Operation",
		 "Production Plan Item", "Production Plan Sales Order", "Project Task", "Purchase Invoice Advance", "Purchase Invoice Item", "Purchase Order Item", 
		 "Purchase Order Item Supplied", "Purchase Receipt Item", "Purchase Receipt Item Supplied", "Purchase Taxes and Charges", "Quality Inspection Reading", "Quotation Item",
		 "Salary Slip Deduction", "Salary Slip Earning", "Salary Structure Deduction", "Salary Structure Earning", "Sales Invoice Advance", "Sales Invoice Item",
		 "Sales Order Item", "Sales Taxes and Charges", "Sales Team", "Shipping Rule Condition", "Shipping Rule Country", "SMS Parameter", "Stock Entry Detail", 
		 "Stock Product Detail", "Stock Reconciliation Item", "Supplier Quotation Item", "Target Detail", "Task Depends On", "Time Log Batch Detail", "Top Bar Item",
		 "TT Document Detail", "UOM Conversion Detail", "UserRole", "Web Form Field", "Website Item Group", "Website Slideshow Item", "Workflow Document State",
		 "Workflow Transition", "Workstation Working Hour"]

NOT_SYNCABLE = MASTER_TABLE + ITEM_TABLE + EXTRA_TABLE
# chetan for reference
'''
abc = doc.as_json(doc)frappe.as_json(doc)
        if isinstance(doc, basestring):
                doc = json.loads(doc)

        doc = frappe.get_doc(doc)

'''
# New Document type
#Remote Document Sync
class RsyncTaskRouter(object):
        def route_for_task(self, task, args=None, kwargs=None):
                if hasattr(frappe.local, 'site'):
                        if kwargs and kwargs.get("event", "").endswith("_rsync"):
                                return get_queue(frappe.local.site, RSYNC_TASK_PREFIX)

                return None


# New Document type
#Remote Document Sync
def add_rm_sync_doc(name, doctype, source_name, docstatus, target_name=''):
	rm_doc_sync =  frappe.new_doc("Remote Document Sync")
	rm_doc_sync.name = name
	rm_doc_sync.doctype_name = doctype
	rm_doc_sync.source_document_name = source_name
	rm_doc_sync.document_status = docstatus
	rm_doc_sync.remote_sync_status = 0
	rm_doc_sync.target_document_name = target_name
        return rm_doc_sync

debug = 0 

@celery_task()
def insert_sync_document(doc_dict):

	if debug:
        	frappe.msgprint(frappe.form_dict)
        if not frappe.conf.has_key('sync_server_ip') or frappe.conf.sync_server_ip == "":
                return

        if not frappe.form_dict: # and not frappe.form_dict.doc:
		return 

	doc_dict = json.loads(doc_dict)	
	name = doc_dict['name']
	doctype = doc_dict['doctype']
	# Removed Non Syncable docs
	if doc["doctype"] in NOT_SYNCABLE:
		return

	docstatus = doc_dict['docstatus']

        if ( not frappe.form_dict.has_key('sync_document_erp2') or 
             not frappe.form_dict['sync_document_erp2'] ): #and not (method=="after_insert" or method=="on_update")
        	return

        rm_doc_name = frappe.get_value("Remote Document Sync",
                                  { 'name': name,
                                    'doctype_name': doctype
                                  },
                                  fieldname='name')
 	frappe.form_dict['sync_document_erp2'] = 0
	if debug:
        	frappe.msgprint(("chetan"))
        if (rm_doc_name):
		rm_doc = frappe.get_doc("Remote Document Sync", rm_doc_name)
	        rm_doc.remote_sync_status = 0
                rm_doc.document_status = docstatus
		rm_doc.save()
               
        else:
        	rm_doc = add_rm_sync_doc(name, doctype, name, docstatus)
		rm_doc.save()
	
        frappe.db.commit()		
	pass

def update_rm_sync_doc(name, target_name = None, document_status = None, remote_sync_status = 0):
	if not name:
		frappe.msgprint("{0} not defined".format(name))
		return
	doc = frappe.get_doc("Remote Document Sync", name)
 	doc_dict = doc.as_dict()
	if target_name: 
		doc_dict["target_document_name"] = target_name
	if document_status:
		doc_dict["document_status"] = document_status
	doc_dict["remote_sync_status"] = remote_sync_status
	doc.update(doc_dict)
	doc.save()
	frappe.db.commit()
	return doc

def sync_document(docs, method):
	client = ''
        # Get User and Password from Database
        user = (frappe.session and frappe.session.user) or doc_dict['modified_by'] or "Administrator" 
        pwd = frappe.db.sql("""select password from __Auth where user=%s;""",(user))
        if not pwd:
                return False

        pwd = pwd[0][0]
        try:
        	client = FrappeClient(frappe.conf.sync_server_ip, user, pwd)
        except:
                frappe.msgprint(("Auth Error"))
                return

        if not client:
                return 
	res = ''
        if method == "bulk_update":
		docs = update_dl(docs)
 		return client.bulk_update(docs)
	else:
		return client.save(docs)

"""
 Get Child Table that are Matched with below Constant List
"""
PREVDOC_DOCTYPE = ['Maintenance Schedule', 'Purchase Order', 'Purchase Receipt', 'Quotation', 'Supplier Quotation', 'Installation Note']
def get_child_table(doctype):
	DOCTYPE = PREVDOC_DOCTYPE
	DATA = []
	TABLE = {}
	if doctype:
		new_doc = frappe.new_doc(doctype)
		if new_doc.meta.get_table_fields():
			for table in new_doc.meta.get_table_fields():
				table_doctype = table.options
				if table_doctype.find(" Item") > 0:
					parent_doc = table_doctype.replace(" Item", "")
					if parent_doc in DOCTYPE:
						TABLE["fieldname"] = table.fieldname
						TABLE["options"] = table.options
						DATA.append(TABLE)
	return DATA

'''Get Target Document Name , Only for
Those docs Which are already Synced with Sync Server '''
def get_target_document(docname):
	TARGET = {}
	if docname:
		values = frappe.db.get_value("Remote Document Sync",
                                                filters= {"source_document_name" : docname,
                                                          "remote_sync_status" : 1},
                                                filedname = "*", as_dict = True)
		if values:
			TARGET = values
	return TARGET

'''Update Prevdoc_docname only for those which are Matched with below constant  List '''
def update_parent(docs):
	ret_list = []
	ROWS = []
        for doc in docs:
		if doc['doctype'] not in PREVDOC_DOCTYPE:
			ret_list.append(doc)
		else:
			doctype = doc["doctype"]
			if doctype:
				data = get_child_table(doctype)
				if data:
					table = data[0]
					fieldname = table["fieldname"]
					table_data = doc[fieldname]
					if table_data:
						for row in table_data:
							if row["prevdoc_docname"]:
								target = get_target_document(row["prevdoc_docname"])
								if target:
									row["prevdoc_docname"] = target["target_document_name"]
							ROWS.append(row)
						doc[fieldname] = ROWS
			ret_list.append(doc)
	return ret_list

"""
 Update Dynamic Link
"""
def update_dl(docs):
	error_msg = []
	modified_docs = []
	if not docs:
		docs
	for doc in docs:
		doctype = doc["doctype"]
		new_doc = frappe.get_doc({"doctype":doctype})
		ref = get_ref_field(new_doc)
		fieldname = ""
		table_name = ""
		tables = []
		if ref:
			data = ref[0]
			fieldname = data["fieldname"]
			table_name = data["tabfieldname"]
			modified_table = []
			if doc.has_key(table_name):
				tables = doc[table_name]
				for table in tables:
					tab_fieldname = table[fieldname]
					if tab_fieldname:
						target_doc = frappe.db.get_value("Remote Document Sync",
                                                                             filters = {"source_document_name" : tab_fieldname,
						                                        "remote_sync_status" : 1},
                                                                             fieldname="*", as_dict = True)
						if target_doc:
							table[fieldname] = target_doc["target_document_name"]
					modified_table.append(table)
				doc[table_name] = modified_table
		modified_docs.append(doc)
	return modified_docs

''' Get Reference Field  of Child Doc'''
def get_ref_field(ddoc):
	flag = False
	data = []
	doctype = {}
	if not ddoc:
		return data
	table_fields = ddoc.meta.get_table_fields()
	if not table_fields:
		return data
	for table in table_fields:
		doctype_name = table.options
		childdoc = frappe.get_doc({"doctype":doctype_name})
		if not childdoc:
			return data
		dls = childdoc.meta.get_dynamic_link_fields()
		if not dls:
			return data
		for dl in dls:
			if dl.fieldname == "reference_name":
				doctype["doctype"] = table.options
				doctype["fieldname"] = dl.fieldname
				doctype["tabfieldname"] = table.fieldname
				data.append(doctype)
	return data

def save_doc(doc):
	docs = []
	docs.append(doc)
	ddocs = update_dl(docs)
	for doc in ddocs:
		name = doc['name']
		doc['name'] = None
		status = sync_document(doc, "save")
		if status and status.has_key("name"):
			update_rm_sync_doc(name,
				target_name = status["name"], remote_sync_status = 1)
		else:
			frappe.msgprint("not synced document {0}".format(name))

def process_sync_documents(docs):
	docs = json.loads(docs)
        update_docs = []
        saved_docs = []
	saved_docs_index = []
	# Data for reference testing
	#data = [{"name":"Payment Tool","target_document_name":"","doctype_name":"DocType"},{"name":"JV-00007","target_document_name":"","doctype_name":"Journal Entry"},{"name":"JV-00003","target_document_name":"","doctype_name":"Journal Entry"},{"name":"TT Document Detail","target_document_name":"TT Document Detail","doctype_name":"DocType"}]
        for index in range(0,len(docs)):
		each = docs[index]
		name = each["name"]
		doctype_name = each["doctype_name"]
		if name == "" or doctype_name == "":
			continue	
		doc = frappe.get_doc(each['doctype_name'], each['name']) 
 		doc = doc.as_dict()
		if each["target_document_name"]:
                        doc['name'] = each["target_document_name"]
			doc['docname'] = each["target_document_name"]
			doc['modified'] = doc['creation']
			update_docs.append(doc)
                else:
			if doc['doctype'] == "Journal Entry":
				saved_docs.append(doc)
			else:
				save_doc(doc)
	for each in saved_docs:
		save_doc(each)	
        status = sync_document(update_docs, "bulk_update") if update_docs else None
	for each in update_docs:
		remote_doc = frappe.get_value("Remote Document Sync", 
                                         { "target_document_name": each['name'],
					   "doctype_name": each['doctype'] },
					 fieldname= "name")
		if remote_doc:
			update_rm_sync_doc(remote_doc, remote_sync_status = 1)			
		else:
			frappe.msgprint("{0} Error ".format(each['name']), exception=True)
		
	'''
	saved_docs_name = []
	not_saved = []
	not_saved_count = 0
	for each in saved_docs:
		status = sync_document(each, "save")
		
		if status and status.has_key("name"):
			saved_docs_name.append(status["name"])
		else:
			not_saved.append(not_saved_count)
		not_saved_count +=1
			 
	count = 0
	faild = ""
	for index in saved_docs_index:
		remote_doc = docs[index]
		if index in not_saved:
			faild += "   " + remote_doc["name"]
			continue
		update_rm_sync_doc(remote_doc["name"], 
			target_name = saved_docs_name[count], remote_sync_status = 1)
		count += 1 
	if faild != "":	
		frappe.msgprint(_("Fails Documents are {}".format(faild)))
	'''
def sync_erp2_queue(doc_list):
	print "sync_erp2_queue"
        if not frappe.conf.has_key('sync_server_ip') or frappe.conf.sync_server_ip == "":
                return
	process_sync_documents(doc_list)
	

'''	
@celery_task()
#@frappe.async.handler
def sync_doc(site, doc, event, method, retry=0):
        if not frappe.conf.has_key('sync_server_ip') or frappe.conf.sync_server_ip == "":
                return

        print "1"
        form_dict = doc.as_dict()
        if not form_dict.has_key('doctype') or (form_dict['doctype'] in ['DocShare', 'Feed']):
 		return
        # Journal Entry, Sales Invoice, Purchase Invoice, Company
        print "2"
        if not frappe.form_dict.doc:
        	return

        frappe_form_dict = json.loads(frappe.form_dict.doc)
        if debug:
        	frappe.msgprint(frappe._(" {0}  {1} {2}".format(method, frappe_form_dict.keys(), frappe_form_dict.values())))
        if ( not frappe_form_dict.has_key('sync_document_erp2') or 
             not frappe_form_dict['sync_document_erp2'] or #and not (method=="after_insert" or method=="on_update")
             not form_dict.has_key('name')):
 		return

        print "3"
        user = (frappe.session and frappe.session.user) or doc_dict['modified_by'] or "Administrator" 
        pwd = frappe.db.sql("""select password from __Auth where user=%s;""",(user))
        if not pwd:
                return False

        print "4"
        pwd = pwd[0][0]
        try:
        	client = FrappeClient(frappe.conf.sync_server_ip, user, pwd)
        except:
                frappe.msgprint(("Auth Error"))
                return

        if not client:
                return
        print "5"
        rm_doc_name = ''
        remote_doc = ''
        rm_doc_sync = ''
        # check if Document exist in remote machine else create new doc and make entry in DB
        require_insert = 0
        remote_doc_dict = {}
        remote_dict = {}

        print "6"
        try:
                print "7"
		remote_doc_dict = client.get_doc(form_dict['doctype'], form_dict['name'])
                #frappe.msgprint(frappe._("{0}".format(remote_doc_dict)))
        except:
                if debug:
        		frappe.msgprint(("Error"))
                pass

        print "8"
        #frappe.msgprint(("after sync_server_ip {0}".format(form_dict)))
  
        rm_doc_name = frappe.get_value("Remote Document Sync",
                                  { 'name': form_dict['name'],
                                    'doctype_name': form_dict['doctype']
                                  },
                                  fieldname='target_document_name')
        
        if rm_doc_name:
                try:
                        print "9"
                        if debug:
                        	frappe.msgprint(frappe._("try"))
                        remote_doc_dict = client.get_doc(form_dict['doctype'], rm_doc_name)
			remote_doc = frappe.get_doc(remote_doc_dict)
                        try:
                        	rm_doc_sync = frappe.get_doc("Remote Document Sync", rm_doc_name)
                        except:
                                rm_doc_sync = add_rm_sync_doc(form_dict['name'], form_dict['doctype'], form_dict['name'], '')
                                
                        #import json
                        #remote_doc.update(json.loads(remote_doc_dict))
                except:
                        print "10"
                        if debug:
                        	frappe.msgprint(frappe._("try2 except {0}".format(form_dict['name'])))
                        if not retry:
                                print "11"
                                sync_doc(site, doc, event, method, 1) 
                                pass
                        else:
                                print "12"
                                if debug:
                                	frappe.msgprint(frappe._("try except else"))
				remote_doc = frappe.new_doc(form_dict['doctype'])
                                rm_doc_sync = add_rm_sync_doc(form_dict['name'], form_dict['doctype'], form_dict['name'], '')
        else:
                print "13"
                if debug:
                	frappe.msgprint(frappe._("try else"))
                remote_doc = frappe.new_doc(form_dict['doctype'])
                rm_doc_sync = add_rm_sync_doc(form_dict['name'], form_dict['doctype'], form_dict['name'], '')

        try:
                print "14"
                if not remote_doc.name:
                        method = "after_insert"

		if method == "after_insert":
			for key in remote_doc.as_dict().keys():
				 if key in ["name", "creation", "modified", "modified_by", "owner", "docstatus", "parent", "parentfield", "parenttype", "idx", "rgt", "lft"]:
					 continue
				 remote_doc.set(key, doc.get(key))
                        print "15"
                        remote_dict = {}
                        print remote_doc
			remote_dict = client.insert(remote_doc)
			rm_doc_sync.target_document_name = remote_dict['name'] if remote_dict and remote_dict.has_key('name') else doc.get('name')
			rm_doc_sync.save()

		if method == "on_update":
			return 
			for key in remote_doc.as_dict().keys():
				 if key in ["name", "creation", "modified", "modified_by", "owner", "docstatus", "parent", "parentfield", "parenttype", "idx", "rgt", "lft"]:
					 continue
				 remote_doc.set(key, doc.get(key))
                        print "16"
                        remote_dict = {}
			remote_dict = client.update(remote_doc)
			rm_doc_sync.target_document_name = remote_dict['name'] if remote_dict and remote_dict.has_key('name') else doc.get('name')
			rm_doc_sync.save()

		elif method == "on_trash":
                        print "17"
			remote_dict = client.delete(doc.get('doctype'), rm_doc_name)
			rm_doc_name = frappe.get_value("Remote Document Sync", 
					    filters={'source_document_name': form_dict['name']},
					    fieldname='name')
                        frappe.delete_doc("Remote Document Sync", rm_doc_name, 1)
			frappe.db.commit()
			 

		elif method == "on_cancel":
                        print "18"
			remote_dict = client.cancel(remote_doc.get('doctype'), rm_doc_name)

		elif method == "on_submit":
                        print "19"
			for key in remote_doc.as_dict().keys():
				 if key in ["name", "creation", "owner", "idx", "rgt", "lft"]:
					 continue
				 remote_doc.set(key, doc.get(key))
			remote_dict = client.submit(remote_doc)
			rm_doc_sync.target_document_name = remote_dict['name'] if remote_dict and remote_dict.has_key('name') else doc.get('name')
			rm_doc_sync.save()

		elif method == "after_rename":
                        print "20"
			remote_dict = client.rename(remote_doc.get('doctype'), rm_doc_name, doc.get('name'))
			rm_doc_sync.target_document_name = doc.get('name')                
			rm_doc_sync.save()
               
        except:
                print "Error while syncing it to ERP2 Server Trying Again once" 
                print "21"
                raise

                if not retry:
                        #sync_doc(site, doc, event, method, 1) 
                        return
        frappe.db.commit()
        # save sync infor to DB for further reference

def sync_doc_remote(doc, method):
        if doc.get('doctype') == "Remote Document Sync":
                return
        user = (frappe.session and frappe.session.user) or doc.get('modified_by') or "Administrator" 
        #result = run_async_task.delay(site=frappe.local.site, user=user, cmd='sync_doc', form_dict=form_dict)
        #result = sync_doc.delay(site=frappe.local.site, event="doc_rsync", form_dict=doc_dict)
        sync_doc(site=frappe.local.site, doc=doc, event="doc_rsync", method = method)
        #print result

'''
#https://zapier.com/blog/async-celery-example-why-and-how/
#https://celery.readthedocs.org/en/latest/userguide/tasks.html
#https://celery.readthedocs.org/en/latest/userguide/calling.html
#http://playdoh.readthedocs.org/en/latest/userguide/celery.html
'''
                        $.ajax("/api/resource/Mode of Payment").success(function(data) {
                                $.each(data.data, function(i, d) { me.modes_of_payment.push(d.name); }); 
                                callback();
                        });
                        $.ajax({
                                url: "/api/resource/Report/" + encodeURIComponent(doc.name),
                                type: "POST",
                                data: {
                                        run_method: "toggle_disable",
                                        disable: doc.disabled ? 0 : 1 
                                }
                        })
self.session.get(self.url + "/api/resource/" + doctype, params=params, verify=self.verify)
'''
#prepare API call for second server with session
# calling this funciton
# erpnext.tasks.send_newsletter.delay(frappe.local.site, self.name, event="bulk_long")
