/* ============================================================
   MCAT CARS Practice — App Logic
   Fetches passages from FastAPI backend (localhost:8000)
   ============================================================ */

const API_BASE = "http://localhost:8000";

// ── STATE ────────────────────────────────────────────────────

let selectedCategory = "all";
let currentPassage   = null;
let submitted        = false;

// ── DOM REFERENCES ───────────────────────────────────────────

const landing         = document.getElementById("landing");
const passageSection  = document.getElementById("passageSection");
const generateBtn     = document.getElementById("generateBtn");
const backBtn         = document.getElementById("backBtn");
const categoryPills   = document.getElementById("categoryPills");
const categoryBadge   = document.getElementById("categoryBadge");
const passageSource   = document.getElementById("passageSource");
const passageTitle    = document.getElementById("passageTitle");
const passageText     = document.getElementById("passageText");
const passageCitation = document.getElementById("passageCitation");
const questionsList   = document.getElementById("questionsList");
const submitBtn       = document.getElementById("submitBtn");
const scoreDisplay    = document.getElementById("scoreDisplay");

// ── EVENT LISTENERS ──────────────────────────────────────────

categoryPills.addEventListener("click", (e) => {
  const pill = e.target.closest(".pill");
  if (!pill) return;
  document.querySelectorAll(".pill").forEach(p => p.classList.remove("active"));
  pill.classList.add("active");
  selectedCategory = pill.dataset.category;
});

generateBtn.addEventListener("click", generatePassage);
backBtn.addEventListener("click", showLanding);
submitBtn.addEventListener("click", submitAnswers);

// ── PASSAGE FETCH ─────────────────────────────────────────────

async function generatePassage() {
  generateBtn.disabled  = true;
  generateBtn.textContent = "Loading…";

  try {
    const url = `${API_BASE}/passages/random?category=${selectedCategory}`;
    const resp = await fetch(url);

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      throw new Error(err.detail || `Server error ${resp.status}`);
    }

    const passage = await resp.json();
    currentPassage = passage;
    submitted = false;

    renderPassage(currentPassage);
    showPassageSection();

  } catch (err) {
    console.error("generatePassage error:", err);
    showError(err.message);
  } finally {
    generateBtn.disabled    = false;
    generateBtn.textContent = "Generate CARS Passage";
  }
}

function showError(msg) {
  const isNoPassages = /no passages|404/i.test(msg);
  const detail = isNoPassages
    ? "The passage database is empty. Make sure the backend is running and has finished scraping."
    : msg;
  alert(`Could not load passage:\n\n${detail}`);
}

// ── RENDER ────────────────────────────────────────────────────

function renderPassage(p) {
  categoryBadge.textContent = p.category_label || p.categoryLabel || "";
  passageSource.textContent = p.source || "";
  passageTitle.textContent  = p.title || "";
  passageText.innerHTML     = p.text  || "";

  // Citation block
  if (p.source_url) {
    passageCitation.innerHTML = `
      <span class="citation-label">Source</span>
      <a class="citation-link" href="${p.source_url}" target="_blank" rel="noopener">
        ${p.source} ↗
      </a>
    `;
    passageCitation.classList.remove("hidden");
  } else {
    passageCitation.classList.add("hidden");
  }

  // Questions
  questionsList.innerHTML = "";
  scoreDisplay.classList.add("hidden");
  scoreDisplay.textContent = "";
  submitBtn.disabled = false;

  const questions = p.questions || [];

  questions.forEach((q, qi) => {
    const block = document.createElement("div");
    block.className = "question-block";
    block.dataset.index = qi;

    const qText = document.createElement("p");
    qText.className = "question-text";
    qText.innerHTML = `<span class="question-num">${qi + 1}.</span> ${q.text}`;
    block.appendChild(qText);

    const ol = document.createElement("ul");
    ol.className = "options-list";

    (q.options || []).forEach((opt, oi) => {
      const li = document.createElement("li");
      li.className = "option-item";
      li.dataset.optionIndex = oi;

      const label  = document.createElement("label");
      const radio  = document.createElement("input");
      const span   = document.createElement("span");

      radio.type  = "radio";
      radio.name  = `q${qi}`;
      radio.value = oi;
      span.textContent = opt;

      label.appendChild(radio);
      label.appendChild(span);
      li.appendChild(label);
      ol.appendChild(li);
    });

    block.appendChild(ol);

    // Explanation placeholder (shown after submit)
    if (q.explanation) {
      const exp = document.createElement("div");
      exp.className = "explanation hidden";
      exp.innerHTML = `<span class="explanation-label">Explanation</span> ${q.explanation}`;
      block.appendChild(exp);
    }

    questionsList.appendChild(block);
  });
}

// ── SUBMIT ────────────────────────────────────────────────────

function submitAnswers() {
  if (submitted) return;

  const blocks  = document.querySelectorAll(".question-block");
  let answered  = 0;
  let correct   = 0;
  const questions = (currentPassage || {}).questions || [];

  blocks.forEach((block, qi) => {
    const selected = block.querySelector(`input[name="q${qi}"]:checked`);
    if (!selected) return;
    answered++;

    const chosenIndex  = parseInt(selected.value);
    const correctIndex = questions[qi]?.correct ?? -1;
    const options      = block.querySelectorAll(".option-item");

    options[correctIndex]?.classList.add("correct");

    if (chosenIndex === correctIndex) {
      correct++;
    } else {
      options[chosenIndex]?.classList.add("wrong");
    }

    block.querySelectorAll("input[type='radio']").forEach(r => (r.disabled = true));

    // Show explanation
    const exp = block.querySelector(".explanation");
    if (exp) exp.classList.remove("hidden");
  });

  const total = questions.length;

  if (answered < total) {
    const unanswered = total - answered;
    const proceed = confirm(
      `You have ${unanswered} unanswered question${unanswered > 1 ? "s" : ""}. Submit anyway?`
    );
    if (!proceed) return;
  }

  submitted             = true;
  submitBtn.disabled    = true;

  scoreDisplay.textContent = `Score: ${correct} / ${total}`;
  scoreDisplay.classList.remove("hidden");
  scoreDisplay.scrollIntoView({ behavior: "smooth", block: "nearest" });

  // Save to history
  saveSession(correct, total);
}

// ── SESSION HISTORY ───────────────────────────────────────────

function saveSession(score, total) {
  if (!currentPassage) return;
  const history = JSON.parse(localStorage.getItem("mcatHistory") || "[]");
  history.unshift({
    date:     new Date().toISOString(),
    title:    currentPassage.title,
    category: currentPassage.category,
    score,
    total,
  });
  // Keep last 100 sessions
  localStorage.setItem("mcatHistory", JSON.stringify(history.slice(0, 100)));
}

// ── VIEW SWITCHING ────────────────────────────────────────────

function showPassageSection() {
  landing.classList.add("hidden");
  passageSection.classList.remove("hidden");
  window.scrollTo({ top: 0, behavior: "instant" });
}

function showLanding() {
  passageSection.classList.add("hidden");
  landing.classList.remove("hidden");
  window.scrollTo({ top: 0, behavior: "instant" });
}
