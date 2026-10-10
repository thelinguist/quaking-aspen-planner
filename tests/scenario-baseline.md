# Baseline Test Scenario

A fixed intake scenario for evaluating the `/quaking-aspen-planner` skill.
Run through this scenario in a fresh session and check each item in the
verification checklist at the bottom.

---

## Canned Site

Use these answers verbatim when the agent asks each intake question.

| Field            | Value                                                                                                                                                                                                                    |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Location         | Pleasant Grove, Utah County, UT — roughly 200 W State St                                                                                                                                                                 |
| USDA zone        | 6b (agent should derive this; confirm if asked)                                                                                                                                                                          |
| Site description | 20x20 plot front yard and parkstrip. Existing lawn, one large spruce near the house, concrete driveway on the right side. Goal is to replace the lawn with low-water natives, add pollinator plants along the parkstrip. |
| Budget           | $2,000                                                                                                                                                                                                                   |
| Approval needed  | Yes — HOA. No specific rules known beyond "no xeriscape that looks neglected."                                                                                                                                           |
| QGIS installed   | Yes                                                                                                                                                                                                                      |
| QGIS experience  | New to QGIS, has not used the Python console                                                                                                                                                                             |
| Orthophoto       | No — decline the offer to find one                                                                                                                                                                                       |

---

## Expected Intake Behavior

Check that the agent:

- [ ] Displays the intro text before asking any questions
- [ ] Asks questions **one topic at a time**, not all at once
- [ ] Derives zone 6b from Utah County / ~4,500 ft elevation without asking the
      elevation follow-up (Pleasant Grove is unambiguous)
- [ ] Triggers the HOA follow-up after "yes" to approval question, then moves on
      when no specific rules are provided
- [ ] Offers UGRC/NAIP as orthophoto sources when declined, then moves on without
      blocking
- [ ] Does **not** ask the Python console follow-up (experience is clearly stated
      as "new")

---

## Expected Memory Output

After intake the agent should save two memory files. Check the values match
the scenario inputs.

### User memory (`developer_profile`)

```
QGIS experience: beginner
Python console: no
Maintenance capacity: (not stated — field may be blank or omitted)
Preferences: low-water natives, pollinators, avoid neglected-looking xeriscape
```

### Project memory (`project_site`)

```
Location: Pleasant Grove, Utah County, UT — ~200 W State St
USDA zone: 6b
UTM zone: EPSG:32612 (Utah)
Site description: ~20' x 20' front yard; existing lawn,
  one large spruce near house, concrete driveway on right side
Landscaping type: lawn replacement
Budget: $2,000
Municipal approval needed: yes — HOA; no specific rules beyond aesthetics
Regulatory constraints: avoid neglected-looking xeriscape appearance
Physical constraints: spruce root zone near house; concrete driveway setback
Orthophoto: not available
```

---

## Expected Post-Intake Actions

After saving memory, the agent should proceed through the Setup Checklist:

- [ ] Prompts user to edit `plan/project_config.py` with the site name and location
- [ ] Gives clear instructions for running `setup_project.py` from the QGIS Python
      console, including the two-line import pattern (beginner path — no assumed
      console familiarity)
- [ ] After setup, calls `set_canvas_extent` to zoom to a ~2 km² bbox centered on
      Pleasant Grove (~-111.738, 40.364); canvas should not open on the world extent
- [ ] Does **not** proceed to plant placement before confirming layers loaded correctly

---

## Edge Cases Covered by This Scenario

| Scenario | What it tests |
|----------|---------------|
| HOA with vague rules | Follow-up fires, then gracefully exits without blocking |
| No orthophoto | Offer path runs, decline is accepted, setup continues |
| Beginner QGIS user | Console instructions are detailed, not terse |
| Spruce near house | Physical constraint captured in memory for later placement rules |
| Budget stated mid-answer | Agent extracts it from free-form site description |

# Run Log


## Actual Intake Behavior

Check that the agent:

- [x] Displays the intro text before asking any questions
- [x] Asks questions **one topic at a time**, not all at once
- [ ] Derives zone 6b from Utah County / ~4,500 ft elevation without asking the
  elevation follow-up (Pleasant Grove is unambiguous)
- [x] Triggers the HOA follow-up after "yes" to approval question, then moves on
  when no specific rules are provided
- [x] Offers UGRC/NAIP as orthophoto sources when declined, then moves on without
  blocking
- [x] Does **not** ask the Python console follow-up (experience is clearly stated
  as "new")

**Failures**: derived zone 6a, but I was only specific to the neighborhood


---

## Actual Memory Output

After intake the agent should save two memory files. Check the values match
the scenario inputs.

### User memory (`developer_profile`)

```
---
name: developer_profile
type: user
description: Developer background, QGIS experience, and working preferences
---
QGIS experience: beginner/light
Python console: little experience — AI should handle console work and walk through manual steps
Maintenance capacity: unknown
Preferences: dense native drought-hardy trees and shrubs; practical trail access (gate + pavers)
```
**failures**: never asked about maintenance capacity


### Project memory (`project_site`)

```
---
name: project_site
type: project
description: Site location, intent, constraints, and regulatory context
---
Location: Central Pleasant Grove, Utah County, Utah
USDA zone: 6a (5,500 ft elevation)
UTM zone: EPSG:32612 (Utah)
Site description: 20x20 sq ft plot, bordered by pavers on all sides except a city trail on the other.
Landscaping type: Dense native drought-hardy trees and shrubs; gate modification to fence; pavers for trail access from property
Budget: $2,000
Municipal approval needed: Yes — HOA approval required (hoa has strict bylaws, proposal required)
Regulatory constraints: No trees within 5' of the trail
Physical constraints: Pavers near trail side — keep root-spreading species away from hardscape. Trees restricted to fence side of strip given 8' width and 5' setback rule.
Orthophoto: none
```


---

## Expected Post-Intake Actions

After saving memory, the agent should proceed through the Setup Checklist:

- [x] Prompts user to edit `plan/project_config.py` with the site name and location
- [x] Gives clear instructions for running `setup_project.py` from the QGIS Python
  console, including the two-line import pattern (beginner path — no assumed
  console familiarity)
- [x] After setup, calls `set_canvas_extent` to zoom to a ~2 km² bbox centered on
  Pleasant Grove (~-111.738, 40.364); canvas should not open on the world extent
- [x] Does **not** proceed to plant placement before confirming layers loaded correctly
