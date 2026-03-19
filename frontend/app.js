// ── State ─────────────────────────────────────────────────
let answered = 0;
let correct = 0;
let total = 0;
let currentTopic = 'all';
let currentPassageData = null;
let currentPassageText = '';
let sessionAnswers = [];
let loadingInterval = null;

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

// ── Loading messages ───────────────────────────────────────
const LOADING_MESSAGES = [
  "Finding a passage…",
  "Evaluating passage quality…",
  "Generating questions with Claude…",
  "Almost ready…",
];

// ── Question type tips ─────────────────────────────────────
const TYPE_TIPS = {
  'PRIMARY PURPOSE': "On 'primary purpose' questions, eliminate answers that are too broad or too narrow.",
  "AUTHOR'S ATTITUDE": "The author's attitude shows in word choice, not just what they say directly.",
  'INFERENCE': "On inference questions, pick the most conservative claim the passage supports.",
  'SPECIFIC DETAIL': "Wrong answers often distort the passage — they're close but not quite right.",
  'APPLICATION': "Analogy questions ask you to apply the author's logic to a new situation.",
};

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
  stopLoadingCycle();
  currentPassageData = data;
  currentPassageText = data.passage || '';
  sessionAnswers = [];

  // Feature 8: Source link footer
  const footerLink = document.getElementById('passage-source-link');
  if (footerLink) {
    footerLink.href = data.source_url || '#';
    footerLink.textContent = data.source_title || data.source_name || '';
  }

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
    .map(p => `<p>${escapeHtml(p.trim())}</p>`)
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
      <div class="explanation" id="exp-${i}">
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

  // Feature 3: Show/hide explanation toggle button
  const showBtn = document.createElement('button');
  showBtn.className = 'show-explanation-btn';
  showBtn.textContent = 'Show explanation';
  showBtn.addEventListener('click', function () {
    if (expEl.classList.contains('revealed')) {
      expEl.classList.remove('revealed');
      this.textContent = 'Show explanation';
    } else {
      expEl.classList.add('revealed');
      this.textContent = 'Hide explanation';
      // Feature 6: Add Ask Claude button once explanation is revealed
      if (!card.querySelector('.ask-followup-btn')) {
        addAskClaudeButton(card, qIndex, selected, correctLetter, expEl);
      }
    }
  });
  expEl.insertAdjacentElement('beforebegin', showBtn);

  answered++;
  const isCorrect = selected === correctLetter;
  if (isCorrect) {
    correct++;
    const correctBtn = choicesEl.querySelector('.choice-btn.correct');
    if (correctBtn) {
      const rect = correctBtn.getBoundingClientRect();
      spawnSparkles(rect.left + rect.width / 2, rect.top + rect.height / 2);
    }
  }

  // Feature 4: Save session state
  sessionAnswers.push({ questionIndex: qIndex, chosen: selected, isCorrect });
  saveSession();

  updateProgress();
  if (answered === total) showResults();
}

// ── Feature 6: Ask Claude follow-up ───────────────────────
function addAskClaudeButton(card, qIndex, selected, correctLetter, expEl) {
  const q = currentPassageData && currentPassageData.questions
    ? currentPassageData.questions[qIndex] : null;

  const askBtn = document.createElement('button');
  askBtn.className = 'ask-followup-btn';
  askBtn.textContent = 'Ask a follow-up';

  const followupContainer = document.createElement('div');
  followupContainer.className = 'followup-container';

  askBtn.addEventListener('click', function () {
    if (followupContainer.querySelector('.followup-form')) return;

    const form = document.createElement('div');
    form.className = 'followup-form';

    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'followup-input';
    input.placeholder = 'Ask Claude about this question…';

    const submitBtn = document.createElement('button');
    submitBtn.className = 'followup-submit-btn';
    submitBtn.textContent = 'Ask';

    const answerArea = document.createElement('div');
    answerArea.className = 'followup-answer-area';

    submitBtn.addEventListener('click', async () => {
      const userQ = input.value.trim();
      if (!userQ) return;

      const choicesEl = document.getElementById(`choices-${qIndex}`);
      const correctBtn = choicesEl ? choicesEl.querySelector(`.choice-btn[data-letter="${correctLetter}"]`) : null;
      const correctText = correctBtn ? correctBtn.querySelector('span:last-child').textContent : correctLetter;
      const selectedBtn = choicesEl ? choicesEl.querySelector(`.choice-btn[data-letter="${selected}"]`) : null;
      const selectedText = selectedBtn ? selectedBtn.querySelector('span:last-child').textContent : selected;

      answerArea.innerHTML = '<div class="claude-followup-answer">Claude is thinking…</div>';

      try {
        const res = await fetch('/api/ask', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            passage: currentPassageText,
            question_text: q ? q.question : '',
            user_answer: selectedText,
            correct_answer: correctText,
            explanation: q ? (q.explanation || '') : '',
            user_question: userQ,
          }),
        });
        if (!res.ok) throw new Error();
        const responseData = await res.json();
        const answer = responseData.answer || responseData.response || JSON.stringify(responseData);
        answerArea.innerHTML = `<div class="claude-followup-answer">${escapeHtml(answer)}</div>`;
      } catch {
        answerArea.innerHTML = '<div class="claude-followup-answer">Couldn\'t reach Claude. Try again.</div>';
      }
    });

    form.appendChild(input);
    form.appendChild(submitBtn);
    form.appendChild(answerArea);
    followupContainer.appendChild(form);
  });

  expEl.insertAdjacentElement('afterend', askBtn);
  askBtn.insertAdjacentElement('afterend', followupContainer);
}

// ── Feature 4: Session persistence ────────────────────────
function saveSession() {
  if (!currentPassageData) return;
  const session = {
    passageId: currentPassageData.id,
    topic: currentPassageData.topic,
    answered,
    correct,
    total,
    answers: sessionAnswers,
  };
  localStorage.setItem('cars_session', JSON.stringify(session));
}

async function continueSession(passageId) {
  document.getElementById('session-restore-banner')?.remove();
  showLoading();
  try {
    const res = await fetch(`/api/passage?id=${passageId}`);
    if (!res.ok) throw new Error();
    const data = await res.json();
    renderPassage(data);
  } catch {
    stopLoadingCycle();
    show('welcome');
    hide('loading');
  }
}

function startFreshSession() {
  localStorage.removeItem('cars_session');
  document.getElementById('session-restore-banner')?.remove();
  show('welcome');
}

function checkSessionRestore() {
  const raw = localStorage.getItem('cars_session');
  if (!raw) { show('welcome'); return; }

  let session;
  try { session = JSON.parse(raw); } catch { show('welcome'); return; }

  if (!session || !session.passageId || session.answered >= session.total) {
    localStorage.removeItem('cars_session');
    show('welcome');
    return;
  }

  const banner = document.createElement('div');
  banner.id = 'session-restore-banner';
  banner.innerHTML =
    'You have an unfinished session. ' +
    `<button onclick="continueSession('${session.passageId}')">Continue</button> ` +
    '<button onclick="startFreshSession()">Start fresh</button>';

  const main = document.querySelector('main') || document.body;
  main.insertBefore(banner, main.firstChild);
  show('welcome');
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
  if (streakData.count >= 2) {
    streakEl.textContent = `🔥 ${streakData.count} day streak — keep it going!`;
  } else if (streakData.count === 1) {
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

  // Feature 4: Clear session on completion
  localStorage.removeItem('cars_session');

  // Feature 5: Contextual CARS tip
  let tipText = '';
  const wrongAnswers = sessionAnswers.filter(a => !a.isCorrect);
  if (wrongAnswers.length === 0) {
    tipText = TIPS[Math.floor(Math.random() * TIPS.length)];
  } else {
    const firstWrongQ = currentPassageData && currentPassageData.questions
      ? currentPassageData.questions[wrongAnswers[0].questionIndex] : null;
    const qType = firstWrongQ
      ? (firstWrongQ.type || firstWrongQ.question_type || '').toUpperCase().trim() : '';
    tipText = TYPE_TIPS[qType] || TIPS[Math.floor(Math.random() * TIPS.length)];
  }

  let resultTipEl = document.getElementById('result-tip');
  if (!resultTipEl) {
    resultTipEl = document.createElement('div');
    resultTipEl.id = 'result-tip';
    document.getElementById('results-card').appendChild(resultTipEl);
  }
  resultTipEl.textContent = tipText;
}

// ── Error / loading states ─────────────────────────────────
function showApiError() {
  stopLoadingCycle();
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
  stopLoadingCycle();
  document.getElementById('error-msg').textContent = msg;
  show('error');
  hide('loading');
  hide('content');
  hide('welcome');
}

function stopLoadingCycle() {
  if (loadingInterval) {
    clearInterval(loadingInterval);
    loadingInterval = null;
  }
}

function showLoading(msg = 'Finding your passage...') {
  stopLoadingCycle();
  let msgEl = document.getElementById('loading-msg');
  if (!msgEl) {
    msgEl = document.createElement('p');
    msgEl.id = 'loading-msg';
    document.getElementById('loading').appendChild(msgEl);
  }
  let idx = 0;
  msgEl.textContent = LOADING_MESSAGES[0];
  loadingInterval = setInterval(() => {
    idx = (idx + 1) % LOADING_MESSAGES.length;
    msgEl.textContent = LOADING_MESSAGES[idx];
  }, 3000);
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

  // Feature 2: Keyboard answer selection (A/B/C/D or 1/2/3/4)
  document.addEventListener('keydown', (e) => {
    const tag = document.activeElement ? document.activeElement.tagName.toUpperCase() : '';
    if (tag === 'INPUT' || tag === 'TEXTAREA') return;

    const keyMap = { 'A': 0, 'B': 1, 'C': 2, 'D': 3, '1': 0, '2': 1, '3': 2, '4': 3 };
    const idx = keyMap[e.key.toUpperCase()];
    if (idx === undefined) return;

    const unanswered = document.querySelectorAll('.question-card:not(.answered)');
    if (!unanswered.length) return;

    const btns = unanswered[0].querySelectorAll('.choice-btn:not([disabled])');
    if (btns[idx]) btns[idx].click();
  });

  // Feature 7: Mobile "Back to passage" button
  const backBtn = document.getElementById('back-to-passage-btn');
  if (backBtn) {
    backBtn.addEventListener('click', () => {
      const passageEl = document.getElementById('passage-text');
      if (passageEl) passageEl.scrollIntoView({ behavior: 'smooth' });
    });

    window.addEventListener('scroll', () => {
      const passageEl = document.getElementById('passage-text');
      if (!passageEl) return;
      const container = passageEl.closest('.card') || passageEl.closest('section') || passageEl;
      const rect = container.getBoundingClientRect();
      if (rect.bottom < 0) {
        backBtn.classList.add('visible');
      } else {
        backBtn.classList.remove('visible');
      }
    });
  }
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
    status.style.color = 'var(--teal-lt)';
    status.textContent = '✓ Thanks! Feedback saved.';
    document.getElementById('feedback-text').value = '';
    setTimeout(closeFeedback, 1800);
  } catch {
    status.style.color = 'var(--red-lt)';
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

// Sync sidebar and mobile filter strips — keeps both in sync regardless of which was clicked
function syncFilters(clickedBtn, index) {
  document.querySelectorAll('.sidebar .filter-btn').forEach((b, i) => {
    b.classList.toggle('active', i === index);
  });
  document.querySelectorAll('.mobile-filters .filter-btn').forEach((b, i) => {
    b.classList.toggle('active', i === index);
  });
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
// Feature 4: Check for unfinished session before showing welcome
checkSessionRestore();
