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
	const PALETTE = ["#c4a574", "#5c3d24", "#0f766e", "#b45309", "#1d4ed8", "#7c3aed", "#dc2626", "#64748b"];

	frappe.pages["leather-dashboard"].on_page_load = function (wrapper) {
		const page = frappe.ui.make_app_page({
			parent: wrapper,
			title: __("Factory Dashboard"),
			single_column: true,
		});
		inject_css();
		wrapper._ld_charts = [];
		$(wrapper).find(".layout-main-section").html(`
			<div class="leature-shell">
				<div class="leature-hero">
					<div>
						<div class="eyebrow">Leature Manufacturing</div>
						<h2>${__("Factory Control")}</h2>
						<div class="sub">${__("Raw hide → beamhouse → wet blue → dyeing → finished leather")}</div>
					</div>
					<div style="text-align:right">
						<div class="eyebrow">${__("Chart.js")}</div>
						<div style="font-size:18px;font-weight:700">${frappe.datetime.str_to_user(frappe.datetime.get_today())}</div>
					</div>
				</div>
				<div class="ld-kpis" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px"></div>
				<div class="ld-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:14px">
					${card(__("Finished grade mix"), __("Area by piece grade"), "ld-grade")}
					${card(__("Hide receiving grades"), __("Pieces after intake grading"), "ld-hide-grade")}
					${card(__("Process output"), __("Kg produced by operation"), "ld-process", true)}
					${card(__("Lot pipeline"), __("Weight sitting in each stage"), "ld-stages")}
					${card(__("Chemicals used"), __("Standard vs actual consumption"), "ld-chem")}
					${card(__("Piece availability"), __("Finished leather by status"), "ld-pieces")}
				</div>
			</div>
		`);
		page.set_primary_action(__("Refresh"), () => load(wrapper), "refresh");
		page.add_inner_button(__("ApexCharts view"), () => frappe.set_route("leather-apex-dashboard"));
		load_chartjs().then(() => load(wrapper));
	};

	function card(title, hint, id, wide) {
		return `<div class="ld-card${wide ? " wide" : ""}" ${wide ? 'style="grid-column:1/-1"' : ""}>
			<h4>${title}</h4>
			<div class="hint">${hint}</div>
			<div class="ld-canvas-wrap" style="height:280px;width:100%;position:relative"><canvas id="${id}"></canvas></div>
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
		const el = wrapper.querySelector("#" + id);
		if (!el || !window.Chart) return;
		const chart = new Chart(el, config);
		wrapper._ld_charts.push(chart);
	}

	function load(wrapper) {
		frappe.call({
			method: "leature_manufacturing.leature_manufacturing.utils.dashboard_data",
			callback(r) {
				const d = r.message || {};
				const k = d.kpis || {};
				$(wrapper).find(".ld-kpis").html(
					[
						kpi("📥", "#f4e8d4", __("Input"), fmt(k.input_kg) + " kg", __("Submitted batches")),
						kpi("📤", "#e7f3ef", __("Output"), fmt(k.output_kg) + " kg", __("Wet-end / finish")),
						kpi("📐", "#efe8fb", __("Finished"), fmt(k.output_area) + " ft²", __("Measured area")),
						kpi("📈", "#fde8d4", __("Yield"), (k.avg_yield || 0).toFixed(1) + "%", __("Weight yield")),
						kpi("🏷️", "#e8eefc", __("Pieces"), k.available_pieces || 0, __("Available now")),
						kpi("🧾", "#fce8e8", __("Orders"), k.open_orders || 0, __("Open sales")),
					].join("")
				);
				destroy(wrapper);
				const grades = nonempty(d.grade_mix, "grade", "area");
				make(wrapper, "ld-grade", doughnut(labels(grades, "grade"), values(grades, "area", "pieces")));
				const hides = nonempty(d.hide_grades, "grade", "pieces");
				make(wrapper, "ld-hide-grade", doughnut(labels(hides, "grade"), values(hides, "pieces")));
				const proc = d.process_output || [];
				make(wrapper, "ld-process", {
					type: "bar",
					data: {
						labels: proc.map((p) => p.process),
						datasets: [
							{ label: __("Batches"), data: proc.map((p) => p.batches || 0), backgroundColor: "#5c3d24", borderRadius: 8 },
							{ label: __("Output kg"), data: proc.map((p) => p.output_kg || 0), backgroundColor: "#c4a574", borderRadius: 8 },
						],
					},
					options: barOpts(),
				});
				const stages = d.stages || [];
				make(wrapper, "ld-stages", {
					type: "bar",
					data: {
						labels: stages.map((s) => s.stage),
						datasets: [{ label: __("Weight kg"), data: stages.map((s) => s.weight_kg || 0), backgroundColor: "#0f766e", borderRadius: 8 }],
					},
					options: { ...barOpts(), indexAxis: "y" },
				});
				const chems = d.chemicals || [];
				make(wrapper, "ld-chem", {
					type: "bar",
					data: {
						labels: chems.map((c) => short(c.chemical)),
						datasets: [
							{ label: __("Standard"), data: chems.map((c) => c.standard_qty || 0), backgroundColor: "#8d7b66", borderRadius: 8 },
							{ label: __("Actual"), data: chems.map((c) => c.actual_qty || 0), backgroundColor: "#b45309", borderRadius: 8 },
						],
					},
					options: barOpts(),
				});
				const pieces = nonempty(d.pieces, "status", "area");
				make(wrapper, "ld-pieces", doughnut(labels(pieces, "status"), values(pieces, "area", "pieces")));
			},
		});
	}

	function doughnut(labelList, valueList) {
		if (!labelList.length) {
			labelList = [__("No data")];
			valueList = [1];
		}
		return {
			type: "doughnut",
			data: {
				labels: labelList,
				datasets: [{ data: valueList, backgroundColor: PALETTE, borderWidth: 0, hoverOffset: 6 }],
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				cutout: "62%",
				plugins: { legend: { position: "bottom", labels: { boxWidth: 10, font: { size: 11 } } } },
			},
		};
	}

	function barOpts() {
		return {
			responsive: true,
			maintainAspectRatio: false,
			plugins: { legend: { position: "bottom", labels: { boxWidth: 10, font: { size: 11 } } } },
			scales: {
				x: { grid: { display: false }, ticks: { font: { size: 11 } } },
				y: { beginAtZero: true, grid: { color: "#f1e8dc" } },
			},
		};
	}

	function nonempty(rows, labelKey, valueKey) {
		return (rows || []).filter((r) => (r[valueKey] || 0) > 0 || r[labelKey]);
	}

	function labels(rows, key) {
		return rows.map((r) => r[key] || "—");
	}

	function values(rows, key, fallback) {
		return rows.map((r) => r[key] || (fallback ? r[fallback] : 0) || 0);
	}

	function short(v) {
		v = String(v || "");
		return v.length > 14 ? v.slice(0, 12) + "…" : v;
	}

	function fmt(n) {
		return (n || 0).toLocaleString(undefined, { maximumFractionDigits: 0 });
	}
})();
