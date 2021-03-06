# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import throw, _
from iot_chan.iot_chan.doctype.iot_chan_settings.iot_chan_settings import IOTChanSettings


def validate_iot_device(doc, method):
	if IOTChanSettings.get_enable_upper_center() == 1:
		if frappe.flags.in_import:
			return

		if not doc.is_new():
			return

		frappe.throw(_("This is an Child IOT Center"), frappe.PermissionError)


def validate_app_category(doc, method):
	if IOTChanSettings.get_enable_upper_center() == 1:
		if frappe.flags.in_import:
			return
		frappe.throw(_("This is an Child IOT Center"), frappe.PermissionError)


def validate_iot_hardware_architecture(doc, method):
	if IOTChanSettings.get_enable_upper_center() == 1:
		if frappe.flags.in_import:
			return
		frappe.throw(_("This is an Child IOT Center"), frappe.PermissionError)


def validate_app_developer(doc, method):
	if IOTChanSettings.get_enable_upper_center() == 1:
		if frappe.flags.in_import:
			return
		frappe.throw(_("This is an Child IOT Center"), frappe.PermissionError)


def validate_iot_application(doc, method):
	if IOTChanSettings.get_enable_upper_center() == 1:
		if frappe.flags.in_import:
			return
		frappe.throw(_("This is an Child IOT Center"), frappe.PermissionError)


def validate_iot_application_version(doc, method):
	if IOTChanSettings.get_enable_upper_center() == 1:
		if frappe.flags.in_import:
			return
		frappe.throw(_("This is an Child IOT Center"), frappe.PermissionError)