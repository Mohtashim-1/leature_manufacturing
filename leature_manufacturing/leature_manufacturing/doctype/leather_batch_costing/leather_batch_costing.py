# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class LeatherBatchCosting(Document):
	def validate(self):
		std = act = 0
		for row in self.items or []:
			row.variance = (row.actual_amount or 0) - (row.standard_amount or 0)
			std += row.standard_amount or 0
			act += row.actual_amount or 0
		self.total_standard = std
		self.total_actual = act
		if self.finished_area_sqft:
			self.cost_per_sqft = act / self.finished_area_sqft
