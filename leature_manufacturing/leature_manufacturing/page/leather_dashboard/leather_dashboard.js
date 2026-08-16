frappe.pages["leather-dashboard"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Leather Manufacturing Dashboard"),
		single_column: true,
	});
	$(wrapper).find(".layout-main-section").html(`
		<div class="leather-dash" style="padding:8px 0 32px;">
			<div class="ld-kpis" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-bottom:16px;"></div>
			<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:12px;">
				<div style="border:1px solid var(--border-color);border-radius:10px;padding:12px;background:var(--card-bg);">
					<h4 style="margin:0 0 8px;">${__("Grade mix (finished lots)")}</h4>
					<div class="ld-grade" style="height:280px;"></div>
				</div>
				<div style="border:1px solid var(--border-color);border-radius:10px;padding:12px;background:var(--card-bg);">
					<h4 style="margin:0 0 8px;">${__("Process batches")}</h4>
					<div class="ld-process" style="height:280px;"></div>
				</div>
			</div>
		</div>
	`);
	page.set_primary_action(__("Refresh"), () => load(wrapper), "refresh");
	load(wrapper);
};

function kpi(label, value) {
	return `<div style="border:1px solid var(--border-color);border-radius:10px;padding:12px;background:var(--card-bg);">
		<div style="font-size:11px;color:var(--text-muted);">${label}</div>
		<div style="font-size:22px;font-weight:700;margin-top:4px;">${value}</div>
	</div>`;
}

function load(wrapper) {
	frappe.call({
		method: "leature_manufacturing.leature_manufacturing.utils.dashboard_data",
		callback(r) {
			const d = r.message || {};
			const k = d.kpis || {};
			$(wrapper)
				.find(".ld-kpis")
				.html(
					[
						kpi(__("Raw hide lots"), k.raw_lots || 0),
						kpi(__("Wet blue lots"), k.wet_blue_lots || 0),
						kpi(__("Finished lots"), k.finished_lots || 0),
						kpi(__("Available pieces"), k.available_pieces || 0),
						kpi(__("Open orders"), k.open_orders || 0),
						kpi(__("Avg yield %"), (k.avg_yield || 0).toFixed(1)),
					].join("")
				);
			const grades = d.grade_mix || [];
			const processes = d.process_output || [];
			if (window.frappe && frappe.Chart) {
				$(wrapper).find(".ld-grade").empty();
				$(wrapper).find(".ld-process").empty();
				if (grades.length) {
					new frappe.Chart($(wrapper).find(".ld-grade")[0], {
						data: {
							labels: grades.map((g) => g.grade || "Ungraded"),
							datasets: [{ name: "Area", values: grades.map((g) => g.area || 0) }],
						},
						type: "pie",
						height: 260,
					});
				}
				if (processes.length) {
					new frappe.Chart($(wrapper).find(".ld-process")[0], {
						data: {
							labels: processes.map((p) => p.process),
							datasets: [{ name: "Batches", values: processes.map((p) => p.batches || 0) }],
						},
						type: "bar",
						height: 260,
					});
				}
			}
		},
	});
}
