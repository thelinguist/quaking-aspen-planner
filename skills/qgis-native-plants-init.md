# qgis-native-plants — Initialization

Run this section at the start of every new project session.

---

## Developer Intake

Before doing anything else, check memory for an existing intake profile.
If one exists, confirm with the developer that it is still current.
If none exists, print out the intro, then work through the questions below **one topic at a time** —
do not dump all questions at once. Listen to each answer, ask a follow-up if
needed, then move on.

### Intro
Display the following text to the user before continuing.

> This agent skill will set you up with a qGIS project, an open source app for mapping. It will then connect the agent
> to the program so it can automate tedious tasks and work alongside you as you plan out your landscaping. First I'll
> ask a few quick questions to understand your background and goals. Then we'll set up the project with some baseline items in the map. Then we'll get designing!
> 
> Are you ready?

### Questions to ask

**1. Where is the site?**
Ask for city, county, and a rough address or neighborhood.
Derive USDA zone and confirm it.
↳ *Follow-up only if zone is uncertain:* Is the site above or below 5,500 ft elevation?

**2. Describe the site and what you want to do.**
One open question — let them describe size, features, and intent freely.
Note anything they mention about budget, restrictions, or existing features.
↳ *Follow-up only if budget not mentioned:* Do you have a budget in mind?

**3. Will this need approval from a city, HOA, or other authority?**
A yes/no anchor. If no, move on immediately.
↳ *Follow-up only if yes:* What body, and do you know of any specific rules
  (setbacks, height limits, water-use restrictions)?

**4. Have you installed QGIS and the MCP plugin?**
If yes and they seem experienced, move on.
If no: direct them to qgis.org and the MCP plugin repo and pause —
nothing else can proceed until QGIS is running.
↳ *Follow-up only if yes but experience unclear:* How comfortable are you
  with QGIS — have you used the Python console before?

**5. Do you have an orthophoto of the site?**
If yes, ask for the file path and set `PATHS["orthophoto"]` in `plan/project_config.py`.
If no, ask if they'd like help finding one — offer UGRC or NAIP
(see `resources/data_sources.md`). If they don't want one, move on.
↳ *Follow-up only if they want help:* Walk them through the UGRC aerial
  photography page for their county.

---

### Memory formats

Save a **user memory** after intake:
```
---
name: developer_profile
type: user
description: Developer background, QGIS experience, and working preferences
---
QGIS experience: <level>
Python console: <yes/no/unsure>
Maintenance capacity: <summary>
Preferences: <any stated plant/style preferences>
```

Save a **project memory** after intake:
```
---
name: project_site
type: project
description: Site location, intent, constraints, and regulatory context
---
Location: <city, county, state> — <address or parcel if known>
USDA zone: <derived>
UTM zone: EPSG:32612 (Utah)
Site description: <summary>
Landscaping type: <type>
Budget: $<amount>
Municipal approval needed: <yes/no/details>
Regulatory constraints: <summary>
Physical constraints: <setbacks, utilities, root-sensitive surfaces>
Orthophoto: <path or "not available" or "pending UGRC download">
```

---

## Project Structure

```
repo/
├── plan/
│   ├── project_config.py   ← developer config (theme, paths, materials)
│   ├── plants.csv          ← plant catalog, populated by AI at runtime
│   └── <project>.qgz       ← QGIS project file
├── output/                 ← exported PDFs
├── scripts/
│   ├── setup_project.py    ← initialize QGIS project (run once)
│   └── generate_report.py  ← build and export PDF report
├── resources/
│   ├── data_sources.md     ← research URLs and data source reference
│   └── images/             ← plant photos fetched by AI
└── skills/
    └── qgis-native-plants.md ← skill index
```

## Setup Checklist

1. Edit `plan/project_config.py` — set project name, location, paths, theme
2. Run `setup_project.py` from the QGIS Python console to create layers and basemaps
3. Use QGIS + AI to digitize site features and place plants on `proposed_plants`
4. For each species placed, research it and append a row to `plan/plants.csv`
5. Run `generate_report.py` to produce the PDF
