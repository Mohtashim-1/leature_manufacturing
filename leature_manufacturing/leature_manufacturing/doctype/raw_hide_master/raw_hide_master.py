# Copyright (c) 2026, mohtashim and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class RawHideMaster(Document):
	def on_update(self):
		from leature_manufacturing.leature_manufacturing.erpnext_bridge import sync_raw_hide

		try:
			sync_raw_hide(self)
		except Exception:
			pass
