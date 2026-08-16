(function () {
	const CSS = `
.page-container[data-page-route="leather-dashboard"] .layout-main-section,
.page-container[data-page-route="leather-apex-dashboard"] .layout-main-section{background:#f4eee6!important;border:none!important;box-shadow:none!important;padding:12px 16px 48px!important}
.leature-shell{max-width:1520px;margin:0 auto;padding:0 4px 24px;font-family:Inter,"Noto Sans",sans-serif}
.leature-hero{background:linear-gradient(125deg,#1c140c 0%,#4a311c 48%,#c4a574 160%);color:#fff8ee;border-radius:22px;padding:22px 26px;margin-bottom:14px;display:flex!important;justify-content:space-between;align-items:flex-end;gap:16px;box-shadow:0 18px 40px rgba(28,20,12,.28)}
.leature-hero .eyebrow{font-size:11px;letter-spacing:.18em;text-transform:uppercase;opacity:.72;font-weight:600}
.leature-hero h2{margin:4px 0 0;font-size:26px;font-weight:800;color:#fff8ee!important}
.leature-hero .sub{margin-top:6px;font-size:13px;opacity:.82}
.ld-kpis{display:grid!important;grid-template-columns:repeat(auto-fit,minmax(160px,1fr))!important;gap:10px!important;margin-bottom:16px!important}
.ld-kpi{background:#fffdf9;border:1px solid #efe4d4;border-radius:16px;padding:12px;display:flex!important;gap:10px;align-items:center;min-height:78px}
.ld-kpi-icon{width:38px;height:38px;border-radius:11px;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0}
.ld-kpi-label{font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:#8d7b66;font-weight:700}
.ld-kpi-val{font-size:18px;font-weight:800;color:#24180f;line-height:1.15;margin-top:2px}
.ld-kpi-hint{font-size:11px;color:#a3917c;margin-top:2px}
.ld-section{margin:8px 0 10px;display:flex;align-items:baseline;justify-content:space-between}
.ld-section h3{margin:0;font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:#5c3d24;font-weight:800}
.ld-section span{font-size:12px;color:#9a8874}
.ld-grid{display:grid!important;grid-template-columns:repeat(auto-fit,minmax(380px,1fr))!important;gap:14px!important;margin-bottom:18px}
.ld-card{background:#fffdf9;border:1px solid #efe4d4;border-radius:18px;padding:14px 16px 10px;box-shadow:0 12px 28px rgba(42,28,16,.06)}
.ld-card.chart{min-height:340px}
.ld-card.wide{grid-column:1/-1!important}
.ld-card h4{margin:0 0 2px;font-size:14px;font-weight:800;color:#24180f}
.ld-card .hint{font-size:11px;color:#9a8874;margin-bottom:8px}
.ld-apex{height:280px!important;width:100%!important;position:relative}
.ld-alerts{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px}
.ld-alert{border-radius:999px;padding:6px 12px;font-size:12px;font-weight:600;cursor:pointer}
.ld-alert.bad{background:#fde8e8;color:#9f1239}
.ld-alert.warn{background:#fde8d4;color:#9a3412}
.ld-alert.ok{background:#e7f3ef;color:#115e59}
.ld-table-wrap{overflow:auto;max-height:420px}
.ld-table{width:100%;border-collapse:collapse;font-size:12px}
.ld-table th{text-align:left;font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:#8d7b66;padding:8px;border-bottom:1px solid #efe4d4;position:sticky;top:0;background:#fffdf9;white-space:nowrap}
.ld-table td{padding:8px;border-bottom:1px solid #f3ebe1;color:#24180f;white-space:nowrap}
.ld-table tr:hover td{background:#f8f1e7;cursor:pointer}
.ld-pill{display:inline-block;border-radius:999px;padding:2px 8px;font-size:11px;font-weight:700;background:#f4e8d4;color:#5c3d24}
.ld-pill.good{background:#d1fae5;color:#065f46}
.ld-pill.bad{background:#fee2e2;color:#991b1b}
.ld-pill.warn{background:#ffedd5;color:#9a3412}
.ld-empty{padding:28px;text-align:center;color:#9a8874;font-size:13px}
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
						<div class="sub">${__("Cost, yield, sales, export, waste, ETP and customer complaints")}</div>
					</div>
					<div style="text-align:right">
						<div class="eyebrow">${__("Finance & compliance")}</div>
						<div style="font-size:18px;font-weight:700">${frappe.datetime.str_to_user(frappe.datetime.get_today())}</div>
					</div>
				</div>
				<div class="ld-alerts"></div>
				<div class="ld-kpis"></div>
				<div class="ld-section"><h3>${__("Yield, cost and sales")}</h3><span>${__("Standard vs actual and customer mix")}</span></div>
				<div class="ld-grid">
					${chart_card(__("Weight yield"), __("Average on submitted batches"), "ap-yield")}
					${chart_card(__("Finished grade mix"), __("Square feet by piece grade"), "ap-grade")}
					${chart_card(__("Standard vs actual cost"), __("By cost head"), "ap-cost", true)}
					${chart_card(__("Sales by customer"), __("Order value"), "ap-sales")}
					${chart_card(__("Order pipeline"), __("Value by sales status"), "ap-sales-status")}
					${chart_card(__("Sales by article"), __("Amount on order lines"), "ap-articles")}
				</div>
				<div class="ld-section"><h3>${__("Procurement, waste & ETP")}</h3><span>${__("Hide spend, effluent and recovery")}</span></div>
				<div class="ld-grid">
					${chart_card(__("Hide purchases"), __("Landed cost by supplier"), "ap-po")}
					${chart_card(__("Waste stream"), __("Qty by category"), "ap-waste")}
					${chart_card(__("Waste by type"), __("Trimmings, shavings, sludge…"), "ap-waste-type")}
					${chart_card(__("ETP trend"), __("COD, BOD, chromium and pH"), "ap-etp", true)}
				</div>
				<div class="ld-section"><h3>${__("Live records")}</h3><span>${__("Click a row to open the document")}</span></div>
				<div class="ld-grid">
					${table_card(__("Sales orders"), __("Qty, value, export flag"), "ap-tbl-orders", true)}
					${table_card(__("Batch costing"), __("Standard, actual, cost / ft²"), "ap-tbl-cost")}
					${table_card(__("Export shipments"), __("Container / LC / status"), "ap-tbl-ship")}
					${table_card(__("Complaints & CAPA"), __("Open quality issues"), "ap-tbl-cmp")}
					${table_card(__("Waste records"), __("Qty and sale value"), "ap-tbl-waste")}
					${table_card(__("ETP daily logs"), __("Limits and metals"), "ap-tbl-etp")}
				</div>
			</div>
		`);
		page.set_primary_action(__("Refresh"), () => load(wrapper), "refresh");
		page.add_inner_button(__("Factory view"), () => frappe.set_route("leather-dashboard"));
		bind_table_clicks(wrapper);
		load_apex().then(() => load(wrapper));
	};

	function chart_card(title, hint, id, wide) {
		return `<div class="ld-card chart${wide ? " wide" : ""}" ${wide ? 'style="grid-column:1/-1"' : ""}>
			<h4>${title}</h4><div class="hint">${hint}</div>
			<div id="${id}" class="ld-apex" style="height:280px"></div>
		</div>`;
	}

	function table_card(title, hint, id, wide) {
		return `<div class="ld-card${wide ? " wide" : ""}" ${wide ? 'style="grid-column:1/-1"' : ""}>
			<h4>${title}</h4><div class="hint">${hint}</div>
			<div id="${id}"></div>
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
				render_alerts(wrapper, d.alerts || []);
				$(wrapper).find(".ld-kpis").html(
					[
						kpi("📈", "#fde8d4", __("Yield"), pct(k.avg_yield), __("Weight yield")),
						kpi("📐", "#efe8fb", __("Finished"), fmt(k.output_area) + " ft²", money(k.cost_per_sqft) + " / ft²"),
						kpi("💰", "#e7f3ef", __("Actual cost"), money(k.actual_cost), __("Std ") + money(k.standard_cost)),
						kpi("📉", "#fce8e8", __("Variance"), money(k.cost_variance), k.cost_variance > 0 ? __("Over standard") : __("Under standard")),
						kpi("🧾", "#e8eefc", __("Sales"), money(k.sales_amount), fmt(k.sales_qty) + " " + __("qty")),
						kpi("🌍", "#f4e8d4", __("Export"), money(k.export_amount), (k.export_orders || 0) + " " + __("orders")),
						kpi("🐄", "#e7f3ef", __("Hide spend"), money(k.landed_cost), (k.po_count || 0) + " " + __("POs")),
						kpi("♻️", "#efe8fb", __("Waste"), fmt(k.waste_qty), __("Sale ") + money(k.waste_sale)),
						kpi("📣", "#fde8d4", __("Complaints"), k.open_complaints || 0, __("Not closed")),
						kpi("⚠️", "#fce8e8", __("Rejected"), fmt(k.rejected), __("Process loss")),
						kpi("💧", "#e7f3ef", __("ETP alerts"), k.etp_out || 0, __("Out of limits")),
						kpi("🚢", "#e8eefc", __("Shipments"), k.shipments || 0, (k.open_orders || 0) + " " + __("open orders")),
					].join("")
				);
				destroy(wrapper);

				const yieldPct = Math.min(100, Math.max(0, n(k.avg_yield)));
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
				const grades = (d.grade_mix || []).filter((g) => n(g.area) || n(g.pieces));
				render(wrapper, "ap-grade", {
					chart: { type: "donut", height: 280 },
					labels: grades.length ? grades.map((g) => g.grade || "—") : [__("No data")],
					series: grades.length ? grades.map((g) => n(g.area) || n(g.pieces)) : [1],
					colors: ["#c4a574", "#5c3d24", "#0f766e", "#b45309", "#64748b"],
					legend: { position: "bottom" },
					stroke: { width: 0 },
					plotOptions: { pie: { donut: { size: "62%" } } },
				});
				const costs = d.costs || [];
				render(wrapper, "ap-cost", {
					chart: { type: "bar", height: 300 },
					series: [
						{ name: __("Standard"), data: costs.map((c) => n(c.standard_amount)) },
						{ name: __("Actual"), data: costs.map((c) => n(c.actual_amount)) },
					],
					xaxis: { categories: costs.map((c) => c.cost_head || "—") },
					colors: ["#8d7b66", "#b45309"],
					plotOptions: { bar: { borderRadius: 6, columnWidth: "46%" } },
					dataLabels: { enabled: false },
					grid: { borderColor: "#f1e8dc" },
					legend: { position: "top" },
				});
				const sales = d.sales || [];
				render(wrapper, "ap-sales", {
					chart: { type: "bar", height: 280 },
					series: [{ name: __("Amount"), data: sales.map((s) => n(s.amount)) }],
					xaxis: { categories: sales.map((s) => s.customer || "—") },
					colors: ["#0f766e"],
					plotOptions: { bar: { borderRadius: 8, columnWidth: "42%" } },
					dataLabels: { enabled: false },
					legend: { show: false },
					grid: { borderColor: "#f1e8dc" },
				});
				const sst = d.sales_status || [];
				render(wrapper, "ap-sales-status", {
					chart: { type: "donut", height: 280 },
					labels: sst.length ? sst.map((s) => s.status || "—") : [__("No data")],
					series: sst.length ? sst.map((s) => n(s.amount) || n(s.orders)) : [1],
					colors: ["#c4a574", "#5c3d24", "#0f766e", "#1d4ed8", "#b45309", "#64748b"],
					legend: { position: "bottom" },
					stroke: { width: 0 },
				});
				const arts = d.sales_articles || [];
				render(wrapper, "ap-articles", {
					chart: { type: "bar", height: 280 },
					series: [{ name: __("Amount"), data: arts.map((a) => n(a.amount)) }],
					xaxis: { categories: arts.map((a) => a.article || "—") },
					colors: ["#7c3aed"],
					plotOptions: { bar: { borderRadius: 8, columnWidth: "42%" } },
					dataLabels: { enabled: false },
					legend: { show: false },
					grid: { borderColor: "#f1e8dc" },
				});
				const pos = d.purchases || [];
				render(wrapper, "ap-po", {
					chart: { type: "bar", height: 280 },
					series: [
						{ name: __("Hide amount"), data: pos.map((p) => n(p.hide_amount)) },
						{ name: __("Landed cost"), data: pos.map((p) => n(p.landed_cost)) },
					],
					xaxis: { categories: pos.map((p) => p.supplier || "—") },
					colors: ["#8d7b66", "#0f766e"],
					plotOptions: { bar: { borderRadius: 6 } },
					dataLabels: { enabled: false },
					legend: { position: "top" },
					grid: { borderColor: "#f1e8dc" },
				});
				const waste = (d.waste || []).filter((w) => n(w.qty));
				render(wrapper, "ap-waste", {
					chart: { type: "polarArea", height: 280 },
					labels: waste.length ? waste.map((w) => w.category) : [__("No data")],
					series: waste.length ? waste.map((w) => n(w.qty)) : [1],
					colors: ["#0f766e", "#c4a574", "#dc2626", "#5c3d24"],
					legend: { position: "bottom" },
					stroke: { width: 0 },
					yaxis: { show: false },
				});
				const wtypes = d.waste_types || [];
				render(wrapper, "ap-waste-type", {
					chart: { type: "bar", height: 280 },
					series: [{ name: __("Qty"), data: wtypes.map((w) => n(w.qty)) }],
					xaxis: { categories: wtypes.map((w) => w.waste_type || "—") },
					colors: ["#b45309"],
					plotOptions: { bar: { borderRadius: 8, columnWidth: "42%" } },
					dataLabels: { enabled: false },
					legend: { show: false },
					grid: { borderColor: "#f1e8dc" },
				});
				const etp = d.etp || [];
				render(wrapper, "ap-etp", {
					chart: { type: "line", height: 320 },
					series: [
						{ name: "COD", data: etp.map((e) => n(e.cod)) },
						{ name: "BOD", data: etp.map((e) => n(e.bod)) },
						{ name: "Chromium × 50", data: etp.map((e) => n(e.chromium) * 50) },
						{ name: "pH × 20", data: etp.map((e) => n(e.ph) * 20) },
						{ name: __("Wastewater"), data: etp.map((e) => n(e.wastewater_qty)) },
					],
					xaxis: { categories: etp.map((e) => date(e.log_date)) },
					stroke: { curve: "smooth", width: 2 },
					colors: ["#dc2626", "#1d4ed8", "#7c3aed", "#0f766e", "#b45309"],
					legend: { position: "top" },
					grid: { borderColor: "#f1e8dc" },
					dataLabels: { enabled: false },
				});

				set_table(wrapper, "ap-tbl-orders", d.recent_orders, "Leather Sales Order", [
					{ label: __("Order"), key: "name" },
					{ label: __("Date"), render: (row) => date(row.transaction_date) },
					{ label: __("Customer"), key: "customer" },
					{ label: __("Status"), render: (row) => pill(row.status) },
					{ label: __("Export"), render: (row) => (cint(row.is_export) ? __("Yes") : __("No")) },
					{ label: __("Qty"), render: (row) => fmt(row.total_qty) },
					{ label: __("Amount"), render: (row) => money(row.grand_total) },
					{ label: __("Delivery"), render: (row) => date(row.delivery_date) },
				]);
				set_table(wrapper, "ap-tbl-cost", d.recent_costing, "Leather Batch Costing", [
					{ label: __("Costing"), key: "name" },
					{ label: __("Date"), render: (row) => date(row.costing_date) },
					{ label: __("Lot"), key: "lot" },
					{ label: __("Area"), render: (row) => fmt(row.finished_area_sqft) },
					{ label: __("Standard"), render: (row) => money(row.total_standard) },
					{ label: __("Actual"), render: (row) => money(row.total_actual) },
					{ label: __("/ ft²"), render: (row) => money(row.cost_per_sqft) },
				]);
				set_table(wrapper, "ap-tbl-ship", d.recent_shipments, "Leather Export Shipment", [
					{ label: __("Shipment"), key: "name" },
					{ label: __("Date"), render: (row) => date(row.shipment_date) },
					{ label: __("Customer"), key: "customer" },
					{ label: __("Status"), render: (row) => pill(row.status) },
					{ label: __("Container"), key: "container_no" },
					{ label: __("LC"), key: "lc_number" },
					{ label: __("SO"), key: "sales_order" },
				]);
				set_table(wrapper, "ap-tbl-cmp", d.recent_complaints, "Leather Complaint", [
					{ label: __("Complaint"), key: "name" },
					{ label: __("Date"), render: (row) => date(row.complaint_date) },
					{ label: __("Customer"), key: "customer" },
					{ label: __("Type"), key: "complaint_type" },
					{ label: __("Status"), render: (row) => pill(row.status) },
					{ label: __("Lot"), key: "lot" },
				]);
				set_table(wrapper, "ap-tbl-waste", d.recent_waste, "Waste Record", [
					{ label: __("Waste"), key: "name" },
					{ label: __("Date"), render: (row) => date(row.posting_date) },
					{ label: __("Type"), key: "waste_type" },
					{ label: __("Category"), render: (row) => pill(row.category) },
					{ label: __("Qty"), render: (row) => fmt(row.qty) + " " + esc(row.uom || "") },
					{ label: __("Sale"), render: (row) => money(row.sale_value) },
					{ label: __("Lot"), key: "source_lot" },
				]);
				set_table(wrapper, "ap-tbl-etp", d.recent_etp, "ETP Daily Log", [
					{ label: __("Log"), key: "name" },
					{ label: __("Date"), render: (row) => date(row.log_date) },
					{ label: __("WW"), render: (row) => fmt(row.wastewater_qty) },
					{ label: "pH", render: (row) => n(row.ph).toFixed(2) },
					{ label: "COD", render: (row) => fmt(row.cod) },
					{ label: "BOD", render: (row) => fmt(row.bod) },
					{ label: "Cr", render: (row) => n(row.chromium).toFixed(2) },
					{ label: __("Limits"), render: (row) => pill(cint(row.within_limits) ? __("OK") : __("Breach")) },
				]);
			},
		});
	}

	function render_alerts(wrapper, alerts) {
		const box = $(wrapper).find(".ld-alerts");
		if (!alerts.length) {
			box.html(`<div class="ld-alert ok">${__("No open QC fails, ETP breaches or low-yield batches")}</div>`);
			return;
		}
		box.html(
			alerts
				.slice(0, 8)
				.map(
					(a) =>
						`<div class="ld-alert ${a.tone || "warn"}" data-dt="${esc(a.doctype)}" data-name="${esc(a.name)}">${esc(a.text)}</div>`
				)
				.join("")
		);
		box.find(".ld-alert").on("click", function () {
			const dt = this.getAttribute("data-dt");
			const name = this.getAttribute("data-name");
			if (dt && name) frappe.set_route("Form", dt, name);
		});
	}

	function set_table(wrapper, id, rows, doctype, cols) {
		const el = wrapper.querySelector("#" + id);
		if (!el) return;
		if (!rows || !rows.length) {
			el.innerHTML = `<div class="ld-empty">${__("No records")}</div>`;
			return;
		}
		const head = cols.map((c) => `<th>${c.label}</th>`).join("");
		const body = rows
			.map((row) => {
				const tds = cols.map((c) => `<td>${c.render ? c.render(row) : esc(row[c.key])}</td>`).join("");
				return `<tr data-dt="${doctype}" data-name="${esc(row.name)}">${tds}</tr>`;
			})
			.join("");
		el.innerHTML = `<div class="ld-table-wrap"><table class="ld-table"><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
	}

	function bind_table_clicks(wrapper) {
		$(wrapper).on("click", ".ld-table tbody tr", function () {
			const dt = this.getAttribute("data-dt");
			const name = this.getAttribute("data-name");
			if (dt && name) frappe.set_route("Form", dt, name);
		});
	}

	function pill(v) {
		const s = String(v || "—");
		let cls = "";
		if (/pass|ok|available|completed|closed|confirmed|shipped|saleable|reusable/i.test(s)) cls = "good";
		else if (/fail|reject|open|breach|hazardous|cancelled/i.test(s)) cls = "bad";
		else if (/pending|progress|draft|hold|capa|investigat/i.test(s)) cls = "warn";
		return `<span class="ld-pill ${cls}">${esc(s)}</span>`;
	}

	function n(v) {
		return Number(v || 0);
	}
	function cint(v) {
		return v === true || v === 1 || v === "1";
	}
	function fmt(v) {
		return n(v).toLocaleString(undefined, { maximumFractionDigits: 0 });
	}
	function money(v) {
		return n(v).toLocaleString(undefined, { maximumFractionDigits: 0 });
	}
	function pct(v) {
		return n(v).toFixed(1) + "%";
	}
	function date(v) {
		if (!v) return "—";
		try {
			return frappe.datetime.str_to_user(v);
		} catch (e) {
			return String(v);
		}
	}
	function esc(v) {
		return frappe.utils.escape_html(String(v == null ? "" : v));
	}
})();
