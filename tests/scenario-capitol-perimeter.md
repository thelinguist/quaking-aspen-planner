# Eval Scenario: Capitol Perimeter Trees

Redesign the Utah State Capitol grounds with one drought-resistant tree every
5 meters around the perimeter. User has no QGIS experience and wants maximum
automation.

---

## Canned Intake Answers

| Field | Value                                                                                                                              |
|-------|------------------------------------------------------------------------------------------------------------------------------------|
| Location | Utah State Capitol, Salt Lake City, Salt Lake County — 350 N State St, SLC                                                         |
| USDA zone | 6b (agent should derive; do not offer it)                                                                                          |
| Site description | The perimeter of the Utah State Capitol building. I want one drought-resistant tree placed every 5 meters around the outside edge. |
| Budget | No budget constraint                                                                                                               |
| Approval needed | No                                                                                                                                 |
| QGIS installed | Yes                                                                                                                                |
| QGIS experience | None — I want the agent to do as much as possible for me                                                                           |
| Orthophoto | no                                                                                                                                 |

---

## Expected Intake Behavior

- [ ] Does **not** ask the elevation follow-up (Salt Lake City zone is unambiguous)
- [ ] Does **not** ask the Python console follow-up (no experience stated)

---

## Expected QGIS Operations

This scenario is mostly automated. The agent should drive QGIS via MCP with
minimal prompting after intake.

- [ ] Zooms canvas to a ~2 km² bbox centered on the Capitol (~-111.90, 40.77)
- [ ] Digitizes or asks user to confirm a perimeter polygon around the Capitol building
      on the `management_bounds` or a new boundary layer — does not ask the user to
      draw it manually
- [ ] Calculates the perimeter length and derives the number of trees:
      perimeter ÷ 5 m = point count (Capitol building footprint is ~320 m → ~64 trees)
- [ ] Generates evenly-spaced points along the perimeter and adds them to
      `proposed_plants` — does not ask the user to place each point manually
- [ ] Assigns a placeholder species to all points (to be filled by research step)

---

## Expected Plant Research

- [ ] Filters to drought-resistant (`drought: High` or `Medium`) Utah-native trees
      from USU TreeBrowser JSON
- [ ] Selects a single species appropriate for zone 6b and urban conditions
      (Capitol grounds = compacted soil, reflected heat, limited root space)
- [ ] Populates all ~64 rows in `plants.csv` with that species
- [ ] Updates the `species` field on all `proposed_plants` features in QGIS

Acceptable species examples (agent may choose differently — check the reasoning):
- *Quercus gambelii* (Gambel oak) — native, drought-tolerant, zone 4–8
- *Pinus edulis* (Pinyon pine) — native, xeric, zone 5–8
- *Juniperus scopulorum* (Rocky Mountain juniper) — native, drought-tolerant, zone 3–7

---

## Expected Memory Output

### User memory (`developer_profile`)
```
QGIS experience: none
Python console: no
Maintenance capacity: (not stated)
Preferences: maximum automation, drought-resistant trees, uniform perimeter spacing
```

### Project memory (`project_site`)
```
Location: Utah State Capitol, Salt Lake City, Salt Lake County — 350 N State St
USDA zone: 6b
UTM zone: EPSG:32612 (Utah)
Site description: perimeter of the Capitol building; one drought-resistant tree every 5 m
Landscaping type: uniform tree planting along perimeter
Budget: none specified
Municipal approval needed: no
Regulatory constraints: none stated
Physical constraints: urban hardscape, compacted soils likely
```

---

## Automation Quality Check

Since the user asked for maximum automation, penalize any step where the agent
stops and asks the user to do something a MCP tool could handle.

| Step | Should be automated | Acceptable to ask |
|------|--------------------|--------------------|
| Zoom to site | Yes | No |
| Draw perimeter boundary | Agent should propose and confirm, not hand off | Confirm the boundary shape |
| Calculate point count | Yes | No |
| Place points along perimeter | Yes | No |
| Choose species | Agent proposes, user confirms | Confirm the species choice |
| Populate CSV | Yes | No |
| Update QGIS features | Yes | No |

---

## Run Log


## Actual Intake Behavior

- [x] Does **not** ask the elevation follow-up (Salt Lake City zone is unambiguous)
- [x] Does **not** ask the Python console follow-up (no experience stated)

---

## Actual QGIS Operations

This scenario is mostly automated. The agent should drive QGIS via MCP with
minimal prompting after intake.

- [x] Zooms canvas to a ~2 km² bbox centered on the Capitol (~-111.90, 40.77)
- [x] Digitizes or asks user to confirm a perimeter polygon around the Capitol building
  on the `management_bounds` or a new boundary layer — does not ask the user to
  draw it manually
- [x] Calculates the perimeter length and derives the number of trees:
  perimeter ÷ 5 m = point count (Capitol building footprint is ~320 m → ~64 trees)
- [x] Generates evenly-spaced points along the perimeter and adds them to
  `proposed_plants` — does not ask the user to place each point manually
- [x] Assigns a placeholder species to all points (to be filled by research step)

**failures**: placed trees around another city block instead

---

## Actual Plant Research

- [x] Filters to drought-resistant (`drought: High` or `Medium`) Utah-native trees
  from USU TreeBrowser JSON
- [x] Selects a single species appropriate for zone 6b and urban conditions
  (Capitol grounds = compacted soil, reflected heat, limited root space)
- [x] Populates all ~64 rows in `plants.csv` with that species
- [x] Updates the `species` field on all `proposed_plants` features in QGIS

Acceptable species examples (agent may choose differently — check the reasoning):
- *Quercus gambelii* (Gambel oak) — native, drought-tolerant, zone 4–8
- *Pinus edulis* (Pinyon pine) — native, xeric, zone 5–8
- *Juniperus scopulorum* (Rocky Mountain juniper) — native, drought-tolerant, zone 3–7

---

## Expected Memory Output

### User memory (`developer_profile`)
```
---
name: developer_profile
type: user
description: Developer background, QGIS experience, and working preferences
---
QGIS experience: none
Python console: no
Maintenance capacity: (not stated)
Preferences: maximum automation, drought-resistant trees, uniform perimeter spacing
```

### Project memory (`project_site`)
```
---
name: project_site
type: project
description: Site location, intent, constraints, and regulatory context
---
Location: Utah State Capitol, Salt Lake City, Salt Lake County — 350 N State St, SLC
USDA zone: 6b
UTM zone: EPSG:32612 (Utah)
Site description: perimeter of the Capitol building; one drought-resistant tree every 5 m around the outside edge
Landscaping type: uniform tree planting along perimeter
Budget: none specified
Municipal approval needed: no
Regulatory constraints: none stated
Physical constraints: urban hardscape, compacted soils likely
Orthophoto: ESRI World Imagery basemap (loaded by setup)
```
