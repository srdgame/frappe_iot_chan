# -*- coding: utf-8 -*-
# Copyright (c) 2020, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
import os
import time
import datetime
import requests
from frappe import throw, _
from frappe.utils import get_files_path
from app_center.app_center.doctype.iot_application_version.iot_application_version import get_latest_version
from iot_chan.iot_chan.doctype.iot_chan_settings.iot_chan_settings import IOTChanSettings
from iot_chan.data_import import import_file


def get_iot_chan_file_path(app):
	basedir = get_files_path('iot_chan_files')
	file_dir = os.path.join(basedir, app)
	if not os.path.exists(file_dir):
		os.makedirs(file_dir)

	return file_dir


def sync_basic_info():
	frappe.enqueue('iot_chan.controllers.sync._sync_basic_info')


def _sync_basic_info():
	if IOTChanSettings.get_enable_upper_center() != 1:
		frappe.logger(__name__).error("IOT Upper Center is not enabled")
		return

	iot_center = IOTChanSettings.get_iot_center()
	auth_code = IOTChanSettings.get_iot_center_auth_code()

	try:
		session = requests.session()
		session.headers['AuthorizationCode'] = auth_code
		session.headers['Content-Type'] = 'application/json'
		session.headers['Accept'] = 'application/json'

		r = requests.session().get(iot_center + "/api/method/iot_chan.sync_api.get_basic_info", timeout=10)
		json_data = r.json()
		if r.status_code != 200 or not json_data:
			frappe.logger(__name__).error(r.text)
			throw(r.text)
		else:
			import_basic_info(json_data)
	except Exception as ex:
		frappe.logger(__name__).error(ex)
		throw(repr(ex))


def import_basic_info(info):
	app_cat = info['App Category']
	iot_hw_arch = info['IOT Hardware Architecture']
	developers = info['App Developer']
	apps = info['IOT Application']
	users = info['User']
	devices = info['IOT Device']

	frappe.logger(__name__).info('Import upper IOT Center basic information')

	importer_dir = get_iot_chan_file_path('____importer')
	frappe.utils.now()

	now_stamp = time.time()
	ts = datetime.datetime.utcfromtimestamp(now_stamp)
	app_cate_path = os.path.join(importer_dir, 'app_cate.' + ts + '.csv')
	iot_hw_arch_path = os.path.join(importer_dir, 'iot_hw_arch.' + ts + '.csv')
	developers_path = os.path.join(importer_dir, 'developers.' + ts + '.csv')
	apps_path = os.path.join(importer_dir, 'apps.' + ts + '.csv')

	with open(app_cate_path, "w") as outfile:
		outfile.write(frappe.as_json(app_cat))

	with open(iot_hw_arch_path, "w") as outfile:
		outfile.write(frappe.as_json(iot_hw_arch))

	with open(apps_path, "w") as outfile:
		outfile.write(frappe.as_json(apps))

	with open(developers_path, "w") as outfile:
		outfile.write(frappe.as_json(developers))

	for user in users:
		if frappe.get_value('User', user, 'name') is None:
			frappe.logger(__name__).info('Import upper IOT Center user: {0}'.format(user))
			new_user = frappe.get_doc(dict(doctype='User', email=user, first_name='Imported User')).insert()
			new_user.save()

	for dev in devices:
		if frappe.get_value('IOT Device', dev, 'name') is None:
			frappe.logger(__name__).info('Import upper IOT Center device: {0}'.format(dev))
			new_dev = frappe.get_doc(dict(doctype='IOT Device', sn=dev, dev_name='Imported Device')).insert()
			new_dev.save()

	frappe.db.commit()

	import_file('App Category', app_cate_path, import_type='Update', submit_after_import=True, console=False)
	import_file('IOT Hardware Architecture', iot_hw_arch_path, import_type='Update', submit_after_import=True, console=False)
	import_file('App Developer', developers_path, import_type='Update', submit_after_import=True, console=False)
	import_file('IOT Application', apps_path, import_type='Update', submit_after_import=True, console=False)

	frappe.db.commit()

	# Trigger all application sync
	for d in frappe.get_all("IOT Application", ["name"]):
		sync_app_versions(d.name)

	return True


def sync_app_versions(app):
	frappe.enqueue('iot_chan.controllers.sync._sync_app_versions', app=app)


def _sync_app_versions(app):
	if IOTChanSettings.get_enable_upper_center() != 1:
		frappe.logger(__name__).error("IOT Upper Center is not enabled")
		return

	iot_center = IOTChanSettings.get_iot_center()
	auth_code = IOTChanSettings.get_iot_center_auth_code()

	base_version = get_latest_version(app, 0)

	try:
		session = requests.session()
		session.headers['AuthorizationCode'] = auth_code
		session.headers['Content-Type'] = 'application/json'
		session.headers['Accept'] = 'application/json'

		params = {"app": app, "base_version": base_version}
		r = requests.session().get(iot_center + "/api/method/iot_chan.api.get_app_versions", params=params, timeout=10)
		json_data = r.json()
		if r.status_code != 200 or not json_data:
			frappe.logger(__name__).error(r.text)
			throw(r.text)
		else:
			import_app_versions(json_data)
	except Exception as ex:
		frappe.logger(__name__).error(ex)
		throw(repr(ex))


def import_app_versions(versions):
	for ver in versions:
		data = dict(
			doctype='IOT Application Version',
			app=ver.app,
			version=ver.version,
			beta=ver.beta,
			comment=ver.comment
		)
		new_version = frappe.get_doc(data).insert()
		new_version.save()

	frappe.db.commit()