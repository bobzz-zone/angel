from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Tools"),
			"icon": "icon-wrench",
			"items": [
				{
					"type": "doctype",
					"name": "Set Shifts",
					"label": _("Set Shifts"),
					"description":_("to Set Shifts"),
				},
			]
		},
	]
