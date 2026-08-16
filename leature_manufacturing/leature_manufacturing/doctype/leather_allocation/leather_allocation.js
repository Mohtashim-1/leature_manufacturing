// Copyright (c) 2026, mohtashim and contributors
// For license information, please see license.txt

frappe.ui.form.on("Leather Allocation", {
	refresh(frm) {
		frm.add_custom_button(__("Suggest Matching Pieces"), () => {
			frappe.call({
				method: "leature_manufacturing.leature_manufacturing.utils.suggest_allocation",
				args: {
					article: frm.doc.article,
					color: frm.doc.color,
					grade: frm.doc.grade,
					required_area: frm.doc.required_area_sqft,
				},
				callback(r) {
					const msg = r.message || {};
					frappe.model.clear_table(frm.doc, "items");
					(msg.pieces || []).forEach((p) => {
						const row = frm.add_child("items");
						row.piece = p.name;
						row.lot = p.lot;
						row.article = p.article;
						row.color = p.color;
						row.grade = p.grade;
						row.area_sqft = p.area_sqft;
					});
					frm.refresh_field("items");
					frm.set_value("allocated_area_sqft", msg.allocated_area || 0);
					frappe.show_alert({
						message: __("Allocated {0} sq. ft.", [msg.allocated_area || 0]),
						indicator: "green",
					});
				},
			});
		});
	},
});
