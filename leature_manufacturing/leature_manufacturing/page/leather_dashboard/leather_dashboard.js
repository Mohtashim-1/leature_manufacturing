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
.ld-canvas-wrap{height:280px!important;width:100%!important;position:relative}
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
	const PALETTE = ["#c4a574", "#5c3d24", "#0f766e", "#b45309", "#1d4ed8", "#7c3aed", "#dc2626", "#64748b", "#0ea5e9", "#a16207"];

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
						<h2>${__("Factory Floor")}</h2>
						<div class="sub">${__("Lots, drums, yield, chemicals, QC and piece stock — live from the tannery")}</div>
					</div>
					<div style="text-align:right">
						<div class="eyebrow">${__("Operations")}</div>
						<div style="font-size:18px;font-weight:700">${frappe.datetime.str_to_user(frappe.datetime.get_today())}</div>
					</div>
				</div>
				<div class="ld-alerts"></div>
				<div class="ld-kpis"></div>
				<div class="ld-section"><h3>${__("Pipeline & process")}</h3><span>${__("Where hide sits and what the drums produced")}</span></div>
				<div class="ld-grid">
					${chart_card(__("Lot pipeline"), __("Weight and pieces by stage"), "ld-stages")}
					${chart_card(__("Yield by process date"), __("Average weight yield %"), "ld-yield")}
					${chart_card(__("Process output"), __("Kg + rejected qty by operation"), "ld-process", true)}
					${chart_card(__("Shift output"), __("Batches and kg by shift"), "ld-shift")}
					${chart_card(__("Drum utilisation"), __("Batches run per drum"), "ld-drum")}
					${chart_card(__("Animal mix in lots"), __("Weight by hide type"), "ld-animal")}
				</div>
				<div class="ld-section"><h3>${__("Grading & finished stock")}</h3><span>${__("Piece-level grade, article, colour and QC")}</span></div>
				<div class="ld-grid">
					${chart_card(__("Finished grade mix"), __("Area by piece grade"), "ld-grade")}
					${chart_card(__("Hide receiving grades"), __("Pieces after intake"), "ld-hide-grade")}
					${chart_card(__("Piece availability"), __("Finished leather by status"), "ld-pieces")}
					${chart_card(__("Piece QC status"), __("Pending / pass / fail / hold"), "ld-piece-qc")}
					${chart_card(__("Stock by article"), __("Available + allocated area"), "ld-article")}
					${chart_card(__("Stock by colour"), __("Area by colour"), "ld-color")}
				</div>
				<div class="ld-section"><h3>${__("Chemicals & QC")}</h3><span>${__("Recipe vs actual and inspection results")}</span></div>
				<div class="ld-grid">
					${chart_card(__("Chemical consumption"), __("Standard vs actual qty"), "ld-chem", true)}
					${chart_card(__("Chemical spend"), __("Amount by chemical"), "ld-chem-amt")}
					${chart_card(__("QC inspections"), __("Pass / fail / pending"), "ld-qc")}
					${chart_card(__("QC by leather stage"), __("Inspections and fails"), "ld-qc-type")}
				</div>
				<div class="ld-section"><h3>${__("Live records")}</h3><span>${__("Click a row to open the document")}</span></div>
				<div class="ld-grid">
					${table_card(__("Lots in the tannery"), __("Latest 12 lots"), "ld-tbl-lots", true)}
					${table_card(__("Recent production batches"), __("Input, output, yield, reject"), "ld-tbl-batches", true)}
					${table_card(__("QC inspections"), __("Holes, scars and overall result"), "ld-tbl-qc")}
					${table_card(__("Hide purchase orders"), __("Landed cost by supplier"), "ld-tbl-po")}
				</div>
			</div>
		`);
		page.set_primary_action(__("Refresh"), () => load(wrapper), "refresh");
		page.add_inner_button(__("Executive view"), () => frappe.set_route("leather-apex-dashboard"));
		bind_table_clicks(wrapper);
		load_chartjs().then(() => load(wrapper));
	};

	function chart_card(title, hint, id, wide) {
		return `<div class="ld-card chart${wide ? " wide" : ""}" ${wide ? 'style="grid-column:1/-1"' : ""}>
			<h4>${title}</h4><div class="hint">${hint}</div>
			<div class="ld-canvas-wrap" style="height:280px"><canvas id="${id}"></canvas></div>
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
		wrapper._ld_charts.push(new Chart(el, config));
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
						kpi("📥", "#f4e8d4", __("Input"), fmt(k.input_kg) + " kg", __("Submitted batches")),
						kpi("📤", "#e7f3ef", __("Output"), fmt(k.output_kg) + " kg", __("Wet-end / finish")),
						kpi("📐", "#efe8fb", __("Finished area"), fmt(k.output_area) + " ft²", __("From production")),
						kpi("📈", "#fde8d4", __("Yield"), pct(k.avg_yield), __("Weight yield")),
						kpi("⚠️", "#fce8e8", __("Rejected"), fmt(k.rejected), __("Process loss ") + fmt(k.production_loss)),
						kpi("🏷️", "#e8eefc", __("Available"), (k.available_pieces || 0) + " pcs", fmt(k.available_area) + " ft²"),
						kpi("📦", "#f4e8d4", __("Lots"), k.total_lots || 0, `${k.raw_lots || 0} raw · ${k.wet_blue_lots || 0} wet blue`),
						kpi("🧪", "#e7f3ef", __("QC fail"), k.qc_fail || 0, `${k.qc_pass || 0} pass · ${k.qc_pending || 0} pending`),
						kpi("💧", "#efe8fb", __("Water"), fmt(k.water_qty), __("Process water")),
						kpi("🧴", "#fde8d4", __("Chemicals"), money(k.chem_amount), fmt(k.chem_qty) + " qty used"),
						kpi("🧾", "#e8eefc", __("Open POs"), k.open_pos || 0, money(k.landed_cost) + " landed"),
						kpi("🛠️", "#fce8e8", __("Maintenance"), k.open_maintenance || 0, __("Open jobs")),
					].join("")
				);
				destroy(wrapper);

				const stages = d.stages || [];
				make(wrapper, "ld-stages", {
					type: "bar",
					data: {
						labels: stages.map((s) => s.stage),
						datasets: [
							{ label: __("Weight kg"), data: stages.map((s) => n(s.weight_kg)), backgroundColor: "#0f766e", borderRadius: 8 },
							{ label: __("Pieces"), data: stages.map((s) => n(s.pieces)), backgroundColor: "#c4a574", borderRadius: 8 },
						],
					},
					options: { ...barOpts(), indexAxis: "y" },
				});

				const ytrend = avg_by_date(d.yield_trend || []);
				make(wrapper, "ld-yield", {
					type: "line",
					data: {
						labels: ytrend.map((x) => date(x.date)),
						datasets: [
							{
								label: __("Yield %"),
								data: ytrend.map((x) => x.yield),
								borderColor: "#b45309",
								backgroundColor: "rgba(180,83,9,.12)",
								fill: true,
								tension: 0.35,
								pointRadius: 3,
							},
						],
					},
					options: lineOpts(),
				});

				const proc = d.process_output || [];
				make(wrapper, "ld-process", {
					type: "bar",
					data: {
						labels: proc.map((p) => p.process),
						datasets: [
							{ label: __("Output kg"), data: proc.map((p) => n(p.output_kg)), backgroundColor: "#5c3d24", borderRadius: 8 },
							{ label: __("Rejected"), data: proc.map((p) => n(p.rejected)), backgroundColor: "#dc2626", borderRadius: 8 },
							{ label: __("Avg yield %"), data: proc.map((p) => n(p.avg_yield)), backgroundColor: "#c4a574", borderRadius: 8 },
						],
					},
					options: barOpts(),
				});

				const shifts = d.shifts || [];
				make(wrapper, "ld-shift", doughnut(shifts.map((s) => s.shift), shifts.map((s) => n(s.output_kg))));
				const drums = d.drums || [];
				make(wrapper, "ld-drum", {
					type: "bar",
					data: {
						labels: drums.map((x) => x.drum),
						datasets: [{ label: __("Batches"), data: drums.map((x) => n(x.batches)), backgroundColor: "#1d4ed8", borderRadius: 8 }],
					},
					options: barOpts(),
				});
				const animals = d.lots_animal || [];
				make(wrapper, "ld-animal", doughnut(animals.map((a) => a.animal_type), animals.map((a) => n(a.weight_kg))));

				const grades = d.grade_mix || [];
				make(wrapper, "ld-grade", doughnut(grades.map((g) => g.grade || "—"), grades.map((g) => n(g.area) || n(g.pieces))));
				const hides = d.hide_grades || [];
				make(wrapper, "ld-hide-grade", doughnut(hides.map((g) => g.grade || "—"), hides.map((g) => n(g.pieces))));
				const pieces = d.pieces || [];
				make(wrapper, "ld-pieces", doughnut(pieces.map((p) => p.status), pieces.map((p) => n(p.area) || n(p.pieces))));
				const pqc = d.piece_qc || [];
				make(wrapper, "ld-piece-qc", doughnut(pqc.map((p) => p.qc_status || "—"), pqc.map((p) => n(p.pieces))));
				const arts = d.piece_articles || [];
				make(wrapper, "ld-article", {
					type: "bar",
					data: {
						labels: arts.map((a) => short(a.article)),
						datasets: [{ label: __("Area ft²"), data: arts.map((a) => n(a.area)), backgroundColor: "#7c3aed", borderRadius: 8 }],
					},
					options: barOpts(),
				});
				const colors = d.piece_colors || [];
				make(wrapper, "ld-color", doughnut(colors.map((c) => c.color), colors.map((c) => n(c.area))));

				const chems = d.chemicals || [];
				make(wrapper, "ld-chem", {
					type: "bar",
					data: {
						labels: chems.map((c) => short(c.chemical)),
						datasets: [
							{ label: __("Standard"), data: chems.map((c) => n(c.standard_qty)), backgroundColor: "#8d7b66", borderRadius: 8 },
							{ label: __("Actual"), data: chems.map((c) => n(c.actual_qty)), backgroundColor: "#b45309", borderRadius: 8 },
						],
					},
					options: barOpts(),
				});
				make(wrapper, "ld-chem-amt", {
					type: "bar",
					data: {
						labels: chems.map((c) => short(c.chemical)),
						datasets: [{ label: __("Amount"), data: chems.map((c) => n(c.amount)), backgroundColor: "#0f766e", borderRadius: 8 }],
					},
					options: barOpts(),
				});
				const qc = d.qc_results || [];
				make(wrapper, "ld-qc", doughnut(qc.map((x) => x.result || "—"), qc.map((x) => n(x.inspections))));
				const qct = d.qc_types || [];
				make(wrapper, "ld-qc-type", {
					type: "bar",
					data: {
						labels: qct.map((x) => x.inspection_type),
						datasets: [
							{ label: __("Inspections"), data: qct.map((x) => n(x.inspections)), backgroundColor: "#5c3d24", borderRadius: 8 },
							{ label: __("Failed"), data: qct.map((x) => n(x.failed)), backgroundColor: "#dc2626", borderRadius: 8 },
						],
					},
					options: barOpts(),
				});

				set_table(wrapper, "ld-tbl-lots", d.recent_lots, "Leather Lot", [
					{ label: __("Lot"), key: "name" },
					{ label: __("Date"), render: (r) => date(r.posting_date) },
					{ label: __("Stage"), key: "lot_stage" },
					{ label: __("Status"), render: (r) => pill(r.status) },
					{ label: __("Animal"), key: "animal_type" },
					{ label: __("Article"), key: "article" },
					{ label: __("Color"), key: "color" },
					{ label: __("Grade"), key: "grade" },
					{ label: __("Pcs"), render: (r) => fmt(r.pieces) },
					{ label: __("Kg"), render: (r) => fmt(r.weight_kg) },
					{ label: __("ft²"), render: (r) => fmt(r.area_sqft) },
				]);
				set_table(wrapper, "ld-tbl-batches", d.recent_batches, "Leather Production Batch", [
					{ label: __("Batch"), key: "name" },
					{ label: __("Date"), render: (r) => date(r.posting_date) },
					{ label: __("Process"), key: "process_stage" },
					{ label: __("Status"), render: (r) => pill(r.status) },
					{ label: __("Shift"), key: "shift" },
					{ label: __("Drum"), key: "drum" },
					{ label: __("In kg"), render: (r) => fmt(r.input_weight_kg) },
					{ label: __("Out kg"), render: (r) => fmt(r.output_weight_kg) },
					{ label: __("ft²"), render: (r) => fmt(r.output_area_sqft) },
					{ label: __("Yield"), render: (r) => pct(r.weight_yield_percent) },
					{ label: __("Reject"), render: (r) => fmt(r.rejected_qty) },
				]);
				set_table(wrapper, "ld-tbl-qc", d.recent_qc, "Leather QC Inspection", [
					{ label: __("QC"), key: "name" },
					{ label: __("Date"), render: (r) => date(r.inspection_date) },
					{ label: __("Type"), key: "inspection_type" },
					{ label: __("Lot"), key: "lot" },
					{ label: __("Result"), render: (r) => pill(r.overall_result) },
					{ label: __("Holes"), key: "hole_count" },
					{ label: __("Scars"), key: "scar_count" },
				]);
				set_table(wrapper, "ld-tbl-po", d.recent_pos, "Hide Purchase Order", [
					{ label: __("PO"), key: "name" },
					{ label: __("Date"), render: (r) => date(r.transaction_date) },
					{ label: __("Supplier"), key: "supplier" },
					{ label: __("Status"), render: (r) => pill(r.status) },
					{ label: __("Origin"), key: "origin_country" },
					{ label: __("Hide amt"), render: (r) => money(r.hide_amount) },
					{ label: __("Landed"), render: (r) => money(r.landed_cost) },
				]);
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
			data: { labels: labelList, datasets: [{ data: valueList, backgroundColor: PALETTE, borderWidth: 0, hoverOffset: 6 }] },
			options: {
				responsive: true,
				maintainAspectRatio: false,
				cutout: "58%",
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

	function lineOpts() {
		return {
			responsive: true,
			maintainAspectRatio: false,
			plugins: { legend: { display: false } },
			scales: {
				x: { grid: { display: false } },
				y: { beginAtZero: true, grid: { color: "#f1e8dc" } },
			},
		};
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
			.map((r) => {
				const tds = cols
					.map((c) => `<td>${c.render ? c.render(r) : esc(r[c.key])}</td>`)
					.join("");
				return `<tr data-dt="${doctype}" data-name="${esc(r.name)}">${tds}</tr>`;
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

	function avg_by_date(rows) {
		const map = {};
		rows.forEach((r) => {
			const key = String(r.posting_date || "");
			if (!key) return;
			if (!map[key]) map[key] = { sum: 0, n: 0 };
			map[key].sum += n(r.yield_pct);
			map[key].n += 1;
		});
		return Object.keys(map)
			.sort()
			.map((date) => ({ date, yield: map[date].n ? map[date].sum / map[date].n : 0 }));
	}

	function pill(v) {
		const s = String(v || "—");
		let cls = "";
		if (/pass|available|completed|closed|confirmed|shipped|in stock/i.test(s)) cls = "good";
		else if (/fail|reject|open|cancelled/i.test(s)) cls = "bad";
		else if (/pending|progress|draft|hold|capa|investigat/i.test(s)) cls = "warn";
		return `<span class="ld-pill ${cls}">${esc(s)}</span>`;
	}

	function n(v) {
		return Number(v || 0);
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
	function short(v) {
		v = String(v || "—");
		return v.length > 16 ? v.slice(0, 14) + "…" : v;
	}
	function esc(v) {
		return frappe.utils.escape_html(String(v == null ? "" : v));
	}
})();
