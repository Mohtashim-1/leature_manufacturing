#!/usr/bin/env python3
"""Generate Leature workspace JSON."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WS = ROOT / "leature_manufacturing" / "leature_manufacturing" / "workspace" / "leature"
WS.mkdir(parents=True, exist_ok=True)

CARDS = {
	"Masters": [
		"Leather Grade",
		"Animal Type",
		"Leather Article",
		"Leather Color",
		"Raw Hide Master",
		"Finished Leather Master",
		"Leather Chemical",
		"Leather Recipe",
		"Leather Process Route",
		"Drum",
		"Leather Machine",
		"Hide Collection Center",
		"Procurement Agent",
		"Leather Settings",
	],
	"Procurement": [
		"Hide Supplier Contract",
		"Hide Purchase Order",
		"Hide Receiving Inspection",
		"Hide Grading",
	],
	"Production": [
		"Leather Lot",
		"Leather Production Batch",
		"Leather Area Measurement",
		"Leather Piece",
		"Leather Production Plan",
		"Drum Schedule",
		"Worker Productivity Log",
		"Leather Maintenance",
	],
	"Quality & Lab": [
		"Leather QC Inspection",
		"Lab Sample",
		"Customer Sample Request",
	],
	"Sales & Export": [
		"Leather Sales Order",
		"Leather Allocation",
		"Leather Packing List",
		"Leather Export Shipment",
		"Leather Complaint",
	],
	"Environment & Cost": [
		"Waste Record",
		"ETP Daily Log",
		"Sustainability Record",
		"Leather Batch Costing",
	],
	"Reports": [
		("Leather Yield Report", "Report"),
		("Chemical Consumption Report", "Report"),
		("Grade Analysis Report", "Report"),
		("Finished Leather Stock", "Report"),
		("Leather Batch Cost Report", "Report"),
		("Lot Traceability Report", "Report"),
	],
}

SHORTCUTS = [
	("Leather Dashboard", "leather-dashboard", "Page", "Blue"),
	("Leather Lot", "Leather Lot", "DocType", "Orange"),
	("Hide Purchase Order", "Hide Purchase Order", "DocType", "Grey"),
	("Production Batch", "Leather Production Batch", "DocType", "Grey"),
	("Leather Piece", "Leather Piece", "DocType", "Grey"),
	("Sales Order", "Leather Sales Order", "DocType", "Green"),
	("QC Inspection", "Leather QC Inspection", "DocType", "Grey"),
	("Batch Costing", "Leather Batch Costing", "DocType", "Grey"),
]


def link(label, link_to, link_type="DocType", onboard=0):
	return {
		"hidden": 0,
		"is_query_report": 1 if link_type == "Report" else 0,
		"label": label,
		"link_count": 0,
		"link_to": link_to,
		"link_type": link_type,
		"onboard": onboard,
		"type": "Link",
	}


def card_break(label, count):
	return {
		"hidden": 0,
		"is_query_report": 0,
		"label": label,
		"link_count": count,
		"link_type": "DocType",
		"onboard": 0,
		"type": "Card Break",
	}


links = []
for card, items in CARDS.items():
	links.append(card_break(card, len(items)))
	for item in items:
		if isinstance(item, tuple):
			links.append(link(item[0], item[0], item[1]))
		else:
			links.append(link(item, item, onboard=1 if card in ("Procurement", "Production") else 0))

content = [{"id": "hdr1", "type": "header", "data": {"text": '<span class="h4">Tannery Flow</span>', "col": 12}}]
for i, (label, *_rest) in enumerate(SHORTCUTS):
	content.append({"id": f"s{i}", "type": "shortcut", "data": {"shortcut_name": label, "col": 3}})
content.append({"id": "hdr2", "type": "header", "data": {"text": '<span class="h4">Modules</span>', "col": 12}})
for i, card in enumerate(CARDS):
	content.append({"id": f"c{i}", "type": "card", "data": {"card_name": card, "col": 4}})

shortcuts = []
for label, link_to, typ, color in SHORTCUTS:
	row = {"color": color, "doc_view": "List", "label": label, "link_to": link_to, "type": typ}
	if typ == "DocType":
		row["stats_filter"] = "[]"
	shortcuts.append(row)

doc = {
	"charts": [],
	"content": json.dumps(content),
	"creation": "2026-08-16 22:00:00.000000",
	"custom_blocks": [],
	"docstatus": 0,
	"doctype": "Workspace",
	"for_user": "",
	"hide_custom": 0,
	"icon": "industry",
	"idx": 0,
	"indicator_color": "orange",
	"is_hidden": 0,
	"label": "Leature",
	"public": 1,
	"title": "Leature",
	"module": "Leature Manufacturing",
	"links": links,
	"modified": "2026-08-16 22:00:00.000000",
	"modified_by": "Administrator",
	"name": "Leature",
	"number_cards": [],
	"owner": "Administrator",
	"parent_page": "",
	"restrict_to_domain": "",
	"roles": [],
	"sequence_id": 1.0,
	"shortcuts": shortcuts,
}

(WS / "leature.json").write_text(json.dumps(doc, indent=1) + "\n")
print("Wrote workspace")
