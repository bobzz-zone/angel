# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe

from frappe.celery_app import celery_task, task_logger
from frappe.frappeclient import FrappeClient
from frappe.tasks import run_async_task

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

from frappe.celery_app import get_queue 

RSYNC_TASK_PREFIX = "rsync@" 
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

@celery_task()
#@frappe.async.handler
def sync_doc(site, doc, event, method, retry=0):
        if not frappe.conf.has_key('sync_server_ip') or frappe.conf.sync_server_ip == "":
                return 

        form_dict = doc.as_dict()
        if form_dict['doctype'] == 'DocShare':
 		return 
        
        user = (frappe.session and frappe.session.user) or doc_dict['modified_by'] or "Administrator" 
        pwd = frappe.db.sql("""select password from __Auth where user=%s;""",(user))
        if not pwd:
                return False

        pwd = pwd[0][0]
        client = FrappeClient(frappe.conf.sync_server_ip, user, pwd)
        if not client:
                return

        rm_doc_name = ''
        remote_doc = ''
        rm_doc_sync = ''
        # check if Document exist in remote machine else create new doc and make entry in DB
        require_insert = 0
        remote_doc_dict = {}

        try:
		remote_doc_dict = client.get_doc(form_dict['doctype'], form_dict['name'])
                #frappe.msgprint(frappe._("{0}".format(remote_doc_dict)))
                if remote_doc_dict:
                	rm_doc_sync =  frappe.new_doc("Remote Document Sync")
               		rm_doc_sync.source_document_name = form_dict['name']
                	rm_doc_sync.target_document_name = remote_doc_dict['name']
                	rm_doc_sync.doctype_name = remote_doc_dict['doctype']
                        rm_doc_sync.save()
                        frappe.db.commit()                
        except:
        	frappe.msgprint(("Error"))
			
        rm_doc_name = frappe.get_value("Remote Document Sync", 
                                  filters={'source_document_name': form_dict['name']}, 
                                  fieldname='target_document_name')
        
        if rm_doc_name:
                try:
                        #frappe.msgprint(frappe._("try2 {0} {1}".format(form_dict['name'], form_dict['doctype'])))
                        remote_doc_dict = client.get_doc(form_dict['doctype'], rm_doc_name)
			remote_doc = frappe.new_doc(form_dict['doctype'])
                        import json
                        remote_doc.update(json.loads(remote_doc_dict))
                except:
                        #frappe.msgprint(frappe._("try2 except {0}".format(form_dict['name'])))
                        if not retry:
                                sync_doc(site, doc, event, method, 1) 
                        else:
                                require_insert = 1
                                #frappe.msgprint(frappe._("try2 except else {0}".format(form_dict['name'])))
				remote_doc = frappe.new_doc(form_dict['doctype'])
				rm_doc_sync =  frappe.new_doc("Remote Document Sync")
				rm_doc_sync.source_document_name = form_dict['name']
				rm_doc_sync.target_document_name = ""                
        else:            
                #frappe.msgprint(frappe._("rm_doc_name else"))
                require_insert = 1
                remote_doc = frappe.new_doc(form_dict['doctype'])
                rm_doc_sync =  frappe.new_doc("Remote Document Sync")
                rm_doc_sync.source_document_name = form_dict['name']
                rm_doc_sync.target_document_name = ""                

        rm_doc_sync.doctype_name = form_dict['doctype']
        try:
		if method == "after_insert":
			#frappe.msgprint(("after_insert chetan "))
			for key in remote_doc.as_dict().keys():
				 if key in ["name", "creation", "modified", "modified_by", "owner", "docstatus", "parent", "parentfield", "parenttype", "idx", "rgt", "lft"]:
					 continue
				 remote_doc.set(key, doc.get(key))
                        remote_dict = {}
			remote_dict = client.insert(remote_doc)
			rm_doc_sync.target_document_name = remote_dict['name']                
			rm_doc_sync.save()
			frappe.db.commit() 

		if method == "on_update":
			for key in remote_doc.as_dict().keys():
				 if key in ["name", "creation", "modified", "modified_by", "owner", "docstatus", "parent", "parentfield", "parenttype", "idx", "rgt", "lft"]:
					 continue
				 remote_doc.set(key, doc.get(key))
                        remote_dict = {}
                        #if require_insert:
			#        remote_dict = client.insert(remote_doc)
                        #else:
			#frappe.msgprint(("chetan {0}".format(remote_doc)))
			remote_dict = client.update(remote_doc)
			rm_doc_sync.target_document_name = remote_dict['name']                
			rm_doc_sync.save()
			frappe.db.commit() 

		elif method == "on_trash":
			remote_dict = client.delete(doc.get('doctype'), rm_doc_name)
			rm_doc_name = frappe.get_value("Remote Document Sync", 
					    filters={'source_document_name': form_dict['name']}, 
					    fieldname='name')
                        frappe.delete_doc("Remote Document Sync", rm_doc_name, 1)
			frappe.db.commit() 
			 

		elif method == "on_cancel":
			remote_dict = client.cancel(remote_doc.get('doctype'), rm_doc_name)

		elif method == "on_submit":
			for key in remote_doc.as_dict().keys():
				 if key in ["name", "creation", "owner", "idx", "rgt", "lft"]:
					 continue
				 remote_doc.set(key, doc.get(key))
			remote_dict = client.submit(remote_doc)
			rm_doc_sync.target_document_name = remote_dict['name']                
			rm_doc_sync.save()
			frappe.db.commit() 

		elif method == "after_rename":
			remote_dict = client.rename(remote_doc.get('doctype'), rm_doc_name, doc.get('name'))
			rm_doc_sync.target_document_name = doc.get('name')                
			rm_doc_sync.save()
			frappe.db.commit() 
               
        except:
                print "Error while syncing it to ERP2 Server Trying Again once" 

                if not retry:
                        #sync_doc(site, doc, event, method, 1) 
                        return
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
