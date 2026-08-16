# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class LeatherMachine(Document):
	def on_update(self):
		from leature_manufacturing.leature_manufacturing.erpnext_bridge import sync_machine

		try:
			sync_machine(self)
		except Exception:
			pass
