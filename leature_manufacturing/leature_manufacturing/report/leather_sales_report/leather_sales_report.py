# Copyright (c) 2026, Leature Manufacturing
import frappe
from frappe import _


def execute(filters=None):
	columns = [
		{"label": _("Order"), "fieldname": "name", "fieldtype": "Link", "options": "Leather Sales Order", "width": 160},
		{"label": _("Date"), "fieldname": "transaction_date", "fieldtype": "Date", "width": 100},
		{"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 180},
		{"label": _("Export"), "fieldname": "is_export", "fieldtype": "Check", "width": 80},
		{"label": _("Qty"), "fieldname": "total_qty", "fieldtype": "Float", "width": 100},
		{"label": _("Grand Total"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 130},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 110},
	]
	data = frappe.get_all(
		"Leather Sales Order",
		filters={"docstatus": ["<", 2]},
		fields=["name", "transaction_date", "customer", "is_export", "total_qty", "grand_total", "status"],
		order_by="transaction_date desc",
	)
	chart = {
		"data": {
			"labels": [d.customer or d.name for d in data],
			"datasets": [{"name": _("Sales"), "values": [d.grand_total or 0 for d in data]}],
		},
		"type": "bar",
		"colors": ["#16a34a"],
	}
	return columns, data, None, chart
