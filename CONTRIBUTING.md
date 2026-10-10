# Contributing

## Core design principle

This project gives an AI agent **pointers to live data sources**, not precompiled copies of that data. The agent fetches and interprets data at runtime — plant catalogs, parcel records, hardiness zones — so results stay current and the repo stays lean.

**Do this:**
```
# resources/data_sources.md
| USU TreeBrowser | https://extension.usu.edu/treebrowser/trees.json | ~400 Utah trees/shrubs, structured JSON |
```

**Not this:**
```
# resources/utah_trees.json  ← 400-row snapshot that will go stale
```

When adding a new data source, document it in `resources/data_sources.md` with the URL, data format, and an agent lookup pattern. The skill can then fetch it live.

---

## What goes where

| Location | Purpose |
|----------|---------|
| `resources/data_sources.md` | URLs, API patterns, and agent lookup instructions for external data |
| `.claude/skills/` | Agent instructions — what to do, not what to know |
| `plan/project_config.py` | User-facing configuration (paths, theme, budget) |
| `scripts/` | Standalone Python scripts that run in the QGIS console |
| `tests/` | Eval scenarios and run logs |

## Adding a skill section

The skill is split into focused sections (init, dev) to avoid loading a monolithic prompt. If a new phase of work is large enough to warrant its own section, follow the same pattern: create `quaking-aspen-planner-<section>.md` and add it to the table in `quaking-aspen-planner.md`.

## Expanding to other regions

The project is scoped to Utah / Wasatch Front. If you adapt it for another region, the main changes are in `resources/data_sources.md` (add a regional section) and `plan/project_config.py` (update CRS and zone defaults). The skill instructions themselves should need minimal changes.

**Example: adding Colorado alongside Utah**

In `resources/data_sources.md`, add a Colorado section following the same pattern — URL, data format, agent lookup instructions:

```markdown
## Colorado Plant Research Sources

| Source | URL | Best for |
|--------|-----|---------|
| Colorado Native Plant Society | https://conps.org/ | Native range, conservation status |
| CSU Extension | https://extension.colostate.edu/ | Care, water needs, Front Range specifics |
| Colorado State Forest Service | https://csfs.colostate.edu/ | Tree species, planting guides |

## Colorado Parcel Data

Colorado county parcels are served by individual county GIS portals — no single
statewide endpoint like UGRC. Front Range counties:

| County | Parcel URL |
|--------|-----------|
| Jefferson | https://data-jeffco.opendata.arcgis.com/ |
| Denver | https://www.denvergov.org/opendata |
| Boulder | https://opendata-bouldercounty.hub.arcgis.com/ |
```

In `plan/project_config.py`, the only fields that change per region are the metric CRS
(Colorado's Front Range is UTM Zone 13N) and the county parcel URL the agent queries:

```python
GIS = {
    "crs_storage": "EPSG:4326",
    "crs_metric": "EPSG:32613",   # UTM Zone 13N — Colorado Front Range
                                   # (Utah uses 32612 — Zone 12N)
    ...
}
```

Nothing in the skill files needs to change — the agent reads the region from
`project_config.py` and picks the right data sources from `data_sources.md` based
on what the user provides during intake.
