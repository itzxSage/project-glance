# Project Glance

A live, auto-updating project dashboard for Jared: **Dashboard**, **Tasks**, a
**Work Together** shared workspace, and a **Calendar**. It consolidates work from
the native Kanban board, the OpenViking knowledge vault, and Google Calendar into
one spot (replacing the old ChatGPT "space tab" workflow).

The page is data-driven: it reads `/data/*.json` and re-fetches every 30 s, so any
change to the data sources shows up automatically.

---

## Delivery (GitHub Pages)

This repo (`itzxSage/project-glance`, main branch) holds the working site:

- Static SPA (`index.html`, `app.js`, `styles.css`)
- `data/` — generated task/knowledge/projects/calendar JSON
- `.github/workflows/glance-sync.yml` — hourly auto-sync action

To publish: GitHub **Settings → Pages → Deploy from a branch → main → `/**.**
GitHub Pages then serves `https://itzxSage.github.io/project-glance/`. The hourly
`Glance auto-sync` action keeps the site current: every run re-runs
`python3 sync.py --demo`, commits any changed `data/` files to main, and Pages
re-builds — so the site stays live and current without you touching it.

---

## Run locally (no install)

```bash
python3 sync.py --demo    # regenerate data/*.json
python3 serve.py          # -> http://127.0.0.1:8000

Kanban tasks in the dashboard come from the repo root `kanban.json` (the live-native
Kanban snapshot). If it is absent, sync.py falls back to the built-in snapshot so the
site is never empty. Drop your exported `kanban.json` into the repo root and the hourly
auto-sync action will pick up any native-Kanban change and push it to `main`.

The auto-sync pipeline is: sync.py --demo -> commit changed data/ -> push main -> Pages
re-build. So it updates as Kanban (or the vault, or repos) change, with no manual rebuild.
```

---

## Views

- **Dashboard** — project cards, task counts (total/done/open), "next actions"
  (top 5 by priority), refresh timestamp.
- **Tasks** — filterable/sortable list; inline title edit; "Work together" jump;
  done-toggle (does not write back to Kanban).
- **Work Together** — shared notes feed + "Save note" (POSTs to `/api/notes`).
- **Calendar** — shown only when calendar data exists; otherwise a clear "not yet
  wired" card (see below).

---

## Google Calendar (the one consent gate)

Calendar wiring needs **your Google account sign-in** — no data is invented.

1. Run the Google Workspace skill's auth setup:
   ```bash
   cd /Users/jrsgagne/.hermes/skills/productivity/google-workspace
   python3 setup.py --auth-url        # complete the browser consent
   ```
2. Make sure the `gws` CLI is available (the same setup), then any later `sync.py
   --demo` will pull real calendar events and flip `calendar_wired` to `true`.

Until that happens the app shows a clear placeholder so nothing looks filled in by
guess. When you come back, run `python3 sync.py --demo` again and the calendar
view will populate.

## Source ownership (authoritative truth today)

- Tasks → native Kanban (canvas-tool-backed). Snapshot is root `kanban.json`;
  a scheduled refresher rewrites it when Kanban changes.
- Knowledge → OpenViking `agent-memory/20-Projects` vault (canonical durable KB).
- Projects → curated `itzxSage` repo index + vault entries.
- Calendar → Google via Google Workspace CLI (consent-gated, see above).

## Legacy

- `agent-memory/20-Projects` (Cash-Mission, Harness-Fleet, Hermes, LifeOS) is the
  durable OpenViking vault for this workspace.
- `personal-secretary` (itzxSage) is the related LifeOS personal assistant repo;
  it is a separate project and not required to run Project Glance.
