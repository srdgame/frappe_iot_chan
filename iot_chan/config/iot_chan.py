# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("IOT Chan"),
			"items": [
				{
					"type": "doctype",
					"name": "IOT Chan Settings",
					"onboard": 1,
					"description": _("IOT Chan Settings"),
				},
				{
					"type": "doctype",
					"name": "IOT Chan Child Node",
					"onboard": 1,
					"description": _("IOT Chan Child Node"),
				}
			]
		}
	]
