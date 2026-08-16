frappe.query_reports["Leather Yield Report"] = {
	filters: [
		{ fieldname: "from_date", label: __("From Date"), fieldtype: "Date" },
		{ fieldname: "to_date", label: __("To Date"), fieldtype: "Date" },
		{ fieldname: "process_stage", label: __("Process"), fieldtype: "Data" },
	],
};
