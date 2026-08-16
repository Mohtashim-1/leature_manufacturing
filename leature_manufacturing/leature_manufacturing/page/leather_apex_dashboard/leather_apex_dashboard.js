(function () {
	const CSS = `
.page-container[data-page-route="leather-dashboard"] .layout-main-section,
.page-container[data-page-route="leather-apex-dashboard"] .layout-main-section{
	background:#f4eee6!important;border:none!important;box-shadow:none!important;padding:12px 16px 36px!important}
.leature-shell{max-width:1360px;margin:0 auto;padding:0 4px 24px;font-family:Inter,"Noto Sans",sans-serif}
.leature-hero{background:linear-gradient(125deg,#1c140c 0%,#4a311c 48%,#c4a574 160%);color:#fff8ee;border-radius:22px;padding:22px 26px;margin-bottom:16px;display:flex!important;justify-content:space-between;align-items:flex-end;gap:16px;box-shadow:0 18px 40px rgba(28,20,12,.28)}
.leature-hero .eyebrow{font-size:11px;letter-spacing:.18em;text-transform:uppercase;opacity:.72;font-weight:600}
.leature-hero h2{margin:4px 0 0;font-size:26px;font-weight:800;letter-spacing:-.03em;color:#fff8ee!important}
.leature-hero .sub{margin-top:6px;font-size:13px;opacity:.82}
.ld-kpis{display:grid!important;grid-template-columns:repeat(auto-fit,minmax(170px,1fr))!important;gap:12px!important;margin-bottom:14px!important}
.ld-kpi{background:#fffdf9;border:1px solid #efe4d4;border-radius:16px;padding:14px 12px;box-shadow:0 10px 24px rgba(42,28,16,.05);display:flex!important;gap:10px;align-items:center;min-height:88px}
.ld-kpi-icon{width:42px;height:42px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0}
.ld-kpi-label{font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:#8d7b66;font-weight:700}
.ld-kpi-val{font-size:22px;font-weight:800;color:#24180f;line-height:1.15;margin-top:2px}
.ld-kpi-hint{font-size:11px;color:#a3917c;margin-top:2px}
.ld-grid{display:grid!important;grid-template-columns:repeat(auto-fit,minmax(420px,1fr))!important;gap:14px!important}
.ld-card{background:#fffdf9;border:1px solid #efe4d4;border-radius:18px;padding:14px 16px 10px;box-shadow:0 12px 28px rgba(42,28,16,.06);min-height:340px}
.ld-card.wide{grid-column:1/-1!important}
.ld-card h4{margin:0 0 2px;font-size:14px;font-weight:800;color:#24180f}
.ld-card .hint{font-size:11px;color:#9a8874;margin-bottom:8px}
.ld-canvas-wrap,.ld-apex{height:280px!important;width:100%!important;position:relative}
@media (max-width:720px){.ld-kpis,.ld-grid{grid-template-columns:1fr!important}.leature-hero{flex-direction:column;align-items:flex-start}}
`;

	frappe.pages["leather-apex-dashboard"].on_page_load = function (wrapper) {
		const page = frappe.ui.make_app_page({
			parent: wrapper,
			title: __("Executive Dashboard"),
			single_column: true,
		});
		inject_css();
		wrapper._apex = [];
		$(wrapper).find(".layout-main-section").html(`
			<div class="leature-shell">
				<div class="leature-hero">
					<div>
						<div class="eyebrow">Leature Manufacturing</div>
						<h2>${__("Executive Control")}</h2>
						<div class="sub">${__("Yield, cost, sales, waste and ETP in one view")}</div>
					</div>
					<div style="text-align:right">
						<div class="eyebrow">${__("ApexCharts")}</div>
						<div style="font-size:18px;font-weight:700">${frappe.datetime.str_to_user(frappe.datetime.get_today())}</div>
					</div>
				</div>
				<div class="ld-kpis" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px"></div>
				<div class="ld-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:14px">
					${card(__("Weight yield"), __("Average across submitted batches"), "ap-yield")}
					${card(__("Finished grade mix"), __("Square feet by piece grade"), "ap-grade")}
					${card(__("Standard vs actual cost"), __("Batch costing heads"), "ap-cost", true)}
					${card(__("ETP trend"), __("COD, BOD and pH"), "ap-etp", true)}
					${card(__("Sales by customer"), __("Open / confirmed orders"), "ap-sales")}
					${card(__("Waste stream"), __("By disposal category"), "ap-waste")}
				</div>
			</div>
		`);
		page.set_primary_action(__("Refresh"), () => load(wrapper), "refresh");
		page.add_inner_button(__("Chart.js view"), () => frappe.set_route("leather-dashboard"));
		load_apex().then(() => load(wrapper));
	};

	function card(title, hint, id, wide) {
		return `<div class="ld-card${wide ? " wide" : ""}" ${wide ? 'style="grid-column:1/-1"' : ""}>
			<h4>${title}</h4>
			<div class="hint">${hint}</div>
			<div id="${id}" class="ld-apex" style="height:280px;width:100%"></div>
		</div>`;
	}

	function kpi(icon, bg, label, value, hint) {
		return `<div class="ld-kpi">
			<div class="ld-kpi-icon" style="background:${bg}">${icon}</div>
			<div>
				<div class="ld-kpi-label">${label}</div>
				<div class="ld-kpi-val">${value}</div>
				<div class="ld-kpi-hint">${hint || ""}</div>
			</div>
		</div>`;
	}

	function inject_css() {
		if (!document.getElementById("leature-dash-inline")) {
			const style = document.createElement("style");
			style.id = "leature-dash-inline";
			style.textContent = CSS;
			document.head.appendChild(style);
		}
		if (!document.getElementById("leature-dash-css")) {
			const el = document.createElement("link");
			el.id = "leature-dash-css";
			el.rel = "stylesheet";
			el.href = "/assets/leature_manufacturing/css/leature_dash.css";
			document.head.appendChild(el);
		}
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
		const node = wrapper.querySelector("#" + el);
		if (!node || !window.ApexCharts) return;
		node.innerHTML = "";
		const chart = new ApexCharts(node, {
			...options,
			chart: { ...(options.chart || {}), fontFamily: "Inter, Noto Sans, sans-serif", toolbar: { show: false } },
		});
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
						kpi("📈", "#fde8d4", __("Yield"), (k.avg_yield || 0).toFixed(1) + "%", __("Weight yield")),
						kpi("📐", "#efe8fb", __("Finished"), fmt(k.output_area) + " ft²", __("From production")),
						kpi("⚠️", "#fce8e8", __("Rejected"), fmt(k.rejected), __("Process loss")),
						kpi("💧", "#e7f3ef", __("Wet blue"), k.wet_blue_lots || 0, __("Lots in stock")),
						kpi("📣", "#fde8d4", __("Complaints"), k.open_complaints || 0, __("Open CAPA")),
						kpi("🧾", "#e8eefc", __("Orders"), k.open_orders || 0, __("Not closed")),
					].join("")
				);
				destroy(wrapper);
				const yieldPct = Math.min(100, Math.max(0, k.avg_yield || 0));
				render(wrapper, "ap-yield", {
					chart: { type: "radialBar", height: 280 },
					series: [Number(yieldPct.toFixed(1))],
					labels: [__("Yield")],
					colors: ["#b45309"],
					plotOptions: {
						radialBar: {
							hollow: { size: "64%" },
							track: { background: "#f4e8d4" },
							dataLabels: {
								name: { fontSize: "13px", color: "#8d7b66", offsetY: 18 },
								value: { fontSize: "28px", fontWeight: 800, color: "#24180f", offsetY: -12 },
							},
						},
					},
				});
				const grades = (d.grade_mix || []).filter((g) => (g.area || g.pieces || 0) > 0);
				render(wrapper, "ap-grade", {
					chart: { type: "donut", height: 280 },
					labels: grades.length ? grades.map((g) => g.grade || "—") : [__("No data")],
					series: grades.length ? grades.map((g) => Number(g.area || g.pieces || 0)) : [1],
					colors: ["#c4a574", "#5c3d24", "#0f766e", "#b45309", "#64748b"],
					legend: { position: "bottom" },
					stroke: { width: 0 },
					plotOptions: { pie: { donut: { size: "62%" } } },
					dataLabels: { enabled: true },
				});
				const costs = d.costs || [];
				render(wrapper, "ap-cost", {
					chart: { type: "bar", height: 300 },
					series: [
						{ name: __("Standard"), data: costs.map((c) => Number(c.standard_amount || 0)) },
						{ name: __("Actual"), data: costs.map((c) => Number(c.actual_amount || 0)) },
					],
					xaxis: { categories: costs.map((c) => c.cost_head || "—") },
					colors: ["#8d7b66", "#b45309"],
					plotOptions: { bar: { borderRadius: 6, columnWidth: "46%" } },
					dataLabels: { enabled: false },
					grid: { borderColor: "#f1e8dc" },
					legend: { position: "top" },
				});
				const etp = d.etp || [];
				render(wrapper, "ap-etp", {
					chart: { type: "area", height: 300 },
					series: [
						{ name: "COD", data: etp.map((e) => Number(e.cod || 0)) },
						{ name: "BOD", data: etp.map((e) => Number(e.bod || 0)) },
						{ name: "pH × 20", data: etp.map((e) => Number((e.ph || 0) * 20)) },
					],
					xaxis: { categories: etp.map((e) => format_date(e.log_date)) },
					stroke: { curve: "smooth", width: 2 },
					fill: { type: "gradient", gradient: { opacityFrom: 0.35, opacityTo: 0.02 } },
					colors: ["#dc2626", "#1d4ed8", "#0f766e"],
					legend: { position: "top" },
					grid: { borderColor: "#f1e8dc" },
					dataLabels: { enabled: false },
				});
				const sales = d.sales || [];
				render(wrapper, "ap-sales", {
					chart: { type: "bar", height: 280 },
					series: [{ name: __("Amount"), data: sales.map((s) => Number(s.amount || 0)) }],
					xaxis: { categories: sales.map((s) => s.customer || "—") },
					colors: ["#0f766e"],
					plotOptions: { bar: { borderRadius: 8, columnWidth: "40%", distributed: true } },
					dataLabels: { enabled: false },
					legend: { show: false },
					grid: { borderColor: "#f1e8dc" },
				});
				const waste = (d.waste || []).filter((w) => (w.qty || 0) > 0);
				render(wrapper, "ap-waste", {
					chart: { type: "polarArea", height: 280 },
					labels: waste.length ? waste.map((w) => w.category) : [__("No data")],
					series: waste.length ? waste.map((w) => Number(w.qty || 0)) : [1],
					colors: ["#0f766e", "#c4a574", "#dc2626", "#5c3d24"],
					legend: { position: "bottom" },
					stroke: { width: 0 },
					yaxis: { show: false },
				});
			},
		});
	}

	function format_date(v) {
		if (!v) return "";
		try {
			return frappe.datetime.str_to_user(v);
		} catch (e) {
			return String(v);
		}
	}

	function fmt(n) {
		return (n || 0).toLocaleString(undefined, { maximumFractionDigits: 0 });
	}
})();
