# -*- coding: utf-8 -*-
# Copyright (c) 2020, dirk and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class IOTDeviceOwnerShip(Document):
	def validate(self):
		self.device_name = frappe.get_value("IOT Device", self.device, "dev_name")
		if self.comments is None:
			self.comments = frappe.get_value("IOT Device", self.device, "description")
