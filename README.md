# Project Glance

A live, auto-updating project dashboard for Jared: **Dashboard**, **Tasks**, a
**Work Together** shared workspace, and a **Calendar**. It consolidates work from
the native Kanban board, the OpenViking knowledge vault, and Google Calendar into
one spot (replacing the old ChatGPT "space tab" workflow).

The page is data-driven: it reads `/data/*.json` and re-fetches every 30 seconds,
so any change to the data sources shows up automatically.

## Run it locally (no install)

```bash
python3 sync.py --demo    # regenerate data/*.json
python3 serve.py          # → http://127.0.0.1:8000
```

Open http://127.0.0.1:8000 (the browser must fetch /data via http, so use `serve.py`
rather than double-clicking `index.html`).

## How the data flows

```
Kanban tasks  ──► data/tasks.json      (read from root kanban.json snapshot)
OpenViking    ──► data/knowledge.json  (agent-memory/20-Projects vault)
Curated repos ──► data/projects.json
Google Calendar ─► data/calendar.json  (NOT WIRED — returns wired:false)
```

- `sync.py --demo` → regenerates everything and prints a quick summary.
- `scripts/auto-sync.sh` → the same, safe to call from a scheduled job.
- Point the auto-runner at `scripts/auto-sync.sh` (Hermes autotask or macOS cron)
  so the page "updates as we go."

## Views

- **Dashboard** — project cards, task counts (total/done/open), "next actions"
  (top 5 by priority), refresh timestamp.
- **Tasks** — filterable/sortable list; inline title edit; "Work together" jump;
  done-toggle (does not write back to Kanban).
- **Work Together** — shared notes feed + "Save note" (POSTs to `/api/notes`).
- **Calendar** — shown only when calendar data exists; otherwise a clear "not
  yet wired" card.

## Google Calendar

OAuth is **not configured**. `data/calendar.json` currently reports `wired:false`.
Wiring needs a Google-account sign-in through the google-workspace skill
(`gws_bridge.py` / `google_api.py`), then wiring `sync.py`'s `calendar_adapter()`.
No real events are invented.

## Deploy (appoint deploy path — no hosting claimed here)

The site is a static SPA + `data/*.json`; any static host works. The low-cost,
no-new-subscription path is GitHub Pages under this repo. Suggested CI:
a GitHub Action that runs `sync.py --demo` and publishes the `data/` + static
files to the `gh-pages` site. Exchange `jared-project-glance` with Jared's chosen
host/domain. **This repo is a new, ownable Project Glance. The existing
`https://jared-project-glance.jrsgagne.chatgpt.site` is a separate site and must
not be overwritten without an explicit go-ahead.**

## Source ownership (authoritative truth today)

- Tasks → native Kanban (canvas-tool-backed). Snapshot is root `kanban.json`;
  a scheduled refresher rewrites it when Kanban changes.
- Knowledge → OpenViking `agent-memory/20-Projects` vault (canonical durable KB).
- Projects → curated `itzxSage` repo index + vault entries.
- Calendar → Google via Google Workspace CLI (not yet wired).

## Legacy

- `agent-memory/20-Projects` (Cash-Mission, Harness-Fleet, Hermes, LifeOS) is the
  durable OpenViking vault for this workspace.
- `personal-secretary` (itzxSage) is the related LifeOS personal assistant repo;
  it is a separate project and not required to run Project Glance.
