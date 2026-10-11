"""
setup_project.py — Initialize a new native-plant QGIS project.

Run once from the QGIS Python console:
    import sys; sys.path.insert(0, '/path/to/repo')
    exec(open('/path/to/repo/scripts/setup_project.py').read())

Creates ESRI basemaps, an optional orthophoto, and a standard set of
empty vector layers. Edit config/project_config.py before running.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qgis.core import (
    QgsProject, QgsRasterLayer, QgsVectorLayer,
    QgsCoordinateReferenceSystem,
)
from qgis.PyQt.QtCore import QVariant
from plan.project_config import PROJECT, GIS, ESRI_LAYERS

proj = QgsProject.instance()
proj.setTitle(PROJECT["name"])
proj.setCrs(QgsCoordinateReferenceSystem(GIS["crs_storage"]))

# ── ESRI basemaps ─────────────────────────────────────────────────────────────
for lc in reversed(ESRI_LAYERS):
    uri = f"type=xyz&url={lc['url']}&zmax=19&zmin=0"
    layer = QgsRasterLayer(uri, lc["name"], "wms")
    if layer.isValid():
        proj.addMapLayer(layer)
        print(f"  basemap: {lc['name']}")
    else:
        print(f"  WARNING: could not load {lc['name']}")

# ── Optional orthophoto ───────────────────────────────────────────────────────
if GIS.get("orthophoto_path"):
    layer = QgsRasterLayer(GIS["orthophoto_path"], "orthophoto", "gdal")
    if layer.isValid():
        proj.addMapLayer(layer)
        print("  orthophoto loaded")
    else:
        print(f"  WARNING: orthophoto not valid — check path: {GIS['orthophoto_path']}")

# ── Standard vector layers ────────────────────────────────────────────────────
# Each entry: (layer_name, geometry_type, [(field_name, QVariant_type), ...])
# Geometry types: Point, LineString, Polygon
STANDARD_LAYERS = [
    ("management_bounds", "LineString", [("side",      QVariant.String)]),
    ("wildflower_areas",  "Polygon",    [
        ("side",      QVariant.String),
        ("patch_num", QVariant.Int),
    ]),
    ("proposed_plants",   "Point",      [
        ("species",     QVariant.String),
        ("common_name", QVariant.String),
        ("plant_type",  QVariant.String),
        ("side",        QVariant.String),   # "city" or "ours"
        ("canopy_m",    QVariant.Double),
    ]),
]

crs = GIS["crs_storage"]
for name, geom, fields in STANDARD_LAYERS:
    field_str = "&".join(
        f"field={fn}:{QVariant.typeToName(ft).lower()}"
        for fn, ft in fields
    )
    uri = f"{geom}?crs={crs}&{field_str}"
    layer = QgsVectorLayer(uri, name, "memory")
    if layer.isValid():
        proj.addMapLayer(layer)
        print(f"  layer: {name}")
    else:
        print(f"  WARNING: could not create layer {name}")

# ── Save ──────────────────────────────────────────────────────────────────────
if GIS.get("project_path"):
    proj.write(GIS["project_path"])
    print(f"\nProject saved → {GIS['project_path']}")
else:
    print("\nProject created (unsaved). Set GIS['project_path'] in config/project_config.py to save.")
