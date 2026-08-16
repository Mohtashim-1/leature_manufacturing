frappe.query_reports["Lot Traceability Report"] = {
	filters: [
		{
			fieldname: "lot",
			label: __("Lot"),
			fieldtype: "Link",
			options: "Leather Lot",
			reqd: 1,
		},
	],
};
