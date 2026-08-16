# Copyright (c) 2026, Leature Manufacturing
import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	lot = filters.get("lot")
	if not lot:
		return [
			{"label": _("Lot"), "fieldname": "name", "fieldtype": "Link", "options": "Leather Lot", "width": 160},
			{"label": _("Stage"), "fieldname": "lot_stage", "fieldtype": "Data", "width": 120},
			{"label": _("Parent Lot"), "fieldname": "parent_lot", "fieldtype": "Link", "options": "Leather Lot", "width": 160},
			{"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 160},
			{"label": _("Article"), "fieldname": "article", "fieldtype": "Link", "options": "Leather Article", "width": 120},
			{"label": _("Grade"), "fieldname": "grade", "fieldtype": "Link", "options": "Leather Grade", "width": 90},
		], []
	from leature_manufacturing.leature_manufacturing.utils import get_lot_chain

	ancestors = get_lot_chain(lot, "reverse")
	descendants = get_lot_chain(lot, "forward")
	seen = set()
	data = []
	for row in list(reversed(ancestors[1:])) + descendants:
		if row.name in seen:
			continue
		seen.add(row.name)
		data.append(row)
	columns = [
		{"label": _("Lot"), "fieldname": "name", "fieldtype": "Link", "options": "Leather Lot", "width": 160},
		{"label": _("Stage"), "fieldname": "lot_stage", "fieldtype": "Data", "width": 120},
		{"label": _("Parent Lot"), "fieldname": "parent_lot", "fieldtype": "Link", "options": "Leather Lot", "width": 160},
		{"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 160},
		{"label": _("Article"), "fieldname": "article", "fieldtype": "Link", "options": "Leather Article", "width": 120},
		{"label": _("Grade"), "fieldname": "grade", "fieldtype": "Link", "options": "Leather Grade", "width": 90},
		{"label": _("Pieces"), "fieldname": "pieces", "fieldtype": "Int", "width": 80},
		{"label": _("Weight kg"), "fieldname": "weight_kg", "fieldtype": "Float", "width": 100},
		{"label": _("Area sq. ft."), "fieldname": "area_sqft", "fieldtype": "Float", "width": 110},
	]
	return columns, data
