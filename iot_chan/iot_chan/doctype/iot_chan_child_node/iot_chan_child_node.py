# -*- coding: utf-8 -*-
# Copyright (c) 2020, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import throw, _
from frappe.model.document import Document
from frappe.core.doctype.data_export.exporter import export_data


class IOTChanChildNode(Document):
	pass


def export_doctyp_to_csv(doctype, filters=None):
	# Keep the response
	org_result = frappe.response.result
	org_type = frappe.response.type
	org_doctype = frappe.response.doctype

	export_data(doctype=doctype, all_doctypes=True, template=True, with_data=True, filters=filters)
	data = frappe.response.result.encode("utf-8")

	# Rollback response
	frappe.response.result = org_result
	frappe.response.type = org_type
	frappe.response.doctype = org_doctype
	return data


def export_apps(node_name):
	filters = {"parent": node_name}
	apps = [d.app for d in frappe.get_all("IOT Chan Child NodeLicensedApp", fields=["app"], filters=filters)]

	return export_doctyp_to_csv('IOT Application', filters={"name": ["in", apps]})


def list_developers(node_name):
	filters = {"parent": node_name}
	developers = set()
	for d in frappe.get_all("IOT Chan Child NodeLicensedApp", fields=["app"], filters=filters):
		developer = frappe.get_value("IOT Application", d.app, "developer")
		developers.add(developer)


def list_developer_users(node_name):
	developers = list_developers(node_name)
	users = []
	for dev in developers:
		user = frappe.get_value("App Developer", dev, "user")
		users.append(user)
	return users


def export_developers(node_name):
	developers = list_developers(node_name)
	return export_doctyp_to_csv('App Developer', filters={"name": ["in", developers]})


def list_devices(node_name):
	return [d.device for d in frappe.get_all("IOT Device Owner Ship", filters={"child_node": node_name}, fields=['device'])]


def export_app_versions(node_name, app, beta=0):
	app_id = frappe.get_value("IOT Chan Child NodeLicensedApp", {"parent": node_name}, "app")
	if app_id != app:
		raise frappe.PermissionError

	filters = {
		"app": app,
		"beta": beta
	}

	return export_doctyp_to_csv('IOT Application Version', filters=filters)