# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

"""Idempotent tannery demo data for leature.codecrestsolutions.com."""

import frappe
from frappe.utils import add_days, now_datetime, today

COMPANY = "Leature Manufacturing"
WH_STORES = "Stores - LM"
WH_WIP = "Work In Progress - LM"
WH_FG = "Finished Goods - LM"


def seed_demo():
	if frappe.db.count("Leather Lot") and frappe.db.count("Leather QC Inspection"):
		return
	from leature_manufacturing.install import seed_masters

	seed_masters()
	_parties()
	_extra_masters()
	recipe = _recipe()
	lots = _lots()
	po = _purchase(lots["raw"])
	_receiving(po, lots["raw"])
	_grading(lots["raw"])
	_batches(lots, recipe)
	_measurement(lots["finished"])
	pieces = _pieces(lots["finished"])
	_qc(lots)
	so = _sales()
	_allocation(so, pieces)
	_packing(so, pieces, lots["finished"])
	_export(so)
	_costing(lots["finished"])
	_etp()
	_waste(lots)
	_complaint(so, lots["finished"])
	_lab(so)
	_schedule()
	_ops()
	frappe.db.commit()


def _submit(doc):
	doc.insert(ignore_permissions=True)
	if getattr(doc.meta, "is_submittable", 0):
		doc.submit()
	return doc


def _parties():
	if not frappe.db.exists("Supplier", "Sindh Hide Traders"):
		frappe.get_doc(
			{
				"doctype": "Supplier",
				"supplier_name": "Sindh Hide Traders",
				"supplier_group": "Raw Material",
				"supplier_type": "Company",
				"country": "Pakistan",
			}
		).insert(ignore_permissions=True)
	if not frappe.db.exists("Supplier", "Punjab Livestock Co"):
		frappe.get_doc(
			{
				"doctype": "Supplier",
				"supplier_name": "Punjab Livestock Co",
				"supplier_group": "Raw Material",
				"supplier_type": "Company",
				"country": "Pakistan",
			}
		).insert(ignore_permissions=True)
	for name, territory in (("ABC Shoes", "Pakistan"), ("Nordic Auto Interiors", "Rest Of The World")):
		if frappe.db.exists("Customer", name):
			continue
		frappe.get_doc(
			{
				"doctype": "Customer",
				"customer_name": name,
				"customer_type": "Company",
				"customer_group": "Commercial",
				"territory": territory,
			}
		).insert(ignore_permissions=True)
	if not frappe.db.exists("Hide Collection Center", "Kasur Collection Yard"):
		frappe.get_doc(
			{
				"doctype": "Hide Collection Center",
				"center_name": "Kasur Collection Yard",
				"center_type": "Collection Center",
				"country": "Pakistan",
				"address": "Kasur Road, Punjab",
				"contact_person": "Imran Malik",
				"phone": "03001234567",
			}
		).insert(ignore_permissions=True)
	if not frappe.db.exists("Procurement Agent", "Rashid Hide Agent"):
		frappe.get_doc(
			{
				"doctype": "Procurement Agent",
				"agent_name": "Rashid Hide Agent",
				"commission_percent": 2.5,
				"phone": "03219876543",
				"territory": "Punjab",
			}
		).insert(ignore_permissions=True)


def _extra_masters():
	if not frappe.db.exists("Finished Leather Master", "FL-NAPPA-BRN"):
		frappe.get_doc(
			{
				"doctype": "Finished Leather Master",
				"product_code": "FL-NAPPA-BRN",
				"product_name": "Soft Nappa Dark Brown 1.2mm",
				"article": "NAPPA-01",
				"color": "BRN-01",
				"end_use": "Shoes",
				"finish": "Aniline",
				"thickness_from_mm": 1.2,
				"thickness_to_mm": 1.4,
				"temper": "Soft",
				"default_grade": "A",
				"sales_uom": "Sq. ft.",
			}
		).insert(ignore_permissions=True)
	if not frappe.db.exists("Hide Supplier Contract", {"supplier": "Sindh Hide Traders"}):
		frappe.get_doc(
			{
				"doctype": "Hide Supplier Contract",
				"naming_series": "HSC-.#####",
				"supplier": "Sindh Hide Traders",
				"animal_type": "Cow",
				"from_date": add_days(today(), -90),
				"to_date": add_days(today(), 275),
				"season": "2026",
				"purchase_uom": "Piece",
				"agreed_rate": 4200,
				"market_rate": 4350,
				"collection_center": "Kasur Collection Yard",
				"agent": "Rashid Hide Agent",
				"commission_percent": 2.5,
				"status": "Active",
			}
		).insert(ignore_permissions=True)


def _recipe():
	if frappe.db.exists("Leather Recipe", {"recipe_name": "Wet Blue Chrome 1000kg"}):
		return frappe.db.get_value("Leather Recipe", {"recipe_name": "Wet Blue Chrome 1000kg"})
	doc = frappe.get_doc(
		{
			"doctype": "Leather Recipe",
			"naming_series": "RCP-.#####",
			"recipe_name": "Wet Blue Chrome 1000kg",
			"recipe_type": "Wet Blue",
			"article": "NAPPA-01",
			"tanning_method": "Chrome Tanning",
			"is_approved": 1,
			"ingredients": [
				{"chemical": "CHM-SALT", "basis": "% of Hide Weight", "qty": 8, "uom": "kg", "stage": "Pickling"},
				{"chemical": "CHM-ACID", "basis": "% of Hide Weight", "qty": 1.5, "uom": "kg", "stage": "Pickling"},
				{"chemical": "CHM-CHROME", "basis": "% of Hide Weight", "qty": 7.5, "uom": "kg", "stage": "Chrome Tanning"},
				{"chemical": "CHM-BICARB", "basis": "% of Hide Weight", "qty": 2, "uom": "kg", "stage": "Chrome Tanning"},
			],
			"process_notes": "Demo wet-blue chrome recipe. Chrome = 7.5% of hide weight.",
		}
	)
	doc.insert(ignore_permissions=True)
	dye = frappe.get_doc(
		{
			"doctype": "Leather Recipe",
			"naming_series": "RCP-.#####",
			"recipe_name": "Nappa Black Dyeing",
			"recipe_type": "Dyeing",
			"article": "NAPPA-01",
			"color": "BLK-01",
			"customer": "ABC Shoes",
			"is_approved": 1,
			"ingredients": [
				{"chemical": "CHM-DYE-BLK", "basis": "% of Hide Weight", "qty": 3.2, "uom": "kg", "stage": "Dyeing"},
				{"chemical": "CHM-FAT", "basis": "% of Hide Weight", "qty": 6, "uom": "kg", "stage": "Fatliquoring"},
				{"chemical": "CHM-PIG", "basis": "% of Hide Weight", "qty": 1.2, "uom": "kg", "stage": "Spray Finishing"},
				{"chemical": "CHM-BIND", "basis": "% of Hide Weight", "qty": 4, "uom": "kg", "stage": "Spray Finishing"},
				{"chemical": "CHM-LAC", "basis": "% of Hide Weight", "qty": 1.5, "uom": "kg", "stage": "Spray Finishing"},
			],
		}
	)
	dye.insert(ignore_permissions=True)
	if not frappe.db.exists("Leather Process Route", {"route_name": "Cow Hide to Soft Nappa"}):
		frappe.get_doc(
			{
				"doctype": "Leather Process Route",
				"naming_series": "RTE-.#####",
				"route_name": "Cow Hide to Soft Nappa",
				"article": "NAPPA-01",
				"animal_type": "Cow",
				"is_default": 1,
				"expected_weight_yield": 62,
				"expected_area_yield": 1.15,
				"operations": [
					{"operation": "Soaking", "sequence": 1, "standard_time_min": 480, "expected_yield_percent": 98},
					{"operation": "Liming", "sequence": 2, "standard_time_min": 720, "expected_yield_percent": 95},
					{"operation": "Chrome Tanning", "sequence": 3, "recipe": doc.name, "standard_time_min": 360, "expected_yield_percent": 88},
					{"operation": "Splitting", "sequence": 4, "standard_time_min": 180, "expected_yield_percent": 92},
					{"operation": "Dyeing", "sequence": 5, "recipe": dye.name, "standard_time_min": 240, "expected_yield_percent": 97},
					{"operation": "Spray Finishing", "sequence": 6, "standard_time_min": 120, "expected_yield_percent": 99},
				],
			}
		).insert(ignore_permissions=True)
	return doc.name


def _lots():
	chain = [
		("raw", "Raw Hide", "In Stock", WH_STORES, "Salted Hide", None, 980, 21560, 0, "B", None, None),
		("beam", "Beamhouse", "In Process", WH_WIP, "Salted Hide", "raw", 980, 22800, 0, "B", None, None),
		("wet", "Wet Blue", "In Stock", WH_WIP, "Wet Blue", "beam", 960, 19800, 0, "B", None, None),
		("split", "Splitting", "In Process", WH_WIP, "Wet Blue", "wet", 960, 17600, 18500, "B", "NAPPA-01", None),
		("dye", "Dyeing", "In Process", WH_WIP, "Crust", "split", 950, 17200, 21400, "A", "NAPPA-01", "BLK-01"),
		("fin", "Finishing", "In Process", WH_WIP, "Finished Leather", "dye", 940, 16900, 22800, "A", "NAPPA-01", "BLK-01"),
		("finished", "Finished", "In Stock", WH_FG, "Finished Leather", "fin", 920, 16500, 24680, "A", "NAPPA-01", "BLK-01"),
		("buf_raw", "Raw Hide", "In Stock", WH_STORES, "Salted Hide", None, 400, 11200, 0, "C", None, None),
		("buf_wet", "Wet Blue", "In Stock", WH_WIP, "Wet Blue", "buf_raw", 390, 9800, 0, "B", None, None),
	]
	created = {}
	dates = {
		"raw": add_days(today(), -12),
		"beam": add_days(today(), -11),
		"wet": add_days(today(), -9),
		"split": add_days(today(), -7),
		"dye": add_days(today(), -5),
		"fin": add_days(today(), -3),
		"finished": add_days(today(), -1),
		"buf_raw": add_days(today(), -6),
		"buf_wet": add_days(today(), -2),
	}
	animal = {"raw": "Cow", "beam": "Cow", "wet": "Cow", "split": "Cow", "dye": "Cow", "fin": "Cow", "finished": "Cow", "buf_raw": "Buffalo", "buf_wet": "Buffalo"}
	hide = {"raw": "RH-COW-SALT", "beam": "RH-COW-SALT", "wet": "RH-COW-SALT", "split": "RH-COW-SALT", "dye": "RH-COW-SALT", "fin": "RH-COW-SALT", "finished": "RH-COW-SALT", "buf_raw": "RH-BUF-SALT", "buf_wet": "RH-BUF-SALT"}
	supplier = "Sindh Hide Traders"
	for key, stage, status, wh, kind, parent, pieces, wt, area, grade, article, color in chain:
		doc = frappe.get_doc(
			{
				"doctype": "Leather Lot",
				"naming_series": "LOT-.YYYY.-.#####",
				"lot_stage": stage,
				"posting_date": dates[key],
				"status": status,
				"company": COMPANY,
				"warehouse": wh,
				"warehouse_kind": kind,
				"supplier": supplier if "buf" not in key else "Punjab Livestock Co",
				"supplier_lot": "SUP-COW-260804" if "buf" not in key else "SUP-BUF-260810",
				"raw_hide": hide[key],
				"animal_type": animal[key],
				"article": article,
				"color": color,
				"finished_product": "FL-NAPPA-BLK" if key in ("fin", "finished") else None,
				"grade": grade,
				"origin_country": "Pakistan",
				"pieces": pieces,
				"weight_kg": wt,
				"area_sqft": area or None,
				"thickness_mm": 1.25 if key in ("fin", "finished") else (1.8 if key == "wet" else 3.2),
				"moisture_percent": 55 if stage == "Wet Blue" else (12 if stage == "Finished" else 40),
				"chrome_content": 3.4 if stage in ("Wet Blue", "Finished", "Finishing", "Dyeing") else None,
				"storage_date": dates[key],
				"rate": 60 if stage == "Finished" else 32,
				"quality_condition": "Demo lot — good salt / grain" if key == "raw" else "Demo",
				"remarks": "DEMO-SEED",
			}
		)
		if parent:
			doc.parent_lot = created[parent]
		_submit(doc)
		created[key] = doc.name
	return created


def _purchase(raw_lot):
	contract = frappe.db.get_value("Hide Supplier Contract", {"supplier": "Sindh Hide Traders"})
	doc = frappe.get_doc(
		{
			"doctype": "Hide Purchase Order",
			"naming_series": "HPO-.YYYY.-.#####",
			"supplier": "Sindh Hide Traders",
			"transaction_date": add_days(today(), -14),
			"company": COMPANY,
			"contract": contract,
			"collection_center": "Kasur Collection Yard",
			"agent": "Rashid Hide Agent",
			"origin_country": "Pakistan",
			"items": [
				{
					"raw_hide": "RH-COW-SALT",
					"animal_type": "Cow",
					"qty": 1000,
					"uom": "Piece",
					"rate": 4200,
					"origin_country": "Pakistan",
					"expected_grade": "B",
				}
			],
			"transport_charges": 185000,
			"loading_charges": 42000,
			"preservation_cost": 28000,
			"commission_amount": 105000,
			"advance_paid": 800000,
			"status": "Received",
			"remarks": "DEMO-SEED cow hide intake",
		}
	)
	_submit(doc)
	buf = frappe.get_doc(
		{
			"doctype": "Hide Purchase Order",
			"naming_series": "HPO-.YYYY.-.#####",
			"supplier": "Punjab Livestock Co",
			"transaction_date": add_days(today(), -8),
			"company": COMPANY,
			"origin_country": "Pakistan",
			"items": [
				{
					"raw_hide": "RH-BUF-SALT",
					"animal_type": "Buffalo",
					"qty": 400,
					"uom": "Piece",
					"rate": 5100,
					"origin_country": "Pakistan",
					"expected_grade": "C",
				}
			],
			"transport_charges": 64000,
			"status": "Received",
			"remarks": "DEMO-SEED buffalo hides",
		}
	)
	_submit(buf)
	return doc.name


def _receiving(po, raw_lot):
	doc = frappe.get_doc(
		{
			"doctype": "Hide Receiving Inspection",
			"naming_series": "HRI-.YYYY.-.#####",
			"purchase_order": po,
			"supplier": "Sindh Hide Traders",
			"inspection_date": add_days(today(), -12),
			"supplier_lot": "SUP-COW-260804",
			"internal_lot": raw_lot,
			"inspector": "Administrator",
			"qc_status": "Approved",
			"items": [
				{
					"raw_hide": "RH-COW-SALT",
					"pieces": 980,
					"gross_weight_kg": 24200,
					"salt_deduction_kg": 1840,
					"moisture_deduction_kg": 800,
					"damaged_hides": 18,
					"rejected_hides": 20,
					"grade": "B",
					"size": "22-26 sqft",
					"thickness_mm": 3.2,
				}
			],
			"short_quantity": 20,
			"inspection_remarks": "DEMO-SEED: 20 short vs PO, salt deduction applied.",
		}
	)
	_submit(doc)


def _grading(raw_lot):
	doc = frappe.get_doc(
		{
			"doctype": "Hide Grading",
			"naming_series": "HGR-.YYYY.-.#####",
			"lot": raw_lot,
			"grading_date": add_days(today(), -12),
			"grader": "Administrator",
			"final_grade": "B",
			"defects": [
				{"defect_type": "Scar", "count": 42, "severity": "Medium"},
				{"defect_type": "Hole", "count": 11, "severity": "Low"},
				{"defect_type": "Tick Mark", "count": 28, "severity": "Low"},
				{"defect_type": "Flay Cut", "count": 9, "severity": "High"},
				{"defect_type": "Branding Mark", "count": 6, "severity": "Medium"},
			],
			"grade_summary": [
				{"grade": "A", "pieces": 350, "weight_kg": 7700, "rate": 4800},
				{"grade": "B", "pieces": 400, "weight_kg": 8800, "rate": 4200},
				{"grade": "C", "pieces": 150, "weight_kg": 3300, "rate": 3600},
				{"grade": "D", "pieces": 60, "weight_kg": 1320, "rate": 2900},
				{"grade": "Reject", "pieces": 20, "weight_kg": 440, "rate": 400},
			],
			"remarks": "DEMO-SEED grade mix after receiving.",
		}
	)
	_submit(doc)


def _batches(lots, recipe):
	plan = [
		("Soaking", lots["raw"], lots["beam"], "D-03", None, 980, 21560, 980, 22800, 0, 28, 8.2, 480, None),
		("Liming", lots["beam"], lots["beam"], "D-03", None, 980, 22800, 975, 22100, 5, 26, 12.4, 720, None),
		("Chrome Tanning", lots["beam"], lots["wet"], "D-01", None, 975, 22100, 960, 19800, 8, 32, 3.8, 360, recipe),
		("Splitting", lots["wet"], lots["split"], None, "M-SPLIT", 960, 19800, 960, 17600, 0, None, None, 180, None),
		("Dyeing", lots["split"], lots["dye"], "D-02", None, 960, 17600, 950, 17200, 6, 45, 5.2, 240, None),
		("Spray Finishing", lots["dye"], lots["finished"], None, "M-SPRAY", 950, 17200, 920, 16500, 12, 28, None, 120, None),
	]
	route = frappe.db.get_value("Leather Process Route", {"route_name": "Cow Hide to Soft Nappa"})
	start = add_days(today(), -11)
	for i, (stage, inp, out, drum, machine, ip, iw, op, ow, rej, temp, ph, runtime, rec) in enumerate(plan):
		chems = []
		if rec:
			chems = [
				{"chemical": "CHM-SALT", "standard_qty": 1768, "actual_qty": 1800, "uom": "kg", "rate": 28},
				{"chemical": "CHM-ACID", "standard_qty": 331.5, "actual_qty": 340, "uom": "kg", "rate": 85},
				{"chemical": "CHM-CHROME", "standard_qty": 1657.5, "actual_qty": 1710, "uom": "kg", "rate": 240},
				{"chemical": "CHM-BICARB", "standard_qty": 442, "actual_qty": 430, "uom": "kg", "rate": 55},
			]
		if stage == "Dyeing":
			chems = [
				{"chemical": "CHM-DYE-BLK", "standard_qty": 563, "actual_qty": 580, "uom": "kg", "rate": 620},
				{"chemical": "CHM-FAT", "standard_qty": 1056, "actual_qty": 1100, "uom": "kg", "rate": 310},
			]
		if stage == "Spray Finishing":
			chems = [
				{"chemical": "CHM-PIG", "standard_qty": 206, "actual_qty": 210, "uom": "kg", "rate": 480},
				{"chemical": "CHM-BIND", "standard_qty": 688, "actual_qty": 700, "uom": "kg", "rate": 190},
				{"chemical": "CHM-LAC", "standard_qty": 258, "actual_qty": 250, "uom": "kg", "rate": 410},
			]
		doc = frappe.get_doc(
			{
				"doctype": "Leather Production Batch",
				"naming_series": "BAT-.YYYY.-.#####",
				"process_stage": stage,
				"posting_date": add_days(start, i * 2),
				"company": COMPANY,
				"status": "Completed",
				"recipe": rec,
				"route": route,
				"tanning_method": "Chrome Tanning" if "Tanning" in stage else None,
				"drum": drum,
				"machine": machine,
				"operator": "Administrator",
				"shift": "A",
				"start_time": now_datetime(),
				"input_lot": inp,
				"input_pieces": ip,
				"input_weight_kg": iw,
				"output_lot": out,
				"output_pieces": op,
				"output_weight_kg": ow,
				"output_area_sqft": 24680 if stage == "Spray Finishing" else (21400 if stage == "Dyeing" else 0),
				"rejected_qty": rej,
				"water_qty": iw * 2 if drum else None,
				"temperature": temp,
				"ph": ph,
				"runtime_min": runtime,
				"chemicals": chems,
				"output_form": "Grain Split" if stage == "Splitting" else "Full Hide",
				"target_thickness_mm": 1.3 if stage in ("Splitting", "Spray Finishing") else None,
				"actual_thickness_mm": 1.25 if stage == "Spray Finishing" else (1.8 if stage == "Splitting" else None),
				"remarks": "DEMO-SEED",
			}
		)
		_submit(doc)
	# in-progress buffalo tanning
	frappe.get_doc(
		{
			"doctype": "Leather Production Batch",
			"naming_series": "BAT-.YYYY.-.#####",
			"process_stage": "Chrome Tanning",
			"posting_date": today(),
			"company": COMPANY,
			"status": "In Progress",
			"recipe": recipe,
			"drum": "D-01",
			"operator": "Administrator",
			"shift": "B",
			"input_lot": lots["buf_raw"],
			"input_pieces": 400,
			"input_weight_kg": 11200,
			"output_lot": lots["buf_wet"],
			"output_pieces": 390,
			"output_weight_kg": 9800,
			"water_qty": 22400,
			"temperature": 31,
			"ph": 3.9,
			"runtime_min": 180,
			"remarks": "DEMO-SEED buffalo still in drum",
		}
	).insert(ignore_permissions=True)


def _measurement(finished):
	doc = frappe.get_doc(
		{
			"doctype": "Leather Area Measurement",
			"naming_series": "LAM-.YYYY.-.#####",
			"lot": finished,
			"measurement_date": add_days(today(), -1),
			"machine": "M-MEAS",
			"operator": "Administrator",
			"uom": "SQ FT",
			"pieces": [
				{"length": 5.2, "width": 4.4, "grade": "A", "thickness_mm": 1.24},
				{"length": 4.8, "width": 4.1, "grade": "A", "thickness_mm": 1.26},
				{"length": 5.6, "width": 4.5, "grade": "B", "thickness_mm": 1.22},
				{"length": 4.4, "width": 3.9, "grade": "A", "thickness_mm": 1.28},
				{"length": 5.1, "width": 4.2, "grade": "B", "thickness_mm": 1.21},
				{"length": 4.9, "width": 4.0, "grade": "A", "thickness_mm": 1.25},
			],
		}
	)
	_submit(doc)


def _pieces(finished):
	areas = [22.8, 19.6, 25.2, 17.1, 21.4, 19.6, 23.5, 18.8, 24.1, 16.4, 20.9, 22.2]
	grades = ["A", "A", "B", "A", "B", "A", "A", "B", "A", "C", "A", "B"]
	names = []
	for i, (area, grade) in enumerate(zip(areas, grades), start=1):
		status = "Available" if i > 6 else "Allocated"
		doc = frappe.get_doc(
			{
				"doctype": "Leather Piece",
				"naming_series": "FL-.YYYY.-.######",
				"lot": finished,
				"article": "NAPPA-01",
				"color": "BLK-01",
				"grade": grade,
				"area_sqft": area,
				"thickness_mm": 1.24 + (i % 5) * 0.02,
				"size": "Side",
				"warehouse": WH_FG,
				"qc_status": "Passed" if grade != "C" else "Hold",
				"status": status,
				"customer": "ABC Shoes" if status == "Allocated" else None,
				"manufacturing_date": add_days(today(), -1),
			}
		)
		doc.insert(ignore_permissions=True)
		names.append(doc.name)
	return names


def _qc(lots):
	_submit(
		frappe.get_doc(
			{
				"doctype": "Leather QC Inspection",
				"naming_series": "LQC-.YYYY.-.#####",
				"inspection_type": "Raw Hide",
				"lot": lots["raw"],
				"inspection_date": add_days(today(), -12),
				"inspector": "Administrator",
				"overall_result": "Pass",
				"hole_count": 11,
				"scar_count": 42,
				"test_rows": [
					{"test_name": "Freshness", "standard_value": "Acceptable", "actual_value": "Good", "test_result": "Pass"},
					{"test_name": "Salt condition", "standard_value": "Well salted", "actual_value": "OK", "test_result": "Pass"},
				],
				"remarks": "DEMO-SEED raw hide QC",
			}
		)
	)
	_submit(
		frappe.get_doc(
			{
				"doctype": "Leather QC Inspection",
				"naming_series": "LQC-.YYYY.-.#####",
				"inspection_type": "Wet Blue",
				"lot": lots["wet"],
				"inspection_date": add_days(today(), -9),
				"inspector": "Administrator",
				"overall_result": "Pass",
				"test_rows": [
					{"test_name": "Chrome content", "standard_value": "3.2-3.8%", "actual_value": "3.4", "test_result": "Pass"},
					{"test_name": "pH", "standard_value": "3.5-4.2", "actual_value": "3.8", "test_result": "Pass"},
					{"test_name": "Moisture", "standard_value": "50-60%", "actual_value": "55", "test_result": "Pass"},
				],
			}
		)
	)
	_submit(
		frappe.get_doc(
			{
				"doctype": "Leather QC Inspection",
				"naming_series": "LQC-.YYYY.-.#####",
				"inspection_type": "Finished Leather",
				"lot": lots["finished"],
				"inspection_date": add_days(today(), -1),
				"inspector": "Administrator",
				"overall_result": "Pass",
				"test_rows": [
					{"test_name": "Thickness", "standard_value": "1.2-1.4 mm", "actual_value": "1.25", "test_result": "Pass"},
					{"test_name": "Tensile strength", "standard_value": ">= 15 N/mm2", "actual_value": "17.2", "test_result": "Pass"},
					{"test_name": "Tear strength", "standard_value": ">= 40 N", "actual_value": "46", "test_result": "Pass"},
					{"test_name": "Flex resistance", "standard_value": "50k cycles", "actual_value": "Pass", "test_result": "Pass"},
					{"test_name": "Color fastness", "standard_value": "4-5", "actual_value": "4", "test_result": "Pass"},
					{"test_name": "Crocking", "standard_value": "Dry 4 / Wet 3", "actual_value": "4 / 3", "test_result": "Pass"},
				],
				"remarks": "DEMO-SEED finished nappa black",
			}
		)
	)


def _sales():
	doc = frappe.get_doc(
		{
			"doctype": "Leather Sales Order",
			"naming_series": "LSO-.YYYY.-.#####",
			"customer": "ABC Shoes",
			"transaction_date": add_days(today(), -4),
			"delivery_date": add_days(today(), 14),
			"company": COMPANY,
			"is_export": 0,
			"customer_po": "ABC-PO-8841",
			"status": "Allocated",
			"items": [
				{
					"finished_product": "FL-NAPPA-BLK",
					"article": "NAPPA-01",
					"color": "BLK-01",
					"thickness": "1.2-1.4 mm",
					"grade": "A",
					"qty": 2500,
					"uom": "Sq. ft.",
					"rate": 95,
					"delivery_date": add_days(today(), 14),
				},
				{
					"finished_product": "FL-NAPPA-BLK",
					"article": "NAPPA-01",
					"color": "BLK-01",
					"thickness": "1.2-1.4 mm",
					"grade": "B",
					"qty": 800,
					"uom": "Sq. ft.",
					"rate": 82,
					"delivery_date": add_days(today(), 14),
				},
			],
			"remarks": "DEMO-SEED local shoe factory order",
		}
	)
	_submit(doc)
	export_so = frappe.get_doc(
		{
			"doctype": "Leather Sales Order",
			"naming_series": "LSO-.YYYY.-.#####",
			"customer": "Nordic Auto Interiors",
			"transaction_date": add_days(today(), -2),
			"delivery_date": add_days(today(), 30),
			"company": COMPANY,
			"is_export": 1,
			"customer_po": "NAI-2026-117",
			"status": "Confirmed",
			"items": [
				{
					"finished_product": "FL-NAPPA-BLK",
					"article": "AUTO-01",
					"color": "BLK-01",
					"thickness": "1.0-1.4 mm",
					"grade": "Export",
					"qty": 12000,
					"uom": "Sq. ft.",
					"rate": 118,
					"delivery_date": add_days(today(), 30),
				}
			],
			"remarks": "DEMO-SEED export automotive program",
		}
	)
	_submit(export_so)
	return doc.name


def _allocation(so, pieces):
	items = []
	for name in pieces[:6]:
		p = frappe.get_doc("Leather Piece", name)
		items.append(
			{
				"piece": p.name,
				"lot": p.lot,
				"article": p.article,
				"color": p.color,
				"grade": p.grade,
				"area_sqft": p.area_sqft,
			}
		)
	doc = frappe.get_doc(
		{
			"doctype": "Leather Allocation",
			"naming_series": "ALC-.YYYY.-.#####",
			"sales_order": so,
			"customer": "ABC Shoes",
			"allocation_date": today(),
			"article": "NAPPA-01",
			"color": "BLK-01",
			"grade": "A",
			"required_area_sqft": 2500,
			"items": items,
			"status": "Short",
		}
	)
	_submit(doc)


def _packing(so, pieces, lot):
	items = []
	for i, name in enumerate(pieces[:6], start=1):
		p = frappe.get_doc("Leather Piece", name)
		items.append(
			{
				"bundle_no": f"BND-00{i}",
				"piece": p.name,
				"lot": lot,
				"article": p.article,
				"color": p.color,
				"grade": p.grade,
				"pieces": 1,
				"area_sqft": p.area_sqft,
				"net_weight": p.area_sqft * 0.55,
				"gross_weight": p.area_sqft * 0.62,
			}
		)
	doc = frappe.get_doc(
		{
			"doctype": "Leather Packing List",
			"naming_series": "PKG-.YYYY.-.#####",
			"sales_order": so,
			"customer": "ABC Shoes",
			"packing_date": today(),
			"customer_po": "ABC-PO-8841",
			"pack_type": "Bundle",
			"status": "Packed",
			"items": items,
		}
	)
	_submit(doc)
	return doc.name


def _export(so):
	frappe.get_doc(
		{
			"doctype": "Leather Export Shipment",
			"naming_series": "EXP-.YYYY.-.#####",
			"sales_order": frappe.db.get_value("Leather Sales Order", {"customer": "Nordic Auto Interiors"}),
			"customer": "Nordic Auto Interiors",
			"shipment_date": add_days(today(), 10),
			"proforma_invoice": "PI-NAI-2026-117",
			"lc_number": "LC-HBL-99821",
			"container_no": "TCLU-452198-7",
			"freight_forwarder": "PIA Cargo / Maersk",
			"status": "Booked",
			"exchange_rate": 278.5,
			"remarks": "DEMO-SEED export booking",
		}
	).insert(ignore_permissions=True)


def _costing(finished):
	batch = frappe.db.get_value("Leather Production Batch", {"process_stage": "Spray Finishing", "docstatus": 1})
	doc = frappe.get_doc(
		{
			"doctype": "Leather Batch Costing",
			"naming_series": "LBC-.YYYY.-.#####",
			"lot": finished,
			"batch": batch,
			"costing_date": today(),
			"finished_area_sqft": 24680,
			"items": [
				{"cost_head": "Hide", "standard_amount": 740000, "actual_amount": 790000},
				{"cost_head": "Chemical", "standard_amount": 296000, "actual_amount": 345000},
				{"cost_head": "Labor", "standard_amount": 123000, "actual_amount": 118000},
				{"cost_head": "Water", "standard_amount": 48000, "actual_amount": 54000},
				{"cost_head": "Electricity", "standard_amount": 72000, "actual_amount": 81000},
				{"cost_head": "Steam", "standard_amount": 36000, "actual_amount": 39000},
				{"cost_head": "Machine", "standard_amount": 55000, "actual_amount": 55000},
				{"cost_head": "Waste Disposal", "standard_amount": 22000, "actual_amount": 26000},
				{"cost_head": "QC", "standard_amount": 18000, "actual_amount": 18000},
				{"cost_head": "Packaging", "standard_amount": 15000, "actual_amount": 16000},
			],
		}
	)
	_submit(doc)


def _etp():
	for i in range(5):
		d = add_days(today(), -i)
		if frappe.db.exists("ETP Daily Log", {"log_date": d}):
			continue
		frappe.get_doc(
			{
				"doctype": "ETP Daily Log",
				"naming_series": "ETP-.YYYY.-.#####",
				"log_date": d,
				"wastewater_qty": 185 + i * 6,
				"ph": 7.2 + i * 0.05,
				"cod": 210 + i * 8,
				"bod": 42 + i,
				"tds": 1850 + i * 20,
				"chromium": 0.8 + i * 0.05,
				"sulfide": 1.1,
				"chloride": 620,
				"sludge_qty": 14 + i,
				"chemical_consumption": "Alum 40 kg, Lime 25 kg, Polyelectrolyte 2 kg",
				"within_limits": 1 if i < 4 else 0,
				"remarks": "DEMO-SEED daily ETP",
			}
		).insert(ignore_permissions=True)


def _waste(lots):
	batch = frappe.db.get_value("Leather Production Batch", {"process_stage": "Splitting"})
	for wtype, cat, qty, sale in (
		("Fleshings", "Saleable", 820, 45000),
		("Shavings", "Reusable", 310, 0),
		("Chrome Waste", "Hazardous", 95, 0),
		("Trimmings", "Saleable", 140, 18000),
	):
		frappe.get_doc(
			{
				"doctype": "Waste Record",
				"naming_series": "WST-.YYYY.-.#####",
				"waste_type": wtype,
				"category": cat,
				"posting_date": add_days(today(), -3),
				"source_batch": batch,
				"source_lot": lots["split"],
				"qty": qty,
				"uom": "kg",
				"disposal_method": "Sold" if cat == "Saleable" else "ETP / licensed disposal",
				"sale_value": sale,
				"remarks": "DEMO-SEED",
			}
		).insert(ignore_permissions=True)


def _complaint(so, lot):
	frappe.get_doc(
		{
			"doctype": "Leather Complaint",
			"naming_series": "CMP-.YYYY.-.#####",
			"customer": "ABC Shoes",
			"complaint_date": today(),
			"complaint_type": "Color Variation",
			"lot": lot,
			"sales_order": so,
			"status": "Investigating",
			"description": "DEMO-SEED: slight shade difference on 2 bundles vs approved swatch.",
			"root_cause": "Dye drum load 4% over standard; fatliquor actual > standard.",
			"capa": "Lock dye recipe; do not exceed 3.2% black dye on Nappa Black.",
		}
	).insert(ignore_permissions=True)


def _lab(so):
	lab = frappe.get_doc(
		{
			"doctype": "Lab Sample",
			"naming_series": "LAB-.YYYY.-.#####",
			"sample_type": "Customer Sample",
			"customer": "Nordic Auto Interiors",
			"article": "AUTO-01",
			"color": "BLK-01",
			"request_date": add_days(today(), -10),
			"status": "Approved",
			"result_notes": "DEMO-SEED: automotive black approved after 2 lab trials.",
		}
	)
	lab.insert(ignore_permissions=True)
	frappe.get_doc(
		{
			"doctype": "Customer Sample Request",
			"naming_series": "CSR-.YYYY.-.#####",
			"customer": "Nordic Auto Interiors",
			"request_date": add_days(today(), -12),
			"article": "AUTO-01",
			"color": "BLK-01",
			"end_use": "Automotive",
			"thickness": "1.0-1.4 mm",
			"finish": "Pigmented, low gloss",
			"hand_feel": "Firm",
			"sample_size": "4 sides",
			"trial_count": 2,
			"development_cost": 85000,
			"lab_sample": lab.name,
			"status": "Approved",
			"customer_comments": "Approved for 12,000 sq. ft. program.",
		}
	).insert(ignore_permissions=True)


def _schedule():
	tanning = frappe.db.get_value("Leather Production Batch", {"process_stage": "Chrome Tanning", "status": "Completed"})
	dyeing = frappe.db.get_value("Leather Production Batch", {"process_stage": "Dyeing"})
	frappe.get_doc(
		{
			"doctype": "Drum Schedule",
			"naming_series": "DRM-.YYYY.-.#####",
			"schedule_date": today(),
			"shift": "A",
			"status": "Released",
			"items": [
				{"drum": "D-01", "batch": tanning, "process_name": "Chrome Tanning", "capacity_kg": 5000},
				{"drum": "D-02", "batch": dyeing, "process_name": "Dyeing", "capacity_kg": 3000},
				{"drum": "D-03", "process_name": "Soaking", "capacity_kg": 4000},
			],
			"notes": "DEMO-SEED drum board",
		}
	).insert(ignore_permissions=True)
	frappe.get_doc(
		{
			"doctype": "Leather Production Plan",
			"naming_series": "LPP-.YYYY.-.#####",
			"plan_date": today(),
			"from_date": today(),
			"to_date": add_days(today(), 14),
			"status": "Released",
			"company": COMPANY,
			"items": [
				{
					"finished_product": "FL-NAPPA-BLK",
					"article": "NAPPA-01",
					"color": "BLK-01",
					"grade": "A",
					"required_area_sqft": 2500,
					"delivery_date": add_days(today(), 14),
					"sales_order": "ABC-PO-8841",
				},
				{
					"article": "AUTO-01",
					"color": "BLK-01",
					"grade": "Export",
					"required_area_sqft": 12000,
					"delivery_date": add_days(today(), 30),
				},
			],
			"notes": "DEMO-SEED fortnight plan",
		}
	).insert(ignore_permissions=True)


def _ops():
	frappe.get_doc(
		{
			"doctype": "Worker Productivity Log",
			"naming_series": "WPL-.YYYY.-.#####",
			"log_date": today(),
			"employee": "Administrator",
			"department": "Finishing",
			"shift": "A",
			"machine": "M-SPRAY",
			"hides_processed": 220,
			"area_finished_sqft": 4850,
			"batches_completed": 1,
		}
	).insert(ignore_permissions=True)
	frappe.get_doc(
		{
			"doctype": "Leather Maintenance",
			"naming_series": "MNT-.YYYY.-.#####",
			"maintenance_type": "Preventive",
			"asset_type": "Drum",
			"drum": "D-01",
			"request_date": add_days(today(), -1),
			"technician": "Administrator",
			"status": "Completed",
			"downtime_hours": 2,
			"repair_cost": 18500,
			"description": "DEMO-SEED: gear oil and door seal on D-01.",
		}
	).insert(ignore_permissions=True)
	if not frappe.db.exists("Sustainability Record", {"period_start": add_days(today(), -30)}):
		frappe.get_doc(
			{
				"doctype": "Sustainability Record",
				"naming_series": "SUS-.YYYY.-.#####",
				"period_start": add_days(today(), -30),
				"period_end": today(),
				"water_consumption": 9200,
				"energy_consumption": 14800,
				"chemical_consumption": 4100,
				"waste_generation": 1365,
				"recycled_water": 2100,
				"chrome_recovery": 180,
				"carbon_footprint": 62.4,
				"reach_compliant": 1,
				"zdhc_compliant": 1,
				"lwg_record": 1,
				"notes": "DEMO-SEED monthly sustainability snapshot",
			}
		).insert(ignore_permissions=True)
