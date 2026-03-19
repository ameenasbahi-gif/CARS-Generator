// ── State ─────────────────────────────────────────────────
let answered = 0;
let correct = 0;
let total = 0;
let currentTopic = 'all';

// ── CARS Tips ──────────────────────────────────────────────
const TIPS = [
  "Read for the author's argument, not just the facts.",
  "Identify the main claim in the first paragraph before reading on.",
  "The correct answer is always defensible from the text — no outside knowledge.",
  "Extreme words like 'always', 'never', 'all' are almost always wrong.",
  "On inference questions, pick the most conservative claim the passage supports.",
  "'However', 'but', and 'yet' signal a shift — pay close attention.",
  "The author's attitude shows in word choice, not just what they say directly.",
  "Wrong answers are often true statements that don't answer the question asked.",
  "For 'author would agree' questions, the answer must follow directly from the text.",
  "Tone matters: 'argues' vs 'suggests' vs 'claims' signal different levels of certainty.",
  "CARS tests reasoning, not knowledge. Unfamiliar topics are fine.",
  "On 'primary purpose' questions, eliminate answers that are too broad or too narrow.",
  "Read actively — ask 'why is the author telling me this?' after each paragraph.",
  "The passage is never neutral. Identify what the author wants you to believe.",
  "If two answers seem right, ask: which is better supported by the passage?",
  "Strengthen/weaken questions test whether you understand the author's core assumption.",
  "Analogy questions ask you to apply the author's logic to a new situation.",
  "The author's purpose is usually to argue, analyze, critique, or compare — identify which.",
  "Structure matters: know what each paragraph is doing before answering questions.",
  "Read carefully the first time. Re-reading costs more time than it saves.",
  "Paired passages: find where authors agree and disagree before answering.",
  "Wrong answers often distort the passage — they're close but not quite right.",
  "On 'except' questions, find the four that ARE true, then pick the leftover.",
  "The passage is your only evidence. Your opinion doesn't count.",
  "Eliminate one wrong answer at a time — don't try to pick the right one first.",
];

// ── Streak ─────────────────────────────────────────────────
function getToday() {
  return new Date().toISOString().slice(0, 10); // 'YYYY-MM-DD'
}

function loadStreak() {
  const data = JSON.parse(localStorage.getItem('cars_streak') || '{"count":0,"lastDate":""}');
  const today = getToday();
  const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);

  if (data.lastDate === today) {
    // Already completed today
  } else if (data.lastDate !== yesterday) {
    // Missed a day — reset streak (but keep count visible until they complete today)
    if (data.lastDate && data.lastDate !== today) {
      data.count = 0;
      localStorage.setItem('cars_streak', JSON.stringify(data));
    }
  }
  return data;
}

function markStreakComplete() {
  const today = getToday();
  const data = JSON.parse(localStorage.getItem('cars_streak') || '{"count":0,"lastDate":""}');
  const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);

  if (data.lastDate === today) return data; // already done today, no change

  data.count = (data.lastDate === yesterday) ? data.count + 1 : 1;
  data.lastDate = today;
  localStorage.setItem('cars_streak', JSON.stringify(data));
  return data;
}

function renderStreak(data) {
  const today = getToday();
  document.getElementById('streak-number').textContent = data.count;
  const mobileEl = document.getElementById('mobile-streak-number');
  if (mobileEl) mobileEl.textContent = data.count;
  const doneEl = document.getElementById('streak-done');
  if (data.lastDate === today) {
    doneEl.classList.remove('hidden');
  } else {
    doneEl.classList.add('hidden');
  }
}

// ── Nav active state ───────────────────────────────────────
function setNavActive(btn) {
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
}

// ── Topic filter ───────────────────────────────────────────
function setTopic(topic, btn) {
  currentTopic = topic;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  // Auto-load a passage with the selected topic
  loadPassage(true);
}

// ── Load passage ───────────────────────────────────────────
async function loadPassage(fresh = false) {
  showLoading(fresh ? 'Scraping a new passage...' : 'Finding your passage...');

  const params = new URLSearchParams();
  const base = fresh ? '/api/passage/new' : '/api/passage';
  if (currentTopic !== 'all') params.set('topic', currentTopic);
  const url = params.toString() ? `${base}?${params}` : base;

  try {
    const res = await fetch(url);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      const msg = err.detail || `Error ${res.status}`;
      if (msg.includes('credit balance')) {
        showApiError();
      } else {
        showError(msg);
      }
      return;
    }
    const data = await res.json();
    renderPassage(data);
  } catch (e) {
    showError('Could not reach the server. Is the backend running?');
  }
}

// ── Render passage ─────────────────────────────────────────
function renderPassage(data) {
  // Topbar
  const modeBadge = document.getElementById('mode-badge');
  modeBadge.textContent = data.cached ? 'Cached' : 'Live';
  modeBadge.className = 'mode-badge' + (data.cached ? ' cached' : '');

  document.getElementById('topic-label').textContent = data.topic || '';

  const sourceLink = document.getElementById('source-link-top');
  sourceLink.href = data.source_url || '#';
  sourceLink.textContent = data.source_title || data.source_name || '';

  // Passage
  document.getElementById('source-badge').textContent = data.source_name || '';
  document.getElementById('passage-text').innerHTML = (data.passage || '')
    .split(/\n\n+/)
    .map(p => `<p>${p.trim()}</p>`)
    .join('');

  // Reset question state
  answered = 0;
  correct = 0;
  total = (data.questions || []).length;

  updateProgress();
  document.getElementById('results-card').classList.add('hidden');

  // Render questions
  const qContainer = document.getElementById('questions');
  qContainer.innerHTML = '';

  (data.questions || []).forEach((q, i) => {
    const card = document.createElement('div');
    card.className = 'question-card';
    card.id = `q-${i}`;

    // Escape correct letter for safe inline handler
    const correctLetter = (q.correct || 'A').replace(/'/g, '');

    const choices = Object.entries(q.choices || {})
      .map(([letter, text]) => `
        <button class="choice-btn"
                onclick="answer(${i}, '${letter}', '${correctLetter}')"
                data-letter="${letter}">
          <span class="choice-letter">${letter}</span>
          <span>${escapeHtml(text)}</span>
        </button>
      `).join('');

    card.innerHTML = `
      <div class="q-number">Question ${i + 1} of ${total}</div>
      <div class="q-text">${escapeHtml(q.question)}</div>
      <div class="choices" id="choices-${i}">${choices}</div>
      <div class="explanation hidden" id="exp-${i}">
        <span class="exp-label">Explanation</span>
        ${escapeHtml(q.explanation || '')}
      </div>
    `;
    qContainer.appendChild(card);
  });

  hide('loading');
  hide('error');
  hide('welcome');
  show('content');
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ── Answer a question ──────────────────────────────────────
function answer(qIndex, selected, correctLetter) {
  const choicesEl = document.getElementById(`choices-${qIndex}`);
  const expEl = document.getElementById(`exp-${qIndex}`);
  const card = document.getElementById(`q-${qIndex}`);

  if (card.classList.contains('answered')) return;
  card.classList.add('answered');

  choicesEl.querySelectorAll('.choice-btn').forEach(b => {
    b.disabled = true;
    if (b.dataset.letter === correctLetter) b.classList.add('correct');
    if (b.dataset.letter === selected && selected !== correctLetter) b.classList.add('wrong');
  });

  expEl.classList.remove('hidden');

  answered++;
  if (selected === correctLetter) {
    correct++;
    const correctBtn = choicesEl.querySelector('.choice-btn.correct');
    if (correctBtn) {
      const rect = correctBtn.getBoundingClientRect();
      spawnSparkles(rect.left + rect.width / 2, rect.top + rect.height / 2);
    }
  }

  updateProgress();
  if (answered === total) showResults();
}

// ── Progress bar ───────────────────────────────────────────
function updateProgress() {
  const pct = total === 0 ? 0 : Math.round((answered / total) * 100);
  document.getElementById('progress-fill').style.width = `${pct}%`;
  document.getElementById('progress-label').textContent =
    answered === 0 ? `${total} questions` : `${answered} of ${total} answered`;
  document.getElementById('score-inline').textContent =
    answered === 0 ? '' : `${correct} correct`;
}

// ── Results ────────────────────────────────────────────────
function showResults() {
  const pct = Math.round((correct / total) * 100);
  let emoji, msg;
  if (pct === 100)    { emoji = '🏆'; msg = 'Perfect score. You are not the one to be tested — you are the one doing the testing.'; }
  else if (pct >= 80) { emoji = '🌟'; msg = 'Strong work. That kind of consistency builds the score.'; }
  else if (pct >= 60) { emoji = '📋'; msg = 'Good session. Read through the explanations — the pattern will click.'; }
  else                { emoji = '🩺'; msg = "Every passage teaches you something. Come back tomorrow."; }

  // Mark streak and show it
  const streakData = markStreakComplete();
  renderStreak(streakData);

  const streakEl = document.getElementById('results-streak');
  const isNewDay = streakData.count > 0;
  if (streakData.count >= 2) {
    streakEl.textContent = `🔥 ${streakData.count} day streak — keep it going!`;
  } else if (isNewDay) {
    streakEl.textContent = `🔥 Day 1 — the streak starts now.`;
  } else {
    streakEl.textContent = '';
  }

  document.getElementById('results-emoji').textContent = emoji;
  document.getElementById('final-score').textContent = `${correct} / ${total}  ·  ${pct}%`;
  document.getElementById('results-msg').textContent = msg;
  document.getElementById('results-card').classList.remove('hidden');

  if (pct >= 60) spawnConfetti();
  document.getElementById('results-card').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ── Error / loading states ─────────────────────────────────
function showApiError() {
  document.getElementById('error-msg').innerHTML =
    'Your Anthropic API account has no credits. ' +
    '<a href="https://console.anthropic.com" target="_blank" style="color:inherit;font-weight:600;text-decoration:underline;">Add credits at console.anthropic.com</a> ' +
    'to start generating passages.';
  show('error');
  hide('loading');
  hide('content');
  hide('welcome');
}

function showError(msg) {
  document.getElementById('error-msg').innerHTML = msg;
  show('error');
  hide('loading');
  hide('content');
  hide('welcome');
}

function showLoading(msg = 'Finding your passage...') {
  document.getElementById('loading-msg').textContent = msg;
  show('loading');
  hide('welcome');
  hide('content');
  hide('error');
}

function goHome() {
  hide('content');
  hide('loading');
  hide('error');
  show('welcome');
}

function show(id) { document.getElementById(id).classList.remove('hidden'); }
function hide(id) { document.getElementById(id).classList.add('hidden'); }

// ── Feedback ───────────────────────────────────────────────
function openFeedback() {
  document.getElementById('feedback-overlay').classList.remove('hidden');
  document.getElementById('feedback-text').focus();
  document.getElementById('feedback-status').textContent = '';
}

function closeFeedback() {
  document.getElementById('feedback-overlay').classList.add('hidden');
  document.getElementById('feedback-text').value = '';
}

// Close on overlay background click only
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('feedback-overlay').addEventListener('click', function(e) {
    if (e.target === this) closeFeedback();
  });
});

async function submitFeedback() {
  const text = document.getElementById('feedback-text').value.trim();
  const status = document.getElementById('feedback-status');
  const btn = document.getElementById('feedback-submit');
  if (!text) { status.textContent = 'Please write something first.'; return; }

  btn.disabled = true;
  btn.textContent = 'Sending...';
  try {
    const res = await fetch('/api/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }),
    });
    if (!res.ok) throw new Error();
    status.style.color = 'var(--forest-glow)';
    status.textContent = '✓ Thanks! Feedback saved.';
    document.getElementById('feedback-text').value = '';
    setTimeout(closeFeedback, 1800);
  } catch {
    status.style.color = 'var(--rose)';
    status.textContent = 'Something went wrong. Try again.';
  } finally {
    btn.disabled = false;
    btn.textContent = 'Send';
  }
}

// ── Confetti ───────────────────────────────────────────────
function spawnConfetti() {
  const container = document.getElementById('confetti-container');
  container.innerHTML = '';
  const colors = ['#1565C0','#00796B','#E8A020','#26A69A','#2E7DD1','#fff'];
  for (let i = 0; i < 48; i++) {
    const el = document.createElement('div');
    el.className = 'confetti-piece';
    el.style.cssText = `
      left: ${Math.random() * 100}%;
      background: ${colors[Math.floor(Math.random() * colors.length)]};
      animation-delay: ${Math.random() * 0.6}s;
      animation-duration: ${0.8 + Math.random() * 0.8}s;
      width: ${5 + Math.random() * 6}px;
      height: ${5 + Math.random() * 6}px;
      border-radius: ${Math.random() > 0.5 ? '50%' : '2px'};
    `;
    container.appendChild(el);
  }
  setTimeout(() => { container.innerHTML = ''; }, 2000);
}

// ── Particles ──────────────────────────────────────────────
const PARTICLES = ['🩺', '🔬', '🧬', '💊', '⚕️', '🩻', '📋', '🧪'];
function spawnParticles() {
  PARTICLES.forEach((emoji, i) => {
    const el = document.createElement('div');
    el.className = 'particle';
    el.textContent = emoji;
    el.style.left = `${Math.random() * 100}vw`;
    el.style.animationDuration = `${14 + Math.random() * 16}s`;
    el.style.animationDelay = `${i * 2.5 + Math.random() * 6}s`;
    el.style.fontSize = `${0.8 + Math.random() * 0.7}rem`;
    document.body.appendChild(el);
  });
}

function spawnSparkles(x, y) {
  ['✅', '⭐', '💫', '🩺'].forEach((s, i) => {
    const el = document.createElement('div');
    el.className = 'sparkle';
    el.textContent = s;
    el.style.left = `${x + (Math.random() - 0.5) * 100}px`;
    el.style.top = `${y + (Math.random() - 0.5) * 50}px`;
    el.style.animationDelay = `${i * 0.08}s`;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 1000);
  });
}

// ── Mobile nav ─────────────────────────────────────────────
function mobileNav(action, btn) {
  document.querySelectorAll('.mobile-nav-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  if (action === 'home') goHome();
  if (action === 'new') loadPassage(true);
}

// Sync sidebar filter buttons with mobile filter strip
function syncFilters(clickedBtn, index) {
  // Sync sidebar filter buttons
  const sidebarBtns = document.querySelectorAll('.sidebar .filter-btn');
  sidebarBtns.forEach(b => b.classList.remove('active'));
  if (sidebarBtns[index]) sidebarBtns[index].classList.add('active');
  // Sync mobile filter strip (deactivate all others)
  document.querySelectorAll('.mobile-filters .filter-btn').forEach(b => b.classList.remove('active'));
  clickedBtn.classList.add('active');
}

function updateMobileStreak(data) {
  const el = document.getElementById('mobile-streak-number');
  if (el) el.textContent = data.count;
}

// ── Init ───────────────────────────────────────────────────
spawnParticles();
// Rotating tip
document.getElementById('cars-tip').textContent = TIPS[Math.floor(Math.random() * TIPS.length)];
// Load and render streak
const initStreak = loadStreak();
renderStreak(initStreak);
updateMobileStreak(initStreak);
show('welcome');
