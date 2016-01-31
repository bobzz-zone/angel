import frappe 

doc = frappe.new_doc("Territory")
doc.territory_name = "xyz4"
doc.is_group = "Yes"
doc.save()
