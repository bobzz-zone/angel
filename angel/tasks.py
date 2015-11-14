
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

# New Document type
#Remote Document Sync

@celery_task()
#@frappe.async.handler
def sync_doc():
	# hack! pass event="bulk_long" to queue in longjob queue
        print frappe.flags
        #print doc 
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
        remote_doc = frappe.new_doc(form_dict['doctype'])
        for key in remote_doc.as_dict().keys():
                 remote_doc.set(key, doc.get(key))
        remote_doc.set('name', 'New ' + doc.get('doctype') + ' 1')
        print remote_doc.as_dict()
        return
        if form_dict['cmd_method'] == "after_insert":
                print client.insert(doc)
                doc =  frappe.new_doc("Remote Document Sync")
                doc.source_document_name = form_dict['name']
                doc.target_document_name = ""                

        elif form_dict['cmd_method'] == "on_trash":
                client.delete(doc)
        elif form_dict['cmd_method'] == "on_update":
                client.update(doc)
        elif form_dict['cmd_method'] == "on_cancel":
                client.cancel(doc)
        elif form_dict['cmd_method'] == "on_submit":
                client.submit(doc)
        elif form_dict['cmd_method'] == "after_rename":
                client.rename(doc)

def sync_doc_remote(doc, method):
        #print "args " + args 
        #print "kw " + kw
        form_dict = frappe._dict()
        doc_dict = doc.as_dict()
        #print doc_dict['name']
        #print doc_dict['doctype']
       
        form_dict['cmd_method'] = method 
        user = (frappe.session and frappe.session.user) or doc_dict['modified_by'] or "Administrator" 
        result = run_async_task.delay(site=frappe.local.site, user=user, cmd='sync_doc', form_dict=form_dict)
        #print result.get()


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
