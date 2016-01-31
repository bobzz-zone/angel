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
	# Removed GL Entry and Bin
        if doctype in ["GL Entry", "Bin"]:
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
	print "1"
	client = ''
        # Get User and Password from Database
        user = (frappe.session and frappe.session.user) or doc_dict['modified_by'] or "Administrator" 
        pwd = frappe.db.sql("""select password from __Auth where user=%s;""",(user))
        if not pwd:
                return False
	print "2"
        pwd = pwd[0][0]
        try:
        	client = FrappeClient(frappe.conf.sync_server_ip, user, pwd)
        except:
                frappe.msgprint(("Auth Error"))
                return
	print "3"
        if not client:
                return 
	res = ''
        if method == "bulk_update":
		print "4"
 		return client.bulk_update(docs)
	else:
		print "5"
		return client.save(docs)
	
def save_doc(doc):
	#saved_docs_index.append(index)
	name = doc['name']
	doc['name'] = None
	#saved_docs.append(doc)	
	status = sync_document(doc, "save")
	if status and status.has_key("name"):
		update_rm_sync_doc(name,
			target_name = status["name"], remote_sync_status = 1)
	else:
		frappe.msgprint("not synced document {0}".format(name))

def process_sync_documents(docs):
	print docs
	print "process_Sync_documents"
	docs = json.loads(docs)
        update_docs = []
        saved_docs = []
	saved_docs_index = []
         
	data = [{"name":"Payment Tool","target_document_name":"","doctype_name":"DocType"},{"name":"JV-00007","target_document_name":"","doctype_name":"Journal Entry"},{"name":"JV-00003","target_document_name":"","doctype_name":"Journal Entry"},{"name":"TT Document Detail","target_document_name":"TT Document Detail","doctype_name":"DocType"}]
        for index in range(0,len(docs)):
		print "inside for"
                # name is not present
		each = docs[index]
		name = each["name"]
		doctype_name = each["doctype_name"]
		if name == "" or doctype_name == "":
			continue	

		doc = frappe.get_doc(each['doctype_name'], each['name']) 
 		doc = doc.as_dict()
		print each
		if each["target_document_name"]:
                        doc['name'] = each["target_document_name"]
			doc['docname'] = each["target_document_name"]
			#hack
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
	print "Status :- " 
	print status
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


# https://github.com/frappe/frappe-client
# frappe/frappe/tests/test_async.py  for testing Async task
# frappe/frappe/tests/test_hooks.py  for testing hooks
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

'''
# Testing case
doc = frappe.new_doc("Territory")
doc.territory_name = "All Territories"
doc.is_group = "Yes"
doc.save()
'''
def preprocess(self, params):
        """convert dicts, lists to json"""
        for key, value in params.iteritems():
                if isinstance(value, (dict, list)):
                        params[key] = json.dumps(value)

        return params

def post_process(self, response):
        try:
                rjson = response.json()
        except ValueError:
                print response.text
                raise

        if rjson and ("exc" in rjson) and rjson["exc"]:
                raise FrappeException(rjson["exc"])
        if 'message' in rjson:
                return rjson['message']
        elif 'data' in rjson:
                return rjson['data']
        else:
                return None

        ret = {}
        frappe.init(site)
        frappe.connect()

        frappe.local.task_id = self.request.id

        if hijack_std:
                original_stdout, original_stderr = sys.stdout, sys.stderr
                sys.stdout, sys.stderr = get_std_streams(self.request.id)
                frappe.local.stdout, frappe.local.stderr = sys.stdout, sys.stderr

        try:
                set_task_status(self.request.id, "Running")
                frappe.db.commit()
                frappe.set_user(user)
                # sleep(60)
                frappe.local.form_dict = frappe._dict(form_dict)
                execute_cmd(cmd, from_async=True)
                ret = frappe.local.response

        except Exception, e:
                frappe.db.rollback()
                ret = frappe.local.response
                http_status_code = getattr(e, "http_status_code", 500)
                ret['status_code'] = http_status_code
                frappe.errprint(frappe.get_traceback())
                frappe.utils.response.make_logs()
                set_task_status(self.request.id, "Error", response=ret)
                task_logger.error('Exception in running {}: {}'.format(cmd, ret['exc']))
        else:
                set_task_status(self.request.id, "Success", response=ret)
                if not frappe.flags.in_test:
                        frappe.db.commit()
        finally:
                if not frappe.flags.in_test:
                        frappe.destroy()
                if hijack_std:
                        sys.stdout.write('\n' + END_LINE)
                        sys.stderr.write('\n' + END_LINE)
                        sys.stdout.close()
