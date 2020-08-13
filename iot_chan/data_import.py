# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.core.doctype.data_import.importer import Importer, get_id_field


class ChanImporter(Importer):
	def process_doc(self, doc):
		id_field = get_id_field(self.doctype)
		if frappe.get_value(self.doctype, doc.get(id_field.fieldname), "name"):
			self.update_record(doc)
		else:
			self.insert_record(doc)


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

	data_import = frappe.new_doc("Data Import")
	data_import.submit_after_import = submit_after_import
	data_import.import_type = (
		"Insert New Records" if import_type.lower() == "insert" else "Update Existing Records"
	)

	i = ChanImporter(
		doctype=doctype, file_path=file_path, data_import=data_import, console=console
	)
	import_log = i.import_data()
	frappe.logger(__name__).info('Import result{0}'.format(import_log))