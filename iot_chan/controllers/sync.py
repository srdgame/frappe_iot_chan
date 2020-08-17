# -*- coding: utf-8 -*-
# Copyright (c) 2020, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
import os
import time
# import pycurl
import requests
from frappe import throw, _, _dict
from frappe.utils import get_files_path
from frappe.core.doctype.version.version import get_diff
from frappe.utils import time_diff_in_seconds
from app_center.app_center.doctype.iot_application_version.iot_application_version import get_latest_version
from app_center.appmgr import get_app_release_filepath, copy_to_latest
from iot_chan.iot_chan.doctype.iot_chan_settings.iot_chan_settings import IOTChanSettings


def get_iot_chan_file_path(app):
	#basedir = get_files_path('iot_chan_files', is_private=1)
	basedir="/tmp" ## the importer parsing filename and extension has bug
	file_dir = os.path.join(basedir, app)
	if not os.path.exists(file_dir):
		os.makedirs(file_dir)

	return os.path.abspath(file_dir)


def sync_api(method, params=None):
	iot_center = IOTChanSettings.get_upper_center()
	auth_code = IOTChanSettings.get_auth_code()
	url = iot_center + "/api/method/iot_chan.api." + method

	session = requests.session()
	session.headers['AuthorizationCode'] = auth_code
	session.headers['Content-Type'] = 'application/json'
	session.headers['Accept'] = 'application/json'

	r = session.get(url, params=params, timeout=10)
	if r.status_code != 200:
		frappe.logger(__name__).error(r.text)
		throw(_("Failed to request: {0}\n text: {1}").format(method, r.text))
	try:
		json_data = _dict(r.json())
		return json_data.message or json_data
	except Exception as ex:
		frappe.logger(__name__).error(ex)
		raise ex


def sync_all():
	frappe.enqueue('iot_chan.controllers.sync._sync_all')


def _sync_all():
	if IOTChanSettings.get_enable_upper_center() != 1:
		frappe.logger(__name__).error("IOT Upper Center is not enabled")
		return

	try:
		json_data = sync_api("get_basic_info")
		import_basic_info(json_data)
	except Exception as ex:
		frappe.logger(__name__).error(ex)
		throw(repr(ex))


def update_doctype_object(doctype, doc):
	doc_name = doc.get('name')
	frappe.logger(__name__).info('update_doctype_object {0}: {1}'.format(doctype, json.dumps(doc)))
	if frappe.get_value(doctype, doc_name, 'name'):
		existing_doc = frappe.get_doc(doctype, doc_name)

		updated_doc = frappe.get_doc(doctype, doc_name)
		updated_doc.update(doc)

		if get_diff(existing_doc, updated_doc):
			frappe.logger(__name__).info('Updating document {0}: {1}'.format(doctype, doc_name))
			if time_diff_in_seconds(existing_doc.modified, updated_doc.modified) > 0:
				frappe.logger(__name__).info('Updating document {0}: {1}\'s modified'.format(doctype, doc_name))
				updated_doc.update_modified()
			updated_doc.save()
		else:
			frappe.logger(__name__).info('Skipped document {0}: {1}'.format(doctype, doc_name))
	else:
		frappe.logger(__name__).info('Insert document {0}: {1}'.format(doctype, doc_name))
		new_doc = frappe.new_doc(doctype)
		new_doc.flags.in_import = True
		new_doc.update(doc)
		new_doc.insert()

	return


def import_basic_info(info):
	lapps = info['IOT Chan LicensedApp']
	app_cat = info['App Category']
	iot_hw_arch = info['IOT Hardware Architecture']
	developers = info['App Developer']
	apps = info['IOT Application']
	users = info['User']
	devices = info['IOT Device']

	frappe.logger(__name__).info('Import upper IOT Center basic information')

	importer_dir = get_iot_chan_file_path('____importer')
	frappe.utils.now()

	now_stamp = str(int(time.time()))

	lapss_path = os.path.join(importer_dir, 'licensed_apps__' + now_stamp + '.csv')
	with open(lapss_path, "w") as outfile:
		outfile.write(frappe.as_json(lapps))

	app_cate_path = os.path.join(importer_dir, 'app_cate__' + now_stamp + '.csv')
	with open(app_cate_path, "w") as outfile:
		outfile.write(frappe.as_json(app_cat))

	iot_hw_arch_path = os.path.join(importer_dir, 'iot_hw_arch__' + now_stamp + '.csv')
	with open(iot_hw_arch_path, "w") as outfile:
		outfile.write(frappe.as_json(iot_hw_arch))

	developers_path = os.path.join(importer_dir, 'developers__' + now_stamp + '.csv')
	with open(developers_path, "w") as outfile:
		outfile.write(frappe.as_json(developers))

	apps_path = os.path.join(importer_dir, 'apps__' + now_stamp + '.csv')
	with open(apps_path, "w") as outfile:
		outfile.write(frappe.as_json(apps))

	users_path = os.path.join(importer_dir, 'users__' + now_stamp + '.csv')
	with open(users_path, "w") as outfile:
		outfile.write(frappe.as_json(users))

	devices_path = os.path.join(importer_dir, 'devices__' + now_stamp + '.csv')
	with open(devices_path, "w") as outfile:
		outfile.write(frappe.as_json(devices))

	apps_updated = []
	try:
		frappe.flags.in_import = True

		for user in users:
			if frappe.get_value('User', user, 'name') is None:
				frappe.logger(__name__).info('Import upper IOT Center user: {0} creating'.format(user))
				user_data = dict(doctype='User', email=user, first_name='Imported User', send_welcome_email=0, enabled=0)
				frappe.get_doc(user_data).insert()
			else:
				frappe.logger(__name__).info('Import upper IOT Center user: {0} exists'.format(user))

		for dev in devices:
			if frappe.get_value('IOT Device', dev, 'name') is None:
				frappe.logger(__name__).info('Import upper IOT Center device: {0} creating'.format(dev))
				dev_data = dict(doctype='IOT Device', sn=dev, dev_name='Imported Device', enabled=1)
				frappe.get_doc(dev_data).insert()
			else:
				frappe.logger(__name__).info('Import upper IOT Center device: {0} exists'.format(dev))

		for doc in app_cat:
			update_doctype_object('App Category', doc)

		for doc in iot_hw_arch:
			update_doctype_object('IOT Hardware Architecture', doc)

		for doc in developers:
			update_doctype_object('App Developer', doc)

		for doc in apps:
			if doc.get('company'):
				doc.pop('company')  # Clear the Company
			if doc.get('app_path'):
				doc.pop('app_path')
			if doc.get('app_name_unique'):
				doc.pop('app_name_unique')
			update_doctype_object('IOT Application', doc)
			apps_updated.append(doc.get('name'))

		for app in lapps:
			data = {
				"parent": "IOT Chan Settings",
				"app": app.get("app"),
				"parentfield": "common_licensed_apps",
				"parenttype": "IOT Chan Settings"
			}
			if not frappe.get_value('IOT Chan LicensedApp', filters=data):
				data.update({
					"doctype": 'IOT Chan LicensedApp',
					"app_name": app.get("app_name")
				})
				frappe.get_doc(data).insert()

		frappe.db.commit()
	except Exception as ex:
		frappe.logger(__name__).exception(ex)
		pass
	finally:
		frappe.flags.in_import = False

	# import_file('App Category', app_cate_path, import_type='Update', submit_after_import=True, console=False)
	# import_file('IOT Hardware Architecture', iot_hw_arch_path, import_type='Update', submit_after_import=True, console=False)
	# import_file('App Developer', developers_path, import_type='Update', submit_after_import=True, console=False)
	# import_file('IOT Application', apps_path, import_type='Update', submit_after_import=True, console=False)

	# Trigger all application sync
	for app in apps_updated:
		frappe.logger(__name__).info('Update IOT Application: {0} versions'.format(app))
		sync_app_versions(app)

	frappe.logger(__name__).info('Import upper IOT Center is done!!')

	return True


def sync_app_versions(app):
	frappe.enqueue('iot_chan.controllers.sync._sync_app_versions', app=app)


def _sync_app_versions(app):
	if IOTChanSettings.get_enable_upper_center() != 1:
		frappe.logger(__name__).error("IOT Upper Center is not enabled")
		return

	try:
		base_version = get_latest_version(app, 0)

		json_data = sync_api("get_app_versions", params={"app": app, "base_version": base_version})

		frappe.flags.in_import = True
		import_app_versions(json_data)
	except Exception as ex:
		frappe.logger(__name__).error(ex)
		pass
	finally:
		frappe.flags.in_import = False

	return


def import_app_versions(versions):
	for ver in versions:
		update_doctype_object('IOT Application Version', ver)
		sync_app_version_file(ver.get('app'), ver.get('version'), ver.get('beta'))

	frappe.db.commit()


def sync_app_version_file(app, version, beta):
	frappe.enqueue('iot_chan.controllers.sync._sync_app_version_file', app=app, version=version, beta=beta)


def _sync_app_version_file(app, version, beta):
	frappe.logger(__name__).info('Import upper IOT Center sync_app_version_file: {0} - {1}'.format(app, version))

	iot_center = IOTChanSettings.get_upper_center()
	ext = frappe.get_value("IOT Application", app, "app_ext")
	url = iot_center + "/files/app_center_files/" + app + "/" + str(version) + "." + ext
	file_path = get_app_release_filepath(app, version)

	'''
	c_bin = pycurl.Curl()
	c_bin.setopt(c_bin.URL, url)

	with open(file_path, 'wb') as f:
		c_bin.setopt(c_bin.WRITEDATA, f)
		c_bin.perform()

	c_md5 = pycurl.Curl()
	c_md5.setopt(c_md5.URL, url + '.md5')

	with open(file_path + '.md5', 'wb') as f:
		c_md5.setopt(c_md5.WRITEDATA, f)
		c_md5.perform()

	# with open(file_path + '.md5', 'wb') as f:
	# 	md5_sum = f.read(32)
	'''
	os.system("curl -o " + file_path + " " + url)
	os.system("curl -o " + file_path + ".md5 " + url + ".md5")

	copy_to_latest(app, version, beta)