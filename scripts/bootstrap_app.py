#!/usr/bin/env python3
"""Generate leather manufacturing doctypes, workspace, reports, and pages."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "leature_manufacturing"
MOD = PKG / "leature_manufacturing"
MODULE = "Leature Manufacturing"
NOW = "2026-08-16 22:00:00.000000"

ANIMAL = "Cow\nBuffalo\nGoat\nSheep\nCalf\nCamel"
PRESERVE = "Fresh\nSalted\nDried\nBrined"
PURCHASE_UOM = "Piece\nKg\nSq. ft.\nSq. meter"
END_USE = "Shoes\nGarments\nBags\nBelts\nAutomotive\nFurniture\nGloves\nUpholstery"
STAGE = (
	"Raw Hide\nBeamhouse\nTanning\nWet Blue\nSplitting\nShaving\nCrust\n"
	"Dyeing\nFinishing\nFinished\nPacked\nShipped\nReject"
)
PROCESS = (
	"Soaking\nLiming\nFleshing\nUnhairing\nDeliming\nBating\nPickling\n"
	"Chrome Tanning\nVegetable Tanning\nChrome-free Tanning\nAldehyde Tanning\n"
	"Synthetic Tanning\nCombination Tanning\nSplitting\nShaving\n"
	"Neutralization\nRetanning\nDyeing\nFatliquoring\nSetting\nSammying\n"
	"Vacuum Drying\nHang Drying\nToggle Drying\nStaking\nMilling\nBuffing\n"
	"Spray Finishing\nRoller Coating\nIroning\nPlating\nEmbossing\nPolishing\nMeasuring"
)
TANNING = "Chrome Tanning\nVegetable Tanning\nChrome-free\nAldehyde\nSynthetic\nCombination"
CHEM_TYPE = (
	"Acid\nAlkali\nTanning Agent\nDye\nPigment\nFatliquor\nEnzyme\n"
	"Retanning Chemical\nFinishing Chemical\nLacquer\nResin\nSalt\nOther"
)
WAREHOUSE_KIND = (
	"Salted Hide\nFresh Hide\nCold Storage\nChemical\nWet Blue\nCrust\n"
	"Finished Leather\nReject\nScrap"
)
DEFECTS = (
	"Scar\nHole\nCut\nTick Mark\nBranding Mark\nVein Mark\nFlay Cut\n"
	"Putrefaction\nSalt Stain\nParasite Damage\nScratch\nMachine Damage\nGrain Damage"
)
WASTE = "Trimmings\nFleshings\nHair\nShavings\nSplits\nChrome Waste\nBuffing Dust\nSludge"
WASTE_CAT = "Reusable\nSaleable\nHazardous\nDisposal"


def f(fieldname, fieldtype, label=None, **kw):
	d = {"fieldname": fieldname, "fieldtype": fieldtype}
	if label:
		d["label"] = label
	d.update(kw)
	return d


def sec(name, label):
	return f(name, "Section Break", label)


def col(name):
	return f(name, "Column Break")


def perms(submittable=False):
	base = [
		{
			"role": "System Manager",
			"create": 1,
			"read": 1,
			"write": 1,
			"delete": 1,
			"export": 1,
			"print": 1,
			"report": 1,
			"share": 1,
			"email": 1,
		},
		{
			"role": "Leather Manager",
			"create": 1,
			"read": 1,
			"write": 1,
			"delete": 1,
			"export": 1,
			"print": 1,
			"report": 1,
			"share": 1,
			"email": 1,
		},
		{
			"role": "Tannery Operator",
			"create": 1,
			"read": 1,
			"write": 1,
			"export": 1,
			"print": 1,
			"report": 1,
		},
		{
			"role": "Leather QC",
			"create": 1,
			"read": 1,
			"write": 1,
			"export": 1,
			"print": 1,
			"report": 1,
		},
		{
			"role": "Leather Sales",
			"create": 1,
			"read": 1,
			"write": 1,
			"export": 1,
			"print": 1,
			"report": 1,
		},
	]
	if submittable:
		for p in base:
			if p["role"] in ("System Manager", "Leather Manager", "Tannery Operator", "Leather QC", "Leather Sales"):
				p["submit"] = 1
			if p["role"] in ("System Manager", "Leather Manager"):
				p["cancel"] = 1
				p["amend"] = 1
	return base


def doctype(
	name,
	fields,
	*,
	autoname=None,
	istable=0,
	issingle=0,
	is_submittable=0,
	title_field=None,
	search_fields=None,
	naming_rule=None,
	track_changes=1,
	sort_field="modified",
	is_tree=0,
	nsm_parent_field=None,
):
	field_order = [x["fieldname"] for x in fields]
	doc = {
		"actions": [],
		"allow_rename": 0 if istable or issingle else 1,
		"creation": NOW,
		"doctype": "DocType",
		"engine": "InnoDB",
		"field_order": field_order,
		"fields": fields,
		"grid_page_length": 50,
		"index_web_pages_for_search": 1,
		"istable": istable,
		"issingle": issingle,
		"is_submittable": is_submittable,
		"links": [],
		"modified": NOW,
		"modified_by": "Administrator",
		"module": MODULE,
		"name": name,
		"owner": "Administrator",
		"permissions": [] if istable else perms(is_submittable),
		"row_format": "Dynamic",
		"sort_field": sort_field,
		"sort_order": "DESC",
		"states": [],
		"track_changes": 0 if istable else track_changes,
	}
	if autoname:
		doc["autoname"] = autoname
	if naming_rule:
		doc["naming_rule"] = naming_rule
	if title_field:
		doc["title_field"] = title_field
		doc["show_title_field_in_link"] = 1
	if search_fields:
		doc["search_fields"] = search_fields
	if istable:
		doc["editable_grid"] = 1
	if is_tree:
		doc["is_tree"] = 1
		doc["nsm_parent_field"] = nsm_parent_field or "parent_leather_lot"
	return doc


def snake(name: str) -> str:
	return (
		name.lower()
		.replace(" / ", " ")
		.replace("/", " ")
		.replace("-", " ")
		.replace("&", "and")
		.replace("  ", " ")
		.strip()
		.replace(" ", "_")
	)


def class_name(name: str) -> str:
	return "".join(p.capitalize() for p in snake(name).split("_"))


def write_doctype(doc: dict, extra_py: str | None = None):
	folder = MOD / "doctype" / snake(doc["name"])
	folder.mkdir(parents=True, exist_ok=True)
	(folder / f"{snake(doc['name'])}.json").write_text(json.dumps(doc, indent=1) + "\n")
	cls = class_name(doc["name"])
	body = extra_py or "\tpass\n"
	py = (
		"# Copyright (c) 2026, mohtashim and contributors\n"
		"# For license information, please see license.txt\n\n"
		"from frappe.model.document import Document\n\n\n"
		f"class {cls}(Document):\n{body}"
	)
	(folder / f"{snake(doc['name'])}.py").write_text(py)
	(folder / f"test_{snake(doc['name'])}.py").write_text(
		"# Copyright (c) 2026, mohtashim and Contributors\n"
		"# See license.txt\n\n"
		"from frappe.tests.utils import FrappeTestCase\n\n\n"
		f"class Test{cls}(FrappeTestCase):\n\tpass\n"
	)
	if not doc.get("istable"):
		(folder / f"{snake(doc['name'])}.js").write_text(
			f"// Copyright (c) 2026, mohtashim and contributors\n"
			f"// For license information, please see license.txt\n\n"
			f"frappe.ui.form.on('{doc['name']}', {{\n\trefresh(frm) {{}}\n}});\n"
		)


# ---------------------------------------------------------------------------
# DocTypes
# ---------------------------------------------------------------------------

DOCTYPES: list[tuple[dict, str | None]] = []

DOCTYPES.append(
	(
		doctype(
			"Leather Grade",
			[
				f("grade_code", "Data", "Grade Code", reqd=1, unique=1, in_list_view=1),
				f("grade_name", "Data", "Grade Name", reqd=1, in_list_view=1),
				col("col_1"),
				f(
					"grade_type",
					"Select",
					"Grade Type",
					options="Raw Hide\nWet Blue\nFinished\nExport\nLocal\nEconomy\nReject",
					in_list_view=1,
				),
				f("sort_order", "Int", "Sort Order", default=1),
				f("is_reject", "Check", "Is Reject"),
				f("price_factor", "Float", "Price Factor", default=1),
				sec("desc_sec", "Description"),
				f("description", "Small Text", "Description"),
			],
			autoname="field:grade_code",
			naming_rule="By fieldname",
			title_field="grade_name",
			search_fields="grade_name,grade_type",
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Animal Type",
			[
				f("animal_name", "Data", "Animal Name", reqd=1, unique=1, in_list_view=1),
				f("typical_hide_weight_kg", "Float", "Typical Hide Weight (kg)"),
				col("col_1"),
				f("typical_area_sqft", "Float", "Typical Area (sq. ft.)"),
				f("expected_yield_percent", "Percent", "Expected Yield %"),
				f("description", "Small Text", "Description"),
			],
			autoname="field:animal_name",
			naming_rule="By fieldname",
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Leather Article",
			[
				f("article_code", "Data", "Article Code", reqd=1, unique=1, in_list_view=1),
				f("article_name", "Data", "Article Name", reqd=1, in_list_view=1),
				col("col_1"),
				f("leather_type", "Data", "Leather Type", in_list_view=1),
				f("end_use", "Select", "End Use", options=END_USE, in_list_view=1),
				f("grain_type", "Data", "Grain Type"),
				f("standard_thickness_from", "Float", "Thickness From (mm)"),
				f("standard_thickness_to", "Float", "Thickness To (mm)"),
				f("temper", "Data", "Temper / Softness"),
				f("disabled", "Check", "Disabled"),
				sec("spec_sec", "Specification"),
				f("surface_finish", "Data", "Surface Finish"),
				f("embossing_pattern", "Data", "Embossing Pattern"),
				f("description", "Text Editor", "Description"),
			],
			autoname="field:article_code",
			naming_rule="By fieldname",
			title_field="article_name",
			search_fields="article_name,leather_type,end_use",
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Leather Color",
			[
				f("color_code", "Data", "Internal Color Code", reqd=1, unique=1, in_list_view=1),
				f("color_name", "Data", "Color Name", reqd=1, in_list_view=1),
				col("col_1"),
				f("customer", "Link", "Customer", options="Customer"),
				f("customer_color_code", "Data", "Customer Color Code", in_list_view=1),
				f("pantone", "Data", "Pantone / Reference"),
				f("gloss_level", "Data", "Gloss Level"),
				f("hex_code", "Data", "Hex Code"),
			],
			autoname="field:color_code",
			naming_rule="By fieldname",
			title_field="color_name",
			search_fields="color_name,customer_color_code,pantone",
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Hide Collection Center",
			[
				f("center_name", "Data", "Center Name", reqd=1, unique=1, in_list_view=1),
				f("center_type", "Select", "Center Type", options="Slaughterhouse\nCollection Center\nAgent Yard\nImport Port", in_list_view=1),
				col("col_1"),
				f("country", "Link", "Country", options="Country"),
				f("address", "Small Text", "Address"),
				f("contact_person", "Data", "Contact Person"),
				f("phone", "Data", "Phone"),
			],
			autoname="field:center_name",
			naming_rule="By fieldname",
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Procurement Agent",
			[
				f("agent_name", "Data", "Agent Name", reqd=1, unique=1, in_list_view=1),
				f("supplier", "Link", "Linked Supplier", options="Supplier"),
				col("col_1"),
				f("commission_percent", "Percent", "Commission %", in_list_view=1),
				f("phone", "Data", "Phone"),
				f("territory", "Data", "Territory"),
				f("disabled", "Check", "Disabled"),
			],
			autoname="field:agent_name",
			naming_rule="By fieldname",
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Drum",
			[
				f("drum_code", "Data", "Drum Code", reqd=1, unique=1, in_list_view=1),
				f("drum_name", "Data", "Drum Name", in_list_view=1),
				col("col_1"),
				f("capacity_kg", "Float", "Capacity (kg)", reqd=1, in_list_view=1),
				f(
					"process_type",
					"Select",
					"Typical Process",
					options="Beamhouse\nTanning\nDyeing\nRetanning\nMulti",
					in_list_view=1,
				),
				f("status", "Select", "Status", options="Available\nIn Use\nCleaning\nMaintenance\nBreakdown", default="Available"),
				f("location", "Data", "Location"),
				f("last_maintenance_on", "Date", "Last Maintenance On"),
			],
			autoname="field:drum_code",
			naming_rule="By fieldname",
			title_field="drum_name",
			search_fields="drum_name,process_type,status",
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Leather Machine",
			[
				f("machine_code", "Data", "Machine Code", reqd=1, unique=1, in_list_view=1),
				f("machine_name", "Data", "Machine Name", reqd=1, in_list_view=1),
				col("col_1"),
				f(
					"machine_type",
					"Select",
					"Machine Type",
					options=(
						"Fleshing\nSplitting\nShaving\nSammying\nStaking\nBuffing\n"
						"Spray\nRoller Coater\nEmbossing\nMeasuring\nIroning\nOther"
					),
					in_list_view=1,
				),
				f("status", "Select", "Status", options="Available\nIn Use\nMaintenance\nBreakdown", default="Available"),
				f("asset", "Link", "Asset", options="Asset"),
				f("location", "Data", "Location"),
			],
			autoname="field:machine_code",
			naming_rule="By fieldname",
			title_field="machine_name",
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Raw Hide Master",
			[
				f("hide_code", "Data", "Hide Code", reqd=1, unique=1, in_list_view=1),
				f("hide_name", "Data", "Hide Name", reqd=1, in_list_view=1),
				f("item", "Link", "Stock Item", options="Item"),
				col("col_1"),
				f("animal_type", "Link", "Animal Type", options="Animal Type", reqd=1, in_list_view=1),
				f("preservation_method", "Select", "Preservation", options=PRESERVE, in_list_view=1),
				f("origin_country", "Link", "Country of Origin", options="Country"),
				f("breed", "Data", "Breed"),
				f("sex", "Select", "Sex", options="Male\nFemale\nMixed"),
				sec("spec_sec", "Size & Quality"),
				f("weight_from_kg", "Float", "Weight From (kg)"),
				f("weight_to_kg", "Float", "Weight To (kg)"),
				col("col_2"),
				f("size_from", "Float", "Size From"),
				f("size_to", "Float", "Size To"),
				f("thickness_from_mm", "Float", "Thickness From (mm)"),
				f("thickness_to_mm", "Float", "Thickness To (mm)"),
				sec("comm_sec", "Commercial"),
				f("purchase_uom", "Select", "Purchase Unit", options=PURCHASE_UOM, default="Piece"),
				f("expected_yield_percent", "Percent", "Expected Yield %"),
				f("defect_tolerance_percent", "Percent", "Defect Tolerance %"),
				f("storage_requirement", "Select", "Storage", options=WAREHOUSE_KIND),
				f("default_grade", "Link", "Default Grade", options="Leather Grade"),
				f("description", "Small Text", "Description"),
			],
			autoname="field:hide_code",
			naming_rule="By fieldname",
			title_field="hide_name",
			search_fields="hide_name,animal_type,preservation_method",
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Finished Leather Master",
			[
				f("product_code", "Data", "Product Code", reqd=1, unique=1, in_list_view=1),
				f("product_name", "Data", "Product Name", reqd=1, in_list_view=1),
				f("item", "Link", "Stock Item", options="Item"),
				col("col_1"),
				f("article", "Link", "Article", options="Leather Article", reqd=1, in_list_view=1),
				f("color", "Link", "Color", options="Leather Color", reqd=1, in_list_view=1),
				f("customer", "Link", "Customer Spec", options="Customer"),
				f("end_use", "Select", "End Use", options=END_USE),
				sec("phys_sec", "Physical Specs"),
				f("finish", "Data", "Finish"),
				f("grain_type", "Data", "Grain Type"),
				f("thickness_from_mm", "Float", "Thickness From (mm)"),
				f("thickness_to_mm", "Float", "Thickness To (mm)"),
				col("col_2"),
				f("temper", "Data", "Temper / Softness"),
				f("size_range", "Data", "Size Range"),
				f("default_grade", "Link", "Default Grade", options="Leather Grade"),
				f("water_resistance", "Data", "Water Resistance"),
				f("flame_retardant", "Data", "Flame-Retardant Spec"),
				f("sales_uom", "Select", "Sales Unit", options=PURCHASE_UOM, default="Sq. ft."),
				sec("test_sec", "Test Requirements"),
				f("physical_test_requirements", "Text Editor", "Physical Test Requirements"),
			],
			autoname="field:product_code",
			naming_rule="By fieldname",
			title_field="product_name",
			search_fields="product_name,article,color,end_use",
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Leather Chemical",
			[
				f("chemical_code", "Data", "Chemical Code", reqd=1, unique=1, in_list_view=1),
				f("chemical_name", "Data", "Chemical Name", reqd=1, in_list_view=1),
				f("item", "Link", "Stock Item", options="Item"),
				col("col_1"),
				f("chemical_type", "Select", "Type", options=CHEM_TYPE, reqd=1, in_list_view=1),
				f("concentration_percent", "Percent", "Concentration %"),
				f("hazard_class", "Data", "Hazard Class"),
				f("uom", "Link", "UOM", options="UOM"),
				sec("store_sec", "Storage & Compliance"),
				f("storage_instructions", "Small Text", "Storage Instructions"),
				f("msds", "Attach", "MSDS"),
				f("shelf_life_days", "Int", "Shelf Life (days)"),
				f("restricted_substance", "Check", "Restricted Substance (RSL/MRSL)"),
				f("zdhc_compliant", "Check", "ZDHC Compliant"),
			],
			autoname="field:chemical_code",
			naming_rule="By fieldname",
			title_field="chemical_name",
			search_fields="chemical_name,chemical_type",
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Leather Recipe Ingredient",
			[
				f("chemical", "Link", "Chemical", options="Leather Chemical", reqd=1, in_list_view=1),
				f("basis", "Select", "Basis", options="% of Hide Weight\nKg\nLiter\nGram\nPercentage Concentration", default="% of Hide Weight", in_list_view=1),
				f("qty", "Float", "Qty / %", reqd=1, in_list_view=1),
				f("uom", "Data", "UOM", in_list_view=1),
				f("stage", "Select", "Process Stage", options=PROCESS),
				f("remarks", "Data", "Remarks"),
			],
			istable=1,
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Leather Recipe",
			[
				f("recipe_name", "Data", "Recipe Name", reqd=1, in_list_view=1),
				f(
					"recipe_type",
					"Select",
					"Recipe Type",
					options="Beamhouse\nWet Blue\nTanning\nDyeing\nRetanning\nFinishing\nLab",
					reqd=1,
					in_list_view=1,
				),
				col("col_1"),
				f("article", "Link", "Article", options="Leather Article"),
				f("color", "Link", "Color", options="Leather Color"),
				f("customer", "Link", "Customer", options="Customer"),
				f("tanning_method", "Select", "Tanning Method", options=TANNING),
				f("is_approved", "Check", "Approved for Production", in_list_view=1),
				sec("ing_sec", "Ingredients (per 1000 kg input unless noted)"),
				f("ingredients", "Table", "Ingredients", options="Leather Recipe Ingredient"),
				sec("note_sec", "Notes"),
				f("process_notes", "Text Editor", "Process Notes"),
			],
			autoname="naming_series:",
			naming_rule="By \"Naming Series\" field",
			title_field="recipe_name",
			search_fields="recipe_name,recipe_type,article,color",
		),
		"\tpass\n",
	)
)
# prepend naming_series on Leather Recipe
DOCTYPES[-1][0]["fields"].insert(
	0, f("naming_series", "Select", "Series", options="RCP-.#####", reqd=1, set_only_once=1)
)
DOCTYPES[-1][0]["field_order"].insert(0, "naming_series")

DOCTYPES.append(
	(
		doctype(
			"Leather Process Operation",
			[
				f("operation", "Select", "Operation", options=PROCESS, reqd=1, in_list_view=1),
				f("sequence", "Int", "Sequence", reqd=1, in_list_view=1),
				f("standard_time_min", "Float", "Std Time (min)", in_list_view=1),
				f("recipe", "Link", "Recipe", options="Leather Recipe"),
				f("workstation", "Data", "Drum / Machine"),
				f("expected_yield_percent", "Percent", "Expected Yield %"),
			],
			istable=1,
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Leather Process Route",
			[
				f("route_name", "Data", "Route Name", reqd=1, in_list_view=1),
				f("article", "Link", "Article", options="Leather Article"),
				col("col_1"),
				f("animal_type", "Link", "Animal Type", options="Animal Type"),
				f("is_default", "Check", "Default Route"),
				sec("op_sec", "Operations"),
				f("operations", "Table", "Operations", options="Leather Process Operation"),
				f("expected_weight_yield", "Percent", "Expected Weight Yield %"),
				f("expected_area_yield", "Float", "Expected Area Yield (sqft / kg)"),
			],
			autoname="naming_series:",
			naming_rule="By \"Naming Series\" field",
			title_field="route_name",
		),
		None,
	)
)
DOCTYPES[-1][0]["fields"].insert(0, f("naming_series", "Select", "Series", options="RTE-.#####", reqd=1, set_only_once=1))
DOCTYPES[-1][0]["field_order"].insert(0, "naming_series")

DOCTYPES.append(
	(
		doctype(
			"Leather Lot",
			[
				f("naming_series", "Select", "Series", options="LOT-.YYYY.-.#####", reqd=1, set_only_once=1),
				f("lot_stage", "Select", "Stage", options=STAGE, reqd=1, in_list_view=1, in_standard_filter=1),
				f("posting_date", "Date", "Date", reqd=1, in_list_view=1),
				col("col_1"),
				f("status", "Select", "Status", options="Draft\nIn Stock\nIn Process\nAllocated\nShipped\nClosed\nRejected", default="Draft", in_list_view=1),
				f("company", "Link", "Company", options="Company"),
				f("warehouse", "Link", "Warehouse", options="Warehouse"),
				f("warehouse_kind", "Select", "Warehouse Type", options=WAREHOUSE_KIND),
				sec("src_sec", "Origin & Trace"),
				f("parent_lot", "Link", "Parent Lot", options="Leather Lot"),
				f("supplier", "Link", "Supplier", options="Supplier"),
				f("supplier_lot", "Data", "Supplier Lot"),
				f("raw_hide", "Link", "Raw Hide", options="Raw Hide Master"),
				f("animal_type", "Link", "Animal Type", options="Animal Type", in_standard_filter=1),
				col("col_2"),
				f("article", "Link", "Article", options="Leather Article"),
				f("color", "Link", "Color", options="Leather Color"),
				f("finished_product", "Link", "Finished Product", options="Finished Leather Master"),
				f("grade", "Link", "Grade", options="Leather Grade", in_list_view=1, in_standard_filter=1),
				f("origin_country", "Link", "Country of Origin", options="Country"),
				sec("qty_sec", "Quantity"),
				f("pieces", "Int", "Pieces", in_list_view=1),
				f("weight_kg", "Float", "Weight (kg)"),
				f("area_sqft", "Float", "Area (sq. ft.)"),
				f("area_sqm", "Float", "Area (sq. m)"),
				col("col_3"),
				f("thickness_mm", "Float", "Thickness (mm)"),
				f("moisture_percent", "Percent", "Moisture %"),
				f("chrome_content", "Float", "Chrome Content"),
				f("storage_date", "Date", "Storage Date"),
				f("aging_days", "Int", "Aging Days", read_only=1),
				sec("val_sec", "Valuation"),
				f("rate", "Currency", "Rate"),
				f("amount", "Currency", "Amount", read_only=1),
				f("quality_condition", "Small Text", "Quality Condition"),
				f("remarks", "Small Text", "Remarks"),
			],
			autoname="naming_series:",
			naming_rule="By \"Naming Series\" field",
			is_submittable=1,
			search_fields="lot_stage,animal_type,article,color,grade,supplier_lot",
		),
		'''	def validate(self):
		from frappe.utils import date_diff, today

		if self.area_sqft and not self.area_sqm:
			self.area_sqm = float(self.area_sqft) * 0.092903
		elif self.area_sqm and not self.area_sqft:
			self.area_sqft = float(self.area_sqm) / 0.092903
		if self.storage_date:
			self.aging_days = date_diff(today(), self.storage_date)
		qty = self.area_sqft or self.weight_kg or self.pieces or 0
		self.amount = (self.rate or 0) * qty
''',
	)
)

DOCTYPES.append(
	(
		doctype(
			"Hide Purchase Item",
			[
				f("raw_hide", "Link", "Raw Hide", options="Raw Hide Master", reqd=1, in_list_view=1),
				f("animal_type", "Link", "Animal Type", options="Animal Type", in_list_view=1),
				f("qty", "Float", "Qty", reqd=1, in_list_view=1),
				f("uom", "Select", "UOM", options=PURCHASE_UOM, default="Piece", in_list_view=1),
				f("rate", "Currency", "Rate", in_list_view=1),
				f("amount", "Currency", "Amount", read_only=1, in_list_view=1),
				f("origin_country", "Link", "Origin", options="Country"),
				f("expected_grade", "Link", "Expected Grade", options="Leather Grade"),
			],
			istable=1,
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Hide Supplier Contract",
			[
				f("naming_series", "Select", "Series", options="HSC-.#####", reqd=1, set_only_once=1),
				f("supplier", "Link", "Supplier", options="Supplier", reqd=1, in_list_view=1),
				f("animal_type", "Link", "Animal Type", options="Animal Type", in_list_view=1),
				col("col_1"),
				f("from_date", "Date", "From Date", reqd=1),
				f("to_date", "Date", "To Date"),
				f("season", "Data", "Season"),
				f("purchase_uom", "Select", "UOM", options=PURCHASE_UOM, default="Piece"),
				f("agreed_rate", "Currency", "Agreed Rate", in_list_view=1),
				f("market_rate", "Currency", "Market Rate"),
				f("collection_center", "Link", "Collection Center", options="Hide Collection Center"),
				f("agent", "Link", "Agent", options="Procurement Agent"),
				f("commission_percent", "Percent", "Commission %"),
				f("status", "Select", "Status", options="Draft\nActive\nExpired\nCancelled", default="Draft"),
				f("terms", "Text Editor", "Terms"),
			],
			autoname="naming_series:",
			naming_rule="By \"Naming Series\" field",
			search_fields="supplier,animal_type,season",
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Hide Purchase Order",
			[
				f("naming_series", "Select", "Series", options="HPO-.YYYY.-.#####", reqd=1, set_only_once=1),
				f("supplier", "Link", "Supplier", options="Supplier", reqd=1, in_list_view=1),
				f("transaction_date", "Date", "Date", reqd=1, in_list_view=1),
				col("col_1"),
				f("company", "Link", "Company", options="Company"),
				f("contract", "Link", "Contract", options="Hide Supplier Contract"),
				f("collection_center", "Link", "Collection Center", options="Hide Collection Center"),
				f("agent", "Link", "Agent", options="Procurement Agent"),
				f("origin_country", "Link", "Country of Origin", options="Country"),
				f("is_import", "Check", "Import Procurement"),
				f("lc_number", "Data", "LC Number"),
				sec("item_sec", "Hides"),
				f("items", "Table", "Items", options="Hide Purchase Item"),
				sec("cost_sec", "Landed Cost"),
				f("hide_amount", "Currency", "Hide Amount", read_only=1),
				f("transport_charges", "Currency", "Transport"),
				f("loading_charges", "Currency", "Loading / Unloading"),
				f("preservation_cost", "Currency", "Preservation Cost"),
				f("commission_amount", "Currency", "Commission"),
				f("advance_paid", "Currency", "Advance Paid"),
				col("col_2"),
				f("landed_cost", "Currency", "Landed Cost", read_only=1),
				f("status", "Select", "Status", options="Draft\nOrdered\nPartially Received\nReceived\nCancelled", default="Draft"),
				f("remarks", "Small Text", "Remarks"),
				f("amended_from", "Link", "Amended From", options="Hide Purchase Order"),
			],
			autoname="naming_series:",
			naming_rule="By \"Naming Series\" field",
			is_submittable=1,
			search_fields="supplier,origin_country,status",
		),
		'''	def validate(self):
		total = 0
		for row in self.items or []:
			row.amount = (row.qty or 0) * (row.rate or 0)
			total += row.amount or 0
		self.hide_amount = total
		self.landed_cost = (
			(self.hide_amount or 0)
			+ (self.transport_charges or 0)
			+ (self.loading_charges or 0)
			+ (self.preservation_cost or 0)
			+ (self.commission_amount or 0)
		)
''',
	)
)

DOCTYPES.append(
	(
		doctype(
			"Hide Receiving Item",
			[
				f("raw_hide", "Link", "Raw Hide", options="Raw Hide Master", in_list_view=1),
				f("pieces", "Int", "Pieces", in_list_view=1),
				f("gross_weight_kg", "Float", "Gross Weight", in_list_view=1),
				f("salt_deduction_kg", "Float", "Salt Deduction"),
				f("moisture_deduction_kg", "Float", "Moisture Deduction"),
				f("net_weight_kg", "Float", "Net Weight", read_only=1, in_list_view=1),
				f("damaged_hides", "Int", "Damaged"),
				f("rejected_hides", "Int", "Rejected"),
				f("grade", "Link", "Grade", options="Leather Grade", in_list_view=1),
				f("size", "Data", "Size"),
				f("thickness_mm", "Float", "Thickness"),
			],
			istable=1,
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Hide Receiving Inspection",
			[
				f("naming_series", "Select", "Series", options="HRI-.YYYY.-.#####", reqd=1, set_only_once=1),
				f("purchase_order", "Link", "Hide Purchase Order", options="Hide Purchase Order"),
				f("supplier", "Link", "Supplier", options="Supplier", reqd=1, in_list_view=1),
				f("inspection_date", "Date", "Date", reqd=1, in_list_view=1),
				col("col_1"),
				f("supplier_lot", "Data", "Supplier Lot"),
				f("internal_lot", "Link", "Internal Lot", options="Leather Lot"),
				f("inspector", "Link", "Inspector", options="User"),
				f("qc_status", "Select", "QC Status", options="Pending\nApproved\nRejected\nPartial", default="Pending", in_list_view=1),
				sec("item_sec", "Received Hides"),
				f("items", "Table", "Items", options="Hide Receiving Item"),
				sec("tot_sec", "Totals"),
				f("total_pieces", "Int", "Total Pieces", read_only=1),
				f("total_gross_weight", "Float", "Gross Weight", read_only=1),
				f("total_net_weight", "Float", "Net Weight", read_only=1),
				f("short_quantity", "Float", "Short Quantity"),
				col("col_2"),
				f("inspection_remarks", "Small Text", "Remarks"),
				f("photos", "Attach Image", "Photos"),
				f("amended_from", "Link", "Amended From", options="Hide Receiving Inspection"),
			],
			autoname="naming_series:",
			naming_rule="By \"Naming Series\" field",
			is_submittable=1,
		),
		'''	def validate(self):
		pieces = gross = net = 0
		for row in self.items or []:
			row.net_weight_kg = (row.gross_weight_kg or 0) - (row.salt_deduction_kg or 0) - (row.moisture_deduction_kg or 0)
			pieces += row.pieces or 0
			gross += row.gross_weight_kg or 0
			net += row.net_weight_kg or 0
		self.total_pieces = pieces
		self.total_gross_weight = gross
		self.total_net_weight = net
''',
	)
)

DOCTYPES.append(
	(
		doctype(
			"Hide Defect Line",
			[
				f("defect_type", "Select", "Defect", options=DEFECTS, reqd=1, in_list_view=1),
				f("count", "Int", "Count", in_list_view=1),
				f("severity", "Select", "Severity", options="Low\nMedium\nHigh", in_list_view=1),
				f("remarks", "Data", "Remarks"),
			],
			istable=1,
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Hide Grade Summary",
			[
				f("grade", "Link", "Grade", options="Leather Grade", reqd=1, in_list_view=1),
				f("pieces", "Int", "Pieces", in_list_view=1),
				f("weight_kg", "Float", "Weight (kg)", in_list_view=1),
				f("rate", "Currency", "Rate", in_list_view=1),
				f("amount", "Currency", "Amount", read_only=1, in_list_view=1),
			],
			istable=1,
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Hide Grading",
			[
				f("naming_series", "Select", "Series", options="HGR-.YYYY.-.#####", reqd=1, set_only_once=1),
				f("lot", "Link", "Leather Lot", options="Leather Lot", reqd=1, in_list_view=1),
				f("grading_date", "Date", "Date", reqd=1, in_list_view=1),
				col("col_1"),
				f("grader", "Link", "Grader", options="User"),
				f("recommended_grade", "Link", "Recommended Grade", options="Leather Grade", read_only=1, in_list_view=1),
				f("final_grade", "Link", "Final Grade", options="Leather Grade"),
				sec("def_sec", "Defects"),
				f("defects", "Table", "Defects", options="Hide Defect Line"),
				sec("sum_sec", "Grade-wise Qty"),
				f("grade_summary", "Table", "Grade Summary", options="Hide Grade Summary"),
				f("remarks", "Small Text", "Remarks"),
				f("amended_from", "Link", "Amended From", options="Hide Grading"),
			],
			autoname="naming_series:",
			naming_rule="By \"Naming Series\" field",
			is_submittable=1,
		),
		'''	def validate(self):
		import frappe

		score = 0
		reject = False
		for row in self.defects or []:
			sev = {"Low": 1, "Medium": 3, "High": 6}.get(row.severity or "Low", 1)
			score += (row.count or 1) * sev
			if row.defect_type in ("Putrefaction",) and (row.severity or "") == "High":
				reject = True
		if reject or score >= 40:
			code = "Reject"
		elif score >= 25:
			code = "D"
		elif score >= 15:
			code = "C"
		elif score >= 6:
			code = "B"
		else:
			code = "A"
		if frappe.db.exists("Leather Grade", code):
			self.recommended_grade = code
		if not self.final_grade:
			self.final_grade = self.recommended_grade
		for row in self.grade_summary or []:
			row.amount = (row.pieces or 0) * (row.rate or 0)
''',
	)
)

DOCTYPES.append(
	(
		doctype(
			"Leather Batch Chemical",
			[
				f("chemical", "Link", "Chemical", options="Leather Chemical", reqd=1, in_list_view=1),
				f("standard_qty", "Float", "Standard Qty", in_list_view=1),
				f("actual_qty", "Float", "Actual Qty", in_list_view=1),
				f("uom", "Data", "UOM", in_list_view=1),
				f("variance", "Float", "Variance", read_only=1),
				f("rate", "Currency", "Rate"),
				f("amount", "Currency", "Amount", read_only=1),
			],
			istable=1,
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Leather Production Batch",
			[
				f("naming_series", "Select", "Series", options="BAT-.YYYY.-.#####", reqd=1, set_only_once=1),
				f("process_stage", "Select", "Process", options=PROCESS, reqd=1, in_list_view=1, in_standard_filter=1),
				f("posting_date", "Date", "Date", reqd=1, in_list_view=1),
				col("col_1"),
				f("company", "Link", "Company", options="Company"),
				f("status", "Select", "Status", options="Draft\nIn Progress\nCompleted\nOn Hold\nCancelled", default="Draft", in_list_view=1),
				f("recipe", "Link", "Recipe", options="Leather Recipe"),
				f("route", "Link", "Process Route", options="Leather Process Route"),
				f("tanning_method", "Select", "Tanning Method", options=TANNING),
				sec("res_sec", "Resources"),
				f("drum", "Link", "Drum", options="Drum"),
				f("machine", "Link", "Machine", options="Leather Machine"),
				f("operator", "Link", "Operator", options="Employee"),
				col("col_2"),
				f("shift", "Select", "Shift", options="A\nB\nC\nGeneral"),
				f("start_time", "Datetime", "Start"),
				f("end_time", "Datetime", "End"),
				sec("in_sec", "Input"),
				f("input_lot", "Link", "Input Lot", options="Leather Lot", reqd=1),
				f("input_pieces", "Int", "Input Pieces"),
				f("input_weight_kg", "Float", "Input Weight (kg)"),
				f("input_area_sqft", "Float", "Input Area (sq. ft.)"),
				col("col_3"),
				f("water_qty", "Float", "Water Qty"),
				f("temperature", "Float", "Temperature"),
				f("ph", "Float", "pH"),
				f("runtime_min", "Float", "Runtime (min)"),
				sec("chem_sec", "Chemicals"),
				f("chemicals", "Table", "Chemicals", options="Leather Batch Chemical"),
				sec("out_sec", "Output"),
				f("output_lot", "Link", "Output Lot", options="Leather Lot"),
				f("output_pieces", "Int", "Output Pieces"),
				f("output_weight_kg", "Float", "Output Weight (kg)"),
				f("output_area_sqft", "Float", "Output Area (sq. ft.)"),
				f("rejected_qty", "Float", "Rejected Qty"),
				col("col_4"),
				f("production_loss", "Float", "Production Loss", read_only=1),
				f("weight_yield_percent", "Percent", "Weight Yield %", read_only=1),
				f("area_yield", "Float", "Area Yield (sqft/kg)", read_only=1),
				f("output_form", "Select", "Output Form", options="Full Hide\nSide\nSplit\nShoulder\nBelly\nGrain Split\nFlesh Split"),
				f("target_thickness_mm", "Float", "Target Thickness (mm)"),
				f("actual_thickness_mm", "Float", "Actual Thickness (mm)"),
				f("remarks", "Small Text", "Remarks"),
				f("amended_from", "Link", "Amended From", options="Leather Production Batch"),
			],
			autoname="naming_series:",
			naming_rule="By \"Naming Series\" field",
			is_submittable=1,
			search_fields="process_stage,drum,input_lot,status",
		),
		'''	def validate(self):
		from leature_manufacturing.leature_manufacturing.utils import apply_recipe_to_batch, calc_yield

		if self.recipe and self.input_weight_kg and not self.chemicals:
			apply_recipe_to_batch(self)
		for row in self.chemicals or []:
			row.variance = (row.actual_qty or 0) - (row.standard_qty or 0)
			row.amount = (row.actual_qty or row.standard_qty or 0) * (row.rate or 0)
		self.production_loss = (self.input_weight_kg or 0) - (self.output_weight_kg or 0) - (self.rejected_qty or 0)
		y = calc_yield(self.input_weight_kg, self.output_weight_kg, self.output_area_sqft)
		self.weight_yield_percent = y["weight_yield"]
		self.area_yield = y["area_yield"]
''',
	)
)

DOCTYPES.append(
	(
		doctype(
			"Leather Area Piece",
			[
				f("piece_no", "Data", "Piece No", in_list_view=1),
				f("length", "Float", "Length", in_list_view=1),
				f("width", "Float", "Width", in_list_view=1),
				f("area_sqft", "Float", "Area (sq. ft.)", in_list_view=1),
				f("area_sqm", "Float", "Area (sq. m)"),
				f("grade", "Link", "Grade", options="Leather Grade", in_list_view=1),
				f("thickness_mm", "Float", "Thickness"),
			],
			istable=1,
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Leather Area Measurement",
			[
				f("naming_series", "Select", "Series", options="LAM-.YYYY.-.#####", reqd=1, set_only_once=1),
				f("lot", "Link", "Lot", options="Leather Lot", reqd=1, in_list_view=1),
				f("measurement_date", "Date", "Date", reqd=1, in_list_view=1),
				col("col_1"),
				f("machine", "Link", "Measuring Machine", options="Leather Machine"),
				f("operator", "Link", "Operator", options="Employee"),
				f("uom", "Select", "UOM", options="SQ FT\nSQ M", default="SQ FT"),
				sec("p_sec", "Pieces"),
				f("pieces", "Table", "Pieces", options="Leather Area Piece"),
				f("total_area_sqft", "Float", "Total sq. ft.", read_only=1, in_list_view=1),
				f("total_area_sqm", "Float", "Total sq. m", read_only=1),
				f("piece_count", "Int", "Piece Count", read_only=1),
				f("amended_from", "Link", "Amended From", options="Leather Area Measurement"),
			],
			autoname="naming_series:",
			naming_rule="By \"Naming Series\" field",
			is_submittable=1,
		),
		'''	def validate(self):
		total_sqft = total_sqm = 0
		for i, row in enumerate(self.pieces or [], start=1):
			if not row.piece_no:
				row.piece_no = f"{i:03d}"
			if row.length and row.width and not row.area_sqft:
				row.area_sqft = (row.length * row.width)
			if row.area_sqft and not row.area_sqm:
				row.area_sqm = row.area_sqft * 0.092903
			elif row.area_sqm and not row.area_sqft:
				row.area_sqft = row.area_sqm / 0.092903
			total_sqft += row.area_sqft or 0
			total_sqm += row.area_sqm or 0
		self.total_area_sqft = total_sqft
		self.total_area_sqm = total_sqm
		self.piece_count = len(self.pieces or [])
''',
	)
)

DOCTYPES.append(
	(
		doctype(
			"Leather Piece",
			[
				f("naming_series", "Select", "Series", options="FL-.YYYY.-.######", reqd=1, set_only_once=1),
				f("lot", "Link", "Lot", options="Leather Lot", reqd=1, in_list_view=1),
				f("article", "Link", "Article", options="Leather Article", in_list_view=1),
				f("color", "Link", "Color", options="Leather Color", in_list_view=1),
				col("col_1"),
				f("grade", "Link", "Grade", options="Leather Grade", in_list_view=1),
				f("area_sqft", "Float", "Area (sq. ft.)", in_list_view=1),
				f("thickness_mm", "Float", "Thickness (mm)"),
				f("size", "Data", "Size"),
				f("warehouse", "Link", "Warehouse", options="Warehouse"),
				f("qc_status", "Select", "QC Status", options="Pending\nPassed\nFailed\nHold", default="Pending"),
				f("status", "Select", "Status", options="Available\nAllocated\nPacked\nShipped\nHold", default="Available", in_list_view=1),
				f("customer", "Link", "Allocated Customer", options="Customer"),
				f("barcode", "Data", "Barcode / QR", read_only=1),
				f("manufacturing_date", "Date", "Manufacturing Date"),
			],
			autoname="naming_series:",
			naming_rule="By \"Naming Series\" field",
			search_fields="lot,article,color,grade,status",
		),
		'''	def before_insert(self):
		pass

	def after_insert(self):
		if not self.barcode:
			self.db_set("barcode", self.name)
''',
	)
)

DOCTYPES.append(
	(
		doctype(
			"Leather QC Test",
			[
				f("test_name", "Data", "Test", reqd=1, in_list_view=1),
				f("standard_value", "Data", "Standard", in_list_view=1),
				f("actual_value", "Data", "Actual", in_list_view=1),
				f("test_result", "Select", "Result", options="Pass\nFail\nNA", in_list_view=1),
				f("remarks", "Data", "Remarks"),
			],
			istable=1,
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Leather QC Inspection",
			[
				f("naming_series", "Select", "Series", options="LQC-.YYYY.-.#####", reqd=1, set_only_once=1),
				f(
					"inspection_type",
					"Select",
					"Type",
					options="Raw Hide\nWet Blue\nCrust\nFinished Leather",
					reqd=1,
					in_list_view=1,
				),
				f("lot", "Link", "Lot", options="Leather Lot", reqd=1),
				f("piece", "Link", "Piece", options="Leather Piece"),
				col("col_1"),
				f("inspection_date", "Date", "Date", reqd=1, in_list_view=1),
				f("inspector", "Link", "Inspector", options="User"),
				f("overall_result", "Select", "Result", options="Pending\nPass\nFail\nConditional", default="Pending", in_list_view=1),
				sec("t_sec", "Tests"),
				f("test_rows", "Table", "Tests", options="Leather QC Test"),
				f("hole_count", "Int", "Hole Count"),
				f("scar_count", "Int", "Scar Count"),
				f("remarks", "Small Text", "Remarks"),
				f("amended_from", "Link", "Amended From", options="Leather QC Inspection"),
			],
			autoname="naming_series:",
			naming_rule="By \"Naming Series\" field",
			is_submittable=1,
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Lab Sample",
			[
				f("naming_series", "Select", "Series", options="LAB-.YYYY.-.#####", reqd=1, set_only_once=1),
				f("sample_type", "Select", "Type", options="Color Matching\nChemical Trial\nCustomer Sample\nRecipe Experiment", reqd=1, in_list_view=1),
				f("customer", "Link", "Customer", options="Customer"),
				col("col_1"),
				f("article", "Link", "Article", options="Leather Article"),
				f("color", "Link", "Color", options="Leather Color"),
				f("request_date", "Date", "Date", reqd=1, in_list_view=1),
				f("recipe", "Link", "Recipe", options="Leather Recipe"),
				f("status", "Select", "Status", options="Draft\nIn Lab\nTested\nApproved\nRejected", default="Draft", in_list_view=1),
				f("test_certificate", "Attach", "Test Certificate"),
				f("result_notes", "Text Editor", "Result Notes"),
			],
			autoname="naming_series:",
			naming_rule="By \"Naming Series\" field",
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Customer Sample Request",
			[
				f("naming_series", "Select", "Series", options="CSR-.YYYY.-.#####", reqd=1, set_only_once=1),
				f("customer", "Link", "Customer", options="Customer", reqd=1, in_list_view=1),
				f("request_date", "Date", "Date", reqd=1, in_list_view=1),
				col("col_1"),
				f("article", "Link", "Article", options="Leather Article"),
				f("color", "Link", "Color", options="Leather Color"),
				f("end_use", "Select", "End Use", options=END_USE),
				f("thickness", "Data", "Thickness"),
				f("finish", "Data", "Finish"),
				f("hand_feel", "Data", "Hand Feel"),
				f("sample_size", "Data", "Sample Size"),
				f("trial_count", "Int", "Number of Trials", default=0),
				f("development_cost", "Currency", "Development Cost"),
				f("lab_sample", "Link", "Lab Sample", options="Lab Sample"),
				f("status", "Select", "Status", options="Requested\nIn Development\nSample Sent\nApproved\nRejected", default="Requested", in_list_view=1),
				f("customer_comments", "Text Editor", "Customer Comments"),
			],
			autoname="naming_series:",
			naming_rule="By \"Naming Series\" field",
			search_fields="customer,article,color,status",
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Drum Schedule Item",
			[
				f("drum", "Link", "Drum", options="Drum", reqd=1, in_list_view=1),
				f("batch", "Link", "Batch", options="Leather Production Batch", in_list_view=1),
				f("process_name", "Select", "Process", options=PROCESS, in_list_view=1),
				f("planned_start", "Datetime", "Start", in_list_view=1),
				f("planned_end", "Datetime", "End", in_list_view=1),
				f("capacity_kg", "Float", "Capacity"),
			],
			istable=1,
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Drum Schedule",
			[
				f("naming_series", "Select", "Series", options="DRM-.YYYY.-.#####", reqd=1, set_only_once=1),
				f("schedule_date", "Date", "Date", reqd=1, in_list_view=1),
				f("shift", "Select", "Shift", options="A\nB\nC\nGeneral", in_list_view=1),
				col("col_1"),
				f("status", "Select", "Status", options="Draft\nReleased\nCompleted", default="Draft"),
				sec("s_sec", "Drums"),
				f("items", "Table", "Items", options="Drum Schedule Item"),
				f("notes", "Small Text", "Notes"),
			],
			autoname="naming_series:",
			naming_rule="By \"Naming Series\" field",
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Leather Production Plan Item",
			[
				f("finished_product", "Link", "Product", options="Finished Leather Master", in_list_view=1),
				f("article", "Link", "Article", options="Leather Article", in_list_view=1),
				f("color", "Link", "Color", options="Leather Color"),
				f("grade", "Link", "Grade", options="Leather Grade"),
				f("required_area_sqft", "Float", "Required sq. ft.", in_list_view=1),
				f("delivery_date", "Date", "Delivery", in_list_view=1),
				f("sales_order", "Data", "Sales Order"),
			],
			istable=1,
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Leather Production Plan",
			[
				f("naming_series", "Select", "Series", options="LPP-.YYYY.-.#####", reqd=1, set_only_once=1),
				f("plan_date", "Date", "Plan Date", reqd=1, in_list_view=1),
				f("from_date", "Date", "From"),
				f("to_date", "Date", "To"),
				col("col_1"),
				f("status", "Select", "Status", options="Draft\nReleased\nIn Progress\nCompleted", default="Draft", in_list_view=1),
				f("company", "Link", "Company", options="Company"),
				sec("i_sec", "Demand"),
				f("items", "Table", "Items", options="Leather Production Plan Item"),
				f("notes", "Small Text", "Notes"),
			],
			autoname="naming_series:",
			naming_rule="By \"Naming Series\" field",
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Waste Record",
			[
				f("naming_series", "Select", "Series", options="WST-.YYYY.-.#####", reqd=1, set_only_once=1),
				f("waste_type", "Select", "Waste Type", options=WASTE, reqd=1, in_list_view=1),
				f("category", "Select", "Category", options=WASTE_CAT, reqd=1, in_list_view=1),
				col("col_1"),
				f("posting_date", "Date", "Date", reqd=1, in_list_view=1),
				f("source_batch", "Link", "Source Batch", options="Leather Production Batch"),
				f("source_lot", "Link", "Source Lot", options="Leather Lot"),
				f("qty", "Float", "Quantity", reqd=1),
				f("uom", "Data", "UOM", default="kg"),
				f("disposal_method", "Data", "Disposal Method"),
				f("buyer", "Link", "Buyer", options="Customer"),
				f("sale_value", "Currency", "Sale Value"),
				f("environmental_doc", "Attach", "Environmental Document"),
				f("remarks", "Small Text", "Remarks"),
			],
			autoname="naming_series:",
			naming_rule="By \"Naming Series\" field",
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"ETP Daily Log",
			[
				f("naming_series", "Select", "Series", options="ETP-.YYYY.-.#####", reqd=1, set_only_once=1),
				f("log_date", "Date", "Date", reqd=1, unique=1, in_list_view=1),
				f("wastewater_qty", "Float", "Wastewater Qty", in_list_view=1),
				col("col_1"),
				f("ph", "Float", "pH"),
				f("cod", "Float", "COD"),
				f("bod", "Float", "BOD"),
				f("tds", "Float", "TDS"),
				f("chromium", "Float", "Chromium"),
				f("sulfide", "Float", "Sulfide"),
				f("chloride", "Float", "Chloride"),
				f("sludge_qty", "Float", "Sludge Production"),
				f("chemical_consumption", "Small Text", "ETP Chemical Consumption"),
				f("within_limits", "Check", "Within Compliance Limits", in_list_view=1),
				f("test_report", "Attach", "Test Report"),
				f("remarks", "Small Text", "Remarks"),
			],
			autoname="naming_series:",
			naming_rule="By \"Naming Series\" field",
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Sustainability Record",
			[
				f("naming_series", "Select", "Series", options="SUS-.YYYY.-.#####", reqd=1, set_only_once=1),
				f("period_start", "Date", "From", reqd=1, in_list_view=1),
				f("period_end", "Date", "To", reqd=1),
				col("col_1"),
				f("water_consumption", "Float", "Water Consumption"),
				f("energy_consumption", "Float", "Energy Consumption"),
				f("chemical_consumption", "Float", "Chemical Consumption"),
				f("waste_generation", "Float", "Waste Generation"),
				f("recycled_water", "Float", "Recycled Water"),
				f("chrome_recovery", "Float", "Chrome Recovery"),
				f("carbon_footprint", "Float", "Carbon Footprint"),
				f("reach_compliant", "Check", "REACH"),
				f("zdhc_compliant", "Check", "ZDHC"),
				f("lwg_record", "Check", "LWG Record"),
				f("notes", "Text Editor", "Notes"),
			],
			autoname="naming_series:",
			naming_rule="By \"Naming Series\" field",
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Leather Sales Order Item",
			[
				f("finished_product", "Link", "Product", options="Finished Leather Master", in_list_view=1),
				f("article", "Link", "Article", options="Leather Article", reqd=1, in_list_view=1),
				f("color", "Link", "Color", options="Leather Color", in_list_view=1),
				f("thickness", "Data", "Thickness"),
				f("grade", "Link", "Grade", options="Leather Grade"),
				f("qty", "Float", "Qty", reqd=1, in_list_view=1),
				f("uom", "Select", "UOM", options=PURCHASE_UOM, default="Sq. ft.", in_list_view=1),
				f("rate", "Currency", "Rate", in_list_view=1),
				f("amount", "Currency", "Amount", read_only=1),
				f("delivery_date", "Date", "Delivery"),
			],
			istable=1,
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Leather Sales Order",
			[
				f("naming_series", "Select", "Series", options="LSO-.YYYY.-.#####", reqd=1, set_only_once=1),
				f("customer", "Link", "Customer", options="Customer", reqd=1, in_list_view=1),
				f("transaction_date", "Date", "Date", reqd=1, in_list_view=1),
				col("col_1"),
				f("delivery_date", "Date", "Delivery Date"),
				f("company", "Link", "Company", options="Company"),
				f("is_export", "Check", "Export Order"),
				f("customer_po", "Data", "Customer PO"),
				f("status", "Select", "Status", options="Draft\nConfirmed\nIn Production\nAllocated\nPacked\nShipped\nClosed\nCancelled", default="Draft", in_list_view=1),
				sec("i_sec", "Items"),
				f("items", "Table", "Items", options="Leather Sales Order Item"),
				f("total_qty", "Float", "Total Qty", read_only=1),
				f("grand_total", "Currency", "Grand Total", read_only=1, in_list_view=1),
				f("remarks", "Small Text", "Remarks"),
				f("amended_from", "Link", "Amended From", options="Leather Sales Order"),
			],
			autoname="naming_series:",
			naming_rule="By \"Naming Series\" field",
			is_submittable=1,
			search_fields="customer,customer_po,status",
		),
		'''	def validate(self):
		qty = amount = 0
		for row in self.items or []:
			row.amount = (row.qty or 0) * (row.rate or 0)
			qty += row.qty or 0
			amount += row.amount or 0
		self.total_qty = qty
		self.grand_total = amount
''',
	)
)

DOCTYPES.append(
	(
		doctype(
			"Leather Allocation Item",
			[
				f("piece", "Link", "Piece", options="Leather Piece", in_list_view=1),
				f("lot", "Link", "Lot", options="Leather Lot", in_list_view=1),
				f("article", "Link", "Article", options="Leather Article"),
				f("color", "Link", "Color", options="Leather Color"),
				f("grade", "Link", "Grade", options="Leather Grade"),
				f("area_sqft", "Float", "Area (sq. ft.)", in_list_view=1),
			],
			istable=1,
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Leather Allocation",
			[
				f("naming_series", "Select", "Series", options="ALC-.YYYY.-.#####", reqd=1, set_only_once=1),
				f("sales_order", "Link", "Leather Sales Order", options="Leather Sales Order", reqd=1, in_list_view=1),
				f("customer", "Link", "Customer", options="Customer", in_list_view=1),
				col("col_1"),
				f("allocation_date", "Date", "Date", reqd=1),
				f("article", "Link", "Article", options="Leather Article"),
				f("color", "Link", "Color", options="Leather Color"),
				f("grade", "Link", "Grade", options="Leather Grade"),
				f("required_area_sqft", "Float", "Required sq. ft."),
				f("allocated_area_sqft", "Float", "Allocated sq. ft.", read_only=1, in_list_view=1),
				sec("i_sec", "Allocated Pieces / Lots"),
				f("items", "Table", "Items", options="Leather Allocation Item"),
				f("status", "Select", "Status", options="Draft\nAllocated\nShort\nCancelled", default="Draft"),
				f("amended_from", "Link", "Amended From", options="Leather Allocation"),
			],
			autoname="naming_series:",
			naming_rule="By \"Naming Series\" field",
			is_submittable=1,
		),
		'''	def validate(self):
		self.allocated_area_sqft = sum((row.area_sqft or 0) for row in self.items or [])
		if self.required_area_sqft and self.allocated_area_sqft < self.required_area_sqft:
			self.status = "Short"
		elif self.allocated_area_sqft:
			self.status = "Allocated"
''',
	)
)

DOCTYPES.append(
	(
		doctype(
			"Leather Packing Item",
			[
				f("bundle_no", "Data", "Bundle / Roll / Box", in_list_view=1),
				f("piece", "Link", "Piece", options="Leather Piece"),
				f("lot", "Link", "Lot", options="Leather Lot", in_list_view=1),
				f("article", "Link", "Article", options="Leather Article"),
				f("color", "Link", "Color", options="Leather Color"),
				f("grade", "Link", "Grade", options="Leather Grade"),
				f("pieces", "Int", "Pieces", in_list_view=1),
				f("area_sqft", "Float", "Area (sq. ft.)", in_list_view=1),
				f("net_weight", "Float", "Net Weight"),
				f("gross_weight", "Float", "Gross Weight"),
			],
			istable=1,
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Leather Packing List",
			[
				f("naming_series", "Select", "Series", options="PKG-.YYYY.-.#####", reqd=1, set_only_once=1),
				f("sales_order", "Link", "Sales Order", options="Leather Sales Order"),
				f("customer", "Link", "Customer", options="Customer", reqd=1, in_list_view=1),
				f("packing_date", "Date", "Date", reqd=1, in_list_view=1),
				col("col_1"),
				f("customer_po", "Data", "Customer PO"),
				f("pack_type", "Select", "Pack Type", options="Bundle\nRoll\nPallet\nBox"),
				f("status", "Select", "Status", options="Draft\nPacked\nShipped", default="Draft"),
				sec("i_sec", "Contents"),
				f("items", "Table", "Items", options="Leather Packing Item"),
				f("total_pieces", "Int", "Total Pieces", read_only=1),
				f("total_area_sqft", "Float", "Total sq. ft.", read_only=1, in_list_view=1),
				f("total_net_weight", "Float", "Net Weight", read_only=1),
				f("total_gross_weight", "Float", "Gross Weight", read_only=1),
				f("amended_from", "Link", "Amended From", options="Leather Packing List"),
			],
			autoname="naming_series:",
			naming_rule="By \"Naming Series\" field",
			is_submittable=1,
		),
		'''	def validate(self):
		self.total_pieces = sum((row.pieces or 0) for row in self.items or [])
		self.total_area_sqft = sum((row.area_sqft or 0) for row in self.items or [])
		self.total_net_weight = sum((row.net_weight or 0) for row in self.items or [])
		self.total_gross_weight = sum((row.gross_weight or 0) for row in self.items or [])
''',
	)
)

DOCTYPES.append(
	(
		doctype(
			"Leather Export Shipment",
			[
				f("naming_series", "Select", "Series", options="EXP-.YYYY.-.#####", reqd=1, set_only_once=1),
				f("sales_order", "Link", "Sales Order", options="Leather Sales Order"),
				f("packing_list", "Link", "Packing List", options="Leather Packing List"),
				f("customer", "Link", "Customer", options="Customer", reqd=1, in_list_view=1),
				col("col_1"),
				f("shipment_date", "Date", "Shipment Date", reqd=1, in_list_view=1),
				f("proforma_invoice", "Data", "Proforma Invoice"),
				f("lc_number", "Data", "LC Number"),
				f("container_no", "Data", "Container"),
				f("freight_forwarder", "Data", "Freight Forwarder"),
				f("bill_of_lading", "Data", "Bill of Lading"),
				f("certificate_of_origin", "Attach", "Certificate of Origin"),
				f("insurance", "Data", "Insurance"),
				f("exchange_rate", "Float", "Exchange Rate"),
				f("status", "Select", "Status", options="Draft\nBooked\nShipped\nDocuments Sent\nRealized\nClosed", default="Draft", in_list_view=1),
				f("remarks", "Small Text", "Remarks"),
			],
			autoname="naming_series:",
			naming_rule="By \"Naming Series\" field",
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Leather Complaint",
			[
				f("naming_series", "Select", "Series", options="CMP-.YYYY.-.#####", reqd=1, set_only_once=1),
				f("customer", "Link", "Customer", options="Customer", reqd=1, in_list_view=1),
				f("complaint_date", "Date", "Date", reqd=1, in_list_view=1),
				col("col_1"),
				f(
					"complaint_type",
					"Select",
					"Type",
					options="Color Variation\nThickness Variation\nPeeling\nCracking\nPoor Finish\nShrinkage\nSize Shortage\nQuantity Shortage\nWrong Grade\nOther",
					reqd=1,
					in_list_view=1,
				),
				f("lot", "Link", "Lot", options="Leather Lot"),
				f("sales_order", "Link", "Sales Order", options="Leather Sales Order"),
				f("status", "Select", "Status", options="Open\nInvestigating\nCAPA\nCredit Note\nReplacement\nClosed", default="Open", in_list_view=1),
				f("description", "Text Editor", "Description"),
				f("root_cause", "Text Editor", "Root Cause"),
				f("capa", "Text Editor", "CAPA"),
			],
			autoname="naming_series:",
			naming_rule="By \"Naming Series\" field",
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Leather Cost Line",
			[
				f("cost_head", "Select", "Cost Head", options="Hide\nChemical\nLabor\nMachine\nWater\nGas\nElectricity\nSteam\nPackaging\nFreight\nWaste Disposal\nQC\nOther", reqd=1, in_list_view=1),
				f("standard_amount", "Currency", "Standard", in_list_view=1),
				f("actual_amount", "Currency", "Actual", in_list_view=1),
				f("variance", "Currency", "Variance", read_only=1, in_list_view=1),
				f("remarks", "Data", "Remarks"),
			],
			istable=1,
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Leather Batch Costing",
			[
				f("naming_series", "Select", "Series", options="LBC-.YYYY.-.#####", reqd=1, set_only_once=1),
				f("lot", "Link", "Finished Lot", options="Leather Lot", reqd=1, in_list_view=1),
				f("batch", "Link", "Production Batch", options="Leather Production Batch"),
				col("col_1"),
				f("costing_date", "Date", "Date", reqd=1),
				f("finished_area_sqft", "Float", "Finished Area (sq. ft.)"),
				sec("c_sec", "Cost Heads"),
				f("items", "Table", "Items", options="Leather Cost Line"),
				f("total_standard", "Currency", "Total Standard", read_only=1),
				f("total_actual", "Currency", "Total Actual", read_only=1, in_list_view=1),
				f("cost_per_sqft", "Currency", "Cost per sq. ft.", read_only=1, in_list_view=1),
				f("amended_from", "Link", "Amended From", options="Leather Batch Costing"),
			],
			autoname="naming_series:",
			naming_rule="By \"Naming Series\" field",
			is_submittable=1,
		),
		'''	def validate(self):
		std = act = 0
		for row in self.items or []:
			row.variance = (row.actual_amount or 0) - (row.standard_amount or 0)
			std += row.standard_amount or 0
			act += row.actual_amount or 0
		self.total_standard = std
		self.total_actual = act
		if self.finished_area_sqft:
			self.cost_per_sqft = act / self.finished_area_sqft
''',
	)
)

DOCTYPES.append(
	(
		doctype(
			"Leather Maintenance",
			[
				f("naming_series", "Select", "Series", options="MNT-.YYYY.-.#####", reqd=1, set_only_once=1),
				f("maintenance_type", "Select", "Type", options="Preventive\nBreakdown", reqd=1, in_list_view=1),
				f("asset_type", "Select", "Asset Type", options="Drum\nMachine\nBoiler\nCompressor\nPump\nSpray Line\nETP\nOther", reqd=1),
				col("col_1"),
				f("drum", "Link", "Drum", options="Drum"),
				f("machine", "Link", "Machine", options="Leather Machine"),
				f("request_date", "Date", "Date", reqd=1, in_list_view=1),
				f("technician", "Link", "Technician", options="User"),
				f("status", "Select", "Status", options="Open\nAssigned\nIn Progress\nCompleted\nClosed", default="Open", in_list_view=1),
				f("downtime_hours", "Float", "Downtime (hrs)"),
				f("repair_cost", "Currency", "Repair Cost"),
				f("description", "Small Text", "Description"),
			],
			autoname="naming_series:",
			naming_rule="By \"Naming Series\" field",
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Worker Productivity Log",
			[
				f("naming_series", "Select", "Series", options="WPL-.YYYY.-.#####", reqd=1, set_only_once=1),
				f("log_date", "Date", "Date", reqd=1, in_list_view=1),
				f("employee", "Link", "Worker", options="User", reqd=1, in_list_view=1),
				col("col_1"),
				f("department", "Select", "Department", options="Beamhouse\nTanning\nDyeing\nFinishing\nQC\nLaboratory\nMaintenance\nWarehouse"),
				f("shift", "Select", "Shift", options="A\nB\nC\nGeneral"),
				f("machine", "Link", "Machine", options="Leather Machine"),
				f("batch", "Link", "Batch", options="Leather Production Batch"),
				f("hides_processed", "Int", "Hides Processed"),
				f("area_finished_sqft", "Float", "Sq. ft. Finished"),
				f("batches_completed", "Int", "Batches Completed"),
			],
			autoname="naming_series:",
			naming_rule="By \"Naming Series\" field",
		),
		None,
	)
)

DOCTYPES.append(
	(
		doctype(
			"Leather Settings",
			[
				f("default_company", "Link", "Default Company", options="Company"),
				f("default_hide_warehouse", "Link", "Default Hide Warehouse", options="Warehouse"),
				f("default_wet_blue_warehouse", "Link", "Default Wet Blue Warehouse", options="Warehouse"),
				f("default_finished_warehouse", "Link", "Default Finished Warehouse", options="Warehouse"),
				f("sqft_to_sqm", "Float", "sq. ft. to sq. m", default=0.092903),
				f("hide_aging_alert_days", "Int", "Hide Aging Alert (days)", default=14),
				f("enable_piece_barcode", "Check", "Enable Piece Barcode", default=1),
			],
			issingle=1,
		),
		None,
	)
)


def write_all_doctypes():
	MOD.mkdir(parents=True, exist_ok=True)
	(MOD / "__init__.py").write_text("")
	(MOD / "doctype").mkdir(parents=True, exist_ok=True)
	(MOD / "doctype" / "__init__.py").write_text("")
	for doc, extra in DOCTYPES:
		write_doctype(doc, extra)
	print(f"Wrote {len(DOCTYPES)} doctypes")


if __name__ == "__main__":
	write_all_doctypes()
