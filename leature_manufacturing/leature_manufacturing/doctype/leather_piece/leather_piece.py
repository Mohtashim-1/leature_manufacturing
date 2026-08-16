# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class LeatherPiece(Document):
	def before_insert(self):
		pass

	def after_insert(self):
		if not self.barcode:
			self.db_set("barcode", self.name)
