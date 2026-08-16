# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class HidePurchaseOrder(Document):
	def validate(self):
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

	def on_submit(self):
		from leature_manufacturing.leature_manufacturing.erpnext_bridge import create_purchase_order

		try:
			create_purchase_order(self)
		except Exception:
			pass
