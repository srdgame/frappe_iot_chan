# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "iot_chan"
app_title = "IOT Chan"
app_publisher = "dirk"
app_description = "IOT Chan"
app_icon = "octicon octicon-server"
app_color = "green"
app_email = "dirk@kooiot.com"
app_license = "MIT"
source_link = "https://github.com/srdgame/frappe_iot_chan"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/iot_chan/css/iot_chan.css"
# app_include_js = "/assets/iot_chan/js/iot_chan.js"

# include js, css files in header of web template
# web_include_css = "/assets/iot_chan/css/iot_chan.css"
# web_include_js = "/assets/iot_chan/js/iot_chan.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "iot_chan.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "iot_chan.install.before_install"
# after_install = "iot_chan.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "iot_chan.notifications.get_notification_config"

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

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"iot_chan.tasks.all"
# 	],
# 	"daily": [
# 		"iot_chan.tasks.daily"
# 	],
# 	"hourly": [
# 		"iot_chan.tasks.hourly"
# 	],
# 	"weekly": [
# 		"iot_chan.tasks.weekly"
# 	]
# 	"monthly": [
# 		"iot_chan.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "iot_chan.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "iot_chan.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "iot_chan.task.get_dashboard_data"
# }

