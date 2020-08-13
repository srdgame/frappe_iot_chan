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
		if frappe.get_value("IOT Virtual Device", doc.sn, "name"):
			return

		throw(_("Child IOT Center blocking check"))


def validate_app_category(doc, method):
	if IOTChanSettings.get_enable_upper_center() == 1:
		if frappe.flags.in_import:
			return
		throw(_("Child IOT Center blocking check"))


def validate_iot_hardware_architecture(doc, method):
	if IOTChanSettings.get_enable_upper_center() == 1:
		if frappe.flags.in_import:
			return
		throw(_("Child IOT Center blocking check"))


def validate_app_developer(doc, method):
	if IOTChanSettings.get_enable_upper_center() == 1:
		if frappe.flags.in_import:
			return
		throw(_("Child IOT Center blocking check"))


def validate_iot_application(doc, method):
	if IOTChanSettings.get_enable_upper_center() == 1:
		if frappe.flags.in_import:
			return
		throw(_("Child IOT Center blocking check"))


def validate_iot_application_version(doc, method):
	if IOTChanSettings.get_enable_upper_center() == 1:
		if frappe.flags.in_import:
			return
		throw(_("Child IOT Center blocking check"))