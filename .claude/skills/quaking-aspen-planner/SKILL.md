---
description: Plan a Utah native plant landscape in QGIS — from blank map to PDF proposal
name: quaking-aspen-planner
---

# quaking-aspen-planner

Framework for building Utah native plant landscaping proposals in QGIS.
Load the section you need; do not load all three unless you have a reason.

| Section | File | When to load |
|---------|------|--------------|
| **Initialization** | `skills/quaking-aspen-planner-init.md` | Starting a new project session — intake questions, memory format, project structure, setup checklist |
| **Development** | `skills/quaking-aspen-planner-dev.md` | Active design work — QGIS MCP patterns, layer schema, plant research, CSV fields |
| **Report** | `skills/quaking-aspen-planner-report.md` | Generating or fixing the PDF proposal — layout setup, map/legend, troubleshooting |

## Quick start

If this is a new project or a new developer, load **Initialization** first.
If the project is already set up and you are digitizing or researching plants, load **Development**.
If the user asks to generate, export, or fix the report PDF, load **Report**.

# Rules & Tips

Hard constraints and gotchas to apply throughout the project.

---

## Plant Placement Rules

- Stay within the project boundary established during intake. Do not spread the
  design into areas outside the agreed scope.
- Keep plants with spreading or surface root systems away from hardscape
  (pavers, paths, foundations). Consult the `root` field in `plants.csv` when
  placing near any paved surface.

## Plant Data Rules

- Never invent or estimate plant data. All fields in `plants.csv` must come from
  the primary sources.
- Attempt to verify current container sizes and prices with a real Utah nursery —
  prices change seasonally. Indicate if prices cannot be verified
- If a species in the QGIS layer has no matching row in `plants.csv`, the report
  will print a WARNING. Resolve it before exporting the final PDF.
- Rebuild the species dropdown widget after every CSV change so the developer's
  manual point-placement stays in sync with the catalog.

## Design Rules

- Use only Utah-native or Utah-adapted low-water species.
- Factor in mature canopy size (`canopy_m`) when spacing plants — crowded
  placements that look fine now will cause problems at maturity.
- Wildflower seed areas count toward the budget; include them in a designated
  polygon layer and record the area.

---

## QGIS Tips

### Screenshots are expensive
`mcp__qgis__get_canvas_screenshot` embeds raw image data (~2-3 MB per call).
After several calls this approaches the 20 MB session limit.

- Prefer `mcp__qgis__render_map` for lightweight visual checks.

### Check layer CRS before transforming
Not all layers are in EPSG:4326. Call `layer.crs().authid()` first — if the
layer is already in EPSG:32612, skip the transform or you will get wrong coordinates.
