# Copyright (c) 2026, Leature Manufacturing
import frappe
from frappe import _


def execute(filters=None):
	columns = [
		{"label": _("Piece"), "fieldname": "name", "fieldtype": "Link", "options": "Leather Piece", "width": 150},
		{"label": _("Lot"), "fieldname": "lot", "fieldtype": "Link", "options": "Leather Lot", "width": 140},
		{"label": _("Article"), "fieldname": "article", "fieldtype": "Link", "options": "Leather Article", "width": 120},
		{"label": _("Color"), "fieldname": "color", "fieldtype": "Link", "options": "Leather Color", "width": 100},
		{"label": _("Grade"), "fieldname": "grade", "fieldtype": "Link", "options": "Leather Grade", "width": 90},
		{"label": _("Area sq. ft."), "fieldname": "area_sqft", "fieldtype": "Float", "width": 110},
		{"label": _("Thickness"), "fieldname": "thickness_mm", "fieldtype": "Float", "width": 100},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
		{"label": _("Warehouse"), "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 140},
	]
	filters = filters or {}
	conds = {"docstatus": ["<", 2]}
	if filters.get("status"):
		conds["status"] = filters.status
	else:
		conds["status"] = ["in", ["Available", "Allocated", "Hold"]]
	if filters.get("article"):
		conds["article"] = filters.article
	if filters.get("color"):
		conds["color"] = filters.color
	data = frappe.get_all(
		"Leather Piece",
		filters=conds,
		fields=["name", "lot", "article", "color", "grade", "area_sqft", "thickness_mm", "status", "warehouse"],
		order_by="modified desc",
	)
	return columns, data
