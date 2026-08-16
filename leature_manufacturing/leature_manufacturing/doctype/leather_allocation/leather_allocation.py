# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class LeatherAllocation(Document):
	def validate(self):
		self.allocated_area_sqft = sum((row.area_sqft or 0) for row in self.items or [])
		if self.required_area_sqft and self.allocated_area_sqft < self.required_area_sqft:
			self.status = "Short"
		elif self.allocated_area_sqft:
			self.status = "Allocated"
