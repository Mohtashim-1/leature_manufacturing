# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class LeatherAreaMeasurement(Document):
	def validate(self):
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
