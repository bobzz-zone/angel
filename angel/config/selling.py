from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Documents"),
			"icon": "icon-cog",
			"items": [
				{
					"type": "doctype",
					"name":"Deal Counter",
					"description": _("Deal Counter")
				}
			]
		},
                {
                        "label": _("Standard Reports"),
                        "icon": "icon-table",
                        "items": [
                                {
                                        "type" : "report",
                                        "name" : "Deal Counter based Sales Orders",
                                        "doctype" : "Deal Counter",
                                        "is_query_report": True
                                }
                        ]
                 }
	]
