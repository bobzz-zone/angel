
from __future__ import unicode_literals
import frappe
#from frappe.celery_app import celery_task, task_logger
from frappe.frappeclient import FrappeClient
from frappe.tasks import run_async_task

frappe.conf.sync_server_ip = "http://localhost:8000"

#@celery_task()
@frappe.asnyc.handler
def sync_doc():
	# hack! pass event="bulk_long" to queue in longjob queue
        print frappe.flags
        print doc 
        print frappe.local
        print frappe.__dict(args)
        form_dict = frappe._dict()
        print cmd 
        user = (frappe.session and frappe.session.user)
        pwd = frappe.db.sql("""select password from __Auth where user=%s;""",(user))
        if not pwd:
                return False
        client = FrappeClient(frappe.conf.sync_server_ip, user, pwd)
        if not client:
                return
        if form_dict['cmd_method'] == "insert":
                client.insert(doc)
        elif form_dict['cmd_method'] == "delete":
                client.delete(doc)
        elif form_dict['cmd_method'] == "update":
                client.update(doc)
        elif form_dict['cmd_method'] == "cancel":
                client.cancel(doc)
        elif form_dict['cmd_method'] == "submit":
                client.submit(doc)
        elif form_dict['cmd_method'] == "rename":
                client.rename(doc)

def insert_doc():
        form_dict = frappe._dict()
        form_dict['cmd_method'] = "insert"
        user = (frappe.session and frappe.session.user) or "Administrator"
        result = run_async_task.delay(site=frappe.local.site, user=user, cmd='sync_doc', form_dict=form_dict)
        print result.get()

def delete_doc():
        form_dict = frappe._dict()
        form_dict['cmd_method'] = "delete"
        user = (frappe.session and frappe.session.user) or "Administrator"
        result = run_async_task.delay(site=frappe.local.site, user=user, cmd='sync_doc', form_dict=form_dict)
        print result.get()

def update_doc():
        form_dict = frappe._dict()
        form_dict['cmd_method'] = "update"
        user = (frappe.session and frappe.session.user) or "Administrator"
        result = run_async_task.delay(site=frappe.local.site, user=user, cmd='sync_doc', form_dict=form_dict)
        print result.get()

def submit_doc():
        form_dict = frappe._dict()
        form_dict['cmd_method'] = "submit"
        user = (frappe.session and frappe.session.user) or "Administrator"
        result = run_async_task.delay(site=frappe.local.site, user=user, cmd='sync_doc', form_dict=form_dict)
        print result.get()

def cancel_doc():
        form_dict = frappe._dict()
        form_dict['cmd_method'] = "cancel"
        user = (frappe.session and frappe.session.user) or "Administrator"
        result = run_async_task.delay(site=frappe.local.site, user=user, cmd='sync_doc', form_dict=form_dict)
        print result.get()

def rename_doc():
        form_dict = frappe._dict()
        form_dict['cmd_method'] = "rename"
        user = (frappe.session and frappe.session.user) or "Administrator"
        result = run_async_task.delay(site=frappe.local.site, user=user, cmd='sync_doc', form_dict=form_dict)
        print result.get()

# https://github.com/frappe/frappe-client
# frappe/frappe/tests/test_async.py  for testing Async task
# frappe/frappe/tests/test_hooks.py  for testing hooks
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
