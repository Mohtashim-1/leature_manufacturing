# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class LeatherPackingList(Document):
	def validate(self):
		self.total_pieces = sum((row.pieces or 0) for row in self.items or [])
		self.total_area_sqft = sum((row.area_sqft or 0) for row in self.items or [])
		self.total_net_weight = sum((row.net_weight or 0) for row in self.items or [])
		self.total_gross_weight = sum((row.gross_weight or 0) for row in self.items or [])
