# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
import timeit
from frappe.utils import cint, flt, update_progress_bar, cstr
from frappe.core.doctype.data_import.importer import Importer, get_id_field


class ChanImporter(Importer):
	def process_doc(self, doc):
		if doc is None:
			frappe.logger(__name__).info('Import process_doc is None')
			return
		frappe.logger(__name__).info('Import process_doc')
		try:
			id_field = get_id_field(self.doctype)
			if frappe.get_value(self.doctype, doc.get(id_field.fieldname), "name"):
				self.update_record(doc)
			else:
				self.insert_record(doc)
		except Exception as ex:
			frappe.logger(__name__).exception(ex)
			return

	def import_data(self):
		self.before_import()

		# parse docs from rows
		payloads = self.import_file.get_payloads_for_import()

		# dont import if there are non-ignorable warnings
		warnings = self.import_file.get_warnings()
		warnings = [w for w in warnings if w.get("type") != "info"]

		frappe.logger(__name__).info('Import process_doc 1111111')

		if warnings:
			if self.console:
				self.print_grouped_warnings(warnings)
			else:
				self.data_import.db_set("template_warnings", json.dumps(warnings))
			return warnings

		frappe.logger(__name__).info('Import process_doc 22222')
		# setup import log
		if self.data_import.import_log:
			import_log = frappe.parse_json(self.data_import.import_log)
		else:
			import_log = []

		# remove previous failures from import log
		import_log = [log for log in import_log if log.get("success")]

		# get successfully imported rows
		imported_rows = []
		for log in import_log:
			log = frappe._dict(log)
			if log.success:
				imported_rows += log.row_indexes

		# start import
		total_payload_count = len(payloads)
		batch_size = frappe.conf.data_import_batch_size or 1000

		for batch_index, batched_payloads in enumerate(
			frappe.utils.create_batch(payloads, batch_size)
		):
			for i, payload in enumerate(batched_payloads):
				doc = payload.doc
				row_indexes = [row.row_number for row in payload.rows]
				current_index = (i + 1) + (batch_index * batch_size)

				if set(row_indexes).intersection(set(imported_rows)):
					print("Skipping imported rows", row_indexes)
					if total_payload_count > 5:
						frappe.publish_realtime(
							"data_import_progress",
							{
								"current": current_index,
								"total": total_payload_count,
								"skipping": True,
								"data_import": self.data_import.name,
							},
						)
					continue

				try:
					start = timeit.default_timer()
					doc = self.process_doc(doc)
					processing_time = timeit.default_timer() - start
					eta = self.get_eta(current_index, total_payload_count, processing_time)

					if self.console:
						update_progress_bar(
							"Importing {0} records".format(total_payload_count),
							current_index,
							total_payload_count,
						)
					elif total_payload_count > 5:
						frappe.publish_realtime(
							"data_import_progress",
							{
								"current": current_index,
								"total": total_payload_count,
								"docname": doc.name,
								"data_import": self.data_import.name,
								"success": True,
								"row_indexes": row_indexes,
								"eta": eta,
							},
						)

					import_log.append(
						frappe._dict(success=True, docname=doc.name, row_indexes=row_indexes)
					)
					# commit after every successful import
					frappe.db.commit()

				except Exception:
					import_log.append(
						frappe._dict(
							success=False,
							exception=frappe.get_traceback(),
							messages=frappe.local.message_log,
							row_indexes=row_indexes,
						)
					)
					frappe.clear_messages()
					# rollback if exception
					frappe.db.rollback()

		# set status
		failures = [log for log in import_log if not log.get("success")]
		if len(failures) == total_payload_count:
			status = "Pending"
		elif len(failures) > 0:
			status = "Partial Success"
		else:
			status = "Success"

		if self.console:
			self.print_import_log(import_log)
		else:
			self.data_import.db_set("status", status)
			self.data_import.db_set("import_log", json.dumps(import_log))

		self.after_import()

		return import_log


def import_file(
	doctype, file_path, import_type, submit_after_import=False, console=False
):
	"""
	Import documents in from CSV or XLSX using data import.

	:param doctype: DocType to import
	:param file_path: Path to .csv, .xls, or .xlsx file to import
	:param import_type: One of "Insert" or "Update"
	:param submit_after_import: Whether to submit documents after import
	:param console: Set to true if this is to be used from command line. Will print errors or progress to stdout.
	"""
	try:
		data_import = frappe.new_doc("Data Import")
		data_import.submit_after_import = submit_after_import
		data_import.import_type = (
			"Insert New Records" if import_type.lower() == "insert" else "Update Existing Records"
		)

		i = ChanImporter(
			doctype=doctype, file_path=file_path, data_import=data_import, console=console
		)
		import_log = i.import_data()
		frappe.logger(__name__).info('Import type: {0} result: {1}'.format(data_import.import_type, import_log))
	except Exception as ex:
		frappe.flags.in_import = False
		raise ex
