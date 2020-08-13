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
	data = frappe.response.result

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
	return developers


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


def list_app_versions(node_name, app, beta=0, base_version=0):
	app_id = frappe.get_value("IOT Chan Child NodeLicensedApp", {"parent": node_name}, "app")
	if app_id != app:
		raise frappe.PermissionError

	filters = {
		"app": app,
		"version": [">", base_version]
	}

	fields = ['app', 'version', 'beta', 'comment']
	order_by = "modified desc"
	versions = frappe.get_all("IOT Application Version", filters=filters, fields=fields, order_by=order_by)
	if len(versions) == 0:
		return []

	beta_comment = 'Comments:'
	beta_version = versions[0].version
	comment = 'Comments:'
	version = 0
	got_release = False
	for ver in versions:
		beta_comment = '\n' + ver.comment
		if version == 0 and ver.beta == 0:
			version = ver.version
			got_release = True
		if got_release:
			comment = comment + '\n' + ver.comment

	data = []
	if beta == 1:
		data.append({
			"app": app,
			"version": beta_version,
			"beta": 1,
			"comment": beta_comment
		})
	if version != 0:
		data.append({
			"app": app,
			"version": version,
			"beta": 0,
			"comment": comment
		})

	return data