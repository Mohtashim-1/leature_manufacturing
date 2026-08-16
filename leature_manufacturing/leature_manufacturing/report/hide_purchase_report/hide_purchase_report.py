# Copyright (c) 2026, Leature Manufacturing
import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	columns = [
		{"label": _("PO"), "fieldname": "name", "fieldtype": "Link", "options": "Hide Purchase Order", "width": 160},
		{"label": _("Date"), "fieldname": "transaction_date", "fieldtype": "Date", "width": 100},
		{"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 180},
		{"label": _("Hide Amount"), "fieldname": "hide_amount", "fieldtype": "Currency", "width": 130},
		{"label": _("Landed Cost"), "fieldname": "landed_cost", "fieldtype": "Currency", "width": 130},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 110},
	]
	conds = ["docstatus < 2"]
	values = {}
	if filters.get("supplier"):
		conds.append("supplier = %(supplier)s")
		values["supplier"] = filters.supplier
	data = frappe.db.sql(
		f"""
		SELECT name, transaction_date, supplier, hide_amount, landed_cost, status
		FROM `tabHide Purchase Order`
		WHERE {" AND ".join(conds)}
		ORDER BY transaction_date DESC
		""",
		values,
		as_dict=True,
	)
	chart = {
		"data": {
			"labels": [d.supplier or d.name for d in data],
			"datasets": [{"name": _("Landed Cost"), "values": [d.landed_cost or 0 for d in data]}],
		},
		"type": "bar",
		"colors": ["#0f766e"],
	}
	return columns, data, None, chart
