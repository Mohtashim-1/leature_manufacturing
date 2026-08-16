# Copyright (c) 2026, Leature Manufacturing
import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	columns = [
		{"label": _("Stage"), "fieldname": "lot_stage", "fieldtype": "Data", "width": 120},
		{"label": _("Grade"), "fieldname": "grade", "fieldtype": "Link", "options": "Leather Grade", "width": 120},
		{"label": _("Lots"), "fieldname": "lots", "fieldtype": "Int", "width": 80},
		{"label": _("Pieces"), "fieldname": "pieces", "fieldtype": "Int", "width": 90},
		{"label": _("Weight kg"), "fieldname": "weight_kg", "fieldtype": "Float", "width": 110},
		{"label": _("Area sq. ft."), "fieldname": "area_sqft", "fieldtype": "Float", "width": 120},
	]
	conds = ["docstatus < 2"]
	values = {}
	if filters.get("lot_stage"):
		conds.append("lot_stage = %(lot_stage)s")
		values["lot_stage"] = filters.lot_stage
	data = frappe.db.sql(
		f"""
		SELECT lot_stage, grade, COUNT(*) as lots, SUM(IFNULL(pieces,0)) as pieces,
			SUM(IFNULL(weight_kg,0)) as weight_kg, SUM(IFNULL(area_sqft,0)) as area_sqft
		FROM `tabLeather Lot`
		WHERE {" AND ".join(conds)}
		GROUP BY lot_stage, grade
		ORDER BY lot_stage, grade
		""",
		values,
		as_dict=True,
	)
	return columns, data
