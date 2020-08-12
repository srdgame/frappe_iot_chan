# -*- coding: utf-8 -*-
# Copyright (c) 2020, dirk and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import throw, _
from frappe.model.document import Document


class IOTChanSettings(Document):
	def validate(self):
		if self.enable_upper_center == 1:
			if self.upper_center is None:
				throw(_("Upper IOT Center is missing!"))
			if self.auth_code is None:
				throw(_("Upper IOT Center Auth Code is missing!"))
			if self.on_behalf_developer is None:
				throw(_("On behalf developer is missing!"))

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
	def get_on_behalf_developer():
		return frappe.db.get_single_value("IOT Chan Settings", "on_behalf_developer")

	@staticmethod
	def get_last_sync_time():
		return frappe.db.get_single_value("IOT Chan Settings", "last_sync_time")

	@staticmethod
	def update_last_sync_time(self):
		frappe.set_value("IOT Chan Settings", "IOT Chan Settings", "last_sync_time", frappe.utils.now())
