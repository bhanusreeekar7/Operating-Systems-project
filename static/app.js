/* ═══════════════════════════════════════════════════════════════════════
   PredictiveGuard — Dashboard Frontend
   Sidebar navigation · animated health gauge · gradient charts
   Manual recovery · alert management · timeline · toast notifications
   ═══════════════════════════════════════════════════════════════════════ */

const REFRESH = 3000;

/* ── Color Palette ──────────────────────────────────────────────────── */
const C = {
    blue:       '#3b82f6',
    blueFade:   'rgba(59,130,246,0.12)',
    green:      '#22c55e',
    greenFade:  'rgba(34,197,94,0.12)',
    amber:      '#f59e0b',
    amberFade:  'rgba(245,158,11,0.12)',
    red:        '#ef4444',
    redFade:    'rgba(239,68,68,0.12)',
    purple:     '#a855f7',
    purpleFade: 'rgba(168,85,247,0.12)',
    grid:       'rgba(255,255,255,0.04)',
    tick:       '#64748b',
};

/* ── State ──────────────────────────────────────────────────────────── */
let charts = {};
let prevAnomalyCount = 0;
let prevPredictionCount = 0;
let autoScroll = true;

/* ═══════════════════════════════════════════════════════════════════════
   NAVIGATION
   ═══════════════════════════════════════════════════════════════════════ */
const sectionTitles = {
    dashboard:   'Dashboard',
    logs:        'Log Viewer',
    anomalies:   'Anomalies',
    predictions: 'Predictions',
    recovery:    'Recovery',
    timeline:    'Timeline',
};

function initNavigation() {
    document.querySelectorAll('.nav-item').forEach(btn => {
        btn.addEventListener('click', () => navigateTo(btn.dataset.section));
    });

    // Mobile menu toggle
    const menuBtn = document.getElementById('mobile-menu-btn');
    const sidebar = document.getElementById('sidebar');
    if (menuBtn) {
        menuBtn.addEventListener('click', () => sidebar.classList.toggle('open'));
        // Close sidebar when clicking a nav item on mobile
        document.querySelectorAll('.nav-item').forEach(btn => {
            btn.addEventListener('click', () => sidebar.classList.remove('open'));
        });
    }

    const urlParams = new URLSearchParams(window.location.search);
    const initialSection = urlParams.get('section') || window.location.hash.replace('#', '');
    if (initialSection && sectionTitles[initialSection]) {
        navigateTo(initialSection);
    }
}

function navigateTo(section) {
    // Update nav active state
    document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
    const activeBtn = document.querySelector(`[data-section="${section}"]`);
    if (activeBtn) activeBtn.classList.add('active');

    // Show section
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    const sec = document.getElementById(`section-${section}`);
    if (sec) sec.classList.add('active');

    // Update page title
    document.getElementById('page-title').textContent = sectionTitles[section] || 'Dashboard';
}

/* ═══════════════════════════════════════════════════════════════════════
   HELPERS
   ═══════════════════════════════════════════════════════════════════════ */
function formatTime(ts) {
    if (!ts) return '--:--:--';
    const d = new Date(ts);
    if (isNaN(d)) return (ts || '').slice(11, 19) || ts;
    return d.toLocaleTimeString([], { hour12: false });
}

function relativeTime(ts) {
    if (!ts) return '';
    const d = new Date(ts);
    if (isNaN(d)) return formatTime(ts);
    const diff = Math.floor((Date.now() - d.getTime()) / 1000);
    if (diff < 5) return 'just now';
    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
}

function levelBadge(level) {
    const l = (level || '').toUpperCase();
    if (l === 'ERROR')    return 'badge-error';
    if (l === 'WARNING')  return 'badge-warning';
    if (l === 'CRITICAL') return 'badge-critical';
    return 'badge-info';
}

function severityBadge(sev) {
    const s = (sev || '').toUpperCase();
    if (s === 'CRITICAL') return 'badge-critical';
    if (s === 'HIGH')     return 'badge-error';
    if (s === 'MEDIUM')   return 'badge-warning';
    return 'badge-info';
}

function statusBadge(st) {
    const s = (st || '').toLowerCase();
    if (s === 'success' || s === 'avoided') return 'badge-success';
    if (s === 'failed' || s === 'rolled_back') return 'badge-error';
    if (s === 'pending' || s === 'executing') return 'badge-warning';
    return 'badge-info';
}

function severityDotColor(sev) {
    const s = (sev || '').toUpperCase();
    if (s === 'CRITICAL') return C.purple;
    if (s === 'HIGH' || s === 'ERROR') return C.red;
    if (s === 'MEDIUM' || s === 'WARNING') return C.amber;
    return C.blue;
}

async function fetchJSON(url) {
    try {
        const r = await fetch(url);
        if (!r.ok) return null;
        return await r.json();
    } catch { return null; }
}

/* ═══════════════════════════════════════════════════════════════════════
   ANIMATED COUNTER
   ═══════════════════════════════════════════════════════════════════════ */
function animateCounter(el, target) {
    const current = parseInt(el.textContent) || 0;
    if (current === target) return;
    const diff = target - current;
    const steps = Math.min(Math.abs(diff), 20);
    const stepSize = diff / steps;
    let step = 0;
    const interval = setInterval(() => {
        step++;
        el.textContent = Math.round(current + stepSize * step).toLocaleString();
        if (step >= steps) {
            el.textContent = target.toLocaleString();
            clearInterval(interval);
        }
    }, 30);
}

/* ═══════════════════════════════════════════════════════════════════════
   HEALTH GAUGE
   ═══════════════════════════════════════════════════════════════════════ */
const GAUGE_CIRCUMFERENCE = 2 * Math.PI * 52; // ~326.73

function updateGauge(score) {
    const fill = document.getElementById('gauge-fill');
    const valEl = document.getElementById('gauge-value');
    const statusEl = document.getElementById('gauge-status');

    const pct = Math.max(0, Math.min(100, score));
    const offset = GAUGE_CIRCUMFERENCE * (1 - pct / 100);
    fill.style.strokeDashoffset = offset;

    valEl.textContent = Math.round(pct);

    // Color based on health
    let color, label;
    if (pct >= 80) {
        color = C.green; label = 'System Healthy';
        valEl.style.color = C.green;
    } else if (pct >= 50) {
        color = C.amber; label = 'System Degraded';
        valEl.style.color = C.amber;
    } else {
        color = C.red; label = 'System Critical';
        valEl.style.color = C.red;
    }

    fill.style.stroke = color;
    fill.style.filter = `drop-shadow(0 0 8px ${color}40)`;
    statusEl.textContent = label;

    // Status dot
    const dot = document.getElementById('status-dot');
    dot.style.background = color;
    document.getElementById('status-text').textContent =
        pct >= 80 ? 'Operational' : pct >= 50 ? 'Degraded' : 'Critical';
}

/* ═══════════════════════════════════════════════════════════════════════
   CHARTS (with gradient fills)
   ═══════════════════════════════════════════════════════════════════════ */
function makeGradient(ctx, color, fadeColor) {
    const grad = ctx.createLinearGradient(0, 0, 0, ctx.canvas.clientHeight);
    grad.addColorStop(0, fadeColor);
    grad.addColorStop(1, 'transparent');
    return grad;
}

function createChart(id, label, color, fadeColor) {
    const canvas = document.getElementById(id);
    const ctx = canvas.getContext('2d');
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label,
                data: [],
                borderColor: color,
                borderWidth: 2,
                pointRadius: 0,
                pointHoverRadius: 4,
                pointHoverBackgroundColor: color,
                fill: true,
                backgroundColor: makeGradient(ctx, color, fadeColor),
                tension: 0.4,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 400, easing: 'easeOutQuart' },
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#1e293b',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1,
                    titleFont: { family: 'Inter', size: 11 },
                    bodyFont: { family: 'Inter', size: 12 },
                    cornerRadius: 8,
                    padding: 10,
                },
            },
            scales: {
                x: {
                    grid: { color: C.grid, drawBorder: false },
                    ticks: { color: C.tick, font: { size: 10, family: 'Inter' }, maxRotation: 0, maxTicksLimit: 5 },
                    border: { display: false },
                },
                y: {
                    grid: { color: C.grid, drawBorder: false },
                    ticks: { color: C.tick, font: { size: 10, family: 'Inter' }, padding: 8 },
                    border: { display: false },
                    beginAtZero: true,
                },
            },
        },
    });
}

function initCharts() {
    charts.cpu     = createChart('cpu-chart',     'CPU %',        C.blue,  C.blueFade);
    charts.memory  = createChart('memory-chart',  'Memory %',     C.amber, C.amberFade);
    charts.disk    = createChart('disk-chart',    'Disk %',       C.green, C.greenFade);
    charts.network = createChart('network-chart', 'Network Recv', C.red,   C.redFade);
}

/* ═══════════════════════════════════════════════════════════════════════
   TOAST NOTIFICATIONS
   ═══════════════════════════════════════════════════════════════════════ */
function showToast(message, color = C.blue) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `<span class="toast-dot" style="background:${color}"></span>${message}`;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4200);
}

/* ═══════════════════════════════════════════════════════════════════════
   DATA UPDATES
   ═══════════════════════════════════════════════════════════════════════ */

async function updateDashboard() {
    const d = await fetchJSON('/api/dashboard');
    if (!d) return;

    animateCounter(document.getElementById('stat-total-logs'), d.total_logs ?? 0);
    animateCounter(document.getElementById('stat-active-anomalies'), d.active_anomalies ?? 0);
    animateCounter(document.getElementById('stat-predictions'), d.predictions_made ?? 0);
    animateCounter(document.getElementById('stat-recoveries'), d.recoveries_executed ?? 0);

    updateGauge(d.health_score ?? 100);
}

async function updateMetrics() {
    const data = await fetchJSON('/api/metrics?minutes=5');
    if (!data || !Array.isArray(data) || data.length === 0) return;

    const MAX = 30;
    const trim = arr => arr.slice(-MAX);
    const labels = trim(data.map(m => formatTime(m.timestamp)));

    function updateChart(chart, labels, values) {
        chart.data.labels = labels;
        chart.data.datasets[0].data = values;
        chart.update('none'); // skip animation for smoother feel
    }

    updateChart(charts.cpu,     labels, trim(data.map(m => m.cpu_percent)));
    updateChart(charts.memory,  labels, trim(data.map(m => m.memory_percent)));
    updateChart(charts.disk,    labels, trim(data.map(m => m.disk_percent)));
    updateChart(charts.network, labels, trim(data.map(m => m.network_bytes_recv)));
}

async function updateLogs() {
    const data = await fetchJSON('/api/logs?limit=60');
    if (!data || !Array.isArray(data)) return;

    const tbody = document.getElementById('log-table-body');
    const viewer = document.getElementById('log-viewer');

    tbody.innerHTML = data.map(l => `
        <tr>
            <td class="font-mono" style="color:${C.tick}">${formatTime(l.timestamp)}</td>
            <td><span class="badge ${levelBadge(l.level)}">${l.level}</span></td>
            <td style="color:${C.tick}">${l.source || '-'}</td>
            <td class="font-mono" style="color:var(--text-secondary)">${l.message || '-'}</td>
        </tr>
    `).join('');

    if (autoScroll) viewer.scrollTop = viewer.scrollHeight;
}

async function updateAnomalies() {
    const data = await fetchJSON('/api/anomalies?limit=15');
    if (!data || !Array.isArray(data)) return;
    const el = document.getElementById('anomalies-list');

    if (data.length === 0) {
        el.innerHTML = '<div class="empty-state glass-card"><p>No anomalies detected yet</p></div>';
        return;
    }

    // Toast on new anomalies
    if (data.length > prevAnomalyCount && prevAnomalyCount > 0) {
        const newest = data[0];
        showToast(`Anomaly: ${newest.description || newest.anomaly_type || 'detected'}`, C.amber);
    }
    prevAnomalyCount = data.length;

    el.innerHTML = data.map(a => `
        <div class="list-card glass-card">
            <div class="list-card-row">
                <span class="badge ${severityBadge(a.severity)}">${a.severity}</span>
                <span class="list-card-time">${relativeTime(a.timestamp)}</span>
            </div>
            <div class="list-card-desc">${a.description || a.anomaly_type || 'Anomaly detected'}</div>
            ${a.score ? `<div class="list-card-time">Score: ${parseFloat(a.score).toFixed(3)}</div>` : ''}
        </div>
    `).join('');
}

async function updatePredictions() {
    const data = await fetchJSON('/api/predictions?limit=15');
    if (!data || !Array.isArray(data)) return;
    const el = document.getElementById('predictions-list');

    if (data.length === 0) {
        el.innerHTML = '<div class="empty-state glass-card"><p>No predictions yet</p></div>';
        return;
    }

    // Toast on new predictions
    if (data.length > prevPredictionCount && prevPredictionCount > 0) {
        const newest = data[0];
        showToast(`Predicted: ${(newest.failure_type || 'failure').replace(/_/g, ' ')}`, C.purple);
    }
    prevPredictionCount = data.length;

    el.innerHTML = data.map(p => {
        const conf = ((p.confidence || 0) * 100).toFixed(0);
        const barColor = conf > 70 ? C.red : conf > 40 ? C.amber : C.blue;
        return `
        <div class="list-card glass-card">
            <div class="list-card-row">
                <span class="list-card-title">${(p.failure_type || 'unknown').replace(/_/g, ' ')}</span>
                <span class="badge ${statusBadge(p.status)}">${p.status || 'pending'}</span>
            </div>
            <div class="confidence-row"><span>Confidence</span><span>${conf}%</span></div>
            <div class="confidence-track">
                <div class="confidence-fill" style="width:${conf}%;background:${barColor}"></div>
            </div>
            <div class="list-card-time">${relativeTime(p.timestamp)}</div>
        </div>
    `}).join('');
}

async function updateRecovery() {
    const data = await fetchJSON('/api/recovery?limit=15');
    if (!data || !Array.isArray(data)) return;
    const el = document.getElementById('recovery-list');

    if (data.length === 0) {
        el.innerHTML = '<div class="empty-state glass-card"><p>No recovery actions yet</p></div>';
        return;
    }

    el.innerHTML = data.map(r => `
        <div class="list-card glass-card">
            <div class="list-card-row">
                <span class="list-card-title">${(r.action_name || 'action').replace(/_/g, ' ')}</span>
                <span class="badge ${statusBadge(r.status)}">${r.status}</span>
            </div>
            <div class="list-card-desc">${r.details || ''}</div>
            <div class="list-card-row">
                <span class="list-card-time">${(r.failure_type || '').replace(/_/g, ' ')}</span>
                <span class="list-card-time">${relativeTime(r.timestamp)}</span>
            </div>
            ${r.pre_health_score != null && r.post_health_score != null ? `
                <div class="confidence-row">
                    <span>Health: ${r.pre_health_score}→${r.post_health_score}</span>
                    <span style="color:${r.post_health_score > r.pre_health_score ? C.green : C.red}">
                        ${r.post_health_score > r.pre_health_score ? '↑' : '↓'} ${Math.abs(r.post_health_score - r.pre_health_score).toFixed(1)}
                    </span>
                </div>
            ` : ''}
        </div>
    `).join('');
}

/* ── Alerts ─────────────────────────────────────────────────────────── */
async function updateAlerts() {
    const data = await fetchJSON('/api/alerts?limit=15');
    if (!data) return;

    const badge = document.getElementById('alert-badge');
    const count = data.unacknowledged_count || 0;
    badge.textContent = count;
    badge.classList.toggle('hidden', count === 0);

    const list = document.getElementById('alert-dropdown-list');
    const alerts = data.alerts || [];

    if (alerts.length === 0) {
        list.innerHTML = '<div class="alert-dropdown-empty">No alerts yet</div>';
        return;
    }

    list.innerHTML = alerts.slice(0, 10).map(a => `
        <div class="alert-dropdown-item ${a.acknowledged ? '' : 'unread'}" data-alert-id="${a.id}">
            <span class="alert-dot" style="background:${severityDotColor(a.severity)}"></span>
            <div>
                <div class="alert-dropdown-msg">${a.message}</div>
                <div class="alert-dropdown-time">${relativeTime(a.timestamp)}</div>
            </div>
        </div>
    `).join('');

    // Click to acknowledge
    list.querySelectorAll('.alert-dropdown-item.unread').forEach(item => {
        item.addEventListener('click', async () => {
            const id = item.dataset.alertId;
            await fetch(`/api/alerts/${id}/acknowledge`, { method: 'POST' });
            item.classList.remove('unread');
            updateAlerts();
        });
    });
}

/* ── Timeline ───────────────────────────────────────────────────────── */
async function updateTimeline() {
    const data = await fetchJSON('/api/timeline?limit=40');
    if (!data || !Array.isArray(data)) return;
    const el = document.getElementById('timeline-container');

    if (data.length === 0) {
        el.innerHTML = '<div class="empty-state glass-card"><p>No events yet</p></div>';
        return;
    }

    const iconMap = {
        log: `<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>`,
        anomaly: `<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/></svg>`,
        prediction: `<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>`,
        recovery: `<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>`,
    };

    el.innerHTML = data.map(e => {
        const type = e.event_type || 'log';
        const dotClass = `dot-${type}`;
        return `
        <div class="timeline-event">
            <div class="timeline-dot ${dotClass}">${iconMap[type] || iconMap.log}</div>
            <div class="timeline-content">
                <div class="timeline-top">
                    <span class="timeline-type" style="color:${severityDotColor(e.severity)}">${type}</span>
                    <span class="badge ${severityBadge(e.severity)}" style="font-size:0.6rem;padding:1px 6px;">${e.severity || 'INFO'}</span>
                    <span class="timeline-time">${relativeTime(e.timestamp)}</span>
                </div>
                <div class="timeline-detail">${(e.detail || '').replace(/_/g, ' ')}</div>
            </div>
        </div>
    `}).join('');
}

/* ═══════════════════════════════════════════════════════════════════════
   MANUAL RECOVERY
   ═══════════════════════════════════════════════════════════════════════ */
function initManualRecovery() {
    const btn = document.getElementById('trigger-recovery-btn');
    const select = document.getElementById('recovery-failure-type');
    const feedback = document.getElementById('recovery-feedback');

    btn.addEventListener('click', async () => {
        const type = select.value;
        if (!type) {
            feedback.textContent = 'Please select a failure type first.';
            feedback.className = 'recovery-feedback error';
            return;
        }

        btn.disabled = true;
        btn.textContent = 'Triggering...';

        try {
            const res = await fetch('/api/recovery/trigger', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ failure_type: type }),
            });
            const data = await res.json();

            feedback.textContent = `✓ ${data.message || 'Recovery triggered successfully'}`;
            feedback.className = 'recovery-feedback success';
            showToast(`Recovery triggered: ${type.replace(/_/g, ' ')}`, C.green);
        } catch (err) {
            feedback.textContent = `✗ Failed to trigger recovery.`;
            feedback.className = 'recovery-feedback error';
        }

        btn.disabled = false;
        btn.innerHTML = `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg> Trigger Recovery`;
    });
}

/* ═══════════════════════════════════════════════════════════════════════
   ALERT BELL
   ═══════════════════════════════════════════════════════════════════════ */
function initAlertBell() {
    const bell = document.getElementById('alert-bell');
    const dropdown = document.getElementById('alert-dropdown');

    bell.addEventListener('click', (e) => {
        e.stopPropagation();
        dropdown.classList.toggle('show');
    });

    document.addEventListener('click', () => dropdown.classList.remove('show'));
    dropdown.addEventListener('click', (e) => e.stopPropagation());

    // Mark all read
    document.getElementById('mark-all-read').addEventListener('click', async () => {
        const data = await fetchJSON('/api/alerts?limit=50');
        if (!data || !data.alerts) return;
        const unread = data.alerts.filter(a => !a.acknowledged);
        for (const a of unread) {
            await fetch(`/api/alerts/${a.id}/acknowledge`, { method: 'POST' });
        }
        updateAlerts();
    });
}

/* ═══════════════════════════════════════════════════════════════════════
   AUTO-SCROLL TOGGLE
   ═══════════════════════════════════════════════════════════════════════ */
function initAutoScroll() {
    const toggle = document.getElementById('auto-scroll-toggle');
    toggle.addEventListener('change', () => { autoScroll = toggle.checked; });
}

/* ═══════════════════════════════════════════════════════════════════════
   MAIN LOOP
   ═══════════════════════════════════════════════════════════════════════ */
async function refreshAll() {
    await Promise.allSettled([
        updateDashboard(),
        updateMetrics(),
        updateLogs(),
        updateAnomalies(),
        updatePredictions(),
        updateRecovery(),
        updateAlerts(),
        updateTimeline(),
    ]);
}

window.addEventListener('load', () => {
    initNavigation();
    initCharts();
    initManualRecovery();
    initAlertBell();
    initAutoScroll();
    refreshAll();
    setInterval(refreshAll, REFRESH);
});
