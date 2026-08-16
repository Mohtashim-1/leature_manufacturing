// Copyright (c) 2026, mohtashim and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hide Purchase Order", {
	refresh(frm) {
		if (frm.doc.erpnext_purchase_order) {
			frm.add_custom_button(
				__("Open Purchase Order"),
				() => frappe.set_route("Form", "Purchase Order", frm.doc.erpnext_purchase_order),
				__("ERPNext")
			);
		}
	},
});
