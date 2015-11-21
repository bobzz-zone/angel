# -*- coding: utf-8 -*-
from __future__ import unicode_literals

app_name = "angel"
app_title = "Angel"
app_publisher = "Korecent Solutions Pvt Ltd"
app_description = "changes to for new server"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "chetan@korecent.com"
app_version = "0.0.1"

error_report_email = "rosyeni@gmail.com"

website_context = {
	"splash_image": "/assets/angel/images/ms-icon-310x310.png",
	"favicon"     :	"/assets/angel/images/favicon-16x16.png"
}

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/angel/css/angel.css"
# app_include_js = "/assets/angel/js/angel.js"

# include js, css files in header of web template
# web_include_css = "/assets/angel/css/angel.css"
# web_include_js = "/assets/angel/js/angel.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "angel.install.before_install"
after_install = "angel.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "angel.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }
doc_events = {
        "*": {
                "after_insert": "angel.tasks.sync_doc_remote",
                "on_update":    "angel.tasks.sync_doc_remote",
                "after_rename": "angel.tasks.sync_doc_remote",
                "on_submit":    "angel.tasks.sync_doc_remote",
                "on_cancel":    "angel.tasks.sync_doc_remote",
                "on_trash":     "angel.tasks.sync_doc_remote"
        }
}


# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"angel.tasks.all"
# 	],
# 	"daily": [
# 		"angel.tasks.daily"
# 	],
# 	"hourly": [
# 		"angel.tasks.hourly"
# 	],
# 	"weekly": [
# 		"angel.tasks.weekly"
# 	]
# 	"monthly": [
# 		"angel.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "angel.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "angel.event.get_events"
       'sync_doc': 'angel.tasks.sync_doc'
}

