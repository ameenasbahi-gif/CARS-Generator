/* ============================================================
   MCAT CARS Practice — Passage Data & App Logic
   ============================================================ */

// ── PASSAGE DATA ────────────────────────────────────────────

const passages = [
  {
    id: 1,
    category: "humanities",
    categoryLabel: "Humanities",
    title: "The Paradox of Artistic Interpretation",
    source: "Humanities — Philosophy of Art",
    citation: {
      note: "Original MCAT CARS-style practice passage. Topics: philosophy of art, intentionalism (E.D. Hirsch), reader-response theory (Roland Barthes). Consistent with AAMC CARS humanities passages.",
      url: "https://students-residents.aamc.org/prepare-mcat-exam/free-planning-and-study-resources",
      urlLabel: "AAMC Free Official Practice Resources ↗"
    },
    text: `
      <p>The relationship between an artwork and its meaning has long been a source of philosophical contention. On one side stand the intentionalists, who argue that the meaning of any work is fixed by what its creator intended to communicate. On the other stand theorists who insist that once a work leaves its creator's hands, it enters a social life entirely independent of its origins. Neither camp has succeeded in extinguishing the other, partly because each captures something that the other ignores.</p>
      <p>The intentionalist position has genuine appeal. When we read a poem, we naturally wonder what the poet was trying to express. Context — biographical, historical, cultural — feels relevant in a way that is hard to dismiss. To know that Keats wrote "Ode to a Nightingale" while contemplating his own mortality is to understand the poem differently than if we knew nothing about him. This knowledge does not seem like a distraction; it seems like information we need.</p>
      <p>Yet intentionalism runs into serious difficulties. Artists frequently report surprise at what critics discover in their work. Whether this represents genuine discovery or mere projection is not always clear, but the frequency of such reports suggests that meaning may arise in ways the artist neither planned nor controlled. Moreover, language itself carries connotations that shift across time and culture, so that even a careful reading of an author's private correspondence cannot settle what a text "really" means to a reader a century later.</p>
      <p>The alternative — sometimes called the "death of the author" view — fares no better. If meaning is entirely a function of how readers respond, then interpretation becomes an exercise in autobiography rather than criticism. Saying that a text means whatever a reader makes of it does not distinguish a perceptive interpretation from a fanciful one. Criticism would lose the normative dimension that makes it worth doing at all.</p>
      <p>A more defensible position acknowledges that meaning is neither locked in an author's intention nor freely invented by each reader. Instead, it emerges from a structured interaction: texts have properties that constrain interpretation, and readers bring conventions and competencies that make certain readings more or less plausible. On this view, interpretation is more like a conversation than a monologue — constrained, but never fully determined in advance.</p>
    `,
    questions: [
      {
        text: "According to the passage, what is the primary appeal of the intentionalist position?",
        options: [
          "It eliminates the subjectivity of reader response.",
          "Biographical and historical context seems genuinely relevant to understanding a work.",
          "It provides a scientific method for analyzing texts.",
          "It grants the reader freedom to assign personal meaning."
        ],
        correct: 1
      },
      {
        text: "The author mentions that artists are often surprised by what critics discover in their work primarily to suggest that:",
        options: [
          "Critics are generally more intelligent than the artists they study.",
          "Artistic meaning may arise beyond what the creator consciously intended.",
          "The intentionalist view is entirely correct.",
          "Readers should ignore what artists say about their own work."
        ],
        correct: 1
      },
      {
        text: "As used in the passage, the phrase 'death of the author' most likely refers to the idea that:",
        options: [
          "Authors are rarely recognized during their lifetimes.",
          "A work's meaning is determined solely by the reader, not the creator.",
          "Literary criticism has become irrelevant in modern culture.",
          "Biographical information should supplement textual analysis."
        ],
        correct: 1
      },
      {
        text: "The author's critique of the 'death of the author' view is that it:",
        options: [
          "Relies too heavily on the creator's intentions.",
          "Ignores the historical context in which a work was produced.",
          "Cannot distinguish a careful interpretation from an arbitrary one.",
          "Overemphasizes the role of language and convention."
        ],
        correct: 2
      },
      {
        text: "The author's preferred view of interpretation is best described as:",
        options: [
          "Meaning is exclusively determined by the author's private intentions.",
          "Meaning is freely invented by individual readers without constraint.",
          "Meaning emerges from an interaction between textual properties and reader conventions.",
          "Meaning is fixed by the historical period in which a work was written."
        ],
        correct: 2
      },
      {
        text: "Which of the following, if true, would most strengthen the intentionalist position as described in the passage?",
        options: [
          "A study shows readers from different cultures consistently interpret the same poem in contradictory ways.",
          "Newly discovered letters reveal that Keats intended every metaphor in his odes to carry specific biographical weight.",
          "A survey finds that most readers never research the lives of authors whose books they enjoy.",
          "Linguists demonstrate that word meanings shift dramatically within a single generation."
        ],
        correct: 1
      }
    ]
  },

  {
    id: 2,
    category: "social",
    categoryLabel: "Social Sciences",
    title: "Trust, Reciprocity, and the Foundations of Social Capital",
    source: "Social Sciences — Sociology & Economics",
    citation: {
      note: "Original MCAT CARS-style practice passage. Topics: social capital theory (Robert Putnam, James Coleman), thin vs. thick trust, institutional foundations of cooperation. Consistent with AAMC CARS social sciences passages.",
      url: "https://students-residents.aamc.org/prepare-mcat-exam/free-planning-and-study-resources",
      urlLabel: "AAMC Free Official Practice Resources ↗"
    },
    text: `
      <p>Social capital — the networks of relationships and norms of reciprocity that enable people to act collectively — has attracted increasing attention from economists and sociologists alike. The concept suggests that societies are not merely aggregations of self-interested individuals but communities held together by webs of trust and obligation. How such trust is built, maintained, and depleted has enormous practical consequences for everything from economic development to democratic participation.</p>
      <p>One influential line of research distinguishes between two types of trust. Thick trust is the deep, personal confidence we place in family members, close friends, and longstanding associates — people whose character and reliability we know firsthand. Thin trust, by contrast, is the generalized expectation that strangers will behave honestly and predictably simply because they are members of the same society. It is thin trust, theorists argue, that is essential for modern economic life, since most market transactions occur between people who will never meet again.</p>
      <p>The mechanisms by which thin trust develops remain poorly understood. Some researchers emphasize institutional foundations: reliable courts, enforceable contracts, and transparent government signal that the social environment is safe enough for strangers to risk cooperative behavior. Others highlight cultural transmission: children who grow up observing adults cooperate and reciprocate learn to expect the same from others. Both accounts may be partially correct, yet neither fully explains why trust levels vary so dramatically across societies with broadly similar institutions or cultural heritages.</p>
      <p>A complicating factor is that trust and trustworthiness are not the same thing. A person can be highly trusting — willing to extend goodwill to strangers — while the strangers she trusts may or may not deserve it. Conversely, a deeply distrustful individual might inhabit a community of entirely reliable neighbors. Measuring social capital requires distinguishing between the disposition to trust and the objective features of the social environment that warrant trust, a distinction that survey research often blurs.</p>
      <p>Perhaps most troubling is evidence that social capital, once eroded, is difficult to rebuild. Communities that have experienced betrayal — whether through institutional failure, economic collapse, or intergroup conflict — show sustained deficits in trust even after the precipitating conditions have improved. This path dependence suggests that policymakers who hope to restore cooperative norms face a considerably harder task than those who seek merely to preserve them.</p>
    `,
    questions: [
      {
        text: "According to the passage, why is 'thin trust' particularly important for modern economic life?",
        options: [
          "It is more reliable than the trust we place in close family members.",
          "Most market transactions occur between people who will never meet again.",
          "It is easier to measure than personal, relationship-based trust.",
          "It develops naturally without any institutional support."
        ],
        correct: 1
      },
      {
        text: "The passage suggests that researchers disagree about how thin trust develops primarily because:",
        options: [
          "Trust levels are entirely random and cannot be explained by social factors.",
          "Neither institutional nor cultural explanations fully account for variation across similar societies.",
          "Survey data have proven that institutions are irrelevant to trust formation.",
          "Cultural transmission has been shown to be more important than legal enforcement."
        ],
        correct: 1
      },
      {
        text: "The distinction the author draws between trust and trustworthiness is meant to show that:",
        options: [
          "Distrustful people are always justified in their suspicions.",
          "High levels of social trust guarantee high levels of cooperative behavior.",
          "Measuring social capital requires separating an individual's disposition from the actual reliability of others.",
          "Cultural accounts of trust formation are superior to institutional accounts."
        ],
        correct: 2
      },
      {
        text: "The concept of 'path dependence' as used in the final paragraph implies that:",
        options: [
          "Trust follows a predictable linear progression in all societies.",
          "Communities rebuild trust rapidly once harmful conditions are removed.",
          "Past experiences of betrayal can have lasting negative effects on cooperative norms.",
          "Policy interventions are never effective in restoring social capital."
        ],
        correct: 2
      },
      {
        text: "Based on the passage, which of the following would a researcher who emphasizes institutional foundations most likely argue?",
        options: [
          "Trust is primarily inherited through family upbringing and cultural tradition.",
          "Reliable legal systems and transparent governance help make cooperative behavior feel safer.",
          "Thin trust arises spontaneously in communities regardless of government quality.",
          "Social capital is an outdated concept that ignores individual self-interest."
        ],
        correct: 1
      }
    ]
  },

  {
    id: 3,
    category: "humanities",
    categoryLabel: "Humanities",
    title: "Memory, Narrative, and the Self",
    source: "Humanities — Philosophy & Cognitive Psychology",
    citation: {
      note: "Original MCAT CARS-style practice passage. Topics: constructive memory (Frederic Bartlett, Elizabeth Loftus), narrative identity theory (Paul Ricoeur, Alasdair MacIntyre). Consistent with AAMC CARS humanities passages.",
      url: "https://students-residents.aamc.org/prepare-mcat-exam/free-planning-and-study-resources",
      urlLabel: "AAMC Free Official Practice Resources ↗"
    },
    text: `
      <p>We tend to think of memory as a faculty that records the past the way a camera records an image — passively, accurately, and more or less permanently. This view has been thoroughly dismantled by decades of psychological research, yet it persists in everyday life and in the courtroom, where eyewitness testimony continues to carry outsized weight. Understanding why the recording model of memory is wrong, and what the alternative implies for our sense of self, is one of the most unsettling challenges that cognitive science poses to ordinary human self-understanding.</p>
      <p>Memory, psychologists now agree, is better understood as reconstruction than as reproduction. Each time we recall an event, we do not simply retrieve a stored representation; we actively rebuild it using available fragments, current knowledge, and the implicit demands of the present context. This means that memory is inevitably shaped by what has happened since the original event, by social pressures on how the event should be recalled, and by the sheer narrative coherence we require of our pasts. We remember, in short, not merely what happened but what makes sense of who we are now.</p>
      <p>The philosophical stakes are considerable. If personal identity depends, as many philosophers have argued, on continuity of memory — on the capacity to connect one's present self to a continuous chain of remembered experiences — then the revisability of memory threatens to undermine personal identity itself. If the memories that constitute "me" are themselves constantly rewritten, in what sense am I the same person who lived through those original events?</p>
      <p>Some philosophers respond by distinguishing between narrative identity and strict psychological continuity. On this view, what makes me the same person over time is not the literal accuracy of my memories but the coherent story I can tell about my life. Personal identity is, on this account, a kind of ongoing authorship: we are the authors of a life-narrative, and memory is less a record than a draft that we continually revise.</p>
      <p>This narrative view has its own difficulties. Authorship implies a degree of control and intentionality that most memory revision lacks — we do not consciously choose to misremember. Moreover, if identity is constituted by the stories we tell, then identity becomes disturbingly malleable: a sufficiently persuasive storyteller, or a therapist who inadvertently plants false memories, could in principle alter who someone is. The consolations of the narrative view come at a cost that many find unacceptably high.</p>
    `,
    questions: [
      {
        text: "The author describes the 'recording model' of memory primarily in order to:",
        options: [
          "Defend its accuracy as a description of how human memory functions.",
          "Introduce a view that subsequent research has challenged.",
          "Argue that eyewitness testimony should never be admitted in court.",
          "Demonstrate that cognitive science has no practical applications."
        ],
        correct: 1
      },
      {
        text: "According to the passage, memory as reconstruction means that recalled events are shaped by all of the following EXCEPT:",
        options: [
          "Events that occurred after the original experience.",
          "Social pressures about how events should be remembered.",
          "The photographic accuracy of the brain's storage systems.",
          "The narrative coherence the person requires of their past."
        ],
        correct: 2
      },
      {
        text: "The philosophical problem the author identifies in paragraph three is best summarized as:",
        options: [
          "Memory is too unreliable to serve as the basis for criminal convictions.",
          "If identity depends on continuous memory, revisable memory destabilizes personal identity.",
          "Psychological research has made philosophy of mind obsolete.",
          "Cognitive science supports the view that the self is permanent and unchanging."
        ],
        correct: 1
      },
      {
        text: "The 'narrative identity' view described in paragraph four holds that personal identity consists in:",
        options: [
          "A chain of literally accurate memories linking past and present selves.",
          "A coherent life-story that the individual continuously authors and revises.",
          "The strict psychological continuity of brain states across time.",
          "An immutable core self that persists regardless of memory changes."
        ],
        correct: 1
      },
      {
        text: "The author's primary objection to the narrative identity view is that it:",
        options: [
          "Ignores the neurological basis of memory storage.",
          "Implies that memory is more accurate than psychologists have found.",
          "Makes identity disturbingly susceptible to external manipulation.",
          "Requires a level of philosophical precision that most people cannot achieve."
        ],
        correct: 2
      },
      {
        text: "Which of the following best describes the overall structure of the passage?",
        options: [
          "A proposal is made, evidence is presented, and a firm conclusion is reached.",
          "A mistaken view is identified, an alternative is introduced, and a second alternative is critiqued.",
          "Two opposing views are presented and then synthesized into a unified theory.",
          "A series of empirical findings are presented in chronological order."
        ],
        correct: 1
      }
    ]
  },

  {
    id: 4,
    category: "natural",
    categoryLabel: "Natural Sciences",
    title: "The Replication Crisis and the Philosophy of Scientific Evidence",
    source: "Natural Sciences — History & Philosophy of Science",
    citation: {
      note: "Original MCAT CARS-style practice passage. Topics: the replication crisis in social psychology, p-hacking, publication bias, pre-registration. Consistent with AAMC CARS natural sciences passages.",
      url: "https://students-residents.aamc.org/prepare-mcat-exam/free-planning-and-study-resources",
      urlLabel: "AAMC Free Official Practice Resources ↗"
    },
    text: `
      <p>Over the past fifteen years, a wave of failed replication attempts has shaken several branches of science, most visibly social psychology. Researchers attempting to reproduce findings that had been widely cited and taught discovered that a substantial proportion of published results could not be reliably reproduced. The episode, quickly labeled the "replication crisis," prompted soul-searching about the methods, incentive structures, and epistemic standards that govern scientific practice.</p>
      <p>One response to the crisis has been methodological: stricter standards for statistical significance, mandatory pre-registration of hypotheses, larger sample sizes, and open sharing of raw data. These reforms target what critics describe as "questionable research practices" — not outright fraud, but a range of flexible analytical choices that, when made post hoc and in the direction of desired results, inflate the apparent strength of evidence. Reformers argue that adopting more transparent and stringent procedures will gradually cleanse the literature of unreliable findings.</p>
      <p>A more philosophically ambitious response questions whether the crisis reveals something deeper about the nature of scientific evidence itself. On a naive view, a statistically significant result at the p &lt; 0.05 threshold constitutes positive evidence for a hypothesis. But statisticians have long pointed out that this threshold is arbitrary: it means only that the observed result would occur by chance less than 5% of the time if the null hypothesis were true. It says nothing directly about the probability that the hypothesis is correct — a fact that most consumers of scientific findings systematically misread.</p>
      <p>Others locate the problem not in statistical methodology but in the publication system. Journals have historically favored novel, positive results over replications and null findings, creating a systematic bias in the published literature. The studies that make it into print are not a representative sample of all studies conducted; they are a selection skewed toward findings that clear the significance threshold by chance. This problem, sometimes called "publication bias," would generate an apparently robust literature of unreliable results even if every individual researcher behaved impeccably.</p>
      <p>The replication crisis has thus become a lens through which scientists and philosophers examine not only the conduct of individual researchers but the institutional machinery of science itself. Whether the crisis ultimately strengthens science by prompting genuine reform, or whether it erodes public confidence in ways that prove difficult to repair, remains to be seen. What seems clear is that the image of science as a self-correcting system that reliably converges on truth will require considerable qualification.</p>
    `,
    questions: [
      {
        text: "According to the passage, 'questionable research practices' refers primarily to:",
        options: [
          "Deliberate fabrication of experimental data.",
          "Flexible analytical decisions made after data collection to favor desired outcomes.",
          "The failure to conduct replications of important findings.",
          "Publication of studies with inadequate sample sizes."
        ],
        correct: 1
      },
      {
        text: "The author states that the p < 0.05 threshold is 'arbitrary' in order to suggest that:",
        options: [
          "All statistical testing should be abolished in scientific research.",
          "Statistical significance at this level does not directly indicate the probability that a hypothesis is true.",
          "Scientists have deliberately chosen a threshold designed to produce false results.",
          "Null findings are inherently more reliable than positive results."
        ],
        correct: 1
      },
      {
        text: "As described in the passage, 'publication bias' creates a distorted scientific literature because:",
        options: [
          "Journals employ editors who lack the expertise to evaluate statistical methods.",
          "Individual researchers routinely fabricate significant results to get published.",
          "The published record overrepresents positive findings that may have cleared the significance bar by chance.",
          "Replication studies are too expensive for most research institutions to fund."
        ],
        correct: 2
      },
      {
        text: "The passage implies that the methodological reforms described in paragraph two are:",
        options: [
          "Universally accepted as sufficient to resolve the replication crisis.",
          "A useful but possibly incomplete response to the underlying problems.",
          "More philosophically sophisticated than statistical critiques of significance testing.",
          "Primarily designed to address publication bias rather than research practices."
        ],
        correct: 1
      },
      {
        text: "The author's overall tone toward the replication crisis can best be described as:",
        options: [
          "Dismissive — the crisis is exaggerated by critics of science.",
          "Alarmed — the crisis proves that scientific results cannot be trusted.",
          "Analytical — the crisis reveals systemic issues that require careful examination.",
          "Celebratory — the crisis demonstrates science's capacity for self-correction."
        ],
        correct: 2
      }
    ]
  }
];

// ── STATE ────────────────────────────────────────────────────

let selectedCategory = "all";
let currentPassage   = null;
let submitted        = false;

// ── DOM REFERENCES ───────────────────────────────────────────

const landing           = document.getElementById("landing");
const passageSection    = document.getElementById("passageSection");
const generateBtn       = document.getElementById("generateBtn");
const backBtn           = document.getElementById("backBtn");
const categoryPills     = document.getElementById("categoryPills");
const categoryBadge     = document.getElementById("categoryBadge");
const passageSource     = document.getElementById("passageSource");
const passageTitle      = document.getElementById("passageTitle");
const passageText       = document.getElementById("passageText");
const passageCitation   = document.getElementById("passageCitation");
const questionsList     = document.getElementById("questionsList");
const submitBtn         = document.getElementById("submitBtn");
const scoreDisplay      = document.getElementById("scoreDisplay");

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

// ── FUNCTIONS ────────────────────────────────────────────────

function generatePassage() {
  const pool = selectedCategory === "all"
    ? passages
    : passages.filter(p => p.category === selectedCategory);

  if (pool.length === 0) {
    alert("No passages available for that category yet. Try 'All' or another category.");
    return;
  }

  // Pick a random passage (avoid repeating last one if pool is large enough)
  let candidate;
  do {
    candidate = pool[Math.floor(Math.random() * pool.length)];
  } while (pool.length > 1 && currentPassage && candidate.id === currentPassage.id);

  currentPassage = candidate;
  submitted = false;

  renderPassage(currentPassage);
  showPassageSection();
}

function renderPassage(p) {
  categoryBadge.textContent  = p.categoryLabel;
  passageSource.textContent  = p.source;
  passageTitle.textContent   = p.title;
  passageText.innerHTML      = p.text;

  // Render citation block
  if (p.citation) {
    passageCitation.innerHTML = `
      <span class="citation-label">Source</span>
      <span class="citation-note">${p.citation.note}</span>
      <a class="citation-link" href="${p.citation.url}" target="_blank" rel="noopener">
        ${p.citation.urlLabel}
      </a>
    `;
    passageCitation.classList.remove("hidden");
  } else {
    passageCitation.classList.add("hidden");
  }

  // Render questions
  questionsList.innerHTML = "";
  scoreDisplay.classList.add("hidden");
  scoreDisplay.textContent = "";
  submitBtn.disabled = false;

  p.questions.forEach((q, qi) => {
    const block = document.createElement("div");
    block.className = "question-block";
    block.dataset.index = qi;

    const qText = document.createElement("p");
    qText.className = "question-text";
    qText.innerHTML = `<span class="question-num">${qi + 1}.</span> ${q.text}`;
    block.appendChild(qText);

    const ol = document.createElement("ul");
    ol.className = "options-list";

    q.options.forEach((opt, oi) => {
      const li = document.createElement("li");
      li.className = "option-item";
      li.dataset.optionIndex = oi;

      const label = document.createElement("label");
      const radio = document.createElement("input");
      radio.type  = "radio";
      radio.name  = `q${qi}`;
      radio.value = oi;

      const span = document.createElement("span");
      span.textContent = opt;

      label.appendChild(radio);
      label.appendChild(span);
      li.appendChild(label);
      ol.appendChild(li);
    });

    block.appendChild(ol);
    questionsList.appendChild(block);
  });
}

function submitAnswers() {
  if (submitted) return;

  const blocks = document.querySelectorAll(".question-block");
  let answered = 0;
  let correct  = 0;

  blocks.forEach((block, qi) => {
    const selected = block.querySelector(`input[name="q${qi}"]:checked`);
    if (!selected) return;
    answered++;

    const chosenIndex  = parseInt(selected.value);
    const correctIndex = currentPassage.questions[qi].correct;
    const options      = block.querySelectorAll(".option-item");

    // Highlight correct answer
    options[correctIndex].classList.add("correct");

    if (chosenIndex === correctIndex) {
      correct++;
    } else {
      options[chosenIndex].classList.add("wrong");
    }

    // Disable all radios in this question
    block.querySelectorAll("input[type='radio']").forEach(r => r.disabled = true);
  });

  if (answered < currentPassage.questions.length) {
    const unanswered = currentPassage.questions.length - answered;
    const proceed = confirm(
      `You have ${unanswered} unanswered question${unanswered > 1 ? "s" : ""}. Submit anyway?`
    );
    if (!proceed) return;
  }

  submitted = true;
  submitBtn.disabled = true;

  scoreDisplay.textContent = `Score: ${correct} / ${currentPassage.questions.length}`;
  scoreDisplay.classList.remove("hidden");
  scoreDisplay.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

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
