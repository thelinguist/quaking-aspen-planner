# Utah Native Plants QGIS Framework

A starter AI framework for designing native plant landscaping projects in Utah — using QGIS and real data sources to go from a blank map to a finished proposal PDF.

---

## What this does

This project helps you plan a native plant landscape by combining:

- **A map** — you compose your site in QGIS, placing plants exactly where you want them
  - it instructs the AI agent to fetch base maps like aerial photos and county parcel maps.
- **A plant catalog** — an AI agent researches each species you choose and records real data (water needs, mature size, price, planting instructions) from Utah-specific sources
- **A report** — a PDF that includes a cost estimate, planting map, species specifications, and instructions — ready to share with a contractor, HOA, or city

The goal is a low-water, Utah-native design that you and an AI can build together interactively.

---

## Scope

- **Geography:** Utah, USDA hardiness zones 4–7
- **Plant types:** Native and Utah-adapted trees, shrubs, perennials, and wildflower mixes
- **Output:** A multi-page PDF proposal — budget, plant schedule, map, and planting instructions
- **Who it's for:** Homeowners, landscape designers, or anyone who wants a documented native plant plan and is comfortable learning QGIS and an AI coding assistant

This is not a plant encyclopedia. Plant data is looked up at runtime from primary sources — the AI researches each species you add to the map.

---

## What is QGIS?

QGIS is a free, open-source mapping application, popular with city planners especially in Europe. It lets you draw on top of base maps and include technical data for planning.

In this project you use QGIS to:
- View an aerial photo of your site
- Draw your property boundary and any site features
- Drop a point for each plant you want to place
- See the finished design as a map

QGIS runs on your computer. Download it free at **https://qgis.org**.

---

## How the AI fits in

Your AI agent can use the [QGIS plugin](https://plugins.qgis.org/plugins/qgis_mcp_plugin/) an MCP server to allow it to manipulate your QGIS file. It will also:
- Look up plant data from primary sources like USU Extension, UNPS, and other Utah sources
- Place and space plants on the map programmatically
- work with QGIS to make a PDF report including the map, budget, bill of materials, etc.

You and the AI work together — you make design decisions, the AI handles the data and map operations. And you can always plot things yourself alongside AI.

---

## Getting started

### 1. Install QGIS

Download and install QGIS from **https://qgis.org**. The Long Term Release (LTR) version is recommended.

### 2. Install the QGIS MCP plugin

The [MCP QGIS plugin](https://plugins.qgis.org/plugins/qgis_mcp_plugin/) plugin lets an AI assistant control QGIS from a chat session.
Install it from the QGIS Plugin Manager or follow the instructions in the plugin repository.

### 3. Clone this repository

```bash
git clone <repo-url>
cd framework
```
Or download it from the github page as a zip

### 4. Configure your project

Open `plan/project_config.py` in any text editor. Fill in:

- Your project name and location
- Absolute file paths for the QGIS project, plants CSV, images folder, and output PDF
- Your budget
- Any changes to the report color theme or materials list

### 5. Start a session with your AI assistant

The skill files live in `.claude/skills/` and are available automatically in any
Claude Code session opened from this directory. To activate the skill, type:

```
/quaking-aspen-planner
```

in the Claude Code input box. The skill will:

1. Ask you a few questions about your site
2. Walk you through running `setup_project.py` to initialize the QGIS project
3. Help you digitize your site and place plants
4. Research each species and populate `plan/plants.csv`
5. Generate the final PDF via `generate_report.py`

---

## Project layout

```
framework/
├── plan/
│   ├── project_config.py   ← start here — configure your project
│   ├── plants.csv          ← populated by AI at runtime
│   └── <project>.qgz       ← your QGIS project file (created by setup script)
├── output/                 ← exported PDFs go here
├── scripts/
│   ├── setup_project.py    ← run once to initialize QGIS layers and basemaps
│   └── generate_report.py  ← run to build and export the PDF
├── resources/
│   ├── data_sources.md     ← all research URLs and data source details
│   └── images/             ← plant photos fetched by AI
└── .claude/
    └── skills/
        ├── quaking-aspen-planner.md       ← skill index — run /quaking-aspen-planner to start
        ├── quaking-aspen-planner-init.md  ← loaded automatically for new projects
        └── quaking-aspen-planner-dev.md   ← loaded automatically for active design work
```

---

## Data sources

Plant data is pulled at runtime from:

| Source | What it provides |
|--------|-----------------|
| USU Extension Yard & Garden | Utah-specific care, water needs, hardiness |
| UNPS Utah Plant List | Full Utah native plant catalog (4,188 taxa, machine-parseable) |
| USU TreeBrowser | ~400 Utah trees/shrubs with structured JSON (drought, height, native flag) |
| Lady Bird Johnson Wildflower Center | Mature size, soil, root system, cultivation detail |
| USDA PLANTS Database | Authoritative taxonomy and hardiness zones |

See `resources/data_sources.md` for full details, API endpoints, and agent lookup patterns.
