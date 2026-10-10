# Data Sources

Reference list of GIS layers, plant research databases, and external APIs
used in Utah native plant QGIS projects.

---

## ESRI Basemap Layers (XYZ tile URLs)

| Layer | URL |
|-------|-----|
| World Imagery | `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}` |
| World Street Map | `https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}` |
| World Topo Map | `https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}` |
| World Hillshade | `https://server.arcgisonline.com/ArcGIS/rest/services/Elevation/World_Hillshade/MapServer/tile/{z}/{y}/{x}` |

Load in QGIS via **Layer → Add Layer → Add XYZ Tiles**, or via `setup_project.py`.

---

## Utah Parcel Data (UGRC)

UGRC hosts county parcel layers as ArcGIS FeatureServer REST endpoints.
Query pattern: filter by bbox in Web Mercator (SRID 3857), return GeoJSON in EPSG:4326.

| County | FeatureServer URL |
|--------|-------------------|
| Davis County | `https://services1.arcgis.com/99lidPhWCzftIe9K/ArcGIS/rest/services/Parcels_Davis/FeatureServer/0` |
| Salt Lake County | `https://services1.arcgis.com/99lidPhWCzftIe9K/ArcGIS/rest/services/Parcels_SaltLake/FeatureServer/0` |
| Utah County | `https://services1.arcgis.com/99lidPhWCzftIe9K/ArcGIS/rest/services/Parcels_Utah/FeatureServer/0` |
| Weber County | `https://services1.arcgis.com/99lidPhWCzftIe9K/ArcGIS/rest/services/Parcels_Weber/FeatureServer/0` |

**Example query (Utah County, bbox in WM):**

The coords below show the Utah State Capitol area as a placeholder. When running
a real query, center the bbox on the project location using a ~2 km² tile:
at Wasatch Front latitudes, `±0.01°` lon and `±0.009°` lat gives roughly that size.

```
https://services1.arcgis.com/99lidPhWCzftIe9K/ArcGIS/rest/services/Parcels_Utah/FeatureServer/0/query
  ?geometry=-111.90,40.77,-111.88,40.79
  &geometryType=esriGeometryEnvelope
  &inSR=4326&outSR=4326&f=geojson&outFields=*&where=1=1
```

For other counties: browse `https://gis.utah.gov/data/cadastre/parcels/` for the correct slug.

---

## Utah Elevation / Terrain

| Dataset | Source | Notes |
|---------|--------|-------|
| Utah DEM (10m) | UGRC | `https://gis.utah.gov/data/elevation-and-terrain/` |
| USGS National Elevation Dataset | USGS TNM | `https://apps.nationalmap.gov/downloader/` |
| Lidar (where available) | UGRC | County-by-county; search by quad |

---

## Plant Research Sources

### Species identification, care, and native range
| Source | URL | Best for |
|--------|-----|---------|
| USU Extension Yard & Garden | `https://extension.usu.edu/yardandgarden/` | Utah-specific care, water needs, hardiness |
| Utah Native Plant Society | `https://www.unps.org/` | Native range, ecology, conservation status |
| UNPS Utah Plant List | `https://www.unps.org/UtahPlantList.php` | Full Utah vascular plant catalog — machine-parseable (see below) |
| Lady Bird Johnson Wildflower Center | `https://www.wildflower.org/plants/` | Cultivation detail, regional native range |
| USDA PLANTS Database | `https://plants.usda.gov/` | Authoritative taxonomy, distribution maps |
| Plants of the World Online (Kew) | `https://powo.science.kew.org/` | Authoritative taxonomy via POWO ID |
| Intermountain Herbarium (USU) | `https://herbarium.usu.edu/` | Utah herbarium records |

### UNPS Utah Plant List — machine-parseable catalog

`UtahPlantList.php` delivers all 4,188 Utah vascular taxa in a single HTML
payload. Each entry is a `<li class="taxonline">` with structured attributes:

```html
<li id='Acer_glabrum_diffusum' n powo='1780-2' class='taxonline'
    title='native; W counties, Tooele, to the south'>
    <b>Acer glabrum var. diffusum</b> (Greene) Smiley; Rocky Mountain maple
</li>
```

| Attribute / position | Field | Example |
|----------------------|-------|---------|
| `id` attr | Taxon key (underscores for spaces) | `Acer_glabrum_diffusum` |
| `<b>` text | Scientific name + author | `Acer glabrum var. diffusum (Greene) Smiley` |
| text after `;` | Common name | `Rocky Mountain maple` |
| nearest preceding `<li f>` | Family | `Aceraceae` |
| `powo` attr | POWO ID → Kew record | `1780-2` |
| `title` attr | County/range notes | `native; W counties, Tooele, to the south` |
| bare `n` attr | Native to Utah | present/absent |
| bare `i` attr | Introduced | present/absent |
| bare `c` attr | Cultivated | present/absent |
| bare `e` attr | Endemic to Utah | present/absent |
| bare `r` attr | Rare | present/absent |

**Agent lookup pattern:**
```
1. GET https://www.unps.org/UtahPlantList.php (fetch once per session)
2. Parse all li.taxonline elements
3. Build {scientific_name → {taxon_key, powo_id, family, native, range_notes}}
4. Filter to entries with bare `n` attribute for native species
5. Construct POWO link: https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:<powo_id>
6. TaxonInfo detail page (currently unreliable): https://www.unps.org/TaxonInfo.php?id=<taxon_key>
```

**Note:** `TaxonInfo.php` is intermittently broken server-side. Use the POWO
link for authoritative taxonomy when the detail page is unavailable.

### USU TreeBrowser — structured JSON catalog

The most machine-readable Utah tree/shrub source. Fetch once per session and filter in-memory.

**JSON feed:** `https://extension.usu.edu/treebrowser/trees.json`
~400 species, 25 fields per entry:

| Field | Type | Values / notes |
|-------|------|----------------|
| `common_name` | string | e.g. `"Juniper, Rocky Mountain"` |
| `scientific_name` | string | e.g. `"Juniperus scopulorum"` |
| `family` | string | e.g. `"Cupressaceae - Cypress"` |
| `type` | string | `"Broadleaf"` or `"Conifer"` |
| `utah_native` | string | `"Yes"` / `"No"` |
| `hardiness_zone_min` | string | USDA zone number, e.g. `"3"` |
| `hardiness_zone_max` | string | USDA zone number, e.g. `"7"` |
| `growth_rate` | string | `"Low"` / `"Medium"` / `"High"` |
| `mature_height` | string | `"Low"` / `"Medium"` / `"High"` |
| `longevity` | string | `"Low"` / `"Medium"` / `"High"` |
| `crown_shape` | string | `"Oval"`, `"Broad"`, etc. |
| `drought` | string | `"Low"` / `"Medium"` / `"High"` |
| `shade` | string | `"Low"` / `"Medium"` / `"High"` |
| `salt` | string | `"Low"` / `"Medium"` / `"High"` |
| `poor_drainage` | string | `"Low"` / `"Medium"` / `"High"` |
| `alkalinity` | string | `"Low"` / `"Medium"` / `"High"` |
| `transplanting` | string | `"Low"` / `"Medium"` / `"High"` |
| `power_lines` | string | `"Yes"` / `"No"` — safe under lines |
| `cultivar_availability` | string | `"Yes"` / `"No"` |
| `bark` / `fall_color` / `flowers` / `foliage` / `fruit` | string | `"Yes"` / `"No"` — ornamental interest flags |
| `url` | string | Full URL to `.php` detail page |
| `image` | string | Full URL to thumbnail JPG |

**Detail pages:** `https://extension.usu.edu/treebrowser/catalog/<slug>.php`
Add full botanical description (leaves, twigs, flowers/fruit, bark), landscape notes, and cultivar lists not present in the JSON. Always use the `url` field from the JSON — do not construct slugs manually.

**Agent lookup pattern:**
```
1. GET https://extension.usu.edu/treebrowser/trees.json (fetch once per session)
2. Index by scientific_name and common_name
3. Filter: utah_native="Yes", int(hardiness_zone_min) <= project_zone, drought="High" or "Medium"
4. For full botanical detail: WebFetch the entry's url field
```

---

### Tree Utah — curated planting lists

**URL:** `https://www.treeutah.org/tree-guide/which-trees-to-plant`

A single HTML page of ~14 curated species lists for Utah conditions.
Common name + scientific name only per entry — no structured fields.
Useful for a quick filtered shortlist before looking up details in TreeBrowser.

| Category | Use |
|----------|-----|
| Water-Wise (large / medium / small / evergreen) | Drought-tolerant selection |
| High Elevation (>6,500 ft) | Above Wasatch Front |
| Valleys (4,000–6,500 ft) | Most Wasatch Front projects |
| Desert (<4,000 ft) | Southern Utah, St. George area |
| Utah Natives / Utah Non-Natives | Native filter |
| Climate-Adapted, Tough & Resilient | Stress-tolerant picks |
| Over-planted (avoid) | Diversity guidance |
| DO NOT Plant | Invasive species — never use |

**Agent lookup pattern:**
```
1. WebFetch https://www.treeutah.org/tree-guide/which-trees-to-plant
2. Parse HTML lists by category heading
3. Cross-reference common/scientific names against TreeBrowser JSON for full field data
```

---

### Water use / xeriscape
| Source | URL |
|--------|-----|
| Utah State University Water Research Lab | `https://uwrl.usu.edu/` |
| Slow the Flow Utah | `https://slowtheflow.org/` |
| Utah Division of Water Resources | `https://water.utah.gov/` |

### Pollinator / wildlife value
| Source | URL |
|--------|-----|
| Xerces Society | `https://www.xerces.org/` |
| Pollinator Partnership | `https://www.pollinator.org/` |

---

## USDA Hardiness Zones (Utah)

| Zone | Approximate location |
|------|---------------------|
| 4b | High mountain valleys (>7,000 ft) |
| 5a–5b | Northern Utah valleys, Wasatch foothills |
| 6a–6b | Utah County, Salt Lake Valley, most Wasatch Front |
| 7a–7b | St. George area, lower Colorado Plateau |

Interactive map: `https://planthardiness.ars.usda.gov/`

---

## CRS Reference

| EPSG | Name | Use |
|------|------|-----|
| 4326 | WGS84 (lat/lon) | Feature storage in GeoPackage |
| 32612 | UTM Zone 12N | Metric distance/area calculations (all of Utah) |
| 3857 | Web Mercator | ESRI/web tile queries |
| 26912 | NAD83 UTM Zone 12N | Some UGRC datasets |

---

## Orthophoto Sources

- **UGRC Aerial Photography**: `https://gis.utah.gov/data/aerial-photography/` — statewide coverage by county/year
- **NAIP** (1m resolution, annual): available via USDA GeoHub
- **Local orthophotos**: contact county assessor's office; often higher resolution
