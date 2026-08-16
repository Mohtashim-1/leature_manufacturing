frappe.query_reports["Finished Leather Stock"] = {
	filters: [
		{ fieldname: "status", label: __("Status"), fieldtype: "Select", options: "\nAvailable\nAllocated\nPacked\nShipped\nHold" },
		{ fieldname: "article", label: __("Article"), fieldtype: "Link", options: "Leather Article" },
		{ fieldname: "color", label: __("Color"), fieldtype: "Link", options: "Leather Color" },
	],
};
