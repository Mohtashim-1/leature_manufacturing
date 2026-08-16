# Copyright (c) 2026, Leature Manufacturing
import frappe
from frappe import _


def execute(filters=None):
	columns = [
		{"label": _("Log"), "fieldname": "name", "fieldtype": "Link", "options": "ETP Daily Log", "width": 150},
		{"label": _("Date"), "fieldname": "log_date", "fieldtype": "Date", "width": 100},
		{"label": _("Wastewater"), "fieldname": "wastewater_qty", "fieldtype": "Float", "width": 110},
		{"label": _("pH"), "fieldname": "ph", "fieldtype": "Float", "width": 80},
		{"label": _("COD"), "fieldname": "cod", "fieldtype": "Float", "width": 80},
		{"label": _("BOD"), "fieldname": "bod", "fieldtype": "Float", "width": 80},
		{"label": _("Chromium"), "fieldname": "chromium", "fieldtype": "Float", "width": 90},
		{"label": _("In Limits"), "fieldname": "within_limits", "fieldtype": "Check", "width": 90},
	]
	data = frappe.get_all(
		"ETP Daily Log",
		fields=["name", "log_date", "wastewater_qty", "ph", "cod", "bod", "chromium", "within_limits"],
		order_by="log_date asc",
	)
	chart = {
		"data": {
			"labels": [str(d.log_date) for d in data],
			"datasets": [
				{"name": _("COD"), "values": [d.cod or 0 for d in data]},
				{"name": _("BOD"), "values": [d.bod or 0 for d in data]},
			],
		},
		"type": "line",
		"colors": ["#dc2626", "#2563eb"],
	}
	return columns, data, None, chart
