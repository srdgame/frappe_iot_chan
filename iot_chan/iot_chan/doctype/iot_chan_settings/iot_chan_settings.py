# -*- coding: utf-8 -*-
# Copyright (c) 2020, dirk and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from itertools import groupby
from frappe import throw, _
from frappe.model.document import Document


class IOTChanSettings(Document):
	def validate(self):
		if self.enable_upper_center == 1:
			if self.upper_center is None:
				throw(_("Upper IOT Center is missing!"))
			if self.auth_code is None:
				throw(_("Upper IOT Center Auth Code is missing!"))
		apps = {}
		for app in self.common_licensed_apps:
			if apps.get(app.app):
				throw(_("Duplicated App {0}").format(app.app))
			else:
				apps[app.app] = app
				app.app_name = frappe.get_value("IOT Application", app.app, "app_name")

	def sync_all(self):
		self.save()
		if self.enable_upper_center == 0:
			throw(_("Upper IOT Center is not enabled!"))
		if 'IOT Manager' not in frappe.get_roles():
			raise frappe.PermissionError

		from iot_chan.controllers.sync import sync_all as _sync_all
		_sync_all()

		self.update_last_sync_time()

	@staticmethod
	def get_enable_upper_center():
		return frappe.db.get_single_value("IOT Chan Settings", "enable_upper_center")

	@staticmethod
	def get_upper_center():
		return frappe.db.get_single_value("IOT Chan Settings", "upper_center")

	@staticmethod
	def get_auth_code():
		return frappe.db.get_single_value("IOT Chan Settings", "auth_code")

	@staticmethod
	def get_last_sync_time():
		return frappe.db.get_single_value("IOT Chan Settings", "last_sync_time")

	@staticmethod
	def update_last_sync_time():
		frappe.set_value("IOT Chan Settings", "IOT Chan Settings", "last_sync_time", frappe.utils.now())
