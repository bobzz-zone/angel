from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
                {
                        "label": _("Documents"),
                        "icon": "icon-star",
                        "items": [
                                {   
                                        "type": "doctype",
                                        "name": "Petty Cash",
                                        "description": _("Petty Cash")
                                },  
                                {   
                                        "type": "doctype",
                                        "name": "TT Document",
                                        "description": _("TT Document")
                                },  
                        ]
                },
		{
			"label": _("Setup"),
			"icon": "icon-cog",
			"items": [
			#	{
			#		"type": "doctype",
			#		"name":"C-Form",
			#		"description": _("C-Form records"),
			#		"country": "India"
			#	}
			]
		}
	]
