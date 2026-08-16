# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class LeatherLot(Document):
	def validate(self):
		from frappe.utils import date_diff, today

		if self.area_sqft and not self.area_sqm:
			self.area_sqm = float(self.area_sqft) * 0.092903
		elif self.area_sqm and not self.area_sqft:
			self.area_sqft = float(self.area_sqm) / 0.092903
		if self.storage_date:
			self.aging_days = date_diff(today(), self.storage_date)
		qty = self.area_sqft or self.weight_kg or self.pieces or 0
		self.amount = (self.rate or 0) * qty
