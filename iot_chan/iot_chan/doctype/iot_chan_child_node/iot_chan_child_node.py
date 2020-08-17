# -*- coding: utf-8 -*-
# Copyright (c) 2020, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import throw, _, _dict
from frappe.model.document import Document
from frappe.core.doctype.data_export.exporter import export_data


class IOTChanChildNode(Document):
	def validate(self):
		apps = {}
		for app in self.licensed_applications:
			if apps.get(app.app):
				throw(_("Duplicated App {0}").format(app.app))
			else:
				apps[app.app] = app
				app.app_name = frappe.get_value("IOT Application", app.app, "app_name")


def get_tags(doctype, name):
	tags = [tag.tag for tag in frappe.get_all("Tag Link", filters={
			"document_type": doctype,
			"document_name": name
		}, fields=["tag"])]

	return ",".join([tag for tag in tags])


def as_dict(doc, keep_modified=True, keep_owner=False, keep_creation=True, keep_docstatus=False, include_tags=False):
	keep_data = _dict({
		"name": doc.name
	})
	if keep_modified:
		keep_data['modified'] = doc.modified
	if keep_owner:
		keep_data['owner'] = doc.owner
	if keep_creation:
		keep_data['creation'] = doc.creation
	if include_tags:
		keep_data['tags'] = get_tags(doc.doctype, doc.name)
	if keep_docstatus:
		keep_data['docstatus'] = doc.docstatus

	return doc.as_dict(no_default_fields=True).update(keep_data)


def get_doc_as_dict(doc_type, name, keep_modified=True, keep_owner=False, keep_creation=True, keep_docstatus=False, include_tags=False):
	doc = None
	try:
		doc = frappe.get_doc(doc_type, name)
	except Exception as ex:
		throw("object_not_found")

	return as_dict(doc, keep_modified=keep_modified, keep_owner=keep_owner, keep_creation=keep_creation, keep_docstatus=keep_docstatus, include_tags=include_tags)


def list_doctype_objects(doctype, filters=None, order_by="creation asc", include_tags=False):
	data = []
	for d in frappe.get_all(doctype, "name", filters=filters, order_by=order_by):
		data.append(get_doc_as_dict(doctype, d.name, include_tags=include_tags, keep_modified=False))
	return data


def list_licensed_apps():
	return list_doctype_objects('IOT Chan LicensedApp', filters={"parent": 'IOT Chan Settings'})


def get_basic_info(node_name):
	return {
		'IOT Chan LicensedApp': list_licensed_apps(),
		'App Category': list_doctype_objects('App Category'),
		'IOT Hardware Architecture': list_doctype_objects('IOT Hardware Architecture'),
		'IOT Application': list_apps(node_name),
		'App Developer': list_developers_info(node_name),
		'User': list_developer_users(node_name),  # only user id
		'IOT Device': list_devices(node_name)
	}


def _list_apps(node_name):
	filters = {"parent": node_name}
	apps = [d.app for d in frappe.get_all("IOT Chan LicensedApp", fields=["app"], filters=filters)]

	settings = frappe.get_doc("IOT Chan Settings")
	for app in settings.common_licensed_apps:
		apps.append(app.app)

	frappe.logger(__name__).info(repr(apps))
	return apps


def list_apps(node_name):
	apps = _list_apps(node_name)

	return list_doctype_objects('IOT Application', filters={"name": ["in", apps]})


def list_developers(node_name):
	developers = set()
	apps = _list_apps(node_name)
	for app in apps:
		developer = frappe.get_value("IOT Application", app, "developer")
		developers.add(developer)
	return developers


def list_developer_users(node_name):
	developers = list_developers(node_name)
	users = []
	for dev in developers:
		user = frappe.get_value("App Developer", dev, "user")
		users.append(user)
	return users


def list_developers_info(node_name):
	developers = list_developers(node_name)
	return list_doctype_objects('App Developer', filters={"name": ["in", developers]})


def list_devices(node_name):
	return [d.device for d in frappe.get_all("IOT Device Owner Ship", filters={"child_node": node_name}, fields=['device'])]


def list_app_versions(node_name, app, beta=0, base_version=0):
	app_id = frappe.get_value("IOT Chan LicensedApp", {"parent": node_name, "app": app}, "app")
	if app_id is None:
		app_id = frappe.get_value("IOT Chan LicensedApp", {"parent": 'IOT Chan Settings', "app": app}, "app")

	if app_id != app:
		raise frappe.PermissionError

	filters = {
		"app": app,
		"version": [">", base_version]
	}

	fields = ['name', 'app', 'version', 'beta', 'comment']
	order_by = "version desc"
	versions = frappe.get_all("IOT Application Version", filters=filters, fields=fields, order_by=order_by)
	if len(versions) == 0:
		return []

	beta_data = versions[0]
	beta_comment = 'Comments:'

	data = None
	comment = 'Comments:'
	got_release = False
	for ver in versions:
		beta_comment = beta_comment + '\n' + ver.comment
		if data is None and ver.beta == 0:
			data = ver
			got_release = True
		if got_release:
			comment = comment + '\n' + ver.comment

	result = []
	if data:
		data.update({"comment": comment})
		result.append(data)

	if beta == 1 and beta_data.beta == 1:
		beta_data.update({"comment": beta_comment})
		result.append(beta_data)

	return result