# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class LeatherSalesOrder(Document):
	def validate(self):
		qty = amount = 0
		for row in self.items or []:
			row.amount = (row.qty or 0) * (row.rate or 0)
			qty += row.qty or 0
			amount += row.amount or 0
		self.total_qty = qty
		self.grand_total = amount

	def on_submit(self):
		from leature_manufacturing.leature_manufacturing.erpnext_bridge import create_sales_order

		try:
			create_sales_order(self)
		except Exception:
			pass
