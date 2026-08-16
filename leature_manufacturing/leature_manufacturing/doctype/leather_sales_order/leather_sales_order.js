// Copyright (c) 2026, mohtashim and contributors
// For license information, please see license.txt

frappe.ui.form.on("Leather Sales Order", {
	refresh(frm) {
		if (frm.doc.erpnext_sales_order) {
			frm.add_custom_button(
				__("Open Sales Order"),
				() => frappe.set_route("Form", "Sales Order", frm.doc.erpnext_sales_order),
				__("ERPNext")
			);
		}
	},
});
