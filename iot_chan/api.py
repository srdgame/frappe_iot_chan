# -*- coding: utf-8 -*-
# Copyright (c) 2020, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import throw, _


def valid_sync_auth_code(auth_code=None):
	auth_code = auth_code or frappe.get_request_header("AuthorizationCode")
	if not auth_code:
		throw(_("AuthorizationCode is required in HTTP Header!"))
	frappe.logger(__name__).debug(_("IOT Chan Child Node AuthorizationCode as {0}").format(auth_code))

	node_name = frappe.get_value("IOT Chan Child Node", {"auth_code": auth_code}, "node_name")
	if not node_name:
		throw(_("Authorization Code {0} is incorrect!").format(auth_code))

	# form dict keeping
	form_dict = frappe.local.form_dict
	frappe.set_user('Administrator')
	frappe.local.form_dict = form_dict

	return frappe.get_doc('IOT Chan Child Node', node_name)


@frappe.whitelist(allow_guest=True)
def get_basic_info():
	node = valid_sync_auth_code()

	from iot_chan.iot_chan.doctype.iot_chan_child_node.iot_chan_child_node import get_basic_info as _get_basic_info

	return _get_basic_info(node.name)


@frappe.whitelist(allow_guest=True)
def get_app_versions(app, base_version=0):
	node = valid_sync_auth_code()

	from iot_chan.iot_chan.doctype.iot_chan_child_node.iot_chan_child_node import list_app_versions

	return list_app_versions(node.name, app, node.beta_version_enabled, base_version)

