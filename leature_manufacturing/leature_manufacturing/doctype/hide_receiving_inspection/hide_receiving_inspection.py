# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class HideReceivingInspection(Document):
	def validate(self):
		pieces = gross = net = 0
		for row in self.items or []:
			row.net_weight_kg = (row.gross_weight_kg or 0) - (row.salt_deduction_kg or 0) - (row.moisture_deduction_kg or 0)
			pieces += row.pieces or 0
			gross += row.gross_weight_kg or 0
			net += row.net_weight_kg or 0
		self.total_pieces = pieces
		self.total_gross_weight = gross
		self.total_net_weight = net
