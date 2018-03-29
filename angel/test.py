from __future__ import unicode_literals,print_function
import frappe
def test():
	sr = frappe.get_doc("Stock Reconciliation","SR/00298")
	sr.submit()

def copy_user_roles_to_has_roles():
	if frappe.db.exists('DocType', 'UserRole') or 1==1:
		for data in frappe.get_all('User', fields = ["name"]):
			print('User {}'.format(data.name))
			if data.name in ["Administrator","Guest","vivi@ocf.com","acc@ofc.com","sherry@ocf.com"]:
				continue
			doc = frappe.get_doc('User', data.name)
			doc.set('roles',[])
						
			for args in frappe.db.sql("""select role from tabUserRole where parent="{}" and parenttype="User" """.format(data.name),as_dict=1):
				print("Roles => {}".format(args.role))
				doc.append('roles', {
                                        'role': args.role
                                })
			for role in doc.roles:
				role.db_update()


def reload_doc():
        frappe.reload_doc("core", 'doctype', "page")
        frappe.reload_doc("core", 'doctype', "report")
        frappe.reload_doc("core", 'doctype', "user")
        frappe.reload_doc("core", 'doctype', "has_role")
