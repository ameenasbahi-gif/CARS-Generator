// ── Type tips for weakspot callout ─────────────────────────
const TYPE_TIPS = {
  'PRIMARY PURPOSE': "On primary purpose questions, eliminate answers that are too broad or too narrow.",
  "AUTHOR'S ATTITUDE": "The author's attitude shows in word choice — look for adjectives and qualifiers.",
  'INFERENCE': "Pick the most conservative inference the passage directly supports.",
  'SPECIFIC DETAIL': "Wrong answers invert or slightly distort a real detail — go back and verify.",
  'APPLICATION': "Apply the author's actual logic to the new scenario, not your own opinion.",
};

// ── Utility ─────────────────────────────────────────────────
function show(id) { document.getElementById(id).classList.remove('hidden'); }
function hide(id) { document.getElementById(id).classList.add('hidden'); }

function getToken() { return localStorage.getItem('cars_token'); }
function getUsername() { return localStorage.getItem('cars_username'); }

function setAuthError(formId, msg) {
  const el = document.getElementById(formId + '-error');
  if (!el) return;
  el.textContent = msg;
  el.classList.remove('hidden');
}
function clearAuthError(formId) {
  const el = document.getElementById(formId + '-error');
  if (el) el.classList.add('hidden');
}

// ── Tab switching ────────────────────────────────────────────
function switchTab(tab) {
  document.getElementById('tab-login').classList.toggle('active', tab === 'login');
  document.getElementById('tab-register').classList.toggle('active', tab === 'register');
  document.getElementById('login-form').classList.toggle('hidden', tab !== 'login');
  document.getElementById('register-form').classList.toggle('hidden', tab !== 'register');
  clearAuthError('login');
  clearAuthError('register');
}

// ── Auth forms ───────────────────────────────────────────────
async function submitLogin(e) {
  e.preventDefault();
  clearAuthError('login');
  const btn = document.getElementById('login-submit');
  btn.disabled = true;
  btn.textContent = 'Signing in…';

  const username = document.getElementById('login-username').value.trim();
  const password = document.getElementById('login-password').value;

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok) { setAuthError('login', data.detail || 'Login failed.'); return; }
    storeAuth(data.token, data.username);
    await showProfile();
  } catch {
    setAuthError('login', 'Could not reach server. Try again.');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Sign In';
  }
}

async function submitRegister(e) {
  e.preventDefault();
  clearAuthError('register');
  const btn = document.getElementById('register-submit');
  btn.disabled = true;
  btn.textContent = 'Creating…';

  const username = document.getElementById('reg-username').value.trim();
  const password = document.getElementById('reg-password').value;

  try {
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok) { setAuthError('register', data.detail || 'Registration failed.'); return; }
    storeAuth(data.token, data.username);
    await showProfile();
  } catch {
    setAuthError('register', 'Could not reach server. Try again.');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Create Account';
  }
}

function storeAuth(token, username) {
  localStorage.setItem('cars_token', token);
  localStorage.setItem('cars_username', username);
}

// ── Logout ───────────────────────────────────────────────────
function logout() {
  localStorage.removeItem('cars_token');
  localStorage.removeItem('cars_username');
  hide('profile-state');
  show('auth-state');
}

// ── Profile rendering ────────────────────────────────────────
async function showProfile() {
  hide('auth-state');

  const token = getToken();
  let meData;
  try {
    const res = await fetch('/api/auth/me', { headers: { 'Authorization': `Bearer ${token}` } });
    if (!res.ok) { logout(); return; }
    meData = await res.json();
  } catch {
    logout(); return;
  }

  document.getElementById('profile-welcome').textContent = `Welcome back, ${meData.username} 👋`;

  // Populate settings
  const prefTopic = (meData.settings || {}).preferred_topic || '';
  const sel = document.getElementById('pref-topic');
  if (sel) sel.value = prefTopic;

  // Fetch stats
  try {
    const res = await fetch('/api/user/stats', { headers: { 'Authorization': `Bearer ${token}` } });
    if (res.ok) {
      const stats = await res.json();
      renderStats(stats);
    }
  } catch { /* stats not critical */ }

  show('profile-state');
}

function renderStats(stats) {
  // Stat cards
  document.getElementById('stat-passages').textContent = stats.total_passages ?? 0;

  const avgScore = stats.total_questions > 0
    ? Math.round((stats.total_correct / stats.total_questions) * 100) + '%'
    : '—';
  document.getElementById('stat-score').textContent = avgScore;
  document.getElementById('stat-streak').textContent =
    stats.current_streak > 0 ? `${stats.current_streak} day${stats.current_streak !== 1 ? 's' : ''}` : '0';
  document.getElementById('stat-topic').textContent = stats.best_topic
    ? capitalize(stats.best_topic) : '—';

  // Weakspot callout
  const wc = document.getElementById('weakspot-card');
  if (stats.weakest_type) {
    const w = stats.weakest_type;
    const pct = w.total > 0 ? Math.round((w.correct / w.total) * 100) : 0;
    document.getElementById('weakspot-type').textContent = capitalize(w.type.toLowerCase());
    document.getElementById('weakspot-detail').textContent =
      `${w.correct} / ${w.total} correct (${pct}%)`;
    const tip = TYPE_TIPS[w.type.toUpperCase()] || 'Keep practicing this question type.';
    document.getElementById('weakspot-tip').textContent = tip;
    wc.style.display = '';
  } else {
    wc.style.display = 'none';
  }

  // Recent activity
  const container = document.getElementById('recent-activity');
  if (!stats.recent || stats.recent.length === 0) {
    container.innerHTML = '<p class="empty-state">No activity yet. Start practicing!</p>';
    return;
  }

  const rows = stats.recent.map(r => {
    const pct = r.total > 0 ? Math.round((r.correct / r.total) * 100) : null;
    const pillClass = pct === null ? '' : pct >= 80 ? 'score-high' : pct >= 60 ? 'score-mid' : 'score-low';
    const scoreText = pct !== null ? `<span class="score-pill ${pillClass}">${pct}%</span>` : '—';
    const topic = r.topic ? capitalize(r.topic) : 'General';
    return `<tr>
      <td>${formatDate(r.date)}</td>
      <td>${r.passages}</td>
      <td>${topic}</td>
      <td>${scoreText}</td>
    </tr>`;
  }).join('');

  container.innerHTML = `
    <table class="activity-table">
      <thead><tr>
        <th>Date</th><th>Passages</th><th>Topic</th><th>Score</th>
      </tr></thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

// ── Settings ─────────────────────────────────────────────────
async function saveSettings() {
  const token = getToken();
  if (!token) return;
  const preferred_topic = document.getElementById('pref-topic').value;
  const statusEl = document.getElementById('settings-status');
  try {
    const res = await fetch('/api/auth/settings', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ settings: { preferred_topic } }),
    });
    if (res.ok) {
      statusEl.textContent = '✓ Saved';
      setTimeout(() => { statusEl.textContent = ''; }, 2000);
    }
  } catch { statusEl.textContent = 'Save failed.'; }
}

// ── Global: save progress from app.js ────────────────────────
window.saveProgressToServer = async function(sessionData) {
  const token = getToken();
  if (!token) return;
  try {
    await fetch('/api/user/progress', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({
        date: new Date().toISOString().slice(0, 10),
        passages_completed: 1,
        questions_correct: sessionData.correct || 0,
        questions_total: sessionData.total || 0,
        topic: sessionData.topic || '',
        question_type_stats: sessionData.question_type_stats || {},
      }),
    });
  } catch { /* silent */ }
};

// ── Helpers ───────────────────────────────────────────────────
function capitalize(str) {
  return str.replace(/\b\w/g, c => c.toUpperCase());
}

function formatDate(dateStr) {
  try {
    const d = new Date(dateStr + 'T00:00:00');
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  } catch { return dateStr; }
}

// ── Init ─────────────────────────────────────────────────────
(async function init() {
  const token = getToken();
  if (!token) {
    show('auth-state');
    return;
  }
  try {
    const res = await fetch('/api/auth/me', { headers: { 'Authorization': `Bearer ${token}` } });
    if (res.ok) {
      await showProfile();
    } else {
      localStorage.removeItem('cars_token');
      localStorage.removeItem('cars_username');
      show('auth-state');
    }
  } catch {
    show('auth-state');
  }
})();
