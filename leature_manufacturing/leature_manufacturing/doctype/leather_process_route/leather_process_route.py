# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class LeatherProcessRoute(Document):
	def on_update(self):
		from leature_manufacturing.leature_manufacturing.erpnext_bridge import sync_routing

		try:
			sync_routing(self)
		except Exception:
			pass
