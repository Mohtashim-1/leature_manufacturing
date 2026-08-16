# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

import frappe

ROLES = [
	"Leather Manager",
	"Tannery Operator",
	"Leather QC",
	"Leather Sales",
]


def after_install():
	ensure_roles()
	seed_masters()
	frappe.clear_cache()


def after_migrate():
	ensure_roles()
	seed_masters()
	import_missing_doctypes()


def import_missing_doctypes():
	from pathlib import Path

	from frappe.modules.import_file import import_file_by_path

	base = Path(frappe.get_app_path("leature_manufacturing")) / "leature_manufacturing" / "doctype"
	needed = ["leather_qc_test", "leather_qc_inspection", "etp_daily_log"]
	for folder in needed:
		name_map = {
			"leather_qc_test": "Leather QC Test",
			"leather_qc_inspection": "Leather QC Inspection",
			"etp_daily_log": "ETP Daily Log",
		}
		if frappe.db.exists("DocType", name_map[folder]):
			continue
		path = base / folder / f"{folder}.json"
		if path.exists():
			import_file_by_path(str(path), force=True)
	frappe.db.commit()


def ensure_roles():
	for role in ROLES:
		if not frappe.db.exists("Role", role):
			frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1}).insert(ignore_permissions=True)


def seed_masters():
	grades = [
		("A", "Grade A", "Raw Hide", 1, 0, 1.15),
		("B", "Grade B", "Raw Hide", 2, 0, 1.0),
		("C", "Grade C", "Raw Hide", 3, 0, 0.85),
		("D", "Grade D", "Raw Hide", 4, 0, 0.7),
		("Reject", "Reject / Scrap", "Reject", 9, 1, 0.1),
		("TR", "TR", "Finished", 1, 0, 1.2),
		("Export", "Export Grade", "Export", 1, 0, 1.25),
		("Local", "Local Grade", "Local", 2, 0, 1.0),
		("Economy", "Economy Grade", "Economy", 3, 0, 0.8),
	]
	for code, name, gtype, sort, reject, factor in grades:
		if frappe.db.exists("Leather Grade", code):
			continue
		frappe.get_doc(
			{
				"doctype": "Leather Grade",
				"grade_code": code,
				"grade_name": name,
				"grade_type": gtype,
				"sort_order": sort,
				"is_reject": reject,
				"price_factor": factor,
			}
		).insert(ignore_permissions=True)

	animals = [
		("Cow", 22, 24, 78),
		("Buffalo", 28, 28, 76),
		("Goat", 4.5, 6, 72),
		("Sheep", 4, 5.5, 70),
		("Calf", 8, 10, 80),
		("Camel", 30, 32, 74),
	]
	for name, wt, area, yld in animals:
		if frappe.db.exists("Animal Type", name):
			continue
		frappe.get_doc(
			{
				"doctype": "Animal Type",
				"animal_name": name,
				"typical_hide_weight_kg": wt,
				"typical_area_sqft": area,
				"expected_yield_percent": yld,
			}
		).insert(ignore_permissions=True)

	articles = [
		("NAPPA-01", "Soft Nappa", "Nappa", "Shoes", "Full Grain", 1.0, 1.2, "Soft"),
		("NUBUCK-01", "Nubuck", "Nubuck", "Shoes", "Corrected", 1.2, 1.4, "Medium"),
		("SUEDE-01", "Suede", "Suede", "Garments", "Split", 0.6, 0.9, "Soft"),
		("UPH-01", "Upholstery Leather", "Finished", "Upholstery", "Full Grain", 1.2, 1.6, "Firm"),
		("AUTO-01", "Automotive Leather", "Finished", "Automotive", "Corrected", 1.0, 1.4, "Firm"),
		("BELT-01", "Belt / Strap", "Crust", "Belts", "Full Grain", 2.0, 3.5, "Firm"),
	]
	for code, name, ltype, end_use, grain, tfrom, tto, temper in articles:
		if frappe.db.exists("Leather Article", code):
			continue
		frappe.get_doc(
			{
				"doctype": "Leather Article",
				"article_code": code,
				"article_name": name,
				"leather_type": ltype,
				"end_use": end_use,
				"grain_type": grain,
				"standard_thickness_from": tfrom,
				"standard_thickness_to": tto,
				"temper": temper,
			}
		).insert(ignore_permissions=True)

	colors = [
		("BLK-01", "Black", "#1a1a1a"),
		("BRN-01", "Dark Brown", "#4a2c2a"),
		("TAN-01", "Tan", "#c4a574"),
		("NVY-01", "Navy", "#1b2a4a"),
		("RED-01", "Burgundy", "#6b1d2a"),
		("NAT-01", "Natural", "#d8c3a5"),
	]
	for code, name, hex_code in colors:
		if frappe.db.exists("Leather Color", code):
			continue
		frappe.get_doc(
			{
				"doctype": "Leather Color",
				"color_code": code,
				"color_name": name,
				"hex_code": hex_code,
			}
		).insert(ignore_permissions=True)

	chemicals = [
		("CHM-SALT", "Common Salt", "Salt", "kg"),
		("CHM-ACID", "Sulfuric Acid", "Acid", "kg"),
		("CHM-CHROME", "Basic Chromium Sulfate", "Tanning Agent", "kg"),
		("CHM-BICARB", "Sodium Bicarbonate", "Alkali", "kg"),
		("CHM-ENZ", "Bating Enzyme", "Enzyme", "kg"),
		("CHM-DYE-BLK", "Black Dye", "Dye", "kg"),
		("CHM-FAT", "Fatliquor", "Fatliquor", "kg"),
		("CHM-PIG", "Pigment", "Pigment", "kg"),
		("CHM-BIND", "Acrylic Binder", "Finishing Chemical", "kg"),
		("CHM-LAC", "Lacquer", "Lacquer", "kg"),
	]
	for code, name, ctype, uom in chemicals:
		if frappe.db.exists("Leather Chemical", code):
			continue
		frappe.get_doc(
			{
				"doctype": "Leather Chemical",
				"chemical_code": code,
				"chemical_name": name,
				"chemical_type": ctype,
				"uom": uom if frappe.db.exists("UOM", uom) else None,
			}
		).insert(ignore_permissions=True)

	drums = [("D-01", "Tanning Drum 01", 5000, "Tanning"), ("D-02", "Dyeing Drum 02", 3000, "Dyeing"), ("D-03", "Beamhouse Drum 03", 4000, "Beamhouse")]
	for code, name, cap, ptype in drums:
		if frappe.db.exists("Drum", code):
			continue
		frappe.get_doc(
			{
				"doctype": "Drum",
				"drum_code": code,
				"drum_name": name,
				"capacity_kg": cap,
				"process_type": ptype,
				"status": "Available",
			}
		).insert(ignore_permissions=True)

	machines = [
		("M-SPLIT", "Splitting Machine", "Splitting"),
		("M-SHAVE", "Shaving Machine", "Shaving"),
		("M-MEAS", "Measuring Machine", "Measuring"),
		("M-SPRAY", "Spray Line", "Spray"),
		("M-EMB", "Embossing Press", "Embossing"),
	]
	for code, name, mtype in machines:
		if frappe.db.exists("Leather Machine", code):
			continue
		frappe.get_doc(
			{
				"doctype": "Leather Machine",
				"machine_code": code,
				"machine_name": name,
				"machine_type": mtype,
				"status": "Available",
			}
		).insert(ignore_permissions=True)

	hides = [
		("RH-COW-SALT", "Salted Cow Hide", "Cow", "Salted", "Piece", 78),
		("RH-BUF-SALT", "Salted Buffalo Hide", "Buffalo", "Salted", "Piece", 76),
		("RH-GOAT-DRY", "Dried Goat Skin", "Goat", "Dried", "Piece", 72),
	]
	for code, name, animal, preserve, uom, yld in hides:
		if frappe.db.exists("Raw Hide Master", code):
			continue
		frappe.get_doc(
			{
				"doctype": "Raw Hide Master",
				"hide_code": code,
				"hide_name": name,
				"animal_type": animal,
				"preservation_method": preserve,
				"purchase_uom": uom,
				"expected_yield_percent": yld,
				"default_grade": "B",
				"storage_requirement": "Salted Hide" if preserve == "Salted" else "Fresh Hide",
			}
		).insert(ignore_permissions=True)

	if not frappe.db.exists("Finished Leather Master", "FL-NAPPA-BLK"):
		frappe.get_doc(
			{
				"doctype": "Finished Leather Master",
				"product_code": "FL-NAPPA-BLK",
				"product_name": "Soft Nappa Black 1.2mm",
				"article": "NAPPA-01",
				"color": "BLK-01",
				"end_use": "Shoes",
				"finish": "Aniline / Pigment",
				"thickness_from_mm": 1.2,
				"thickness_to_mm": 1.4,
				"temper": "Soft",
				"default_grade": "A",
				"sales_uom": "Sq. ft.",
			}
		).insert(ignore_permissions=True)
