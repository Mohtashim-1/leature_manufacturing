# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class LeatherProductionBatch(Document):
	def validate(self):
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

	def on_submit(self):
		from leature_manufacturing.leature_manufacturing.erpnext_bridge import create_work_order

		try:
			create_work_order(self)
		except Exception:
			pass
