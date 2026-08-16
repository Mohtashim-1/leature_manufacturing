# Copyright (c) 2026, Leature Manufacturing
import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	columns = [
		{"label": _("Batch"), "fieldname": "name", "fieldtype": "Link", "options": "Leather Production Batch", "width": 160},
		{"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
		{"label": _("Process"), "fieldname": "process_stage", "fieldtype": "Data", "width": 140},
		{"label": _("Input Lot"), "fieldname": "input_lot", "fieldtype": "Link", "options": "Leather Lot", "width": 140},
		{"label": _("Input kg"), "fieldname": "input_weight_kg", "fieldtype": "Float", "width": 100},
		{"label": _("Output kg"), "fieldname": "output_weight_kg", "fieldtype": "Float", "width": 100},
		{"label": _("Weight Yield %"), "fieldname": "weight_yield_percent", "fieldtype": "Percent", "width": 120},
		{"label": _("Area Yield"), "fieldname": "area_yield", "fieldtype": "Float", "width": 110},
		{"label": _("Rejected"), "fieldname": "rejected_qty", "fieldtype": "Float", "width": 100},
		{"label": _("Drum"), "fieldname": "drum", "fieldtype": "Link", "options": "Drum", "width": 100},
	]
	conds = ["docstatus < 2"]
	values = {}
	if filters.get("from_date"):
		conds.append("posting_date >= %(from_date)s")
		values["from_date"] = filters.from_date
	if filters.get("to_date"):
		conds.append("posting_date <= %(to_date)s")
		values["to_date"] = filters.to_date
	if filters.get("process_stage"):
		conds.append("process_stage = %(process_stage)s")
		values["process_stage"] = filters.process_stage
	data = frappe.db.sql(
		f"""
		SELECT name, posting_date, process_stage, input_lot, input_weight_kg, output_weight_kg,
			weight_yield_percent, area_yield, rejected_qty, drum
		FROM `tabLeather Production Batch`
		WHERE {" AND ".join(conds)}
		ORDER BY posting_date DESC
		""",
		values,
		as_dict=True,
	)
	return columns, data
