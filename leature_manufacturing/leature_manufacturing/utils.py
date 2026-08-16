# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt


def calc_yield(input_weight, output_weight, output_area=None):
	input_weight = flt(input_weight)
	output_weight = flt(output_weight)
	output_area = flt(output_area)
	weight_yield = (output_weight / input_weight * 100) if input_weight else 0
	area_yield = (output_area / input_weight) if input_weight else 0
	return {"weight_yield": weight_yield, "area_yield": area_yield}


def chemical_requirement(batch_weight, percent):
	return flt(batch_weight) * flt(percent) / 100.0


def apply_recipe_to_batch(batch):
	if not batch.recipe or not batch.input_weight_kg:
		return
	recipe = frappe.get_doc("Leather Recipe", batch.recipe)
	existing = {row.chemical for row in batch.chemicals or []}
	for ing in recipe.ingredients or []:
		if ing.chemical in existing:
			continue
		qty = flt(ing.qty)
		if (ing.basis or "").startswith("%"):
			qty = chemical_requirement(batch.input_weight_kg, ing.qty)
		batch.append(
			"chemicals",
			{
				"chemical": ing.chemical,
				"standard_qty": qty,
				"uom": ing.uom,
			},
		)


def get_lot_chain(lot_name, direction="forward"):
	"""Walk parent_lot links. forward = children, reverse = ancestors."""
	chain = []
	if not lot_name:
		return chain
	if direction == "reverse":
		current = lot_name
		seen = set()
		while current and current not in seen:
			seen.add(current)
			doc = frappe.db.get_value(
				"Leather Lot",
				current,
				["name", "lot_stage", "parent_lot", "supplier", "article", "color", "grade", "pieces", "weight_kg", "area_sqft"],
				as_dict=True,
			)
			if not doc:
				break
			chain.append(doc)
			current = doc.parent_lot
		return chain

	# forward: lots that list this as parent, recursively
	queue = [lot_name]
	seen = set()
	while queue:
		current = queue.pop(0)
		if current in seen:
			continue
		seen.add(current)
		doc = frappe.db.get_value(
			"Leather Lot",
			current,
			["name", "lot_stage", "parent_lot", "supplier", "article", "color", "grade", "pieces", "weight_kg", "area_sqft"],
			as_dict=True,
		)
		if doc:
			chain.append(doc)
		children = frappe.get_all("Leather Lot", filters={"parent_lot": current}, pluck="name")
		queue.extend(children)
	return chain


@frappe.whitelist()
def trace_lot(lot):
	return {
		"ancestors": get_lot_chain(lot, "reverse"),
		"descendants": get_lot_chain(lot, "forward"),
	}


@frappe.whitelist()
def suggest_allocation(article=None, color=None, grade=None, thickness_from=None, thickness_to=None, required_area=None):
	filters = {"status": "Available", "docstatus": ["<", 2]}
	if article:
		filters["article"] = article
	if color:
		filters["color"] = color
	if grade:
		filters["grade"] = grade
	pieces = frappe.get_all(
		"Leather Piece",
		filters=filters,
		fields=["name", "lot", "article", "color", "grade", "area_sqft", "thickness_mm", "warehouse"],
		order_by="area_sqft desc",
		limit=200,
	)
	if thickness_from:
		pieces = [p for p in pieces if flt(p.thickness_mm) >= flt(thickness_from)]
	if thickness_to:
		pieces = [p for p in pieces if not p.thickness_mm or flt(p.thickness_mm) <= flt(thickness_to)]
	selected = []
	running = 0
	need = flt(required_area)
	for p in pieces:
		selected.append(p)
		running += flt(p.area_sqft)
		if need and running >= need:
			break
	return {"pieces": selected, "allocated_area": running}


@frappe.whitelist()
def dashboard_data():
	def count(doctype, filters=None):
		return frappe.db.count(doctype, filters or {})

	grade_rows = frappe.db.sql(
		"""
		SELECT grade, SUM(IFNULL(area_sqft, 0)) as area, COUNT(*) as pieces
		FROM `tabLeather Piece`
		GROUP BY grade
		""",
		as_dict=True,
	)
	if not grade_rows:
		grade_rows = frappe.db.sql(
			"""
			SELECT grade, SUM(IFNULL(area_sqft, 0)) as area, SUM(IFNULL(pieces, 0)) as pieces
			FROM `tabLeather Lot`
			WHERE docstatus < 2
			GROUP BY grade
			""",
			as_dict=True,
		)
	hide_grades = frappe.db.sql(
		"""
		SELECT grade, SUM(IFNULL(pieces, 0)) as pieces, SUM(IFNULL(weight_kg, 0)) as weight_kg
		FROM `tabHide Grade Summary`
		GROUP BY grade
		""",
		as_dict=True,
	)
	process_rows = frappe.db.sql(
		"""
		SELECT process_stage as process, COUNT(*) as batches, SUM(IFNULL(output_weight_kg, 0)) as output_kg
		FROM `tabLeather Production Batch`
		WHERE docstatus < 2
		GROUP BY process_stage
		ORDER BY batches DESC
		LIMIT 12
		""",
		as_dict=True,
	)
	yield_row = frappe.db.sql(
		"""
		SELECT AVG(weight_yield_percent) as avg_yield, SUM(IFNULL(rejected_qty, 0)) as rejected,
			SUM(IFNULL(input_weight_kg, 0)) as input_kg, SUM(IFNULL(output_weight_kg, 0)) as output_kg,
			SUM(IFNULL(output_area_sqft, 0)) as output_area
		FROM `tabLeather Production Batch`
		WHERE docstatus = 1
		""",
		as_dict=True,
	)
	stage_rows = frappe.db.sql(
		"""
		SELECT lot_stage as stage, COUNT(*) as lots, SUM(IFNULL(weight_kg,0)) as weight_kg,
			SUM(IFNULL(area_sqft,0)) as area_sqft
		FROM `tabLeather Lot`
		WHERE docstatus < 2
		GROUP BY lot_stage
		""",
		as_dict=True,
	)
	chem_rows = frappe.db.sql(
		"""
		SELECT chemical, SUM(IFNULL(standard_qty,0)) as standard_qty,
			SUM(IFNULL(actual_qty,0)) as actual_qty, SUM(IFNULL(amount,0)) as amount
		FROM `tabLeather Batch Chemical`
		WHERE parenttype = 'Leather Production Batch'
		GROUP BY chemical
		ORDER BY amount DESC
		LIMIT 8
		""",
		as_dict=True,
	)
	cost_rows = frappe.db.sql(
		"""
		SELECT cost_head, SUM(IFNULL(standard_amount,0)) as standard_amount,
			SUM(IFNULL(actual_amount,0)) as actual_amount
		FROM `tabLeather Cost Line`
		GROUP BY cost_head
		""",
		as_dict=True,
	)
	etp_rows = frappe.db.sql(
		"""
		SELECT log_date, wastewater_qty, ph, cod, bod, chromium, within_limits
		FROM `tabETP Daily Log`
		ORDER BY log_date ASC
		LIMIT 14
		""",
		as_dict=True,
	)
	sales_rows = frappe.db.sql(
		"""
		SELECT customer, SUM(IFNULL(grand_total,0)) as amount, SUM(IFNULL(total_qty,0)) as qty
		FROM `tabLeather Sales Order`
		WHERE docstatus < 2
		GROUP BY customer
		""",
		as_dict=True,
	)
	waste_rows = frappe.db.sql(
		"""
		SELECT category, SUM(IFNULL(qty,0)) as qty
		FROM `tabWaste Record`
		GROUP BY category
		""",
		as_dict=True,
	)
	yield_trend = frappe.db.sql(
		"""
		SELECT posting_date, process_stage, AVG(weight_yield_percent) as yield_pct,
			SUM(IFNULL(output_weight_kg,0)) as output_kg
		FROM `tabLeather Production Batch`
		WHERE docstatus < 2
		GROUP BY posting_date, process_stage
		ORDER BY posting_date
		""",
		as_dict=True,
	)
	piece_rows = frappe.db.sql(
		"""
		SELECT status, COUNT(*) as pieces, SUM(IFNULL(area_sqft,0)) as area
		FROM `tabLeather Piece`
		GROUP BY status
		""",
		as_dict=True,
	)
	yr = yield_row[0] if yield_row else frappe._dict()
	return {
		"kpis": {
			"raw_lots": count("Leather Lot", {"lot_stage": "Raw Hide"}),
			"wet_blue_lots": count("Leather Lot", {"lot_stage": "Wet Blue"}),
			"finished_lots": count("Leather Lot", {"lot_stage": "Finished"}),
			"open_orders": count(
				"Leather Sales Order",
				{"status": ["not in", ["Closed", "Cancelled"]], "docstatus": ["<", 2]},
			),
			"open_complaints": count("Leather Complaint", {"status": ["not in", ["Closed"]]}),
			"available_pieces": count("Leather Piece", {"status": "Available"}),
			"avg_yield": flt(yr.avg_yield),
			"input_kg": flt(yr.input_kg),
			"output_kg": flt(yr.output_kg),
			"output_area": flt(yr.output_area),
			"rejected": flt(yr.rejected),
		},
		"grade_mix": grade_rows,
		"hide_grades": hide_grades,
		"process_output": process_rows,
		"stages": stage_rows,
		"chemicals": chem_rows,
		"costs": cost_rows,
		"etp": etp_rows,
		"sales": sales_rows,
		"waste": waste_rows,
		"yield_trend": yield_trend,
		"pieces": piece_rows,
	}
