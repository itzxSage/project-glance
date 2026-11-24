const DATA = {
  tasks: [],
  knowledge: { projects: [] },
  projects: { repos: [] },
  calendar: { entries: [] },
};

let lastFetch = new Date();
let refreshTimer = null;

async function api(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${path}`);
  return res.json();
}

function esc(s) {
  return String(s ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function statusLabel(s) {
  if (!s) return '';
  return s.charAt(0).toUpperCase() + s.slice(1).replace(/-/g, ' ');
}

function renderDashboard() {
  const d = DATA;
  const card = document.getElementById('dashboard-card');
  const projects = d.projects.repos || [];
  const tasks = d.tasks || [];
  const done = tasks.filter(t => t.status === 'done').length;
  const open = tasks.length - done;

  const projectCards = projects.slice(0, 8).map(p => `
    <div class="project">
      <div class="project-name">${esc(p.name)}</div>
      <div class="muted">${esc(p.desc || (p.owner || '') + '/' + (p.repo || ''))}</div>
      <div class="muted">${p.public ? 'public' : 'private'}</div>
    </div>`).join('');

  const next = (tasks.slice()
    .sort((a, b) => (b.priority || 0) - (a.priority || 0))
    .slice(0, 5).map(t => `
    <li><div class="next-title">${esc(t.title)}</div>
      <div class="muted">${esc(t.assignee || '')} · ${statusLabel(t.status)} · ${t.priority ?? ''}</div></li>`).join(''));

  card.innerHTML = `
    <h2>Dashboard</h2>
    <div class="stat-grid">
      <div class="stat"><span class="stat-num">${tasks.length}</span><span class="stat-lab">Tasks</span></div>
      <div class="stat"><span class="stat-num">${done}</span><span class="stat-lab">Done</span></div>
      <div class="stat"><span class="stat-num">${open}</span><span class="stat-lab">Open</span></div>
      <div class="stat"><span class="stat-num">${projects.length}</span><span class="stat-lab">Projects</span></div>
    </div>
    <div class="card-sep"></div>
    <h3>Active projects</h3>
    <div class="grid">${projectCards || '<p class="muted">No projects listed.</p>'}</div>
    <div class="card-sep"></div>
    <h3>Next actions</h3>
    <ul class="next-list">${next || '<p class="muted">No tasks.</p>'}</ul>
    <p class="muted">Updated ${esc(lastFetch.toLocaleTimeString())} · auto-refreshes every 30s.</p>
  `;
}

function renderTasks() {
  const tasks = DATA.tasks || [];
  const list = document.getElementById('task-list');
  const filterStatus = document.getElementById('filter-status').value;
  const filterAssignee = document.getElementById('filter-assignee').value;
  const sortBy = document.getElementById('sort-by').value;

  const filtered = tasks.filter(t => {
    if (filterStatus !== 'all' && t.status !== filterStatus) return false;
    if (filterAssignee !== 'all' && t.assignee !== filterAssignee) return false;
    return true;
  });

  const sorted = filtered.slice().sort((a, b) => {
    if (sortBy === 'priority-desc') return (b.priority || 0) - (a.priority || 0);
    if (sortBy === 'priority-asc') return (a.priority || 0) - (b.priority || 0);
    return String(a.title).localeCompare(String(b.title));
  });

  if (!sorted.length) {
    list.innerHTML = '<li class="muted">No tasks match the current filters.</li>';
    return;
  }

  list.innerHTML = sorted.map(t => `
    <li class="task ${t.status}">
      <div class="task-main">
        <div class="task-id">${esc(t.id)}</div>
        <div class="task-title">${esc(t.title)}</div>
        <div class="task-meta">
          <span>${esc(t.assignee || '')}</span>
          <span>${statusLabel(t.status)}</span>
          <span>priority ${t.priority ?? '—'}</span>
        </div>
      </div>
      <div class="task-actions">
        <button class="mini" data-edit="${esc(t.id)}">Edit</button>
        <button class="mini" data-openwork="${esc(t.id)}">Work together</button>
        <label class="check"><input type="checkbox" data-complete="${esc(t.id)}"> done</label>
      </div>
    </li>`).join('');

  list.querySelectorAll('[data-edit]').forEach(b => {
    b.addEventListener('click', () => {
      const row = b.closest('.task');
      const title = row.querySelector('.task-title');
      const input = document.createElement('input');
      input.type = 'text';
      input.className = 'edit-input';
      input.value = title.textContent;
      title.replaceWith(input);
      input.focus();
      input.select();
      const done = () => { const v = input.value.trim(); if (v) title.textContent = v; input.replaceWith(title); };
      input.addEventListener('blur', done);
      input.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); input.blur(); } });
    });
  });

  list.querySelectorAll('[data-openwork]').forEach(b => {
    b.addEventListener('click', () => {
      document.querySelector('[data-view="work"]').hidden = false;
      document.querySelector('[data-view="dashboard"]').hidden = true;
      document.querySelector('[data-view="tasks"]').hidden = true;
      document.querySelector('[data-view="calendar"]').hidden = true;
      const feed = document.getElementById('notes-feed');
      const notes = JSON.parse(localStorage.getItem('glance_notes') || '[]');
      feed.innerHTML = notes.slice().reverse().map(n => `<div class="note">${esc(n)}</div>`).join('');
      document.querySelector('[data-view="work"] .card').scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  list.querySelectorAll('[data-complete]').forEach(cb => {
    cb.addEventListener('change', () => {
      if (cb.checked) cb.closest('.task').classList.add('done');
      else cb.closest('.task').classList.remove('done');
    });
  });

  document.getElementById('filter-assignee').innerHTML = ['all', ...new Set(tasks.map(t => t.assignee).filter(Boolean))].map(a =>
    `<option value="${esc(a)}">${esc(a)}</option>`).join('');
}

function renderWork() {
  const feed = document.getElementById('notes-feed');
  const stored = JSON.parse(localStorage.getItem('glance_notes') || '[]');
  feed.innerHTML = stored.slice().reverse().map(n => `<div class="note">${esc(n)}</div>`).join('');
  document.getElementById('note-saved').textContent = '';
}

function renderCalendar() {
  const card = document.getElementById('calendar-card');
  if (DATA.calendar.entries && DATA.calendar.entries.length) {
    card.innerHTML = `<h2>Calendar</h2><ul class="task-list">${DATA.calendar.entries.map(e => `<li>${esc(e.summary || e.title)}</li>`).join('')}</ul>`;
  } else {
    card.innerHTML = `
      <h2>Calendar</h2>
      <p class="muted">Calendar not yet wired &mdash; data source is Google Calendar via the Google Workspace CLI, and OAuth is not configured.</p>
      <p class="muted">Pending: connect the calendar feed so this view shows real events.</p>
    `;
  }
}

function render() {
  renderDashboard();
  renderTasks();
  renderWork();
  renderCalendar();
  document.getElementById('refresh-hint').textContent = `Last update: ${lastFetch.toLocaleTimeString()}`;
}

async function loadData() {
  try {
    const [t, k, p, c] = await Promise.all([
      api('data/tasks.json'),
      api('data/knowledge.json'),
      api('data/projects.json'),
      api('data/calendar.json'),
    ]);
    DATA.tasks = Array.isArray(t) ? t : t.tasks || [];
    DATA.knowledge = k;
    DATA.projects = p;
    DATA.calendar = c;
    lastFetch = new Date();
    if (refreshTimer) clearInterval(refreshTimer);
    refreshTimer = setInterval(loadData, 30000);
    render();
  } catch (e) {
    document.getElementById('dashboard-card').innerHTML =
      `<p class="muted">Could not load data: ${esc(e.message)}</p><p class="muted">Is serve.py running? Run: python3 serve.py</p>`;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-view]').forEach(a => {
    a.addEventListener('click', () => {
      document.querySelectorAll('.view').forEach(v => v.hidden = true);
      document.getElementById('view-' + a.dataset.view).hidden = false;
      const selection = a.hash;
      if (selection) { const el = document.querySelector(selection); if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
      render();
    });
  });
  document.getElementById('note-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = document.getElementById('note-text').value.trim();
    if (!text) return;
    try {
      const res = await fetch('api/notes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ note: text }),
      });
      const data = await res.json();
      if (res.ok) {
        localStorage.setItem('glance_notes', JSON.stringify([...JSON.parse(localStorage.getItem('glance_notes') || '[]'), text]));
        document.getElementById('note-text').value = '';
        document.getElementById('note-saved').textContent = 'Saved (note feed will refresh locally).';
      } else {
        document.getElementById('note-saved').textContent = 'Save failed: ' + data.error;
      }
    } catch (err) {
      document.getElementById('note-saved').textContent = 'Save failed: ' + err.message;
    }
  });
  loadData();
});
