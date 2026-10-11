"""
generate_report.py — Generate the native-plant design report PDF.

Run from the QGIS Python console:
    import sys; sys.path.insert(0, '/path/to/repo')
    exec(open('/path/to/repo/scripts/generate_report.py').read())

Reads plant layers live from the open QGIS project, builds HTML report
pages, pushes them into the print layout, and exports a PDF.
Report appearance is controlled by REPORT_THEME in config/project_config.py.
Plant specs are loaded from plan/plants.csv via PATHS["plants_csv"].
"""

import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qgis.core import (
    QgsProject, QgsLayoutItemHtml, QgsLayoutExporter,
    QgsCoordinateTransform, QgsCoordinateReferenceSystem,
)
from collections import defaultdict

from plan.project_config import PROJECT, PATHS, GIS, MATERIALS, TAX_RATE, REPORT_THEME

# ── Load plant catalog from CSV ───────────────────────────────────────────────
def load_catalog(csv_path):
    """Read plants.csv into a dict keyed by the 'species' field."""
    catalog = {}
    if not csv_path or not os.path.exists(csv_path):
        print(f"WARNING: plants_csv not set or not found at '{csv_path}'")
        return catalog
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = row.get("species", "").strip()
            if key:
                # coerce numeric field
                try:
                    row["unit_price"] = float(row["unit_price"])
                except (ValueError, KeyError):
                    row["unit_price"] = 0.0
                catalog[key] = row
    return catalog

CATALOG = load_catalog(PATHS.get("plants_csv"))

proj    = QgsProject.instance()
T       = REPORT_THEME   # shorthand
SEED_SQFT_PER_BAG = 200
SEED_PRICE        = 20

# ── CSS (driven by REPORT_THEME) ──────────────────────────────────────────────
def build_css():
    return f"""<style>
body{{font-family:{T['font_family']};font-size:{T['font_size_body']};color:#222;margin:{T['page_margin']};}}
h1{{font-size:15pt;color:{T['primary_color']};border-bottom:2px solid {T['primary_color']};padding-bottom:3px;margin:0 0 8px 0;}}
h2{{font-size:10pt;color:{T['secondary_color']};margin:9px 0 3px 0;border-bottom:1px solid #aaccaa;}}
h3{{font-size:9pt;color:#3a5a3c;margin:7px 0 2px 0;}}
p,li{{font-size:{T['font_size_small']};margin:2px 0;}}
p.sm{{font-size:{T['font_size_small']};margin:2px 0 5px 0;}}
ul{{margin:2px 0 5px 14px;padding:0;}}
table{{width:100%;border-collapse:collapse;font-size:{T['font_size_small']};margin-bottom:6px;}}
th{{background:{T['secondary_color']};color:#fff;padding:4px 6px;text-align:left;font-size:{T['font_size_note']};}}
td{{padding:3px 5px;border-bottom:1px solid #e0e0e0;vertical-align:middle;}}
tr.even td{{background:#f4faf4;}}
tr.sec  td{{background:{T['accent_color']};font-weight:bold;color:#1a3a1a;padding:3px 5px;}}
tr.total td{{background:{T['total_row_color']};font-weight:bold;border-top:2px solid {T['secondary_color']};}}
tr.grand td{{background:{T['primary_color']};color:#fff;font-weight:bold;font-size:10pt;}}
.imgcell{{width:76px;text-align:center;}}
.imgcell img{{width:70px;height:70px;border-radius:3px;border:1px solid #ccc;}}
.note{{font-size:{T['font_size_note']};color:#666;font-style:italic;}}
.col2{{column-count:2;column-gap:16px;}}
.badge{{display:inline-block;padding:1px 5px;border-radius:3px;font-size:{T['font_size_note']};font-weight:bold;}}
.city{{background:{T['city_bg']};color:{T['city_text']};}}
.ours{{background:{T['ours_bg']};color:{T['ours_text']};}}
.w{{color:{T['water_color']};font-weight:bold;}}
.wm{{color:{T['water_mod_color']};font-weight:bold;}}
</style>"""

CSS = build_css()

# ── Query layers ──────────────────────────────────────────────────────────────
counts = defaultdict(lambda: {"count": 0, "side": ""})
for layer_name in ["proposed_plants", "proposed_plants_ours", "proposed_trees_city"]:
    lyr = proj.mapLayersByName(layer_name)
    if not lyr:
        continue
    for feat in lyr[0].getFeatures():
        sp = feat["species"]
        counts[sp]["count"] += 1
        counts[sp]["side"] = feat["side"]
        if sp not in CATALOG:
            print(f"WARNING: '{sp}' not in plants.csv — research and add it")

wf_area_sqft = 0
wf_lyr = proj.mapLayersByName("wildflower_areas")
if wf_lyr:
    xform = QgsCoordinateTransform(
        QgsCoordinateReferenceSystem(GIS["crs_storage"]),
        QgsCoordinateReferenceSystem(GIS["crs_metric"]), proj)
    for feat in wf_lyr[0].getFeatures():
        g = feat.geometry(); g.transform(xform)
        wf_area_sqft += g.area() * 10.7639
seed_bags = max(1, round(wf_area_sqft / SEED_SQFT_PER_BAG))

# ── Helpers ───────────────────────────────────────────────────────────────────
SIDE_ORDER = {"city": 0, "ours": 1}
TYPE_ORDER = {"tree": 0, "shrub": 1}

def sorted_sp():
    return sorted(
        (s for s in counts if s in CATALOG),
        key=lambda s: (SIDE_ORDER.get(counts[s]["side"], 9),
                       TYPE_ORDER.get(CATALOG[s]["plant_type"], 9),
                       CATALOG[s]["common"]))

def alt(i):    return ' class="even"' if i % 2 else ''
def sl(s):     return "City" if s == "city" else "Ours"
def badge(s):  return f'<span class="badge {"city" if s=="city" else "ours"}">{sl(s)}</span>'
def wc(w):     return f'<span class="{"wm" if "Mod" in w else "w"}">{w}</span>'

# ── Page builders ─────────────────────────────────────────────────────────────

def build_intro():
    city_sp     = [s for s in sorted_sp() if counts[s]["side"] == "city"]
    city_trees  = [s for s in city_sp if CATALOG[s]["plant_type"] == "tree"]
    city_shrubs = [s for s in city_sp if CATALOG[s]["plant_type"] == "shrub"]
    tree_list   = ", ".join(f'{CATALOG[s]["common"]} ×{counts[s]["count"]}' for s in city_trees)
    shrub_list  = ", ".join(f'{CATALOG[s]["common"]} ×{counts[s]["count"]}' for s in city_shrubs)

    photo_html = ""
    if PROJECT.get("photo_path"):
        w, h = PROJECT.get("photo_width_px", 533), PROJECT.get("photo_height_px", 400)
        photo_html = f"""
<div style="text-align:center;margin-bottom:8px;">
  <img src="file://{PROJECT['photo_path']}" style="width:{w}px;height:{h}px;border-radius:4px;border:1px solid #ccc;">
  <p class="note" style="margin:3px 0 8px 0;">{PROJECT.get('photo_caption','')}</p>
</div>"""

    return CSS + f"""
<h1>{PROJECT['name']} — {PROJECT.get('subtitle','')}</h1>
{photo_html}
<div style="overflow:hidden;margin-top:6px;">
<div style="float:left;width:48%;margin-right:4%;">
  <h2>Summary</h2>
  <p>This proposal requests a land-management agreement to plant and maintain a native
  drought-tolerant buffer in <b>{PROJECT['location']}</b> (USDA Zone {PROJECT['usda_zone']}).</p>
  <h2>City-Side Scope</h2>
  <ul>
    <li><b>Trees ({len(city_trees)} species, {sum(counts[s]['count'] for s in city_trees)} plants):</b> {tree_list}</li>
    <li><b>Shrubs ({len(city_shrubs)} species, {sum(counts[s]['count'] for s in city_shrubs)} plants):</b> {shrub_list}</li>
    <li><b>Wildflower seed:</b> {wf_area_sqft:.0f} sqft native mix</li>
  </ul>
</div>
<div style="float:left;width:48%;">
  <h2>Benefits</h2>
  <ul>
    <li>Native canopy provides shade, wind buffer, and wildlife habitat</li>
    <li>Drought-tolerant species require <b>no irrigation</b> after establishment</li>
    <li>Dense shrub layer reduces erosion and weed pressure</li>
  </ul>
  <p class="note">Full cost estimate, planting plan, and horticultural specifications on following pages.</p>
</div>
</div>"""


def build_budget():
    rows = ""; plants_total = 0; cur_sec = None; i = 0
    for sp in sorted_sp():
        d = counts[sp]; cat = CATALOG[sp]
        sec = f"{cat['plant_type'].upper()}S — {'City' if d['side']=='city' else 'Our'} Side"
        if sec != cur_sec:
            rows += f'<tr class="sec"><td colspan="8">{sec}</td></tr>\n'
            cur_sec = sec; i = 0
        qty = d["count"]; p = cat["unit_price"]; tot = qty * p; plants_total += tot
        rows += (f'<tr{alt(i)}><td>{cat["common"]}</td><td><i>{cat["scientific"]}</i></td>'
                 f'<td>{sl(d["side"])}</td><td>{cat["plant_type"].capitalize()}</td>'
                 f'<td>{cat["container"]}</td><td>{qty}</td><td>${p}</td><td>${tot}</td></tr>\n')
        i += 1
    seed_tot = seed_bags * SEED_PRICE; plants_total += seed_tot
    rows += (f'<tr class="sec"><td colspan="8">WILDFLOWER SEED</td></tr>\n'
             f'<tr><td>Native Wildflower Mix</td><td><i>Various</i></td>'
             f'<td>City</td><td>Seed</td><td>1-lb bag</td><td>{seed_bags}</td>'
             f'<td>${SEED_PRICE}</td><td>${seed_tot}</td></tr>\n')
    n_plants = sum(d["count"] for d in counts.values())
    rows += (f'<tr class="total"><td colspan="7">Plants Subtotal ({n_plants} plants)</td>'
             f'<td>${plants_total:,}</td></tr>\n')

    mat_rows = ""; mat_total = 0
    for j, (desc, qty, unit, uprice) in enumerate(MATERIALS):
        tot = int(qty * uprice); mat_total += tot
        mat_rows += f'<tr{alt(j)}><td>{desc}</td><td>{qty}</td><td>{unit}</td><td>${uprice:.2f}</td><td>${tot}</td></tr>\n'
    tax   = int((plants_total + mat_total) * TAX_RATE)
    grand = plants_total + mat_total + tax
    mat_rows += (f'<tr class="total"><td colspan="4">Materials Subtotal</td><td>${mat_total:,}</td></tr>\n'
                 f'<tr><td colspan="4">Sales Tax ({TAX_RATE*100:.1f}%)</td><td>${tax:,}</td></tr>\n'
                 f'<tr class="grand"><td colspan="4">GRAND TOTAL</td><td>${grand:,}</td></tr>')

    return (CSS + '<h1>Budget Estimate</h1>'
            '<p class="sm">Plant quantities from map layers. Prices are Utah nursery averages.</p>'
            '<table><tr><th>Item</th><th>Scientific Name</th><th>Side</th><th>Type</th>'
            '<th>Size</th><th>Qty</th><th>Unit $</th><th>Total</th></tr>\n' + rows + '</table>'
            '<h2>Materials &amp; Installation</h2>'
            '<table><tr><th>Item</th><th>Qty</th><th>Unit</th><th>Unit $</th><th>Total</th></tr>\n'
            + mat_rows + '</table>')


def build_viz():
    rows = ""; cur_sec = None; i = 0
    for sp in sorted_sp():
        d = counts[sp]; cat = CATALOG[sp]
        sec = f'{"TREES" if cat["plant_type"]=="tree" else "SHRUBS"} — {"City" if d["side"]=="city" else "Our"} Side'
        if sec != cur_sec:
            rows += f'<tr class="sec"><td colspan="8">{sec}</td></tr>\n'; cur_sec = sec; i = 0
        img_path = cat.get("image_path", "").strip()
        if img_path and not os.path.isabs(img_path):
            img_path = os.path.join(os.path.dirname(PATHS.get("plants_csv") or ""), img_path)
        img = (f'<img src="file://{img_path}">' if img_path and os.path.exists(img_path)
               else '<span style="font-size:7pt;color:#aaa;">no image</span>')
        rows += (f'<tr{alt(i)}><td class="imgcell">{img}</td>'
                 f'<td><b>{cat["common"]}</b><br><i style="font-size:7pt">{cat["scientific"]}</i></td>'
                 f'<td>{sl(d["side"])}</td><td>{cat["form"]}</td>'
                 f'<td>{cat["height"]}</td><td>{cat["width"]}</td>'
                 f'<td>{cat["growth"]}</td><td>{cat["seasonal"]}</td></tr>\n')
        i += 1
    return (CSS + '<h1>Plant Visualization — Mature Size &amp; Form</h1>'
            '<table><tr><th class="imgcell">Photo</th><th>Common / Scientific</th>'
            '<th>Side</th><th>Form</th><th>Height</th><th>Width</th>'
            '<th>Growth</th><th>Seasonal Notes</th></tr>\n' + rows + '</table>')


def build_instructions():
    city_sp    = [s for s in sorted_sp() if counts[s]["side"] == "city"]
    ours_sp    = [s for s in sorted_sp() if counts[s]["side"] == "ours"]
    sp_notes   = "".join(
        f'<h3>{CATALOG[s]["common"]} {badge(counts[s]["side"])}</h3><p>{CATALOG[s]["instr"]}</p>\n'
        for s in sorted_sp())
    def sp_summary(lst):
        return ", ".join(f'{CATALOG[s]["common"]} (×{counts[s]["count"]})' for s in lst)
    return (CSS + '<h1>Planting Instructions</h1>'
            '<div class="col2">'
            '<h3>When to Plant</h3><ul>'
            '<li><b>Best: Sep 15 – Oct 31</b> — roots establish before freeze.</li>'
            '<li>Second best: Mar 15 – Apr 30.</li>'
            '<li>Avoid: Jun–Aug and frozen ground.</li></ul>'
            '<h3>Hole Preparation</h3><ul>'
            '<li>Dig 2–3× wider than root ball, same depth.</li>'
            '<li>City-side: backfill with native soil only — no amendments.</li>'
            '<li>Our-side: mix 20% compost into backfill.</li></ul>'
            '<h3>Mulching</h3><ul>'
            '<li>Apply 3 in bark mulch; keep 2 in from stem.</li></ul></div>'
            f'<h2>City Side ({sp_summary(city_sp)})</h2>'
            f'<h2>Our Side ({sp_summary(ours_sp)})</h2>'
            '<h2>Species Notes</h2><div class="col2">' + sp_notes + '</div>')


def build_specs():
    rows = ""; cur_sec = None; i = 0
    for sp in sorted_sp():
        d = counts[sp]; cat = CATALOG[sp]
        sec = f'{"TREES" if cat["plant_type"]=="tree" else "SHRUBS"} — {"City" if d["side"]=="city" else "Our"} Side'
        if sec != cur_sec:
            rows += f'<tr class="sec"><td colspan="11">{sec}</td></tr>\n'; cur_sec = sec; i = 0
        rows += (f'<tr{alt(i)}><td><b>{cat["common"]}</b></td><td><i>{cat["scientific"]}</i></td>'
                 f'<td>{sl(d["side"])}</td><td>{cat["height"]}</td><td>{cat["width"]}</td>'
                 f'<td>{wc(cat["water"])}</td><td>{cat["sun"]}</td><td>{cat["zone"]}</td>'
                 f'<td>{cat["root"]}</td><td>{cat["soil"]}</td><td>{cat["notes"]}</td></tr>\n')
        i += 1
    return (CSS + '<h1>Horticultural Specifications</h1>'
            '<p class="sm">USDA Zone ' + PROJECT["usda_zone"] + '. Plant counts from map layers.</p>'
            '<table><tr><th>Common</th><th>Scientific</th><th>Side</th>'
            '<th>H</th><th>W</th><th>Water</th><th>Sun</th><th>Zone</th>'
            '<th>Root</th><th>Soil</th><th>Notes</th></tr>\n' + rows + '</table>')


# ── Push to layout and export ─────────────────────────────────────────────────
layout_name = GIS.get("layout_name", "Project Report")
layout = proj.layoutManager().layoutByName(layout_name)
if not layout:
    print(f"ERROR: layout '{layout_name}' not found — create it in QGIS Layout Manager first.")
else:
    mfs = sorted(
        [mf for mf in layout.multiFrames() if isinstance(mf, QgsLayoutItemHtml)],
        key=lambda m: m.frames()[0].page())

    pages = [build_intro(), build_budget(), build_viz(), build_instructions(), build_specs()]
    for mf, html in zip(mfs, pages):
        mf.beginCommand("update html"); mf.setHtml(html); mf.loadHtml(); mf.endCommand()

    proj.write()

    pdf_path = PATHS.get("output_pdf") or os.path.join(
        os.path.dirname(PATHS.get("qgis_project") or "/tmp"), "report.pdf")
    exporter = QgsLayoutExporter(layout)
    s = QgsLayoutExporter.PdfExportSettings()
    s.dpi = GIS.get("export_dpi", 150)
    result = exporter.exportToPdf(pdf_path, s)
    size_kb = os.path.getsize(pdf_path) // 1024
    print(f"✓ PDF exported: {pdf_path} ({size_kb} KB), result={result}")
