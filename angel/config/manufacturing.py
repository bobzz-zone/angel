from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
                {
                        "label": _("Standard Reports"),
                        "icon": "icon-table",
                        "items": [
                                {
                                        "type" : "report",
                                        "name" : "Workstation Wise PO-Items",
                                        "doctype" : "Workstation",
                                        "is_query_report": True
                                }
                        ]
                 }
	]
