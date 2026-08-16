# Copyright (c) 2026, Leature Manufacturing
import frappe
from frappe import _


def execute(filters=None):
	columns = [
		{"label": _("Costing"), "fieldname": "name", "fieldtype": "Link", "options": "Leather Batch Costing", "width": 150},
		{"label": _("Lot"), "fieldname": "lot", "fieldtype": "Link", "options": "Leather Lot", "width": 140},
		{"label": _("Date"), "fieldname": "costing_date", "fieldtype": "Date", "width": 100},
		{"label": _("Area sq. ft."), "fieldname": "finished_area_sqft", "fieldtype": "Float", "width": 110},
		{"label": _("Standard"), "fieldname": "total_standard", "fieldtype": "Currency", "width": 120},
		{"label": _("Actual"), "fieldname": "total_actual", "fieldtype": "Currency", "width": 120},
		{"label": _("Cost / sq. ft."), "fieldname": "cost_per_sqft", "fieldtype": "Currency", "width": 120},
	]
	data = frappe.get_all(
		"Leather Batch Costing",
		filters={"docstatus": ["<", 2]},
		fields=["name", "lot", "costing_date", "finished_area_sqft", "total_standard", "total_actual", "cost_per_sqft"],
		order_by="costing_date desc",
	)
	return columns, data
