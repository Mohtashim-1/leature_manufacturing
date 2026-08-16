# Copyright (c) 2026, Leature Manufacturing
import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	columns = [
		{"label": _("Batch"), "fieldname": "parent", "fieldtype": "Link", "options": "Leather Production Batch", "width": 160},
		{"label": _("Chemical"), "fieldname": "chemical", "fieldtype": "Link", "options": "Leather Chemical", "width": 180},
		{"label": _("Standard"), "fieldname": "standard_qty", "fieldtype": "Float", "width": 110},
		{"label": _("Actual"), "fieldname": "actual_qty", "fieldtype": "Float", "width": 110},
		{"label": _("Variance"), "fieldname": "variance", "fieldtype": "Float", "width": 110},
		{"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 120},
	]
	conds = ["parenttype = 'Leather Production Batch'"]
	values = {}
	if filters.get("chemical"):
		conds.append("chemical = %(chemical)s")
		values["chemical"] = filters.chemical
	data = frappe.db.sql(
		f"""
		SELECT parent, chemical, standard_qty, actual_qty, variance, amount
		FROM `tabLeather Batch Chemical`
		WHERE {" AND ".join(conds)}
		ORDER BY parent DESC
		""",
		values,
		as_dict=True,
	)
	return columns, data
