# quaking-aspen-planner — Development

Reference for active design and coding work: QGIS patterns, layer schema,
plant research, and report generation.

---

## QGIS MCP Server

The MCP server exposes ~100 tools prefixed `mcp__qgis__`.
The single most important is `mcp__qgis__execute_code` — use it for almost
everything geometric or layer-related.

### Key PyQGIS imports
```python
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry,
    QgsPointXY, QgsCoordinateReferenceSystem,
    QgsCoordinateTransform, QgsVectorFileWriter,
    QgsEditorWidgetSetup,
)
```

### CRS conventions
- Features stored in **EPSG:4326** (WGS84 lat/lon)
- All metric math done in **EPSG:32612** (UTM Zone 12N, meters)

```python
crs_4326 = QgsCoordinateReferenceSystem("EPSG:4326")
crs_utm  = QgsCoordinateReferenceSystem("EPSG:32612")
to_utm   = QgsCoordinateTransform(crs_4326, crs_utm, QgsProject.instance())
to_4326  = QgsCoordinateTransform(crs_utm, crs_4326, QgsProject.instance())
pt_utm   = to_utm.transform(QgsPointXY(lon, lat))
pt_4326  = to_4326.transform(pt_utm)
```

### Save a memory layer to GeoPackage
```python
QgsVectorFileWriter.writeAsVectorFormat(
    layer, "/path/to/file.gpkg", "utf-8", layer.crs(), "GPKG")
```

### Layer tree reorder
```python
root = QgsProject.instance().layerTreeRoot()
node = root.findLayer(layer_id)
clone = node.clone()
root.removeChildNode(node)
root.insertChildNode(0, clone)   # 0 = top
```

---

## Standard Layer Schema

`proposed_plants` is the only required layer. All other layers represent
site-specific features (boundaries, paths, structures, planting areas) and
are created by `setup_project.py` based on what the developer describes
during intake. Their names, geometries, and fields should match the site.

### proposed_plants (required)

| Field | Type | Notes |
|-------|------|-------|
| `species` | String | Key matching a row in `plants.csv`; use a dropdown widget (see below) |
| `common_name` | String | Human-readable label; auto-filled by agent when placing points |
| `plant_type` | String | `"tree"` or `"shrub"` |
| `side` | String | Ownership zone, e.g. `"city"` or `"private"` — adapt to the project |
| `canopy_m` | Double | Estimated mature canopy radius in meters |

---

## Species Dropdown Widget

After researching each new species and adding it to `plants.csv`, update the
`species` field widget on `proposed_plants` to a **ValueMap dropdown**. This
lets the developer drop points manually and pick a species from a list without
typing — matching exactly what the agent uses as keys.

**Rebuild the dropdown whenever the CSV changes:**

```python
import csv
from qgis.core import QgsEditorWidgetSetup

proj  = QgsProject.instance()
layer = proj.mapLayersByName("proposed_plants")[0]

csv_path = "/absolute/path/to/plan/plants.csv"  # PATHS["plants_csv"]
with open(csv_path, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

# ValueMap format: [{display_label: stored_value}, ...]
value_map = [{f"{r['common']} ({r['species']})": r["species"]} for r in rows if r.get("species")]

idx = layer.fields().indexFromName("species")
layer.setEditorWidgetSetup(idx, QgsEditorWidgetSetup("ValueMap", {"map": value_map}))
proj.write()
print(f"Dropdown updated with {len(value_map)} species.")
```

The display label shows the common name with the key in parentheses so the
developer can identify each entry. The stored value is the bare `species` key,
which is what the report script looks up in `plants.csv`.

---

## Plant Catalog — Research Pattern

`plan/plants.csv` starts with only a header row. Whenever a new species
is added to the `proposed_plants` layer, research it from primary sources and
append a real row. Never invent or estimate plant data.

### Research sources (in priority order)
1. **USU Extension Yard & Garden** — `https://extension.usu.edu/yardandgarden/`
   Utah-specific care, water needs, container sizes, and local nursery context
2. **Utah Native Plant Society** — `https://www.unps.org/`
   Native range confirmation, ecology, conservation status
3. **Lady Bird Johnson Wildflower Center** — `https://www.wildflower.org/plants/`
   Mature size, soil, sun, root system, cultivation detail
4. **USDA PLANTS Database** — `https://plants.usda.gov/`
   Authoritative taxonomy, USDA hardiness zones, distribution maps

### Research workflow per species
```
1. WebSearch: "<common name> OR <scientific name> site:extension.usu.edu"
2. WebFetch the top USU result → extract water need, hardiness, care notes
3. WebFetch wildflower.org plant page → extract mature H×W, root type, soil, sun
4. Verify Utah native range at unps.org or plants.usda.gov
5. Check a local Utah nursery (e.g. Millcreek Gardens, Cactus and Tropicals)
   for current container sizes and prices
6. Fetch a plant image (see below) and record the absolute path in image_path
7. Rebuild the species dropdown widget (see above)
```

### Fetching plant images

For each species, find and download one openly-licensed photo to
`resources/images/<species_key>.jpg` (use the same key as the CSV `species` field).

**Image sources in priority order:**
1. **Wikimedia Commons** — search `https://commons.wikimedia.org/w/index.php?search=<scientific+name>`
   Filter to CC0 or CC BY / CC BY-SA licensed files. Download medium-resolution (800–1200px wide).
2. **USDA PLANTS** — `https://plants.usda.gov/home/plantProfile?symbol=<PLANTS_symbol>`
   Profile pages often link public-domain gallery images.
3. **iNaturalist** — `https://www.inaturalist.org/taxa/<taxon-id>/browse_photos`
   Use only photos marked CC0 or CC BY.

**Download pattern:**
```python
import urllib.request, os
img_dir  = "/absolute/path/to/resources/images"   # from PATHS["images_dir"] in project_config.py
img_path = os.path.join(img_dir, f"{species_key}.jpg")
urllib.request.urlretrieve(image_url, img_path)
```

Record the **absolute path** in the CSV's `image_path` column.
If no freely-licensed image is found, leave `image_path` blank — the report
renders a "no image" placeholder automatically.

### Required CSV fields
```
species     — short key matching feat["species"] in QGIS (e.g. "pinus_edulis")
scientific  — full scientific name
common      — common name
plant_type  — "tree" or "shrub"
container   — nursery size: "1-gal", "5-gal", "15-gal"
unit_price  — USD float — verify with a current Utah nursery price
height      — mature height range, e.g. "10–20 ft"
width       — mature width range
water       — e.g. "Very Low", "Low", "Low–Mod"
sun         — e.g. "Full", "Full–Part"
zone        — USDA zone range, e.g. "4–8"
root        — root system description
soil        — preferred soil
form        — growth form / canopy shape
growth      — "Slow", "Moderate", "Fast", etc.
seasonal    — one sentence: key seasonal interest
notes       — short field note for report tables
instr       — planting and first-year care instructions
image_path  — absolute path to downloaded image, or blank
```

---

## Layer Styling

### proposed_plants — canopy-width symbols

All plants in `proposed_plants` must be rendered as circles whose **diameter
equals the mature canopy width** (`canopy_m * 2`). This is especially important
for shrubs, where the spread is the dominant design dimension.

This requires the map canvas CRS to be EPSG:32612 (meters) so that Map Units
resolve to meters on screen. Switch the project CRS before applying the style:

```python
from qgis.core import (
    QgsProject, QgsCoordinateReferenceSystem,
    QgsSingleSymbolRenderer, QgsMarkerSymbol,
    QgsSymbolLayer, QgsProperty, QgsUnitTypes,
)

# Switch canvas to metric CRS so Map Units = meters
QgsProject.instance().setCrs(QgsCoordinateReferenceSystem("EPSG:32612"))

layer = QgsProject.instance().mapLayersByName("proposed_plants")[0]

symbol = QgsMarkerSymbol.createSimple({
    "name":          "circle",
    "color":         "34,139,34,180",
    "outline_style": "solid",
    "outline_color": "0,100,0,255",
    "outline_width": "0.3",
})
symbol.setSizeUnit(QgsUnitTypes.RenderMapUnits)
symbol.setDataDefinedProperty(
    QgsSymbolLayer.PropertySize,
    QgsProperty.fromExpression('"canopy_m" * 2'),
)

layer.setRenderer(QgsSingleSymbolRenderer(symbol))
layer.triggerRepaint()
print("Canopy-width symbols applied.")
```

Apply this style immediately after placing the first batch of plants, and
re-run whenever `canopy_m` values are updated. The canvas CRS change is
permanent for the session — save the project afterwards.

---

## Report Generation

To generate or troubleshoot the PDF report, load the **Report** skill section:
`skills/quaking-aspen-planner-report.md`

It covers the complete layout setup (map item, legend, HTML frames), how to run
`generate_report.py`, and a troubleshooting guide for the common failure modes
(missing map, missing legend, overlapping tables, WARNING species).
