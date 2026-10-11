# quaking-aspen-planner — Report

Full procedure for creating the print layout and exporting the PDF proposal.
Load this section when the user asks to generate, fix, or re-export the report.

---

## Pre-flight Checklist

Before running the report:

1. **`PATHS` are set** in `plan/project_config.py` — `plants_csv`, `qgis_project`,
   `output_pdf` must all be absolute paths pointing to real files/directories.
2. **No WARNING species** — run the checklist block below and resolve any
   species present in `proposed_plants` but missing from `plants.csv`.
3. **Canvas is zoomed to the site** — the layout map item captures the current
   canvas extent. Zoom to the project boundary before setting up the layout.

### Quick species check
```python
import sys, os, csv
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from plan.project_config import PATHS
from qgis.core import QgsProject

catalog = {}
with open(PATHS["plants_csv"], newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        catalog[row["species"].strip()] = True

proj = QgsProject.instance()
missing = set()
for lname in ["proposed_plants", "proposed_plants_ours", "proposed_trees_city"]:
    lyr = proj.mapLayersByName(lname)
    if lyr:
        for feat in lyr[0].getFeatures():
            sp = feat["species"]
            if sp and sp not in catalog:
                missing.add(sp)

if missing:
    print("WARNING: missing from plants.csv:", missing)
else:
    print("OK: all species in catalog.")
```

---

## Layout Setup

Run this **once per project** to create the print layout with all required items:
a map, a legend, and five HTML content frames (one per report section). Re-run
it any time you need to reset a broken layout.

Set `REPO_ROOT` to the absolute path of the project repo before running.

```python
import sys, os
REPO_ROOT = "/absolute/path/to/repo"   # ← set this
sys.path.insert(0, REPO_ROOT)
from plan.project_config import GIS

from qgis.core import (
    QgsProject, QgsPrintLayout, QgsLayoutSize, QgsLayoutPoint,
    QgsLayoutItemPage, QgsLayoutItemMap, QgsLayoutItemLegend,
    QgsLayoutItemHtml, QgsLayoutFrame, QgsUnitTypes,
)

proj = QgsProject.instance()
lm   = proj.layoutManager()

# Remove stale layout if present
existing = lm.layoutByName(GIS["layout_name"])
if existing:
    lm.removeLayout(existing)

layout = QgsPrintLayout(proj)
layout.initializeDefaults()
layout.setName(GIS["layout_name"])

# A4 portrait (mm)
PW, PH = 210, 297
MARGIN  = 10   # page margin (mm)
GAP     = 10   # gap between pages in layout coordinate space (mm)
MAP_H   = 95   # height reserved for map + legend on page 1

# Size page 1 (already created by initializeDefaults)
pc = layout.pageCollection()
pc.pages()[0].setPageSize(QgsLayoutSize(PW, PH, QgsUnitTypes.LayoutMillimeters))

# Add pages 2-5
for _ in range(4):
    page = QgsLayoutItemPage(layout)
    page.setPageSize(QgsLayoutSize(PW, PH, QgsUnitTypes.LayoutMillimeters))
    pc.addPage(page)

def abs_y(page_index, y_on_page):
    """Convert page-local y to absolute layout y (accounts for page gap)."""
    return page_index * (PH + GAP) + y_on_page

# ── Page 1: Map item (left) ───────────────────────────────────────────────────
MAP_W = PW - 2 * MARGIN - 58   # leave 58mm for legend column
map_item = QgsLayoutItemMap(layout)
map_item.attemptMove(QgsLayoutPoint(MARGIN, abs_y(0, MARGIN),
                                    QgsUnitTypes.LayoutMillimeters))
map_item.attemptResize(QgsLayoutSize(MAP_W, MAP_H, QgsUnitTypes.LayoutMillimeters))
map_item.setExtent(iface.mapCanvas().extent())
layout.addLayoutItem(map_item)

# ── Page 1: Legend (right of map) ────────────────────────────────────────────
legend = QgsLayoutItemLegend(layout)
legend.setLinkedMap(map_item)
legend.setAutoUpdateModel(True)
legend.attemptMove(QgsLayoutPoint(PW - MARGIN - 55, abs_y(0, MARGIN),
                                  QgsUnitTypes.LayoutMillimeters))
legend.attemptResize(QgsLayoutSize(55, MAP_H, QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(legend)

# ── HTML frames: one per report section, one per page ────────────────────────
# Page 1 frame starts below the map; pages 2-5 fill the whole page.
P1_HTML_Y = MARGIN + MAP_H + 4
frame_specs = [
    # (page_index, y_on_page, height)
    (0, P1_HTML_Y,  PH - P1_HTML_Y - MARGIN),   # intro  (below map)
    (1, MARGIN,     PH - 2 * MARGIN),            # budget
    (2, MARGIN,     PH - 2 * MARGIN),            # visualization
    (3, MARGIN,     PH - 2 * MARGIN),            # instructions
    (4, MARGIN,     PH - 2 * MARGIN),            # specs
]
HTML_W = PW - 2 * MARGIN

for page_idx, y_on_page, h in frame_specs:
    html_mf = QgsLayoutItemHtml(layout)
    html_mf.setResizeMode(QgsLayoutItemHtml.UseExistingFrames)
    layout.addMultiFrame(html_mf)
    frame = QgsLayoutFrame(layout, html_mf)
    frame.attemptMove(QgsLayoutPoint(MARGIN, abs_y(page_idx, y_on_page),
                                     QgsUnitTypes.LayoutMillimeters))
    frame.attemptResize(QgsLayoutSize(HTML_W, h, QgsUnitTypes.LayoutMillimeters))
    html_mf.addFrame(frame)

lm.addLayout(layout)
proj.write()
print(f"Layout '{GIS['layout_name']}' created: 5 pages, map+legend on p1.")
```

---

## Running the Report

After the layout exists, run `generate_report.py` from the QGIS Python console:

```python
import sys; sys.path.insert(0, '/absolute/path/to/repo')
exec(open('/absolute/path/to/repo/scripts/generate_report.py').read())
```

Or via MCP:
```python
# mcp__qgis__execute_code
exec(open(PATHS["repo_root"] + "/scripts/generate_report.py").read())
```

The script prints the PDF path and file size on success.

---

## Troubleshooting

### Map is blank or missing from page 1

The layout has no map item, or the map item's extent was not set.

**Fix:** Re-run the layout setup script above. Zoom the canvas to the project
site *before* running it — `map_item.setExtent(iface.mapCanvas().extent())`
captures the current view at creation time.

### Legend is missing

The layout has no legend item.

**Fix:** Re-run the layout setup script. A legend linked to the map item is
created automatically.

### Report sections overlap or show on the wrong page

The HTML frames are on the same page, or their y-positions don't match the
page breaks.

**Root cause:** The layout was created manually without correct absolute y
offsets. Each page in a QGIS print layout starts at `page_index × (PH + GAP)`
in absolute layout coordinates — frames placed at `y=10` without accounting for
the page index all land on page 1.

**Fix:** Re-run the layout setup script. The `abs_y()` helper computes correct
positions for all five frames.

### A section is cut off (content taller than frame)

The HTML content for that section exceeds the frame height. This is most likely
on the budget page (many species) or specs page.

**Fix:** Increase the frame height in the layout setup script. The budget and
specs sections need roughly 4 mm per data row plus ~20 mm overhead. With 60
plants you need ~260 mm — the default of `PH - 2*MARGIN = 277 mm` is sufficient
for most cases, but increase `PH` or reduce `MARGIN` if not.

Alternatively, split long sections: duplicate the `QgsLayoutItemHtml` entry for
that page and add a second page for overflow.

### `WARNING: 'species_key' not in plants.csv`

A feature in `proposed_plants` has a `species` value with no matching row in
`plants.csv`. The report skips it and the plant won't appear in any table.

**Fix:** Research the species and append a complete row to `plants.csv` before
re-running the report. See the Development skill for the research workflow.

### `ERROR: layout 'Project Report' not found`

`GIS["layout_name"]` in `project_config.py` doesn't match the actual layout
name, or the layout was deleted.

**Fix:** Either re-run the layout setup (which uses the configured name), or
update `GIS["layout_name"]` to match the existing layout name.