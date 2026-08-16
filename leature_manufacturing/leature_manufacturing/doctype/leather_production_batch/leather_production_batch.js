// Copyright (c) 2026, mohtashim and contributors
// For license information, please see license.txt

frappe.ui.form.on("Leather Production Batch", {
	refresh(frm) {
		if (frm.doc.recipe && frm.doc.input_weight_kg) {
			frm.add_custom_button(__("Load Recipe Chemicals"), () => {
				frm.trigger("recipe");
			});
		}
		if (frm.doc.work_order) {
			frm.add_custom_button(
				__("Open Work Order"),
				() => frappe.set_route("Form", "Work Order", frm.doc.work_order),
				__("ERPNext")
			);
		}
		if (frm.doc.job_card) {
			frm.add_custom_button(
				__("Open Job Card"),
				() => frappe.set_route("Form", "Job Card", frm.doc.job_card),
				__("ERPNext")
			);
		}
	},
	recipe(frm) {
		if (!frm.doc.recipe || !frm.doc.input_weight_kg) {
			frappe.show_alert(__("Set recipe and input weight first"));
			return;
		}
		frappe.model.clear_table(frm.doc, "chemicals");
		frappe.call({
			method: "frappe.client.get",
			args: { doctype: "Leather Recipe", name: frm.doc.recipe },
			callback(r) {
				const recipe = r.message || {};
				(recipe.ingredients || []).forEach((ing) => {
					let qty = ing.qty || 0;
					if ((ing.basis || "").startsWith("%")) {
						qty = (frm.doc.input_weight_kg * qty) / 100.0;
					}
					const row = frm.add_child("chemicals");
					row.chemical = ing.chemical;
					row.standard_qty = qty;
					row.uom = ing.uom;
				});
				frm.refresh_field("chemicals");
			},
		});
	},
	input_weight_kg(frm) {
		if (frm.doc.recipe && !(frm.doc.chemicals || []).length) {
			frm.trigger("recipe");
		}
	},
});
