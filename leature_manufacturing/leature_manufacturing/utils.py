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
		try:
			return frappe.db.count(doctype, filters or {})
		except Exception:
			return 0

	def q(sql, values=None):
		try:
			return frappe.db.sql(sql, values or {}, as_dict=True) or []
		except Exception:
			return []

	def first(rows):
		return rows[0] if rows else frappe._dict()

	grade_rows = q(
		"""
		SELECT grade, SUM(IFNULL(area_sqft, 0)) as area, COUNT(*) as pieces
		FROM `tabLeather Piece`
		GROUP BY grade
		"""
	)
	if not grade_rows:
		grade_rows = q(
			"""
			SELECT grade, SUM(IFNULL(area_sqft, 0)) as area, SUM(IFNULL(pieces, 0)) as pieces
			FROM `tabLeather Lot`
			WHERE docstatus < 2
			GROUP BY grade
			"""
		)

	yr = first(
		q(
			"""
			SELECT AVG(weight_yield_percent) as avg_yield, AVG(area_yield) as avg_area_yield,
				SUM(IFNULL(rejected_qty, 0)) as rejected,
				SUM(IFNULL(input_weight_kg, 0)) as input_kg,
				SUM(IFNULL(output_weight_kg, 0)) as output_kg,
				SUM(IFNULL(output_area_sqft, 0)) as output_area,
				SUM(IFNULL(production_loss, 0)) as production_loss,
				SUM(IFNULL(water_qty, 0)) as water_qty,
				COUNT(*) as submitted_batches
			FROM `tabLeather Production Batch`
			WHERE docstatus = 1
			"""
		)
	)
	cost_tot = first(
		q(
			"""
			SELECT SUM(IFNULL(total_standard,0)) as standard_cost,
				SUM(IFNULL(total_actual,0)) as actual_cost,
				AVG(IFNULL(cost_per_sqft,0)) as cost_per_sqft
			FROM `tabLeather Batch Costing`
			WHERE docstatus < 2
			"""
		)
	)
	sales_tot = first(
		q(
			"""
			SELECT SUM(IFNULL(grand_total,0)) as sales_amount, SUM(IFNULL(total_qty,0)) as sales_qty,
				SUM(CASE WHEN IFNULL(is_export,0)=1 THEN IFNULL(grand_total,0) ELSE 0 END) as export_amount
			FROM `tabLeather Sales Order`
			WHERE docstatus < 2
			"""
		)
	)
	po_tot = first(
		q(
			"""
			SELECT SUM(IFNULL(landed_cost,0)) as landed_cost, SUM(IFNULL(hide_amount,0)) as hide_amount,
				COUNT(*) as po_count
			FROM `tabHide Purchase Order`
			WHERE docstatus < 2
			"""
		)
	)
	waste_tot = first(
		q(
			"""
			SELECT SUM(IFNULL(qty,0)) as waste_qty, SUM(IFNULL(sale_value,0)) as waste_sale
			FROM `tabWaste Record`
			"""
		)
	)
	piece_area = first(
		q(
			"""
			SELECT SUM(CASE WHEN status='Available' THEN IFNULL(area_sqft,0) ELSE 0 END) as available_area,
				SUM(IFNULL(area_sqft,0)) as piece_area, COUNT(*) as piece_count
			FROM `tabLeather Piece`
			"""
		)
	)
	chem_tot = first(
		q(
			"""
			SELECT SUM(IFNULL(amount,0)) as chem_amount,
				SUM(IFNULL(actual_qty,0)) as chem_qty
			FROM `tabLeather Batch Chemical`
			WHERE parenttype = 'Leather Production Batch'
			"""
		)
	)

	alerts = []
	for row in q(
		"""
		SELECT name, lot, overall_result, inspection_type, inspection_date
		FROM `tabLeather QC Inspection`
		WHERE overall_result = 'Fail' AND docstatus < 2
		ORDER BY inspection_date DESC LIMIT 8
		"""
	):
		alerts.append(
			{
				"tone": "bad",
				"text": f"QC fail {row.inspection_type or ''} on {row.lot or row.name}",
				"doctype": "Leather QC Inspection",
				"name": row.name,
			}
		)
	for row in q(
		"""
		SELECT name, log_date, cod, bod, chromium
		FROM `tabETP Daily Log`
		WHERE IFNULL(within_limits,0)=0
		ORDER BY log_date DESC LIMIT 5
		"""
	):
		alerts.append(
			{
				"tone": "warn",
				"text": f"ETP out of limits on {row.log_date} (COD {flt(row.cod):.0f})",
				"doctype": "ETP Daily Log",
				"name": row.name,
			}
		)
	for row in q(
		"""
		SELECT name, customer, complaint_type, status
		FROM `tabLeather Complaint`
		WHERE status != 'Closed'
		ORDER BY complaint_date DESC LIMIT 5
		"""
	):
		alerts.append(
			{
				"tone": "warn",
				"text": f"Complaint {row.complaint_type} — {row.customer} ({row.status})",
				"doctype": "Leather Complaint",
				"name": row.name,
			}
		)
	for row in q(
		"""
		SELECT name, process_stage, weight_yield_percent
		FROM `tabLeather Production Batch`
		WHERE docstatus < 2 AND IFNULL(weight_yield_percent,0) < 90
		ORDER BY posting_date DESC LIMIT 5
		"""
	):
		alerts.append(
			{
				"tone": "warn",
				"text": f"Low yield {flt(row.weight_yield_percent):.1f}% on {row.name} ({row.process_stage})",
				"doctype": "Leather Production Batch",
				"name": row.name,
			}
		)

	return {
		"kpis": {
			"raw_lots": count("Leather Lot", {"lot_stage": "Raw Hide"}),
			"beamhouse_lots": count("Leather Lot", {"lot_stage": "Beamhouse"}),
			"wet_blue_lots": count("Leather Lot", {"lot_stage": "Wet Blue"}),
			"crust_lots": count("Leather Lot", {"lot_stage": "Crust"}),
			"dyeing_lots": count("Leather Lot", {"lot_stage": "Dyeing"}),
			"finishing_lots": count("Leather Lot", {"lot_stage": "Finishing"}),
			"finished_lots": count("Leather Lot", {"lot_stage": "Finished"}),
			"in_process_lots": count("Leather Lot", {"status": "In Process"}),
			"total_lots": count("Leather Lot"),
			"open_orders": count(
				"Leather Sales Order",
				{"status": ["not in", ["Closed", "Cancelled"]], "docstatus": ["<", 2]},
			),
			"export_orders": count("Leather Sales Order", {"is_export": 1, "docstatus": ["<", 2]}),
			"open_complaints": count("Leather Complaint", {"status": ["not in", ["Closed"]]}),
			"available_pieces": count("Leather Piece", {"status": "Available"}),
			"allocated_pieces": count("Leather Piece", {"status": "Allocated"}),
			"packed_pieces": count("Leather Piece", {"status": "Packed"}),
			"qc_pending": count("Leather QC Inspection", {"overall_result": "Pending"}),
			"qc_pass": count("Leather QC Inspection", {"overall_result": "Pass"}),
			"qc_fail": count("Leather QC Inspection", {"overall_result": "Fail"}),
			"open_pos": count(
				"Hide Purchase Order",
				{"status": ["not in", ["Closed", "Cancelled"]], "docstatus": ["<", 2]},
			),
			"open_maintenance": count(
				"Leather Maintenance", {"status": ["not in", ["Closed", "Completed"]]}
			),
			"lab_open": count("Lab Sample", {"status": ["in", ["Draft", "In Lab"]]}),
			"avg_yield": flt(yr.avg_yield),
			"avg_area_yield": flt(yr.avg_area_yield),
			"input_kg": flt(yr.input_kg),
			"output_kg": flt(yr.output_kg),
			"output_area": flt(yr.output_area),
			"rejected": flt(yr.rejected),
			"production_loss": flt(yr.production_loss),
			"water_qty": flt(yr.water_qty),
			"submitted_batches": flt(yr.submitted_batches),
			"standard_cost": flt(cost_tot.standard_cost),
			"actual_cost": flt(cost_tot.actual_cost),
			"cost_variance": flt(cost_tot.actual_cost) - flt(cost_tot.standard_cost),
			"cost_per_sqft": flt(cost_tot.cost_per_sqft),
			"sales_amount": flt(sales_tot.sales_amount),
			"sales_qty": flt(sales_tot.sales_qty),
			"export_amount": flt(sales_tot.export_amount),
			"landed_cost": flt(po_tot.landed_cost),
			"hide_amount": flt(po_tot.hide_amount),
			"po_count": flt(po_tot.po_count),
			"waste_qty": flt(waste_tot.waste_qty),
			"waste_sale": flt(waste_tot.waste_sale),
			"available_area": flt(piece_area.available_area),
			"piece_area": flt(piece_area.piece_area),
			"piece_count": flt(piece_area.piece_count),
			"chem_amount": flt(chem_tot.chem_amount),
			"chem_qty": flt(chem_tot.chem_qty),
			"etp_out": count("ETP Daily Log", {"within_limits": 0}),
			"shipments": count("Leather Export Shipment"),
		},
		"alerts": alerts,
		"grade_mix": grade_rows,
		"hide_grades": q(
			"""
			SELECT grade, SUM(IFNULL(pieces, 0)) as pieces, SUM(IFNULL(weight_kg, 0)) as weight_kg
			FROM `tabHide Grade Summary`
			GROUP BY grade
			"""
		),
		"process_output": q(
			"""
			SELECT process_stage as process, COUNT(*) as batches,
				SUM(IFNULL(output_weight_kg, 0)) as output_kg,
				SUM(IFNULL(output_area_sqft, 0)) as output_area,
				AVG(weight_yield_percent) as avg_yield,
				SUM(IFNULL(rejected_qty, 0)) as rejected
			FROM `tabLeather Production Batch`
			WHERE docstatus < 2
			GROUP BY process_stage
			ORDER BY batches DESC
			LIMIT 16
			"""
		),
		"stages": q(
			"""
			SELECT lot_stage as stage, COUNT(*) as lots, SUM(IFNULL(weight_kg,0)) as weight_kg,
				SUM(IFNULL(area_sqft,0)) as area_sqft, SUM(IFNULL(pieces,0)) as pieces
			FROM `tabLeather Lot`
			WHERE docstatus < 2
			GROUP BY lot_stage
			"""
		),
		"chemicals": q(
			"""
			SELECT chemical, SUM(IFNULL(standard_qty,0)) as standard_qty,
				SUM(IFNULL(actual_qty,0)) as actual_qty, SUM(IFNULL(amount,0)) as amount
			FROM `tabLeather Batch Chemical`
			WHERE parenttype = 'Leather Production Batch'
			GROUP BY chemical
			ORDER BY amount DESC
			LIMIT 12
			"""
		),
		"costs": q(
			"""
			SELECT cost_head, SUM(IFNULL(standard_amount,0)) as standard_amount,
				SUM(IFNULL(actual_amount,0)) as actual_amount
			FROM `tabLeather Cost Line`
			GROUP BY cost_head
			"""
		),
		"etp": q(
			"""
			SELECT log_date, wastewater_qty, ph, cod, bod, tds, chromium, sulfide, chloride,
				sludge_qty, within_limits
			FROM `tabETP Daily Log`
			ORDER BY log_date ASC
			LIMIT 21
			"""
		),
		"sales": q(
			"""
			SELECT customer, SUM(IFNULL(grand_total,0)) as amount, SUM(IFNULL(total_qty,0)) as qty
			FROM `tabLeather Sales Order`
			WHERE docstatus < 2
			GROUP BY customer
			"""
		),
		"sales_status": q(
			"""
			SELECT status, COUNT(*) as orders, SUM(IFNULL(grand_total,0)) as amount
			FROM `tabLeather Sales Order`
			WHERE docstatus < 2
			GROUP BY status
			"""
		),
		"sales_articles": q(
			"""
			SELECT article, SUM(IFNULL(qty,0)) as qty, SUM(IFNULL(amount,0)) as amount
			FROM `tabLeather Sales Order Item`
			GROUP BY article
			ORDER BY amount DESC
			LIMIT 10
			"""
		),
		"waste": q(
			"""
			SELECT category, SUM(IFNULL(qty,0)) as qty, SUM(IFNULL(sale_value,0)) as sale_value
			FROM `tabWaste Record`
			GROUP BY category
			"""
		),
		"waste_types": q(
			"""
			SELECT waste_type, SUM(IFNULL(qty,0)) as qty
			FROM `tabWaste Record`
			GROUP BY waste_type
			ORDER BY qty DESC
			"""
		),
		"yield_trend": q(
			"""
			SELECT posting_date, process_stage, AVG(weight_yield_percent) as yield_pct,
				SUM(IFNULL(output_weight_kg,0)) as output_kg,
				SUM(IFNULL(rejected_qty,0)) as rejected
			FROM `tabLeather Production Batch`
			WHERE docstatus < 2
			GROUP BY posting_date, process_stage
			ORDER BY posting_date
			"""
		),
		"pieces": q(
			"""
			SELECT status, COUNT(*) as pieces, SUM(IFNULL(area_sqft,0)) as area
			FROM `tabLeather Piece`
			GROUP BY status
			"""
		),
		"piece_articles": q(
			"""
			SELECT IFNULL(article,'—') as article, COUNT(*) as pieces, SUM(IFNULL(area_sqft,0)) as area
			FROM `tabLeather Piece`
			GROUP BY article
			ORDER BY area DESC
			LIMIT 10
			"""
		),
		"piece_colors": q(
			"""
			SELECT IFNULL(color,'—') as color, COUNT(*) as pieces, SUM(IFNULL(area_sqft,0)) as area
			FROM `tabLeather Piece`
			GROUP BY color
			ORDER BY area DESC
			LIMIT 10
			"""
		),
		"piece_qc": q(
			"""
			SELECT qc_status, COUNT(*) as pieces, SUM(IFNULL(area_sqft,0)) as area
			FROM `tabLeather Piece`
			GROUP BY qc_status
			"""
		),
		"lots_animal": q(
			"""
			SELECT IFNULL(animal_type,'—') as animal_type, COUNT(*) as lots,
				SUM(IFNULL(weight_kg,0)) as weight_kg, SUM(IFNULL(pieces,0)) as pieces
			FROM `tabLeather Lot`
			WHERE docstatus < 2
			GROUP BY animal_type
			"""
		),
		"qc_results": q(
			"""
			SELECT overall_result as result, COUNT(*) as inspections
			FROM `tabLeather QC Inspection`
			WHERE docstatus < 2
			GROUP BY overall_result
			"""
		),
		"qc_types": q(
			"""
			SELECT inspection_type, COUNT(*) as inspections,
				SUM(CASE WHEN overall_result='Fail' THEN 1 ELSE 0 END) as failed
			FROM `tabLeather QC Inspection`
			WHERE docstatus < 2
			GROUP BY inspection_type
			"""
		),
		"qc_tests": q(
			"""
			SELECT test_name, test_result, COUNT(*) as tests
			FROM `tabLeather QC Test`
			GROUP BY test_name, test_result
			"""
		),
		"purchases": q(
			"""
			SELECT supplier, COUNT(*) as orders, SUM(IFNULL(landed_cost,0)) as landed_cost,
				SUM(IFNULL(hide_amount,0)) as hide_amount
			FROM `tabHide Purchase Order`
			WHERE docstatus < 2
			GROUP BY supplier
			"""
		),
		"purchase_animals": q(
			"""
			SELECT IFNULL(animal_type,'—') as animal_type, SUM(IFNULL(qty,0)) as qty,
				SUM(IFNULL(amount,0)) as amount
			FROM `tabHide Purchase Item`
			GROUP BY animal_type
			"""
		),
		"shifts": q(
			"""
			SELECT IFNULL(shift,'—') as shift, COUNT(*) as batches,
				SUM(IFNULL(output_weight_kg,0)) as output_kg
			FROM `tabLeather Production Batch`
			WHERE docstatus < 2
			GROUP BY shift
			"""
		),
		"drums": q(
			"""
			SELECT IFNULL(drum,'—') as drum, COUNT(*) as batches,
				SUM(IFNULL(output_weight_kg,0)) as output_kg
			FROM `tabLeather Production Batch`
			WHERE docstatus < 2
			GROUP BY drum
			ORDER BY batches DESC
			LIMIT 8
			"""
		),
		"recent_lots": q(
			"""
			SELECT name, posting_date, lot_stage, status, animal_type, article, color, grade,
				pieces, weight_kg, area_sqft, supplier
			FROM `tabLeather Lot`
			WHERE docstatus < 2
			ORDER BY modified DESC
			LIMIT 12
			"""
		),
		"recent_batches": q(
			"""
			SELECT name, posting_date, process_stage, status, input_lot, output_lot, drum, shift,
				input_weight_kg, output_weight_kg, output_area_sqft, weight_yield_percent,
				rejected_qty, production_loss
			FROM `tabLeather Production Batch`
			WHERE docstatus < 2
			ORDER BY posting_date DESC, modified DESC
			LIMIT 12
			"""
		),
		"recent_qc": q(
			"""
			SELECT name, inspection_date, inspection_type, lot, overall_result, hole_count, scar_count
			FROM `tabLeather QC Inspection`
			WHERE docstatus < 2
			ORDER BY inspection_date DESC
			LIMIT 10
			"""
		),
		"recent_orders": q(
			"""
			SELECT name, transaction_date, customer, status, is_export, total_qty, grand_total, delivery_date
			FROM `tabLeather Sales Order`
			WHERE docstatus < 2
			ORDER BY transaction_date DESC
			LIMIT 10
			"""
		),
		"recent_pos": q(
			"""
			SELECT name, transaction_date, supplier, status, hide_amount, landed_cost, origin_country
			FROM `tabHide Purchase Order`
			WHERE docstatus < 2
			ORDER BY transaction_date DESC
			LIMIT 8
			"""
		),
		"recent_complaints": q(
			"""
			SELECT name, complaint_date, customer, complaint_type, status, lot
			FROM `tabLeather Complaint`
			ORDER BY complaint_date DESC
			LIMIT 8
			"""
		),
		"recent_shipments": q(
			"""
			SELECT name, shipment_date, customer, status, container_no, lc_number, sales_order
			FROM `tabLeather Export Shipment`
			ORDER BY shipment_date DESC
			LIMIT 8
			"""
		),
		"recent_costing": q(
			"""
			SELECT name, costing_date, lot, finished_area_sqft, total_standard, total_actual, cost_per_sqft
			FROM `tabLeather Batch Costing`
			WHERE docstatus < 2
			ORDER BY costing_date DESC
			LIMIT 8
			"""
		),
		"recent_waste": q(
			"""
			SELECT name, posting_date, waste_type, category, qty, uom, sale_value, source_lot
			FROM `tabWaste Record`
			ORDER BY posting_date DESC
			LIMIT 8
			"""
		),
		"recent_etp": q(
			"""
			SELECT name, log_date, wastewater_qty, ph, cod, bod, chromium, within_limits
			FROM `tabETP Daily Log`
			ORDER BY log_date DESC
			LIMIT 8
			"""
		),
	}
