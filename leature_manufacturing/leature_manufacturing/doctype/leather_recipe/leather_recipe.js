// Copyright (c) 2026, mohtashim and contributors
// For license information, please see license.txt

frappe.ui.form.on("Leather Recipe", {
	refresh(frm) {
		if (frm.doc.bom) {
			frm.add_custom_button(__("Open BOM"), () => frappe.set_route("Form", "BOM", frm.doc.bom), __("ERPNext"));
		} else if (!frm.is_new() && frm.doc.is_approved) {
			frm.add_custom_button(__("Create BOM"), () => sync_now(frm), __("ERPNext"));
		}
	},
});

function sync_now(frm) {
	frappe.call({
		method: "leature_manufacturing.leature_manufacturing.erpnext_bridge.sync_existing",
		freeze: true,
		callback() {
			frm.reload_doc();
		},
	});
}
