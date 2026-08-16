frappe.pages["leather-dashboard"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Leather Dashboard — Chart.js"),
		single_column: true,
	});
	wrapper._ld_charts = [];
	$(wrapper).find(".layout-main-section").html(`
		<div class="leature-dash">
			<div class="ld-kpis"></div>
			<div class="ld-grid">
				${card(__("Grade mix (finished area)"), "ld-grade")}
				${card(__("Process batches"), "ld-process")}
				${card(__("Yield % by process"), "ld-yield")}
				${card(__("Lot pipeline (weight kg)"), "ld-stages")}
				${card(__("Chemical standard vs actual"), "ld-chem")}
				${card(__("Piece status"), "ld-pieces")}
			</div>
		</div>
	`);
	page.set_primary_action(__("Refresh"), () => load(wrapper), "refresh");
	page.add_inner_button(__("ApexCharts Dashboard"), () => frappe.set_route("leather-apex-dashboard"));
	load_chartjs().then(() => load(wrapper));
};

function card(title, id) {
	return `<div class="ld-card"><h4>${title}</h4><div class="ld-canvas-wrap"><canvas id="${id}"></canvas></div></div>`;
}

function kpi(label, value) {
	return `<div class="ld-kpi"><div class="ld-kpi-label">${label}</div><div class="ld-kpi-val">${value}</div></div>`;
}

function load_chartjs() {
	if (window.Chart) return Promise.resolve();
	return new Promise((resolve, reject) => {
		const s = document.createElement("script");
		s.src = "https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js";
		s.onload = resolve;
		s.onerror = reject;
		document.head.appendChild(s);
	});
}

function destroy(wrapper) {
	(wrapper._ld_charts || []).forEach((c) => c.destroy());
	wrapper._ld_charts = [];
}

function make(wrapper, id, config) {
	const el = document.getElementById(id);
	if (!el) return;
	const chart = new Chart(el, config);
	wrapper._ld_charts.push(chart);
}

function colors(n) {
	const base = ["#1d4ed8", "#7c3aed", "#ea580c", "#16a34a", "#0f766e", "#dc2626", "#ca8a04", "#64748b"];
	return Array.from({ length: n }, (_, i) => base[i % base.length]);
}

function load(wrapper) {
	frappe.call({
		method: "leature_manufacturing.leature_manufacturing.utils.dashboard_data",
		callback(r) {
			const d = r.message || {};
			const k = d.kpis || {};
			$(wrapper).find(".ld-kpis").html(
				[
					kpi(__("Input kg"), fmt(k.input_kg)),
					kpi(__("Output kg"), fmt(k.output_kg)),
					kpi(__("Finished sq. ft."), fmt(k.output_area)),
					kpi(__("Avg yield %"), (k.avg_yield || 0).toFixed(1)),
					kpi(__("Available pieces"), k.available_pieces || 0),
					kpi(__("Open orders"), k.open_orders || 0),
				].join("")
			);
			if (!window.Chart) return;
			destroy(wrapper);
			const grades = d.grade_mix || [];
			make(wrapper, "ld-grade", {
				type: "doughnut",
				data: {
					labels: grades.map((g) => g.grade || __("Ungraded")),
					datasets: [{ data: grades.map((g) => g.area || 0), backgroundColor: colors(grades.length) }],
				},
				options: donutOpts(),
			});
			const proc = d.process_output || [];
			make(wrapper, "ld-process", {
				type: "bar",
				data: {
					labels: proc.map((p) => p.process),
					datasets: [
						{ label: __("Batches"), data: proc.map((p) => p.batches || 0), backgroundColor: "#1d4ed8" },
						{ label: __("Output kg"), data: proc.map((p) => p.output_kg || 0), backgroundColor: "#ea580c" },
					],
				},
				options: barOpts(),
			});
			make(wrapper, "ld-yield", {
				type: "bar",
				data: {
					labels: proc.map((p) => p.process),
					datasets: [
						{
							label: __("Output kg"),
							data: proc.map((p) => p.output_kg || 0),
							backgroundColor: "#0f766e",
						},
					],
				},
				options: barOpts(),
			});
			const stages = d.stages || [];
			make(wrapper, "ld-stages", {
				type: "bar",
				data: {
					labels: stages.map((s) => s.stage),
					datasets: [{ label: __("Weight kg"), data: stages.map((s) => s.weight_kg || 0), backgroundColor: "#7c3aed" }],
				},
				options: { ...barOpts(), indexAxis: "y" },
			});
			const chems = d.chemicals || [];
			make(wrapper, "ld-chem", {
				type: "bar",
				data: {
					labels: chems.map((c) => c.chemical),
					datasets: [
						{ label: __("Standard"), data: chems.map((c) => c.standard_qty || 0), backgroundColor: "#64748b" },
						{ label: __("Actual"), data: chems.map((c) => c.actual_qty || 0), backgroundColor: "#dc2626" },
					],
				},
				options: barOpts(),
			});
			const pieces = d.pieces || [];
			make(wrapper, "ld-pieces", {
				type: "pie",
				data: {
					labels: pieces.map((p) => p.status),
					datasets: [{ data: pieces.map((p) => p.area || p.pieces || 0), backgroundColor: colors(pieces.length) }],
				},
				options: donutOpts(),
			});
		},
	});
}

function fmt(n) {
	return (n || 0).toLocaleString(undefined, { maximumFractionDigits: 0 });
}

function donutOpts() {
	return { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: "bottom" } } };
}

function barOpts() {
	return {
		responsive: true,
		maintainAspectRatio: false,
		plugins: { legend: { position: "bottom" } },
		scales: { y: { beginAtZero: true } },
	};
}
