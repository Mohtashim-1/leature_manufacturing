# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

"""Map tannery documents onto standard ERPNext Item / BOM / Routing /
Work Order / Job Card / Sales Order / Purchase Order."""

import frappe
from frappe.utils import cint, flt, getdate, now_datetime, today

COMPANY = "Leature Manufacturing"
WH_STORES = "Stores - LM"
WH_WIP = "Work In Progress - LM"
WH_FG = "Finished Goods - LM"

PROCESS_OPS = [
	"Soaking",
	"Liming",
	"Fleshing",
	"Unhairing",
	"Deliming",
	"Bating",
	"Pickling",
	"Chrome Tanning",
	"Vegetable Tanning",
	"Splitting",
	"Shaving",
	"Retanning",
	"Dyeing",
	"Fatliquoring",
	"Spray Finishing",
	"Measuring",
]


def _has_field(doctype, field):
	try:
		return bool(frappe.get_meta(doctype).has_field(field))
	except Exception:
		return False


def sync_enabled():
	if not frappe.db.exists("DocType", "Item"):
		return False
	if frappe.db.exists("DocType", "Leather Settings") and _has_field("Leather Settings", "sync_with_erpnext"):
		return cint(frappe.db.get_single_value("Leather Settings", "sync_with_erpnext") or 1)
	return True


def company():
	if frappe.db.exists("DocType", "Leather Settings"):
		c = frappe.db.get_single_value("Leather Settings", "default_company")
		if c:
			return c
	if frappe.db.exists("Company", COMPANY):
		return COMPANY
	return frappe.defaults.get_user_default("Company") or frappe.db.get_single_value("Global Defaults", "default_company")


def warehouse(kind="stores"):
	settings_map = {
		"stores": "default_hide_warehouse",
		"wip": "default_wet_blue_warehouse",
		"fg": "default_finished_warehouse",
	}
	fallback = {"stores": WH_STORES, "wip": WH_WIP, "fg": WH_FG}
	if frappe.db.exists("DocType", "Leather Settings") and _has_field("Leather Settings", settings_map[kind]):
		val = frappe.db.get_single_value("Leather Settings", settings_map[kind])
		if val:
			return val
	name = fallback[kind]
	return name if frappe.db.exists("Warehouse", name) else None


def uom(name):
	if not name:
		name = "Kg"
	candidates = [name, name.title(), name.upper(), "Kg" if str(name).lower() == "kg" else None, "Nos"]
	for cand in candidates:
		if cand and frappe.db.exists("UOM", cand):
			return cand
	doc = frappe.get_doc({"doctype": "UOM", "uom_name": name}).insert(ignore_permissions=True)
	return doc.name


def item_group(name, parent="All Item Groups"):
	if frappe.db.exists("Item Group", name):
		return name
	parent = parent if frappe.db.exists("Item Group", parent) else "All Item Groups"
	frappe.get_doc(
		{
			"doctype": "Item Group",
			"item_group_name": name,
			"parent_item_group": parent,
			"is_group": 0,
		}
	).insert(ignore_permissions=True)
	return name


def ensure_setup():
	if not sync_enabled():
		return
	if not frappe.db.exists("Item Group", "Leather"):
		frappe.get_doc(
			{
				"doctype": "Item Group",
				"item_group_name": "Leather",
				"parent_item_group": "All Item Groups",
				"is_group": 1,
			}
		).insert(ignore_permissions=True)
	for grp in ("Raw Hide", "Leather Chemical", "Finished Leather", "Wet Blue"):
		item_group(grp, "Leather")
	for op in PROCESS_OPS:
		ensure_operation(op)
	if frappe.db.exists("DocType", "Manufacturing Settings"):
		try:
			ms = frappe.get_single("Manufacturing Settings")
			if not cint(ms.disable_capacity_planning):
				ms.disable_capacity_planning = 1
				ms.save(ignore_permissions=True)
		except Exception:
			pass
	if frappe.db.exists("DocType", "Leather Settings"):
		try:
			s = frappe.get_single("Leather Settings")
			changed = False
			if not s.default_company and frappe.db.exists("Company", COMPANY):
				s.default_company = COMPANY
				changed = True
			if not s.default_hide_warehouse and frappe.db.exists("Warehouse", WH_STORES):
				s.default_hide_warehouse = WH_STORES
				changed = True
			if not s.default_wet_blue_warehouse and frappe.db.exists("Warehouse", WH_WIP):
				s.default_wet_blue_warehouse = WH_WIP
				changed = True
			if not s.default_finished_warehouse and frappe.db.exists("Warehouse", WH_FG):
				s.default_finished_warehouse = WH_FG
				changed = True
			if _has_field("Leather Settings", "sync_with_erpnext") and s.sync_with_erpnext is None:
				s.sync_with_erpnext = 1
				changed = True
			if changed:
				s.save(ignore_permissions=True)
		except Exception:
			pass


def ensure_operation(name):
	if not name:
		return None
	if frappe.db.exists("Operation", name):
		return name
	frappe.get_doc({"doctype": "Operation", "name": name, "description": name}).insert(ignore_permissions=True)
	return name


def ensure_workstation(code, label=None, warehouse_name=None):
	if not code:
		return None
	name = label or code
	if frappe.db.exists("Workstation", name):
		return name
	if frappe.db.exists("Workstation", code):
		return code
	doc = frappe.get_doc(
		{
			"doctype": "Workstation",
			"workstation_name": name,
			"production_capacity": 1,
			"warehouse": warehouse_name or warehouse("wip"),
			"hour_rate_labour": 500,
			"working_hours": [{"start_time": "08:00:00", "end_time": "17:00:00"}],
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


def ensure_item(code, item_name, group, stock_uom="Kg", purchase=1, sales=0, manufacture=0):
	if not code:
		return None
	if frappe.db.exists("Item", code):
		return code
	doc = frappe.get_doc(
		{
			"doctype": "Item",
			"item_code": code,
			"item_name": item_name or code,
			"item_group": item_group(group, "Leather"),
			"stock_uom": uom(stock_uom),
			"is_stock_item": 1,
			"include_item_in_manufacturing": 1,
			"is_purchase_item": cint(purchase),
			"is_sales_item": cint(sales),
			"default_material_request_type": "Manufacture" if manufacture else "Purchase",
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


def _set_if_empty(doc, field, value):
	if value and _has_field(doc.doctype, field) and not doc.get(field):
		doc.db_set(field, value, update_modified=False)


def sync_raw_hide(doc):
	if not sync_enabled():
		return
	ensure_setup()
	item = ensure_item(doc.hide_code, doc.hide_name, "Raw Hide", doc.purchase_uom or "Nos", purchase=1, sales=0)
	_set_if_empty(doc, "item", item)
	return item


def sync_finished(doc):
	if not sync_enabled():
		return
	ensure_setup()
	item = ensure_item(
		doc.product_code,
		doc.product_name,
		"Finished Leather",
		doc.sales_uom or "Nos",
		purchase=0,
		sales=1,
		manufacture=1,
	)
	_set_if_empty(doc, "item", item)
	return item


def sync_chemical(doc):
	if not sync_enabled():
		return
	ensure_setup()
	item = ensure_item(doc.chemical_code, doc.chemical_name, "Leather Chemical", doc.uom or "Kg", purchase=1)
	_set_if_empty(doc, "item", item)
	return item


def sync_drum(doc):
	if not sync_enabled():
		return
	ws = ensure_workstation(doc.drum_code, doc.drum_name or doc.drum_code, warehouse("wip"))
	_set_if_empty(doc, "workstation", ws)
	return ws


def sync_machine(doc):
	if not sync_enabled():
		return
	ws = ensure_workstation(doc.machine_code, doc.machine_name or doc.machine_code, warehouse("wip"))
	_set_if_empty(doc, "workstation", ws)
	return ws


def finished_item_for_article(article=None, color=None):
	filters = {}
	if article:
		filters["article"] = article
	if color:
		filters["color"] = color
	name = frappe.db.get_value("Finished Leather Master", filters, "name") if filters else None
	if not name:
		name = frappe.db.get_value("Finished Leather Master", {"article": article} if article else {}, "name")
	if not name:
		name = frappe.db.get_value("Finished Leather Master", {}, "name")
	if not name:
		return ensure_item("FL-GENERIC", "Finished Leather", "Finished Leather", "Nos", sales=1, manufacture=1)
	master = frappe.get_doc("Finished Leather Master", name)
	return sync_finished(master)


def hide_item_for_animal(animal=None):
	name = None
	if animal:
		name = frappe.db.get_value("Raw Hide Master", {"animal_type": animal}, "name")
	if not name:
		name = frappe.db.get_value("Raw Hide Master", {}, "name")
	if not name:
		return ensure_item("RH-GENERIC", "Raw Hide", "Raw Hide", "Nos", purchase=1)
	master = frappe.get_doc("Raw Hide Master", name)
	return sync_raw_hide(master)


def sync_routing(doc):
	if not sync_enabled():
		return None
	ensure_setup()
	route_name = (doc.route_name or doc.name)[:140]
	ws = None
	drum = frappe.db.get_value("Drum", {}, "name")
	if drum:
		ws = sync_drum(frappe.get_doc("Drum", drum))
	ops = []
	for row in doc.operations or []:
		op = ensure_operation(row.operation)
		ops.append(
			{
				"operation": op,
				"sequence_id": row.sequence or len(ops) + 1,
				"time_in_mins": flt(row.standard_time_min) or 60,
				"workstation": ws,
				"hour_rate": 500,
				"batch_size": 1,
				"fixed_time": 1,
			}
		)
	if not ops:
		return None
	if frappe.db.exists("Routing", route_name):
		routing = frappe.get_doc("Routing", route_name)
		if routing.docstatus == 0:
			routing.operations = []
			for op in ops:
				routing.append("operations", op)
			routing.save(ignore_permissions=True)
	else:
		routing = frappe.get_doc({"doctype": "Routing", "routing_name": route_name, "operations": ops})
		routing.insert(ignore_permissions=True)
	if routing.docstatus == 0:
		routing.submit()
	_set_if_empty(doc, "routing", routing.name)
	return routing.name


def sync_bom(doc):
	if not sync_enabled():
		return None
	ensure_setup()
	fg = finished_item_for_article(doc.article, doc.color)
	hide = hide_item_for_animal()
	existing = None
	if _has_field("Leather Recipe", "bom") and doc.get("bom"):
		existing = doc.bom
	if existing and frappe.db.exists("BOM", existing):
		return existing
	existing = frappe.db.get_value("BOM", {"item": fg, "is_active": 1, "docstatus": 1}, "name")
	if existing:
		_set_if_empty(doc, "bom", existing)
		return existing

	routing = None
	route_name = frappe.db.get_value("Leather Process Route", {"article": doc.article}, "name")
	if not route_name:
		route_name = frappe.db.get_value("Leather Process Route", {}, "name")
	if route_name:
		routing = sync_routing(frappe.get_doc("Leather Process Route", route_name))

	bom_qty = 100.0
	items = [{"item_code": hide, "qty": 90, "uom": frappe.db.get_value("Item", hide, "stock_uom")}]
	for ing in doc.ingredients or []:
		chem = frappe.get_doc("Leather Chemical", ing.chemical)
		item = sync_chemical(chem)
		qty = flt(ing.qty)
		if (ing.basis or "").startswith("%"):
			qty = 90 * qty / 100.0
		if qty <= 0:
			qty = 0.01
		items.append({"item_code": item, "qty": qty, "uom": frappe.db.get_value("Item", item, "stock_uom")})

	bom = frappe.get_doc(
		{
			"doctype": "BOM",
			"item": fg,
			"company": company(),
			"quantity": bom_qty,
			"uom": frappe.db.get_value("Item", fg, "stock_uom"),
			"is_active": 1,
			"is_default": 1,
			"with_operations": 1 if routing else 0,
			"routing": routing,
			"rm_cost_as_per": "Valuation Rate",
			"items": items,
		}
	)
	if routing:
		route = frappe.get_doc("Routing", routing)
		for op in route.operations:
			bom.append(
				"operations",
				{
					"operation": op.operation,
					"workstation": op.workstation,
					"time_in_mins": op.time_in_mins or 60,
					"hour_rate": op.hour_rate or 500,
					"sequence_id": op.sequence_id,
					"batch_size": 1,
					"fixed_time": 1,
				},
			)
	bom.insert(ignore_permissions=True)
	bom.submit()
	_set_if_empty(doc, "bom", bom.name)
	return bom.name


def create_sales_order(doc):
	if not sync_enabled() or doc.docstatus != 1:
		return None
	ensure_setup()
	if _has_field("Leather Sales Order", "erpnext_sales_order") and doc.get("erpnext_sales_order"):
		return doc.erpnext_sales_order
	co = doc.company or company()
	delivery = doc.delivery_date or doc.transaction_date or today()
	items = []
	for row in doc.items or []:
		item = None
		if row.finished_product and frappe.db.exists("Finished Leather Master", row.finished_product):
			item = sync_finished(frappe.get_doc("Finished Leather Master", row.finished_product))
		if not item:
			item = finished_item_for_article(row.article, row.color)
		items.append(
			{
				"item_code": item,
				"qty": flt(row.qty) or 1,
				"rate": flt(row.rate),
				"uom": frappe.db.get_value("Item", item, "stock_uom"),
				"delivery_date": row.delivery_date or delivery,
				"warehouse": warehouse("fg"),
			}
		)
	if not items:
		return None
	so = frappe.get_doc(
		{
			"doctype": "Sales Order",
			"customer": doc.customer,
			"company": co,
			"transaction_date": doc.transaction_date or today(),
			"delivery_date": delivery,
			"po_no": doc.customer_po,
			"order_type": "Sales",
			"items": items,
			"leather_sales_order": doc.name if _has_field("Sales Order", "leather_sales_order") else None,
		}
	)
	so.flags.ignore_permissions = True
	so.insert()
	try:
		so.submit()
	except Exception:
		frappe.log_error(title="Leature Sales Order submit")
	_set_if_empty(doc, "erpnext_sales_order", so.name)
	return so.name


def create_purchase_order(doc):
	if not sync_enabled() or doc.docstatus != 1:
		return None
	ensure_setup()
	if _has_field("Hide Purchase Order", "erpnext_purchase_order") and doc.get("erpnext_purchase_order"):
		return doc.erpnext_purchase_order
	items = []
	schedule = doc.transaction_date or today()
	for row in doc.items or []:
		item = None
		if row.raw_hide and frappe.db.exists("Raw Hide Master", row.raw_hide):
			item = sync_raw_hide(frappe.get_doc("Raw Hide Master", row.raw_hide))
		if not item:
			item = hide_item_for_animal(row.animal_type)
		items.append(
			{
				"item_code": item,
				"qty": flt(row.qty) or 1,
				"rate": flt(row.rate),
				"uom": frappe.db.get_value("Item", item, "stock_uom"),
				"schedule_date": schedule,
				"warehouse": warehouse("stores"),
			}
		)
	if not items:
		return None
	po = frappe.get_doc(
		{
			"doctype": "Purchase Order",
			"supplier": doc.supplier,
			"company": doc.company or company(),
			"transaction_date": doc.transaction_date or today(),
			"schedule_date": schedule,
			"items": items,
		}
	)
	po.flags.ignore_permissions = True
	po.insert()
	try:
		po.submit()
	except Exception:
		frappe.log_error(title="Leature Purchase Order submit")
	_set_if_empty(doc, "erpnext_purchase_order", po.name)
	return po.name


def create_work_order(doc):
	if not sync_enabled() or doc.docstatus != 1:
		return None
	ensure_setup()
	if _has_field("Leather Production Batch", "work_order") and doc.get("work_order"):
		_link_job_card(doc, doc.work_order)
		return doc.work_order

	recipe_name = doc.recipe or frappe.db.get_value("Leather Recipe", {"is_approved": 1}, "name")
	bom = None
	fg = None
	if recipe_name:
		recipe = frappe.get_doc("Leather Recipe", recipe_name)
		bom = sync_bom(recipe)
		fg = frappe.db.get_value("BOM", bom, "item") if bom else finished_item_for_article(recipe.article)
	if not fg:
		fg = finished_item_for_article()
	if not bom:
		bom = frappe.db.get_value("BOM", {"item": fg, "docstatus": 1, "is_active": 1}, "name")
	if not bom:
		return None

	qty = flt(doc.output_area_sqft) or flt(doc.output_weight_kg) or flt(doc.input_weight_kg) or 1
	wo = frappe.get_doc(
		{
			"doctype": "Work Order",
			"production_item": fg,
			"bom_no": bom,
			"qty": qty,
			"company": doc.company or company(),
			"planned_start_date": now_datetime(),
			"fg_warehouse": warehouse("fg"),
			"wip_warehouse": warehouse("wip"),
			"source_warehouse": warehouse("stores"),
			"scrap_warehouse": warehouse("wip"),
			"skip_transfer": 1,
			"use_multi_level_bom": 0,
		}
	)
	wo.flags.ignore_permissions = True
	wo.get_items_and_operations_from_bom()
	wo.insert()
	try:
		wo.submit()
	except Exception:
		frappe.log_error(title="Leature Work Order submit")
	_set_if_empty(doc, "work_order", wo.name)
	_link_job_card(doc, wo.name)
	return wo.name


def _link_job_card(batch, work_order):
	if not work_order or not frappe.db.exists("DocType", "Job Card"):
		return
	jc = frappe.db.get_value(
		"Job Card",
		{"work_order": work_order, "operation": batch.process_stage, "docstatus": ["<", 2]},
		"name",
	)
	if not jc:
		jc = frappe.db.get_value("Job Card", {"work_order": work_order, "docstatus": ["<", 2]}, "name")
	if jc:
		_set_if_empty(batch, "job_card", jc)


def backfill_job_cards():
	frappe.db.sql("UPDATE `tabBOM Operation` SET fixed_time=1 WHERE IFNULL(fixed_time,0)=0")
	for name in frappe.get_all("Work Order", filters={"docstatus": 1}, pluck="name"):
		wo = frappe.get_doc("Work Order", name)
		if not wo.operations:
			wo.get_items_and_operations_from_bom()
			wo.flags.ignore_validate_update_after_submit = True
			wo.flags.ignore_permissions = True
			wo.save()
		if wo.operations and not frappe.db.exists("Job Card", {"work_order": wo.name}):
			try:
				wo.create_job_card()
			except Exception:
				frappe.log_error(title="Leature Job Card create")


@frappe.whitelist()
def sync_existing():
	"""Backfill Items / BOM / Routing / SO / PO / WO / Job Card from tannery docs."""
	if not sync_enabled():
		return {"ok": 0, "reason": "disabled"}
	ensure_setup()
	counts = {"items": 0, "boms": 0, "routings": 0, "sales_orders": 0, "purchase_orders": 0, "work_orders": 0}

	def each(doctype, fn, counter=None):
		for name in frappe.get_all(doctype, pluck="name"):
			try:
				if fn(frappe.get_doc(doctype, name)) and counter:
					counts[counter] += 1
				elif counter is None:
					counts["items"] += 1
			except Exception:
				frappe.log_error(title=f"Leature sync {doctype}")

	each("Raw Hide Master", sync_raw_hide)
	each("Finished Leather Master", sync_finished)
	each("Leather Chemical", sync_chemical)
	each("Drum", sync_drum)
	each("Leather Machine", sync_machine)
	each("Leather Process Route", sync_routing, "routings")
	each("Leather Recipe", sync_bom, "boms")

	for name in frappe.get_all("Leather Sales Order", filters={"docstatus": 1}, pluck="name"):
		try:
			if create_sales_order(frappe.get_doc("Leather Sales Order", name)):
				counts["sales_orders"] += 1
		except Exception:
			frappe.log_error(title="Leature sync Sales Order")
	for name in frappe.get_all("Hide Purchase Order", filters={"docstatus": 1}, pluck="name"):
		try:
			if create_purchase_order(frappe.get_doc("Hide Purchase Order", name)):
				counts["purchase_orders"] += 1
		except Exception:
			frappe.log_error(title="Leature sync Purchase Order")
	# one work order per distinct recipe/output lot family — use submitted batches
	seen_lots = set()
	for name in frappe.get_all(
		"Leather Production Batch", filters={"docstatus": 1}, order_by="posting_date asc", pluck="name"
	):
		batch = frappe.get_doc("Leather Production Batch", name)
		key = batch.output_lot or batch.input_lot or name
		try:
			if key in seen_lots and batch.get("work_order"):
				_link_job_card(batch, batch.work_order)
				continue
			existing_wo = None
			if batch.output_lot:
				existing_wo = frappe.db.get_value(
					"Leather Production Batch", {"output_lot": batch.output_lot, "work_order": ["!=", ""]}, "work_order"
				)
			if not existing_wo and batch.input_lot:
				existing_wo = frappe.db.get_value(
					"Leather Production Batch", {"input_lot": batch.input_lot, "work_order": ["!=", ""]}, "work_order"
				)
			if existing_wo:
				_set_if_empty(batch, "work_order", existing_wo)
				_link_job_card(batch, existing_wo)
				seen_lots.add(key)
				continue
			if create_work_order(batch):
				counts["work_orders"] += 1
				seen_lots.add(key)
		except Exception:
			frappe.log_error(title="Leature sync Work Order")
	try:
		backfill_job_cards()
		for name in frappe.get_all("Leather Production Batch", filters={"docstatus": 1}, pluck="name"):
			batch = frappe.get_doc("Leather Production Batch", name)
			if batch.work_order:
				_link_job_card(batch, batch.work_order)
	except Exception:
		frappe.log_error(title="Leature Job Card backfill")
	frappe.db.commit()
	return counts
