### Leature Manufacturing

Leather / tannery ERP on ERPNext. First-class concepts are **Lot, Piece, Area, Weight, Grade, Recipe, Yield, and Traceability** — not a generic manufacturing BOM.

Flow:

Raw Hide → Receiving & Grading → Beamhouse → Tanning / Wet Blue → Splitting & Shaving → Dyeing → Finishing → Piece selection → Sales / Export

### Installation

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench --site your.site install-app erpnext
bench --site your.site install-app leature_manufacturing
```

Open Desk workspace **Leature**, or https://your.site/app/leature

### What is included

- Hide / skin masters, article, color, grade, chemical, drum, machine
- Lot-based purchasing, receiving inspection, defect grading, grade-wise valuation
- Production batches for beamhouse, tanning, dyeing, finishing (recipe % of hide weight)
- Area measurement (sq. ft. / sq. m), piece barcodes, QC and lab samples
- Sales allocation against matching pieces, packing, export shipment, complaints
- Batch costing (cost per sq. ft.), ETP log, waste, sustainability
- Yield, chemical consumption, grade mix, stock, costing, and lot traceability reports
- Factory dashboard

ERPNext covers GL, AP/AR, stock items (optional link), HR, and tax. This app is the tannery layer on top.
