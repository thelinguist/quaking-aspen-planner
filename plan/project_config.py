"""
project_config.py — Edit this file to configure your project.
This is the primary developer touchpoint: set your project details,
file paths, and report appearance here before running any scripts.
"""

# ── Project metadata ──────────────────────────────────────────────────────────
PROJECT = {
    "name":      "My Native Plant Project",
    "subtitle":  "Utah Native Landscaping Proposal",
    "location":  "County, UT",
    "usda_zone": "6-7",
    "budget_usd": 2000,
    # Optional: absolute path to a site photo shown on the report cover page.
    # Set to None to omit the photo.
    "photo_path": None,
    # Caption shown beneath the photo.
    "photo_caption": "Site overview",
    # Width × height in pixels at the report's export DPI.
    "photo_width_px":  533,
    "photo_height_px": 400,
}

# ── Paths ─────────────────────────────────────────────────────────────────────
# All paths are absolute. The AI agent sets these during project setup.
PATHS = {
    # QGIS project file — lives in plan/
    "qgis_project":  None,   # e.g. "/path/to/repo/plan/project.qgz"
    # Plant catalog CSV — lives in plan/
    "plants_csv":    None,   # e.g. "/path/to/repo/plan/plants.csv"
    # Plant images directory — lives in resources/images/
    "images_dir":    None,   # e.g. "/path/to/repo/resources/images"
    # Optional orthophoto GeoTIFF
    "orthophoto":    None,
    # Output PDF
    "output_pdf":    None,   # e.g. "/path/to/repo/output/report.pdf"
}

# ── GIS / QGIS settings ───────────────────────────────────────────────────────
GIS = {
    # CRS used for storing all vector features.
    "crs_storage": "EPSG:4326",
    # Metric CRS for area / distance calculations (UTM Zone 12N covers all of Utah).
    "crs_metric": "EPSG:32612",
    # Name of the QGIS print layout to export.
    "layout_name": "Project Report",
    # PDF export DPI.
    "export_dpi": 150,
}

# ── ESRI basemap layers ───────────────────────────────────────────────────────
# setup_project.py loads these into every new project.
# Add or remove entries to change which basemaps are available.
ESRI_LAYERS = [
    {
        "name": "ESRI World Imagery",
        "url":  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    },
    {
        "name": "ESRI World Street Map",
        "url":  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
    },
]

# ── Report appearance ─────────────────────────────────────────────────────────
# These values are injected into the report CSS. Change colors and fonts here
# to restyle the entire report without touching the script logic.
REPORT_THEME = {
    # Headings and primary borders
    "primary_color":    "#1a4a1c",
    # Subheadings and table header backgrounds
    "secondary_color":  "#2c5f2e",
    # Section row backgrounds in tables
    "accent_color":     "#c8e6c9",
    # Grand-total row
    "total_row_color":  "#e8f5e8",
    # City-side badge
    "city_bg":          "#d4edda",
    "city_text":        "#155724",
    # Our-side badge
    "ours_bg":          "#cce5ff",
    "ours_text":        "#004085",
    # Water need indicators
    "water_color":      "#2980b9",
    "water_mod_color":  "#f39c12",
    # Typography
    "font_family":      "Arial, sans-serif",
    "font_size_body":   "9pt",
    "font_size_small":  "8pt",
    "font_size_note":   "7.5pt",
    "page_margin":      "8px",
}

# ── Materials and non-plant costs ─────────────────────────────────────────────
# Add, remove, or edit rows to match your project's materials.
# Format: (description, qty, unit, unit_price_usd)
MATERIALS = [
    ("Bark mulch (3 in depth)",       3,  "cu yd", 30.0),
    ("Compost / soil amendment",       2,  "cu yd", 22.0),
    ("Drip emitters + tubing",         1,  "set",   120.0),
    ("Plant stakes, flags, labels",    1,  "set",    30.0),
]

TAX_RATE = 0.087   # County sales tax — adjust for your county

# ── Plant catalog ─────────────────────────────────────────────────────────────
# Plant data lives in plan/plants.csv — do not duplicate it here.
# The AI agent populates the CSV by researching each species at runtime.
# generate_report.py reads the CSV directly via PATHS["plants_csv"].

