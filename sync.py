#!/usr/bin/env python3
"""
sync.py — Project Glance data layer.

Reads source snapshots and writes data/*.json for the SPA:

    Kanban tasks        -> data/tasks.json     (reads root kanban.json)
    OpenViking vault    -> data/knowledge.json (agent-memory/20-Projects + viking URIs)
    Curated projects    -> data/projects.json
    Google Calendar     -> data/calendar.json  (NOT WIRED yet: returns wired:false)

Run:
    python3 sync.py --demo          # build data/*.json + print summary
    python3 sync.py --kanban-snapshot  # write a small sample kanban.json (contract proof)
    python3 sync.py --projects-snapshot  # write sample projects.json for testing

Stdlib only. No third-party deps.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
ADAPTERS = {}

# Minimal, explicit Kanban snapshot (library-backed, no network needed at read time).
# The real source is the native Kanban canvas store; this file is the verified snapshot
# used for the demo. A scheduled refresher rewrites this file when Kanban changes.
kanban_tasks = [
    {"id": "t_efe7195a", "title": "Hold voice checkpoint pending complete physical iPhone evidence", "status": "blocked", "priority": 110, "assignee": "default"},
    {"id": "t_49d50bd7", "title": "Improve phone calls: minimal latency AND best natural sound quality", "status": "blocked", "priority": 110, "assignee": "coder"},
    {"id": "t_c76524e7", "title": "Fix reported phone split-view layout without resetting chat", "status": "blocked", "priority": 10, "assignee": "aster"},
    {"id": "t_a47656c9", "title": "Q phone: make wallpaper visible and fix tab switcher", "status": "blocked", "priority": 10, "assignee": "default"},
    {"id": "t_d7a98e23", "title": "Keep Q phone research blocked pending authorized continuation", "status": "blocked", "priority": 0, "assignee": "researcher"},
    {"id": "t_fad64944", "title": "Build and exercise Q as an installable iPhone app, preserving existing chat", "status": "blocked", "priority": 0, "assignee": "default"},
    {"id": "t_18fe2f48", "title": "Validate Jev role and model decisions at the native delegation boundary", "status": "blocked", "priority": 0, "assignee": "coder"},
    {"id": "t_285449bd", "title": "Glance: Verify current Hello Heart support role and application requirements", "status": "done", "priority": 90, "assignee": "coder"},
    {"id": "t_1ea0cc40", "title": "Glance: Recover existing career materials and prepare a truthful reusable evidence pack", "status": "done", "priority": 85, "assignee": "scribe"},
    {"id": "t_1917fbe7", "title": "Glance: Verify Wayfinder role terms and ChatGPT-only compatibility gates", "status": "done", "priority": 80, "assignee": "researcher"},
    {"id": "t_64303798", "title": "Glance: Reconcile available tax records and isolate genuinely missing facts", "status": "done", "priority": 70, "assignee": "researcher"},
    {"id": "t_a5312748", "title": "Glance: Resolve Agent OS startup and command-interface boundaries from retained evidence", "status": "done", "priority": 70, "assignee": "coder"},
    {"id": "t_1ea5671f", "title": "Glance: Finish the existing 13-attempt tool-comparison gate review", "status": "done", "priority": 65, "assignee": "scribe"},
    {"id": "t_90b30299", "title": "Glance: Prepare review-only Hello Heart application draft from verified materials", "status": "done", "priority": 60, "assignee": "scribe"},
    {"id": "t_7baaf896", "title": "Glance: Prepare conditional Wayfinder review packet without commitments", "status": "done", "priority": 55, "assignee": "scribe"},
    {"id": "t_bace9721", "title": "Glance: Verify companion source supported live-interaction boundaries", "status": "done", "priority": 50, "assignee": "scribe"},
    {"id": "t_f6b4e76e", "title": "Glance: Check scoped iPhone Mirroring gate and map supported device controls", "status": "done", "priority": 40, "assignee": "researcher"},
    {"id": "t_f086bb8a", "title": "Glance: Check retained Calendar replay and failure recovery in isolation", "status": "done", "priority": 35, "assignee": "scribe"},
    {"id": "t_f39a3e65", "title": "Glance: Advance the stronger Zero-versus-conventional baseline comparison", "status": "done", "priority": 20, "assignee": "coder"},
    {"id": "t_e2be32c7", "title": "Glance: Run one harder real-task tool comparison only after the retained gate passes", "status": "done", "priority": 15, "assignee": "coder"},
    {"id": "t_5013c518", "title": "Make conversation search recover cleanly without stale results", "status": "done", "priority": 10, "assignee": "coder"},
    {"id": "t_795fe256", "title": "Stage a signed macOS app with the accepted search improvement", "status": "done", "priority": 10, "assignee": "coder"},
    {"id": "t_1863652c", "title": "Fix automatic re-review of tasks escalated for human input", "status": "done", "priority": 10, "assignee": "default"},
    {"id": "t_48c01c78", "title": "Fix reported phone split-view layout without resetting chat", "status": "done", "priority": 8, "assignee": "coder"},
    {"id": "t_ebeed982", "title": "Review the six-profile fleet-workflow rules without editing", "status": "done", "priority": 8, "assignee": "researcher"},
    {"id": "t_3caa68b9", "title": "Adversarially test the fleet workflow overlay", "status": "done", "priority": 8, "assignee": "researcher"},
    {"id": "t_b6d24799", "title": "Apply the fleet workflow contract to all six agent identities", "status": "done", "priority": 8, "assignee": "commander"},
    {"id": "t_e87c40ca", "title": "Repair the observed AutoRAG connector Error without delaying fleet integration", "status": "done", "priority": 5, "assignee": "researcher"},
    {"id": "t_5aab1ccf", "title": "Smoke test mission: Verify the Commander foundation", "status": "done", "priority": 0, "assignee": "commander"},
    {"id": "t_d44d318a", "title": "Researcher: Write 3 verified facts about Hermes Kanban system", "status": "done", "priority": 0, "assignee": "researcher"},
    {"id": "t_04796393", "title": "Scribe: Append dated status line to Commander/Smoke-Test.md", "status": "done", "priority": 0, "assignee": "scribe"},
    {"id": "t_614929de", "title": "Make Hermes Jared's daily-driver agent: overnight build and verification", "status": "done", "priority": 0, "assignee": "commander"},
    {"id": "t_2a9a4181", "title": "Implement and exercise standalone Dot replica against captured reference", "status": "done", "priority": 0, "assignee": "coder"},
    {"id": "t_036c8c2d", "title": "Enable jailbreak kernel across profiles and adapt GODMODE for subscription access", "status": "done", "priority": 0, "assignee": "default"},
    {"id": "t_8bf8f801", "title": "Audit Hermes daily-use gaps and define overnight acceptance cases", "status": "done", "priority": 0, "assignee": "researcher"},
    {"id": "t_c167a7b8", "title": "Implement and exercise high-value daily-driver improvements in Hermes", "status": "done", "priority": 0, "assignee": "coder"},
    {"id": "t_6a4d1d68", "title": "Verify native memory save, fresh-session recall, correction and profile isolation", "status": "done", "priority": 0, "assignee": "researcher"},
    {"id": "t_cd4473bc", "title": "Complete native memory canary with the existing provisioned runtime", "status": "done", "priority": 0, "assignee": "researcher"},
    {"id": "t_e2baa33a", "title": "Close isolated rendered-UI and fresh-model memory acceptance gaps", "status": "done", "priority": 0, "assignee": "coder"},
    {"id": "t_6c7b8651", "title": "Correct managed-worker refusal status presentation without replay", "status": "done", "priority": 0, "assignee": "coder"},
    {"id": "t_be0f5e97", "title": "Apply reviewed daily-driver candidate to installed Hermes and packaged desktop", "status": "done", "priority": 0, "assignee": "coder"},
    {"id": "t_769a9d08", "title": "Extract ChatGPT and Dot context for evidence-backed Hermes migration", "status": "done", "priority": 0, "assignee": "researcher"},
    {"id": "t_07cafc69", "title": "Consolidate ChatGPT migration into Hermes knowledge and verify fresh recall", "status": "done", "priority": 0, "assignee": "scribe"},
    {"id": "t_3a306220", "title": "Extract recovered Cash Fleet archive into migration evidence", "status": "done", "priority": 0, "assignee": "researcher"},
    {"id": "t_a4474bef", "title": "Integrate recovered ChatGPT memories, instructions, rules and archive", "status": "done", "priority": 0, "assignee": "scribe"},
    {"id": "t_4d2f5bd8", "title": "Validate approved native continuity slice with real fresh-model evidence", "status": "done", "priority": 0, "assignee": "coder"},
    {"id": "t_166e9d9f", "title": "Inspect native continuity and read-only evaluation seams in parallel", "status": "done", "priority": 0, "assignee": "researcher"},
    {"id": "t_94297500", "title": "Verify one real installed-Desktop orientation journey without restart", "status": "done", "priority": 0, "assignee": "researcher"},
    {"id": "t_6cfc5d29", "title": "Use installed Hermes to publish the current mission pointer and verify fresh recovery", "status": "done", "priority": 0, "assignee": "scribe"},
    {"id": "t_8f367fee", "title": "Execute and settle the bounded installed-app continuation control test", "status": "done", "priority": 0, "assignee": "researcher"},
    {"id": "t_db2e91e2", "title": "Q phone: glass polish, refined navy branding and Dictate/Call gesture", "status": "done", "priority": 0, "assignee": "aster"},
    {"id": "t_6604633d", "title": "Q + Hermes collaboration: dedicated default-agent research and plan", "status": "done", "priority": 0, "assignee": "default"},
    {"id": "t_5d3e56b6", "title": "Connect Hermes Discord voice and verify a real PS5 working session", "status": "scheduled", "priority": 0, "assignee": "default"},
    {"id": "t_8e831b7b", "title": "Glance: finish FocusGate renewal handoff and verify retained signing evidence", "status": "done", "priority": 0, "assignee": "researcher"},
    {"id": "t_6ef115a8", "title": "Glance: verify Mac Shortcuts readiness without creating or running shortcuts", "status": "done", "priority": 0, "assignee": "coder"},
    {"id": "t_d497feae", "title": "Glance: resolve supported subscription-only GPT connection options for Neuralese", "status": "done", "priority": 0, "assignee": "scribe"},
    {"id": "t_89898022", "title": "Glance: read November 17 live Calendar and prepare a private agenda", "status": "done", "priority": 0, "assignee": "researcher"},
    {"id": "t_5b907517", "title": "Correct stale installation status in daily-driver morning handoff", "status": "done", "priority": 0, "assignee": "scribe"},
    {"id": "t_9db6bef8", "title": "Write one concise morning handoff for the delivered improvements", "status": "done", "priority": 0, "assignee": "scribe"},
    {"id": "t_9d587939", "title": "Give phone UI navy Q branding and open artifacts in separate windows", "status": "done", "priority": 0, "assignee": "default"},
    {"id": "t_cc9eeb4d", "title": "GPT-Live: verify phone runtime activation and OAuth preservation", "status": "done", "priority": 0, "assignee": "coder"},
    {"id": "t_8894f17a", "title": "Q Home Screen app: isolated installable iPhone package", "status": "done", "priority": 0, "assignee": "coder"},
    {"id": "t_c19f7183", "title": "Bot overhaul: audit every OMO agent prompt and orchestration mechanism", "status": "done", "priority": 0, "assignee": "researcher"},
    {"id": "t_853f56ec", "title": "Bot overhaul: audit Capabilities, plugins, skills, MCPs and delegation runtime", "status": "done", "priority": 0, "assignee": "coder"},
    {"id": "t_4c91a0ba", "title": "Bot overhaul: design complementary role prompts and coding delegation workflow", "status": "done", "priority": 0, "assignee": "scribe"},
    {"id": "t_2cce2118", "title": "Integrate and exercise the full six-bot overhaul and coding delegation", "status": "done", "priority": 0, "assignee": "commander"},
    {"id": "t_0ddb7f42", "title": "Audit current Hermes delivery capabilities and real blockers", "status": "done", "priority": 0, "assignee": "coder"},
    {"id": "t_1d48ca7e", "title": "Research the smallest business-delivery stack and compliance gates", "status": "done", "priority": 0, "assignee": "researcher"},
    {"id": "t_3191583d", "title": "Recover the private phone app host and verify the served chat path", "status": "done", "priority": 0, "assignee": "coder"},
    {"id": "t_9593146e", "title": "Build the playable Tabernacle Prayer game revision", "status": "done", "priority": 0, "assignee": "coder"},
    {"id": "t_02d8ca94", "title": "Tabernacle art and historical source check", "status": "done", "priority": 0, "assignee": "researcher"},
    {"id": "t_3c042a41", "title": "Independently playtest the Tabernacle revision", "status": "done", "priority": 0, "assignee": "aster"},
    {"id": "t_1227c329", "title": "Fix and verify Tabernacle free-walk and four-preset baked shadows", "status": "done", "priority": 0, "assignee": "coder"},
    {"id": "t_01b32d96", "title": "Fix the Tabernacle playtest's fullscreen and prayer HUD blockers", "status": "done", "priority": 0, "assignee": "aster"},
]


def load_kanban_json():
    path = ROOT / "kanban.json"
    if path.exists():
        return json.loads(path.read_text())
    return {"tasks": kanban_tasks, "_notice": "used built-in snapshot; root kanban.json not present"}


def kanban_adapter():
    data = load_kanban_json()
    tasks = data.get("tasks", data if isinstance(data, list) else [])
    return {"tasks": tasks, "count": len(tasks), "source": "kanban.json (native Kanban snapshot)"}


def _vault_projects():
    projects = []
    base = ROOT / "agent-memory" / "20-Projects"
    if not base.exists():
        return [{"name": "Unknown (vault unreadable)", "status": "unknown", "source": "vault path missing"}]
    for d in sorted(base.iterdir()):
        if not d.is_dir():
            continue
        readme = d / "README.md"
        entry = {"name": d.name, "status": "active", "source": "agent-memory", "path": str(readme)}
        if readme.exists():
            text = readme.read_text(errors="replace")
            entry["desc"] = " ".join(text.splitlines()[2:4])[:160]
        projects.append(entry)
    projects.insert(0, {"name": "Harness-Fleet validation", "status": "active", "source": "agent-memory", "path": "agent-memory/20-Projects/Harness-Fleet/Overview"})
    return projects


def knowledge_adapter():
    return {"projects": _vault_projects(),
            "source": "OpenViking agent-memory vault (20-Projects)"}


def projects_adapter():
    return {"repos": [
        {"name": "dot-mailbox", "owner": "itzxSage", "desc": "Private, on-demand exchange of approved project updates", "public": False},
        {"name": "personal-secretary", "owner": "itzxSage", "desc": "Private Life Engine: goals, memory, scheduling, voice/conversation contracts", "public": True},
        {"name": "agent-os", "owner": "itzxSage", "desc": "Agent OS", "public": False},
        {"name": "cash-mission", "owner": "itzxSage", "desc": "Cash Fleet mission code (private)", "public": False},
        {"name": "budget-bridge", "owner": "itzxSage", "desc": "Headless manual and CSV budgeting ledger with MCP tools", "public": True},
        {"name": "omo-drive", "owner": "itzxSage", "desc": "Voice-driven remote interface for OpenCode", "public": True},
        {"name": "tabernacle-prayer", "owner": "itzxSage", "desc": "First-person, seven-stop Tabernacle prayer walkthrough", "public": True},
        {"name": "hermes-friend-starter", "owner": "itzxSage", "desc": "Portable Codex setup kit for an independent Windows Hermes", "public": False},
        {"name": "q-oauth-prototype", "owner": "itzxSage", "desc": "OAuth prototype for Q", "public": False},
        {"name": "q-mobilebuildmcp-pilot", "owner": "itzxSage", "desc": "Q mobile build MCP pilot", "public": False},
    ], "vault_projects": knowledge_adapter()["projects"]}


def calendar_adapter():
    # Google Calendar is NOT yet wired. OAuth requires a browser sign-in; not configured.
    return {"entries": [], "wired": False,
            "note": "Calendar not yet wired (Google Calendar via Google Workspace CLI, OAuth not configured). No events invented."}


def write_json(name, obj):
    DATA.mkdir(exist_ok=True)
    (DATA / name).write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def demo():
    write_json("tasks.json", kanban_adapter()["tasks"])
    write_json("knowledge.json", knowledge_adapter())
    write_json("projects.json", projects_adapter())
    write_json("calendar.json", calendar_adapter())
    t = kanban_adapter()
    k = knowledge_adapter()
    print(json.dumps({
        "task_count": t["count"],
        "knowledge_projects": len(k["projects"]),
        "repo_count": len(projects_adapter()["repos"]),
        "calendar_entries": 0,
        "calendar_wired": False,
        "data_dir": str(DATA),
    }, indent=2))


if __name__ == "__main__":
    opts = set(sys.argv[1:])
    if "--demo" in opts:
        demo()
    elif "--kanban-snapshot" in opts:
        DATA.mkdir(exist_ok=True)
        (DATA / "kanban.json").write_text(json.dumps({"tasks": kanban_tasks, "_source": "built-in demo snapshot"}), encoding="utf-8")
        print("wrote data/kanban.json with", len(kanban_tasks), "sample tasks")
    elif "--projects-snapshot" in opts:
        DATA.mkdir(exist_ok=True)
        (DATA / "projects.json").write_text(json.dumps(projects_adapter()), encoding="utf-8")
        print("wrote data/projects.json")
    else:
        print(__doc__)
        sys.stderr.write("run: python3 sync.py --demo | --kanban-snapshot | --projects-snapshot\n")
        sys.exit(1)
