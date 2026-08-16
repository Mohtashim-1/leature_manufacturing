frappe.pages["leather-apex-dashboard"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Leather Dashboard — ApexCharts"),
		single_column: true,
	});
	wrapper._apex = [];
	$(wrapper).find(".layout-main-section").html(`
		<div class="leature-dash">
			<div class="ld-kpis"></div>
			<div class="ld-grid">
				${card(__("Yield gauge"), "ap-yield")}
				${card(__("Grade mix"), "ap-grade")}
				${card(__("Standard vs actual cost"), "ap-cost")}
				${card(__("ETP COD / BOD / pH"), "ap-etp")}
				${card(__("Sales by customer"), "ap-sales")}
				${card(__("Waste by category"), "ap-waste")}
			</div>
		</div>
	`);
	page.set_primary_action(__("Refresh"), () => load(wrapper), "refresh");
	page.add_inner_button(__("Chart.js Dashboard"), () => frappe.set_route("leather-dashboard"));
	load_apex().then(() => load(wrapper));
};

function card(title, id) {
	return `<div class="ld-card"><h4>${title}</h4><div id="${id}" class="ld-apex"></div></div>`;
}

function kpi(label, value) {
	return `<div class="ld-kpi"><div class="ld-kpi-label">${label}</div><div class="ld-kpi-val">${value}</div></div>`;
}

function load_apex() {
	if (window.ApexCharts) return Promise.resolve();
	return new Promise((resolve, reject) => {
		const s = document.createElement("script");
		s.src = "https://cdn.jsdelivr.net/npm/apexcharts@3.54.1/dist/apexcharts.min.js";
		s.onload = resolve;
		s.onerror = reject;
		document.head.appendChild(s);
	});
}

function destroy(wrapper) {
	(wrapper._apex || []).forEach((c) => {
		try {
			c.destroy();
		} catch (e) {
			/* ignore */
		}
	});
	wrapper._apex = [];
}

function render(wrapper, el, options) {
	const node = document.querySelector("#" + el);
	if (!node) return;
	node.innerHTML = "";
	const chart = new ApexCharts(node, options);
	chart.render();
	wrapper._apex.push(chart);
}

function load(wrapper) {
	frappe.call({
		method: "leature_manufacturing.leature_manufacturing.utils.dashboard_data",
		callback(r) {
			const d = r.message || {};
			const k = d.kpis || {};
			$(wrapper).find(".ld-kpis").html(
				[
					kpi(__("Avg yield %"), (k.avg_yield || 0).toFixed(1)),
					kpi(__("Finished sq. ft."), (k.output_area || 0).toLocaleString()),
					kpi(__("Rejected qty"), k.rejected || 0),
					kpi(__("Wet blue lots"), k.wet_blue_lots || 0),
					kpi(__("Open complaints"), k.open_complaints || 0),
					kpi(__("Open orders"), k.open_orders || 0),
				].join("")
			);
			if (!window.ApexCharts) return;
			destroy(wrapper);
			const yieldPct = Math.min(100, Math.max(0, k.avg_yield || 0));
			render(wrapper, "ap-yield", {
				chart: { type: "radialBar", height: 280 },
				series: [Number(yieldPct.toFixed(1))],
				labels: [__("Weight yield")],
				colors: ["#1d4ed8"],
				plotOptions: {
					radialBar: {
						hollow: { size: "58%" },
						dataLabels: { value: { fontSize: "22px" } },
					},
				},
			});
			const grades = d.grade_mix || [];
			render(wrapper, "ap-grade", {
				chart: { type: "donut", height: 280 },
				labels: grades.map((g) => g.grade || __("Ungraded")),
				series: grades.map((g) => Number(g.area || 0)),
				colors: ["#1d4ed8", "#7c3aed", "#ea580c", "#16a34a", "#64748b"],
				legend: { position: "bottom" },
			});
			const costs = d.costs || [];
			render(wrapper, "ap-cost", {
				chart: { type: "bar", height: 280, stacked: false },
				series: [
					{ name: __("Standard"), data: costs.map((c) => Number(c.standard_amount || 0)) },
					{ name: __("Actual"), data: costs.map((c) => Number(c.actual_amount || 0)) },
				],
				xaxis: { categories: costs.map((c) => c.cost_head) },
				colors: ["#0f766e", "#ea580c"],
				dataLabels: { enabled: false },
				legend: { position: "bottom" },
			});
			const etp = d.etp || [];
			render(wrapper, "ap-etp", {
				chart: { type: "line", height: 280, toolbar: { show: false } },
				series: [
					{ name: "COD", data: etp.map((e) => Number(e.cod || 0)) },
					{ name: "BOD", data: etp.map((e) => Number(e.bod || 0)) },
					{ name: "pH", data: etp.map((e) => Number(e.ph || 0)) },
				],
				xaxis: { categories: etp.map((e) => e.log_date) },
				stroke: { curve: "smooth", width: 2 },
				colors: ["#dc2626", "#2563eb", "#16a34a"],
				legend: { position: "bottom" },
			});
			const sales = d.sales || [];
			render(wrapper, "ap-sales", {
				chart: { type: "bar", height: 280 },
				series: [{ name: __("Amount"), data: sales.map((s) => Number(s.amount || 0)) }],
				xaxis: { categories: sales.map((s) => s.customer) },
				colors: ["#16a34a"],
				dataLabels: { enabled: false },
			});
			const waste = d.waste || [];
			render(wrapper, "ap-waste", {
				chart: { type: "polarArea", height: 280 },
				labels: waste.map((w) => w.category),
				series: waste.map((w) => Number(w.qty || 0)),
				colors: ["#0f766e", "#ca8a04", "#dc2626", "#64748b"],
				legend: { position: "bottom" },
			});
		},
	});
}
