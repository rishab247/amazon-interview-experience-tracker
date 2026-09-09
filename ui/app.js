/**
 * Amazon LeetCode Interview Explorer - App Logic
 */

// Application State
const PAGE_SIZE = 30;

const renderedTabs = {
  questions: false,
  lp: false,
  analytics: false
};

const state = {
  experiences: [],
  filteredExperiences: [],
  displayedCount: PAGE_SIZE,
  questions: [],
  filteredQuestions: [],
  activeTab: 'experiences', // 'experiences' | 'questions' | 'lp' | 'analytics'
  viewMode: 'grid', // 'grid' | 'list'
  searchQuery: '',
  selectedOutcome: 'all',
  selectedRole: 'all',
  selectedLocation: 'all',
  selectedDatePreset: 'all', // 'all' | '2026' | '2025' | '2024' | 'last-30' | 'last-90' | 'custom'
  dateFrom: '',
  dateTo: '',
  sortBy: 'recent',
  bookmarkedOnly: false,
  bookmarkedIds: new Set(JSON.parse(localStorage.getItem('amz_bookmarked_ids') || '[]')),
  currentModalExp: null,
  qbSearchQuery: '',
  qbCategory: 'all',
  qbDifficulty: 'all',
  qbDatePreset: 'all', // 'all' | '2026' | '2025' | '2024' | 'last-30' | 'last-90' | 'custom'
  qbDateFrom: '',
  qbDateTo: '',
  qbSort: 'frequency-desc',
  qbDisplayedCount: 24,
  questionFreqMap: new Map(),
  lpSearchQuery: '',
};

// Fallback Embedded Dataset if fetch is blocked by CORS (e.g. file:// protocol)
const EMBEDDED_FALLBACK_DATA = [];

// 16 Official Amazon Leadership Principles
const LEADERSHIP_PRINCIPLES = [
  {
    num: 1,
    name: "Customer Obsession",
    tagline: "Leaders start with the customer and work backwards.",
    description: "They work vigorously to earn and keep customer trust. Although leaders pay attention to competitors, they obsess over customers.",
    sampleQuestions: [
      "Tell me about a time you had to deal with an unreasonable customer request.",
      "Give an example of a time when you went above and beyond for a customer without being asked.",
      "Describe a situation where customer feedback radically changed your engineering roadmap."
    ],
    goodSignals: "Demonstrates deep empathy, prioritizes long-term trust over short-term revenue, instruments metrics to measure user satisfaction.",
    badSignals: "Building features because they are cool rather than useful; blaming users when they fail to adopt a tool."
  },
  {
    num: 2,
    name: "Ownership",
    tagline: "Leaders are owners. They think long term and don't sacrifice long-term value for short-term results.",
    description: "They act on behalf of the entire company, beyond just their own team. They never say 'that's not my job.'",
    sampleQuestions: [
      "Tell me about a time you took on a task that was outside your direct job scope.",
      "Describe a time you saw a problem in another team's service and fixed it or escalated it.",
      "Give an example of when you had to take ownership of a major production outage."
    ],
    goodSignals: "Fixes broken windows, volunteers for unglamorous reliability work, leaves systems cleaner than they found them.",
    badSignals: "Saying 'another team was supposed to do that' or abdicating responsibility after handoff."
  },
  {
    num: 3,
    name: "Invent and Simplify",
    tagline: "Leaders expect and require innovation and invention from their teams and always find ways to simplify.",
    description: "They are externally aware, look for new ideas from everywhere, and are not limited by 'not invented here.' As we do new things we accept that we may be misunderstood for long periods of time.",
    sampleQuestions: [
      "Tell me about a time you simplified a complex system architecture or process.",
      "Describe an innovative solution you devised to a stubborn technical bottleneck.",
      "Have you ever replaced a heavy legacy framework with a much simpler bespoke component?"
    ],
    goodSignals: "Focuses on simplicity, reduces cognitive load for teammates, automates manual repetitive tasks.",
    badSignals: "Over-engineering simple requirements with fashionable distributed architectures."
  },
  {
    num: 4,
    name: "Are Right, A Lot",
    tagline: "Leaders are right a lot. They have strong judgment and good instincts.",
    description: "They seek diverse perspectives and work to disconfirm their beliefs.",
    sampleQuestions: [
      "Tell me about a time you had to make an important decision with insufficient information.",
      "Describe a time you realized your initial technical hypothesis was completely wrong.",
      "How do you calibrate your technical instincts when working in an unfamiliar domain?"
    ],
    goodSignals: "Data-driven, acknowledges cognitive biases, proactively asks 'what would prove me wrong?'.",
    badSignals: "Arrogance, relying solely on gut feeling without validating metrics or consulting domain experts."
  },
  {
    num: 5,
    name: "Learn and Be Curious",
    tagline: "Leaders are never done learning and always seek to improve themselves.",
    description: "They are curious about new possibilities and act to explore them.",
    sampleQuestions: [
      "Tell me about a new programming language, technology, or architecture you learned recently.",
      "Describe a time when you asked deep questions that uncovered an underlying flaw in a project.",
      "How do you stay abreast of rapid advancements in distributed systems and AI?"
    ],
    goodSignals: "Reads RFCs and papers, experiments with side projects, shares learnings via tech talks.",
    badSignals: "Comfortable stagnating with old stacks; defensive when questioned on unfamiliar topics."
  },
  {
    num: 6,
    name: "Hire and Develop the Best",
    tagline: "Leaders raise the performance bar with every hire and promotion.",
    description: "They recognize exceptional talent, and willingly move them throughout the organization. Leaders develop leaders and take seriously their role in coaching others.",
    sampleQuestions: [
      "Tell me about an engineer you mentored who achieved a promotion or significant technical milestone.",
      "How do you handle an underperforming teammate or direct report?",
      "How do you evaluate candidates during interviews to ensure you raise the company bar?"
    ],
    goodSignals: "Invests time in code reviews, provides actionable feedback, advocates for junior engineers.",
    badSignals: "Treating mentorship as a chore, keeping all high-impact work to themselves."
  },
  {
    num: 7,
    name: "Insist on the Highest Standards",
    tagline: "Leaders have relentlessly high standards — many people may think these standards are unreasonably high.",
    description: "Leaders are continually raising the bar and drive their teams to deliver high quality products, services, and processes. Leaders ensure that defects do not get sent down the line and that problems are fixed so they stay fixed.",
    sampleQuestions: [
      "Tell me about a time you refused to compromise on quality despite immense pressure to ship.",
      "How do you maintain code quality and test coverage in a fast-paced release environment?",
      "Describe a time when someone submitted substandard work and how you handled it."
    ],
    goodSignals: "Strict test automation, zero-tolerance for flaky CI/CD, builds resilient alerting.",
    badSignals: "Allowing known critical bugs to slide into production without mitigation."
  },
  {
    num: 8,
    name: "Think Big",
    tagline: "Thinking small is a self-fulfilling prophecy.",
    description: "Leaders create and communicate a bold direction that inspires results. They think differently and look around corners for ways to serve customers.",
    sampleQuestions: [
      "Describe a multi-year technical vision you proposed and executed.",
      "Tell me about a time you looked beyond the immediate requirement to build a platform capability.",
      "Give an example of an idea you pitched that radically expanded your project's scope."
    ],
    goodSignals: "Designs for 10x-100x scale, modularizes components for reuse across orgs, anticipates edge cases.",
    badSignals: "Myopic focus on immediate patch fixes; inability to articulate a 1-2 year technical roadmap."
  },
  {
    num: 9,
    name: "Bias for Action",
    tagline: "Speed matters in business. Many decisions and actions are reversible and do not need extensive study.",
    description: "We value calculated risk taking. Most decisions are two-way doors that can be reversed quickly.",
    sampleQuestions: [
      "Tell me about a time you took a calculated risk to launch a feature quickly.",
      "Describe a situation where analysis paralysis was slowing down the team and how you broke the deadlock.",
      "Have you ever made a major technical decision without managerial approval?"
    ],
    goodSignals: "Distinguishes between one-way and two-way doors, releases MVPs to gather real customer signal.",
    badSignals: "Endless meetings, waiting for 100% consensus when 70% data is sufficient."
  },
  {
    num: 10,
    name: "Frugality",
    tagline: "Accomplish more with less. Constraints breed resourcefulness, self-sufficiency, and invention.",
    description: "There are no extra points for growing headcount, budget size, or fixed expense.",
    sampleQuestions: [
      "Tell me about a time you optimized AWS cloud infrastructure costs or server fleet spend.",
      "Describe how you solved a difficult computing problem with limited hardware or budget.",
      "Have you ever identified redundant software licenses or idle compute resources?"
    ],
    goodSignals: "Profiles CPU/memory footprints, adopts spot instances/serverless, removes idle caches.",
    badSignals: "Throwing expensive hardware or more machines at unoptimized algorithms."
  },
  {
    num: 11,
    name: "Earn Trust",
    tagline: "Leaders listen attentively, speak candidly, and treat others respectfully.",
    description: "They are vocally self-critical, even when doing so is awkward or embarrassing. Leaders do not believe their or their team's body odor smells of perfume.",
    sampleQuestions: [
      "Tell me about a time you had to deliver difficult feedback to a coworker or manager.",
      "Describe a major mistake you made. How did you communicate it to stakeholders?",
      "Give an example of how you earned the trust of a skeptical cross-functional partner."
    ],
    goodSignals: "Admits mistakes early, credits teammates, conducts blameless post-mortems.",
    badSignals: "Passing blame, hiding outages, getting defensive when questioned."
  },
  {
    num: 12,
    name: "Dive Deep",
    tagline: "Leaders operate at all levels, stay connected to the details, audit frequently, and are skeptical when metrics and anecdotes differ.",
    description: "No task is beneath them. They inspect logs, metrics, code, and ground truths directly.",
    sampleQuestions: [
      "Tell me about the most complex bug you have ever debugged down to the assembly, OS, or network packet level.",
      "Describe a time when you audited a system and found metrics were masking a real customer problem.",
      "How deep do you go into database query plans or heap dumps when diagnosing latency spikes?"
    ],
    goodSignals: "Looks at flame graphs, reads library source code, inspects raw metrics rather than summary averages.",
    badSignals: "Relying on hand-wavy explanations or stopping at the first superficial explanation."
  },
  {
    num: 13,
    name: "Have Backbone; Disagree and Commit",
    tagline: "Leaders are obligated to respectfully challenge decisions when they disagree, even when doing so is uncomfortable or exhausting.",
    description: "Leaders have conviction and are tenacious. They do not compromise for the sake of social cohesion. Once a decision is determined, they commit wholly.",
    sampleQuestions: [
      "Tell me about a time you strongly disagreed with your team lead or engineering manager.",
      "Describe a situation where you had to advocate for an unpopular technical choice.",
      "Have you ever disagreed with a product decision, voiced your dissent with data, but then committed 100% when overruled?"
    ],
    goodSignals: "Presents structured data to defend a thesis, stays professional, commits wholeheartedly once decided.",
    badSignals: "Passive-aggressive compliance, dragging feet after being overruled, giving up at the first pushback."
  },
  {
    num: 14,
    name: "Deliver Results",
    tagline: "Leaders focus on the key inputs for their business and deliver them with the right quality and in a timely fashion.",
    description: "Despite setbacks, they rise to the occasion and never settle.",
    sampleQuestions: [
      "Tell me about a time a project was critically behind schedule and what you did to hit the launch date.",
      "Describe an instance where unexpected blockers arose right before release and how you navigated them.",
      "Give an example of a goal you met despite extreme resource constraints."
    ],
    goodSignals: "Ruthlessly prioritizes high-leverage work, removes blockers, delivers measurable business impact.",
    badSignals: "Providing excuses instead of outcomes; missing deadlines without proactive mitigation."
  },
  {
    num: 15,
    name: "Strive to be Earth's Best Employer",
    tagline: "Leaders work every day to create a safer, more productive, higher performing, more diverse, and more just work environment.",
    description: "They lead with empathy, have fun at work, and make it easy for others to have fun. Leaders ask themselves: Are my fellow employees growing?",
    sampleQuestions: [
      "How do you ensure psychological safety and inclusivity in code reviews and team discussions?",
      "Tell me about a time you advocated for team work-life balance during a high-stress launch.",
      "Describe how you supported a colleague experiencing burnout or personal challenges."
    ],
    goodSignals: "Champion of inclusive culture, creates psychological safety, promotes healthy on-call rotations.",
    badSignals: "Promoting toxic crunch culture, dismissing teammate wellness concerns."
  },
  {
    num: 16,
    name: "Success and Scale Bring Broad Responsibility",
    tagline: "We started in a garage, but we're not there anymore. We are big, we impact the world, and we are far from perfect.",
    description: "We must be humble and thoughtful about even the secondary effects of our actions. We must begin each day with a determination to make better, do better, and be better for our customers, our employees, our partners, and the world at large.",
    sampleQuestions: [
      "How do you consider ethics, privacy, security, and unintended consequences in software you build?",
      "Tell me about a time you flagged a potential safety, privacy, or environmental concern in your software.",
      "How do you design systems that respect user data privacy beyond bare minimum legal compliance?"
    ],
    goodSignals: "Considers downstream societal impacts, implements defense-in-depth security and privacy protections.",
    badSignals: "Viewing privacy or compliance as mere check-the-box annoyances."
  }
];

// Initialize on DOM Load
document.addEventListener('DOMContentLoaded', async () => {
  initTheme();
  setupKeyboardShortcuts();
  setupScrollObserver();
  if (window.lucide) lucide.createIcons(); // Initialize static header/nav icons while containers are empty
  await loadExperiencesData();
});

// Theme Initialization
function initTheme() {
  const savedTheme = localStorage.getItem('amz_theme');
  if (savedTheme === 'light') {
    document.documentElement.classList.remove('dark');
  } else {
    document.documentElement.classList.add('dark');
  }
}

function toggleTheme() {
  const isDark = document.documentElement.classList.toggle('dark');
  localStorage.setItem('amz_theme', isDark ? 'dark' : 'light');
}

// Loading State Controller
function setLoadingState(isLoading, message = 'Loading experiences...') {
  const loadingState = document.getElementById('experiences-loading-state');
  const container = document.getElementById('experiences-container');
  const paginationEl = document.getElementById('experiences-pagination');
  const progressBar = document.getElementById('global-progress-bar');
  const progressIndicator = document.getElementById('global-progress-indicator');
  const statusEl = document.getElementById('header-status-text');
  const statusDot = document.getElementById('header-status-dot');
  const spinnerMsg = document.getElementById('loading-spinner-message');

  if (isLoading) {
    if (loadingState) {
      loadingState.classList.remove('hidden');
      if (window.lucide) lucide.createIcons({ root: loadingState });
    }
    if (container) container.classList.add('hidden');
    if (paginationEl) paginationEl.classList.add('hidden');

    if (progressBar && progressIndicator) {
      progressBar.classList.remove('opacity-0');
      progressIndicator.style.width = '25%';
      setTimeout(() => {
        if (progressIndicator) progressIndicator.style.width = '70%';
      }, 150);
    }

    if (statusEl) statusEl.textContent = message;
    if (spinnerMsg) spinnerMsg.textContent = message;
    if (statusDot) {
      statusDot.className = 'w-2 h-2 rounded-full bg-amber-500 animate-ping';
    }
  } else {
    if (progressIndicator) {
      progressIndicator.style.width = '100%';
    }
    setTimeout(() => {
      if (progressBar) progressBar.classList.add('opacity-0');
      if (progressIndicator) progressIndicator.style.width = '0%';
    }, 400);

    if (loadingState) loadingState.classList.add('hidden');
    if (container) container.classList.remove('hidden');
    if (statusDot) {
      statusDot.className = 'w-2 h-2 rounded-full bg-emerald-500 animate-pulse';
    }
  }
}

// Data Fetcher with Fallback Chain
async function loadExperiencesData() {
  setLoadingState(true, 'Loading 1,300+ interview experiences...');

  // 1. Try /api/experiences
  try {
    const res = await fetch('/api/experiences');
    if (res.ok) {
      state.experiences = await res.json();
      console.log('Loaded from /api/experiences');
      onDataLoaded();
      return;
    }
  } catch (e) {}

  // 2. Try ../data/experiences.json
  try {
    const res = await fetch('../data/experiences.json');
    if (res.ok) {
      state.experiences = await res.json();
      console.log('Loaded from ../data/experiences.json');
      onDataLoaded();
      return;
    }
  } catch (e) {}

  // 3. Try experiences.json
  try {
    const res = await fetch('experiences.json');
    if (res.ok) {
      state.experiences = await res.json();
      console.log('Loaded from experiences.json');
      onDataLoaded();
      return;
    }
  } catch (e) {}

  // 4. Inlined dataset fallback (Guaranteed offline & file:// support)
  console.log('Using embedded fallback experiences dataset');
  state.experiences = EMBEDDED_FALLBACK_DATA;
  onDataLoaded();
}

function onDataLoaded() {
  const statusEl = document.getElementById('header-status-text');
  if (statusEl) statusEl.textContent = `${state.experiences.length} Verified Experiences Loaded`;
  
  // Populate locations dropdown
  populateLocationDropdown();
  
  // Extract questions for Question Bank
  extractQuestions();

  // Apply filters
  applyFilters();
  
  // Update live stat bar
  updateLiveStats();

  // Dismiss loading state and display actual experiences
  setLoadingState(false);
}

async function reloadData() {
  const btn = document.getElementById('btn-refresh');
  if (btn) btn.classList.add('animate-spin');
  setLoadingState(true, 'Refreshing verified experiences...');
  await loadExperiencesData();
  renderAllViews();
  setTimeout(() => {
    if (btn) btn.classList.remove('animate-spin');
    showToast('Data refreshed successfully', 'check', 'emerald');
  }, 500);
}

// Populate Location Filter Dropdown
function populateLocationDropdown() {
  const locSelect = document.getElementById('filter-location');
  if (!locSelect) return;

  const locations = new Set();
  state.experiences.forEach(exp => {
    if (exp.location) locations.add(exp.location);
  });

  // Keep 'all' as first option
  locSelect.innerHTML = '<option value="all">All Locations</option>';
  Array.from(locations).sort().forEach(loc => {
    const opt = document.createElement('option');
    opt.value = loc;
    opt.textContent = loc;
    locSelect.appendChild(opt);
  });
}

// Extract Questions across all Experiences
function extractQuestions() {
  const questionsMap = new Map();

  // Known generic or malformed strings to exclude from Question Bank
  const isGenericOrMalformed = (str) => {
    if (!str || str.length < 4) return true;
    const s = str.trim().toLowerCase();
    if (s.startsWith('s on ') || s.startsWith('s are ') || s.startsWith('s do ') || s.startsWith('is to ') || s.startsWith('ulate ') || s.startsWith('s in total') || s.startsWith('s about ')) return true;
    if (s.includes('disguised in long corporate stories') || s.includes('subtle traps that cause') || s.includes('not test random trivia')) return true;
    if (s.includes('data structures & algorithms problem') || s.includes('coding problem / technical discussion') || s.includes('leadership principles discussion')) return true;
    if (s === 'technical assessment' || s === 'technical discussion' || s.includes('star format leadership principles')) return true;
    if (s.includes('4026')) return true;
    if (s.includes('hackerrank algorithmic coding') || s.includes('work simulation') || s.includes('deep dive into past project') || s.includes('have backbone; disagree') || s.includes('customer obsession & ownership') || s.includes('scalability, partitioning, and fault-tolerance')) return true;
    return false;
  };

  state.experiences.forEach(exp => {
    if (!exp.rounds) return;
    exp.rounds.forEach(round => {
      if (!round.questions) return;
      round.questions.forEach(q => {
        const isString = typeof q === 'string';
        let qName = isString ? q.trim() : (q.name || '').trim();
        
        // Skip placeholders and malformed regex artifacts
        if (isGenericOrMalformed(qName)) return;

        // Clean up URL fragments if any
        if (qName.includes('leetcode.com/problems/')) {
          const match = qName.match(/leetcode\.com\/problems\/([a-z0-9\-]+)/i);
          if (match) {
            qName = match[1].split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
          }
        }

        const key = qName.toLowerCase();
        if (!key || key.length < 3) return;

        if (!questionsMap.has(key)) {
          questionsMap.set(key, {
            name: qName,
            leetcodeEquivalent: isString ? '' : (q.leetcode_equivalent || ''),
            difficulty: isString ? 'Medium' : (q.difficulty || 'Medium'),
            category: isString ? (round.round_name || round.round_type || 'Algorithms & Data Structures') : (q.category || round.round_type || 'Algorithms & Data Structures'),
            description: isString ? (round.details || round.notes || '') : (q.description || ''),
            codeSnippet: isString ? '' : (q.code_snippet || ''),
            occurrences: [],
            testedInRoles: new Set()
          });
        }

        const item = questionsMap.get(key);
        // Avoid duplicate occurrence entry for the same experience
        if (!item.occurrences.some(o => o.expId === exp.id)) {
          item.occurrences.push({
            expId: exp.id,
            expTitle: exp.title,
            roundName: round.round_name || round.round_type || 'Interview Round',
            role: exp.role,
            outcome: exp.outcome,
            date: exp.post_date || exp.date || ''
          });
        }
        if (exp.role) item.testedInRoles.add(exp.role);
      });
    });
  });

  // Sort questions by occurrence frequency descending
  state.questions = Array.from(questionsMap.values()).sort((a, b) => b.occurrences.length - a.occurrences.length);
  state.filteredQuestions = [...state.questions];

  // Populate fast question frequency lookup map
  state.questionFreqMap = new Map();
  state.questions.forEach(q => {
    state.questionFreqMap.set(q.name.toLowerCase(), q.occurrences.length);
    if (q.leetcodeEquivalent) {
      state.questionFreqMap.set(q.leetcodeEquivalent.toLowerCase(), q.occurrences.length);
    }
  });

  const qbBadge = document.getElementById('tab-badge-questions');
  if (qbBadge) qbBadge.textContent = state.questions.length;

  // Update Question Bank Date dropdown counts dynamically if present
  const qbDatePresetEl = document.getElementById('qb-filter-date-preset');
  if (qbDatePresetEl) {
    const qCount2026 = state.questions.filter(q => q.occurrences.some(o => (o.date || '').startsWith('2026'))).length;
    const qCount2025 = state.questions.filter(q => q.occurrences.some(o => (o.date || '').startsWith('2025'))).length;
    const qCount2024 = state.questions.filter(q => q.occurrences.some(o => (o.date || '').startsWith('2024'))).length;
    
    qbDatePresetEl.innerHTML = `
      <option value="all">All Years (${state.questions.length} questions)</option>
      <option value="2026">2026 (${qCount2026} questions)</option>
      <option value="2025">2025 (${qCount2025} questions)</option>
      <option value="2024">2024 (${qCount2024} questions)</option>
      <option value="last-30">Last 30 Days</option>
      <option value="last-90">Last 90 Days</option>
      <option value="custom">Custom Date Range...</option>
    `;
    qbDatePresetEl.value = state.qbDatePreset;
  }
}

// Date Filter Helpers
function isDateInFilter(dateStr, preset, fromDate, toDate) {
  if (!preset || preset === 'all') return true;
  if (!dateStr) return false;
  if (preset === '2026') return dateStr.startsWith('2026');
  if (preset === '2025') return dateStr.startsWith('2025');
  if (preset === '2024') return dateStr.startsWith('2024');
  if (preset === 'last-30') {
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - 30);
    return new Date(dateStr) >= cutoff;
  }
  if (preset === 'last-90') {
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - 90);
    return new Date(dateStr) >= cutoff;
  }
  if (preset === 'custom') {
    if (fromDate && dateStr < fromDate) return false;
    if (toDate && dateStr > toDate) return false;
    return true;
  }
  return true;
}

function getDatePresetLabel(preset, fromDate, toDate) {
  if (preset === '2026') return '2026';
  if (preset === '2025') return '2025';
  if (preset === '2024') return '2024';
  if (preset === 'last-30') return 'Last 30 Days';
  if (preset === 'last-90') return 'Last 90 Days';
  if (preset === 'custom') {
    if (fromDate && toDate) return `${fromDate} to ${toDate}`;
    if (fromDate) return `Since ${fromDate}`;
    if (toDate) return `Until ${toDate}`;
    return 'Custom Range';
  }
  return 'All Time';
}

// Filter and Sort Processing
function applyFilters() {
  let list = [...state.experiences];

  // 1. Outcome filter
  if (state.selectedOutcome !== 'all') {
    list = list.filter(exp => (exp.outcome || '').toLowerCase() === state.selectedOutcome.toLowerCase());
  }

  // 2. Role filter
  if (state.selectedRole !== 'all') {
    list = list.filter(exp => (exp.role || '').toLowerCase() === state.selectedRole.toLowerCase());
  }

  // 3. Location filter
  if (state.selectedLocation !== 'all') {
    list = list.filter(exp => (exp.location || '').toLowerCase() === state.selectedLocation.toLowerCase());
  }

  // 4. Date filter
  if (state.selectedDatePreset !== 'all') {
    list = list.filter(exp => isDateInFilter(exp.post_date || exp.date || '', state.selectedDatePreset, state.dateFrom, state.dateTo));
  }

  // 5. Bookmarked only
  if (state.bookmarkedOnly) {
    list = list.filter(exp => state.bookmarkedIds.has(exp.id));
  }

  // 5. Search Query
  if (state.searchQuery.trim()) {
    const q = state.searchQuery.toLowerCase();
    list = list.filter(exp => {
      const matchTitle = (exp.title || '').toLowerCase().includes(q);
      const matchRole = (exp.role || '').toLowerCase().includes(q);
      const matchLocation = (exp.location || '').toLowerCase().includes(q);
      const matchCompany = (exp.current_company || '').toLowerCase().includes(q);
      const matchAuthor = (exp.author || '').toLowerCase().includes(q);
      const matchTags = (exp.tags || []).some(t => t.toLowerCase().includes(q));
      const matchLPs = (exp.leadership_principles || []).some(lp => lp.toLowerCase().includes(q));
      
      // Check question names
      let matchQuestions = false;
      if (exp.rounds) {
        for (const round of exp.rounds) {
          if (round.questions) {
            for (const item of round.questions) {
              if ((item.name || '').toLowerCase().includes(q) || (item.category || '').toLowerCase().includes(q) || (item.leetcode_equivalent || '').toLowerCase().includes(q)) {
                matchQuestions = true;
                break;
              }
            }
          }
          if (round.lp_questions) {
            for (const lpq of round.lp_questions) {
              if (lpq.toLowerCase().includes(q)) {
                matchQuestions = true;
                break;
              }
            }
          }
        }
      }

      return matchTitle || matchRole || matchLocation || matchCompany || matchAuthor || matchTags || matchLPs || matchQuestions;
    });
  }

  // 6. Sorting
  if (state.sortBy === 'recent') {
    list.sort((a, b) => new Date(b.post_date || b.date || 0) - new Date(a.post_date || a.date || 0));
  } else if (state.sortBy === 'upvotes') {
    list.sort((a, b) => (b.votes ?? b.upvotes ?? 0) - (a.votes ?? a.upvotes ?? 0));
  } else if (state.sortBy === 'views') {
    list.sort((a, b) => (b.views || 0) - (a.views || 0));
  } else if (state.sortBy === 'rounds') {
    list.sort((a, b) => ((b.rounds || []).length) - ((a.rounds || []).length));
  }

  state.displayedCount = PAGE_SIZE;
  state.filteredExperiences = list;
  renderExperiences();
  renderActiveFilterChips();
  updateResultsCount();
}

// Filter Event Handlers
function onSearchInput(val) {
  state.searchQuery = val;
  const clearBtn = document.getElementById('search-clear-btn');
  if (clearBtn) {
    if (val.trim()) clearBtn.classList.remove('hidden');
    else clearBtn.classList.add('hidden');
  }
  applyFilters();
}

function clearSearch() {
  const input = document.getElementById('search-input');
  if (input) {
    input.value = '';
    input.focus();
  }
  onSearchInput('');
}

function setOutcomeFilter(outcome) {
  state.selectedOutcome = outcome;
  ['all', 'Offer', 'Rejected', 'Pending'].forEach(o => {
    const btn = document.getElementById(`filter-outcome-${o}`);
    if (!btn) return;
    if (o.toLowerCase() === outcome.toLowerCase()) {
      btn.className = 'px-3 py-1.5 rounded-lg text-xs font-semibold transition bg-amber-500 text-white shadow-sm';
    } else {
      btn.className = 'px-3 py-1.5 rounded-lg text-xs font-semibold transition bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700';
    }
  });
  applyFilters();
}

function onRoleChange(val) {
  state.selectedRole = val;
  applyFilters();
}

function onLocationChange(val) {
  state.selectedLocation = val;
  applyFilters();
}

function onDatePresetChange(val) {
  state.selectedDatePreset = val;
  const container = document.getElementById('custom-date-container');
  if (container) {
    if (val === 'custom') {
      container.classList.remove('hidden');
      container.classList.add('flex');
    } else {
      container.classList.remove('flex');
      container.classList.add('hidden');
    }
  }
  applyFilters();
}

function onCustomDateChange() {
  const f = document.getElementById('filter-date-from');
  const t = document.getElementById('filter-date-to');
  state.dateFrom = f ? f.value : '';
  state.dateTo = t ? t.value : '';
  applyFilters();
}

function onSortChange(val) {
  state.sortBy = val;
  applyFilters();
}

function toggleBookmarkedOnly() {
  state.bookmarkedOnly = !state.bookmarkedOnly;
  const btn = document.getElementById('filter-bookmarked-btn');
  if (btn) {
    if (state.bookmarkedOnly) {
      btn.classList.add('bg-amber-500/20', 'text-amber-600', 'dark:text-amber-400', 'border-amber-500/50');
      btn.classList.remove('text-slate-600', 'dark:text-slate-300');
    } else {
      btn.classList.remove('bg-amber-500/20', 'text-amber-600', 'dark:text-amber-400', 'border-amber-500/50');
      btn.classList.add('text-slate-600', 'dark:text-slate-300');
    }
  }
  applyFilters();
}

function setViewMode(mode) {
  state.viewMode = mode;
  const gridBtn = document.getElementById('view-grid-btn');
  const listBtn = document.getElementById('view-list-btn');
  if (mode === 'grid') {
    gridBtn.className = 'p-1.5 rounded-md bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs';
    listBtn.className = 'p-1.5 rounded-md text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white';
  } else {
    listBtn.className = 'p-1.5 rounded-md bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs';
    gridBtn.className = 'p-1.5 rounded-md text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white';
  }
  renderExperiences();
}

function resetAllFilters() {
  state.searchQuery = '';
  state.selectedOutcome = 'all';
  state.selectedRole = 'all';
  state.selectedLocation = 'all';
  state.selectedDatePreset = 'all';
  state.dateFrom = '';
  state.dateTo = '';
  state.sortBy = 'recent';
  state.bookmarkedOnly = false;

  const sInput = document.getElementById('search-input');
  if (sInput) sInput.value = '';
  const clearBtn = document.getElementById('search-clear-btn');
  if (clearBtn) clearBtn.classList.add('hidden');

  const rSelect = document.getElementById('filter-role');
  if (rSelect) rSelect.value = 'all';
  const lSelect = document.getElementById('filter-location');
  if (lSelect) lSelect.value = 'all';
  const dPreset = document.getElementById('filter-date-preset');
  if (dPreset) dPreset.value = 'all';
  const cContainer = document.getElementById('custom-date-container');
  if (cContainer) {
    cContainer.classList.remove('flex');
    cContainer.classList.add('hidden');
  }
  const dFrom = document.getElementById('filter-date-from');
  if (dFrom) dFrom.value = '';
  const dTo = document.getElementById('filter-date-to');
  if (dTo) dTo.value = '';

  const sortSelect = document.getElementById('filter-sort');
  if (sortSelect) sortSelect.value = 'recent';

  const bmBtn = document.getElementById('filter-bookmarked-btn');
  if (bmBtn) {
    bmBtn.classList.remove('bg-amber-500/20', 'text-amber-600', 'dark:text-amber-400', 'border-amber-500/50');
    bmBtn.classList.add('text-slate-600', 'dark:text-slate-300');
  }

  setOutcomeFilter('all');
  showToast('Filters reset to default', 'rotate-ccw', 'amber');
}

// Active Filter Chips
function renderActiveFilterChips() {
  const container = document.getElementById('active-filter-chips');
  if (!container) return;

  const chips = [];
  if (state.selectedOutcome !== 'all') chips.push({ label: `Outcome: ${state.selectedOutcome}`, clear: () => setOutcomeFilter('all') });
  if (state.selectedRole !== 'all') chips.push({ label: `Role: ${state.selectedRole}`, clear: () => onRoleChange('all') });
  if (state.selectedLocation !== 'all') chips.push({ label: `Location: ${state.selectedLocation}`, clear: () => onLocationChange('all') });
  if (state.selectedDatePreset !== 'all') {
    let dLabel = `Date: ${state.selectedDatePreset}`;
    if (state.selectedDatePreset === 'custom') {
      dLabel = `Date: ${state.dateFrom || 'start'} to ${state.dateTo || 'end'}`;
    } else if (state.selectedDatePreset === 'last-30') {
      dLabel = 'Date: Last 30 Days';
    } else if (state.selectedDatePreset === 'last-90') {
      dLabel = 'Date: Last 90 Days';
    }
    chips.push({
      label: dLabel,
      clear: () => {
        onDatePresetChange('all');
        const dPreset = document.getElementById('filter-date-preset');
        if (dPreset) dPreset.value = 'all';
      }
    });
  }
  if (state.bookmarkedOnly) chips.push({ label: 'Saved only', clear: () => toggleBookmarkedOnly() });
  if (state.searchQuery) chips.push({ label: `Search: "${state.searchQuery}"`, clear: () => clearSearch() });

  if (chips.length === 0) {
    container.classList.add('hidden');
    container.innerHTML = '';
    return;
  }

  container.classList.remove('hidden');
  container.innerHTML = '<span class="text-xs text-slate-400 font-medium">Active filters:</span>';

  chips.forEach(chip => {
    const chipEl = document.createElement('div');
    chipEl.className = 'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/30';
    chipEl.innerHTML = `
      <span>${escapeHtml(chip.label)}</span>
      <button class="hover:text-amber-800 dark:hover:text-amber-200">
        <i data-lucide="x" class="w-3 h-3"></i>
      </button>
    `;
    chipEl.querySelector('button').addEventListener('click', chip.clear);
    container.appendChild(chipEl);
  });

  if (window.lucide) lucide.createIcons({ root: container });
}

function updateResultsCount() {
  const countEl = document.getElementById('results-count-text');
  if (countEl) {
    countEl.textContent = `Showing ${state.filteredExperiences.length} of ${state.experiences.length} experiences`;
  }
  const expBadge = document.getElementById('tab-badge-experiences');
  if (expBadge) expBadge.textContent = state.filteredExperiences.length;

  const bmLabel = document.getElementById('bookmark-count-label');
  if (bmLabel) bmLabel.textContent = state.bookmarkedIds.size;
}

// Live Metrics Banner Calculation
function updateLiveStats() {
  const total = state.experiences.length;
  let offers = 0;
  let rejections = 0;
  let totalUpvotes = 0;
  const lpCountMap = {};

  state.experiences.forEach(exp => {
    const outcome = (exp.outcome || '').toLowerCase();
    if (outcome === 'offer') offers++;
    else if (outcome === 'rejected') rejections++;

    totalUpvotes += (exp.upvotes || 0);

    // Count LPs
    if (exp.leadership_principles) {
      exp.leadership_principles.forEach(lp => {
        lpCountMap[lp] = (lpCountMap[lp] || 0) + 1;
      });
    }
  });

  // Set Top LP
  let topLp = 'Customer Obsession';
  let topLpCount = 0;
  for (const [lp, count] of Object.entries(lpCountMap)) {
    if (count > topLpCount) {
      topLpCount = count;
      topLp = lp;
    }
  }

  const offerRate = total > 0 ? Math.round((offers / total) * 100) : 0;
  const rejectionRate = total > 0 ? Math.round((rejections / total) * 100) : 0;
  const avgUpvotes = total > 0 ? Math.round(totalUpvotes / total) : 0;

  // Set Hero Stats
  const statTotal = document.getElementById('stat-total');
  if (statTotal) statTotal.textContent = total;

  const statOfferRate = document.getElementById('stat-offer-rate');
  if (statOfferRate) statOfferRate.textContent = `${offerRate}%`;

  const statOffersCount = document.getElementById('stat-offers-count');
  if (statOffersCount) statOffersCount.textContent = `(${offers} offers)`;

  const statRejections = document.getElementById('stat-rejections');
  if (statRejections) statRejections.textContent = rejections;

  const statRejectionRate = document.getElementById('stat-rejection-rate');
  if (statRejectionRate) statRejectionRate.textContent = `(${rejectionRate}%)`;

  const statQuestions = document.getElementById('stat-questions');
  if (statQuestions) statQuestions.textContent = state.questions.length;

  const statTopLp = document.getElementById('stat-top-lp');
  if (statTopLp) statTopLp.textContent = topLp;

  const statTopLpFreq = document.getElementById('stat-top-lp-freq');
  if (statTopLpFreq) statTopLpFreq.textContent = `${topLpCount} occurrences`;

  const statAvgUpvotes = document.getElementById('stat-avg-upvotes');
  if (statAvgUpvotes) statAvgUpvotes.textContent = avgUpvotes;

  // Outcome pills counters
  const pillOffer = document.getElementById('count-pill-offer');
  if (pillOffer) pillOffer.textContent = `(${offers})`;

  const pillRej = document.getElementById('count-pill-rejected');
  if (pillRej) pillRej.textContent = `(${rejections})`;

  const pillPending = document.getElementById('count-pill-pending');
  if (pillPending) pillPending.textContent = `(${total - offers - rejections})`;
}

// Card Template Builders
function buildCardHtml(exp) {
  const outcome = exp.outcome || 'Pending';
  const isBookmarked = state.bookmarkedIds.has(exp.id);
  
  let outcomeClass = 'badge-pending';
  let outcomeIcon = 'clock';
  if (outcome.toLowerCase() === 'offer') {
    outcomeClass = 'badge-offer';
    outcomeIcon = 'check-circle-2';
  } else if (outcome.toLowerCase() === 'rejected') {
    outcomeClass = 'badge-rejected';
    outcomeIcon = 'x-circle';
  }

  const roundsList = (exp.rounds || []).map(r => {
    const rName = r.round_name || r.round_type || 'Round';
    return `<span class="px-2 py-0.5 rounded-md text-[10px] font-medium bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700/60">${escapeHtml(rName)}</span>`;
  }).join('');

  return `
    <div class="glass-card rounded-2xl p-5 flex flex-col justify-between group relative overflow-hidden" data-exp-id="${escapeHtml(exp.id)}">
      <div>
        <div class="flex items-center justify-between gap-2 mb-3">
          <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold ${outcomeClass}">
            <i data-lucide="${outcomeIcon}" class="w-3.5 h-3.5"></i>
            <span>${escapeHtml(outcome)}</span>
          </span>

          <div class="flex items-center gap-1 text-xs">
            <button onclick="toggleBookmark('${exp.id}', event)" class="p-1.5 rounded-lg text-slate-400 hover:text-amber-500 transition" title="Save to bookmarks">
              <i data-lucide="bookmark" class="w-4 h-4 ${isBookmarked ? 'fill-amber-500 text-amber-500' : ''}"></i>
            </button>
          </div>
        </div>

        <div class="flex items-center gap-2 text-xs mb-2">
          <span class="font-bold text-amber-600 dark:text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/30">
            ${escapeHtml(exp.role)} ${exp.level ? '(' + escapeHtml(exp.level) + ')' : ''}
          </span>
          <span class="text-slate-500 dark:text-slate-400 flex items-center gap-1">
            <i data-lucide="map-pin" class="w-3 h-3"></i> ${escapeHtml(exp.location || 'Undisclosed')}
          </span>
        </div>

        <h3 class="font-bold text-base text-slate-900 dark:text-white group-hover:text-amber-500 transition line-clamp-2 mb-2 leading-snug cursor-pointer" onclick="openModal('${exp.id}')">
          ${escapeHtml(exp.title)}
        </h3>

        <div class="flex flex-col gap-1.5 text-[11px] mb-3">
          <div class="flex items-center justify-between">
            <span class="font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
              <i data-lucide="calendar" class="w-3.5 h-3.5 text-blue-500 shrink-0"></i>
              <span>Interview: <strong class="text-blue-600 dark:text-blue-400 font-bold">${escapeHtml(exp.interview_date || formatDate(exp.post_date))}</strong></span>
            </span>
            ${exp.yoe ? `<span class="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 px-2 py-0.5 rounded text-[10px] font-semibold border border-slate-200 dark:border-slate-700">${escapeHtml(exp.yoe)} YOE</span>` : ''}
          </div>
          <div class="flex items-center gap-2 text-[10px] text-slate-400">
            <span>By ${escapeHtml(exp.author || 'Anonymous')}</span>
            <span>•</span>
            <span class="flex items-center gap-1"><i data-lucide="clock" class="w-3 h-3"></i> Posted: ${formatDate(exp.post_date || exp.date)}</span>
          </div>
        </div>

        ${(() => {
          const uniqueQuestions = [];
          const seenQ = new Set();
          (exp.rounds || []).forEach(r => {
            (r.questions || []).forEach(q => {
              const qName = (typeof q === 'string' ? q : (q.name || '')).trim();
              const k = qName.toLowerCase();
              if (!k || seenQ.has(k) || k.length < 4) return;
              if (k.includes('data structures') || k.includes('leadership principles') || k.includes('coding problem')) return;
              seenQ.add(k);
              const freq = state.questionFreqMap?.get(k) || 1;
              uniqueQuestions.push({ name: qName, freq });
            });
          });

          if (uniqueQuestions.length === 0) return '';
          return `
            <div class="mb-3">
              <div class="text-[11px] font-semibold text-slate-400 mb-1 flex items-center justify-between">
                <span>Key Questions Encountered:</span>
              </div>
              <div class="flex flex-wrap gap-1">
                ${uniqueQuestions.slice(0, 2).map(q => `
                  <span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-500/10 text-amber-700 dark:text-amber-300 border border-amber-500/30 flex items-center gap-1">
                    <span class="truncate max-w-[130px]">${escapeHtml(q.name)}</span>
                    <span class="font-extrabold text-amber-600 dark:text-amber-400">(${q.freq}x)</span>
                  </span>
                `).join('')}
                ${uniqueQuestions.length > 2 ? `<span class="text-[10px] text-slate-400 self-center">+${uniqueQuestions.length - 2} more</span>` : ''}
              </div>
            </div>
          `;
        })()}

        <div class="mb-4">
          <div class="text-[11px] font-semibold text-slate-400 mb-1.5">Interview Rounds (${(exp.rounds || []).length}):</div>
          <div class="flex flex-wrap gap-1.5">
            ${roundsList || '<span class="text-xs text-slate-400">Not specified</span>'}
          </div>
        </div>
      </div>

      <div class="pt-3 border-t border-slate-200/80 dark:border-slate-800 flex items-center justify-between mt-auto">
        <div class="flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400">
          <span class="flex items-center gap-1"><i data-lucide="thumbs-up" class="w-3 h-3"></i> ${exp.votes ?? exp.upvotes ?? 0}</span>
          <span class="flex items-center gap-1"><i data-lucide="eye" class="w-3 h-3"></i> ${exp.views || 0}</span>
        </div>

        <button onclick="openModal('${exp.id}')" class="px-3 py-1.5 text-xs font-semibold rounded-xl bg-slate-100 hover:bg-amber-500 dark:bg-slate-800 dark:hover:bg-amber-500 text-slate-700 dark:text-slate-300 hover:text-white dark:hover:text-white transition flex items-center gap-1">
          <span>Details</span>
          <i data-lucide="arrow-right" class="w-3 h-3"></i>
        </button>
      </div>
    </div>
  `;
}

function buildListItemHtml(exp) {
  const outcome = exp.outcome || 'Pending';
  const isBookmarked = state.bookmarkedIds.has(exp.id);
  let outcomeClass = 'badge-pending';
  if (outcome.toLowerCase() === 'offer') outcomeClass = 'badge-offer';
  else if (outcome.toLowerCase() === 'rejected') outcomeClass = 'badge-rejected';

  return `
    <div class="glass-card rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 cursor-pointer" onclick="openModal('${exp.id}')" data-exp-id="${escapeHtml(exp.id)}">
      <div class="flex items-start sm:items-center gap-3">
        <span class="px-2.5 py-1 rounded-full text-xs font-bold ${outcomeClass} shrink-0">
          ${escapeHtml(outcome)}
        </span>

        <div>
          <div class="flex flex-wrap items-center gap-2 mb-1">
            <span class="font-bold text-xs text-amber-600 dark:text-amber-400">${escapeHtml(exp.role)}</span>
            <span class="text-xs text-slate-400">• ${escapeHtml(exp.location || 'Undisclosed')}</span>
            <span class="text-xs font-bold text-blue-600 dark:text-blue-400 flex items-center gap-1">
              <i data-lucide="calendar" class="w-3 h-3"></i> ${escapeHtml(exp.interview_date || formatDate(exp.post_date))}
            </span>
            <span class="text-[10px] text-slate-400">• Posted: ${formatDate(exp.post_date || exp.date)}</span>
          </div>
          <h4 class="text-sm font-bold text-slate-900 dark:text-white hover:text-amber-500 transition">${escapeHtml(exp.title)}</h4>
        </div>
      </div>

      <div class="flex items-center gap-4 text-xs text-slate-400 self-end sm:self-auto shrink-0">
        <span class="flex items-center gap-1"><i data-lucide="thumbs-up" class="w-3.5 h-3.5"></i> ${exp.votes ?? exp.upvotes ?? 0}</span>
        <span class="flex items-center gap-1"><i data-lucide="list" class="w-3.5 h-3.5"></i> ${(exp.rounds || []).length} rounds</span>
        <button onclick="toggleBookmark('${exp.id}', event)" class="p-1 rounded text-slate-400 hover:text-amber-500">
          <i data-lucide="bookmark" class="w-4 h-4 ${isBookmarked ? 'fill-amber-500 text-amber-500' : ''}"></i>
        </button>
      </div>
    </div>
  `;
}

// Render Experiences View with Chunked Pagination
function renderExperiences() {
  const container = document.getElementById('experiences-container');
  const emptyState = document.getElementById('experiences-empty-state');
  const paginationEl = document.getElementById('experiences-pagination');
  if (!container) return;

  if (state.filteredExperiences.length === 0) {
    container.innerHTML = '';
    if (emptyState) emptyState.classList.remove('hidden');
    if (paginationEl) paginationEl.classList.add('hidden');
    return;
  }

  if (emptyState) emptyState.classList.add('hidden');

  const items = state.filteredExperiences.slice(0, state.displayedCount);
  if (state.viewMode === 'list') {
    container.className = 'flex flex-col gap-3';
    container.innerHTML = items.map(buildListItemHtml).join('');
  } else {
    container.className = 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5';
    container.innerHTML = items.map(buildCardHtml).join('');
  }

  updatePaginationControls();
  if (window.lucide) lucide.createIcons({ root: container });
}

function loadMoreExperiences() {
  const container = document.getElementById('experiences-container');
  if (!container) return;
  if (state.displayedCount >= state.filteredExperiences.length) return;

  const prevCount = state.displayedCount;
  const nextCount = prevCount + PAGE_SIZE;
  const newItems = state.filteredExperiences.slice(prevCount, nextCount);
  state.displayedCount = nextCount;

  if (newItems.length > 0) {
    const tempDiv = document.createElement('div');
    if (state.viewMode === 'list') {
      tempDiv.innerHTML = newItems.map(buildListItemHtml).join('');
    } else {
      tempDiv.innerHTML = newItems.map(buildCardHtml).join('');
    }

    const fragment = document.createDocumentFragment();
    const newElements = [];
    while (tempDiv.firstChild) {
      const node = tempDiv.firstChild;
      if (node.nodeType === Node.ELEMENT_NODE) newElements.push(node);
      fragment.appendChild(node);
    }
    container.appendChild(fragment);

    if (window.lucide) {
      newElements.forEach(el => lucide.createIcons({ root: el }));
    }
  }

  updatePaginationControls();
}

function loadAllExperiences() {
  state.displayedCount = state.filteredExperiences.length;
  renderExperiences();
}

function updatePaginationControls() {
  const paginationEl = document.getElementById('experiences-pagination');
  if (!paginationEl) return;

  const total = state.filteredExperiences.length;
  const current = Math.min(state.displayedCount, total);

  if (total <= PAGE_SIZE) {
    paginationEl.classList.add('hidden');
    return;
  }

  paginationEl.classList.remove('hidden');
  const currentCountEl = document.getElementById('pagination-current-count');
  const totalCountEl = document.getElementById('pagination-total-count');
  const btnLoadMore = document.getElementById('btn-load-more');
  const btnLoadMoreText = document.getElementById('btn-load-more-text');
  const btnLoadAll = document.getElementById('btn-load-all');

  if (currentCountEl) currentCountEl.textContent = current;
  if (totalCountEl) totalCountEl.textContent = total;

  if (current >= total) {
    if (btnLoadMore) btnLoadMore.classList.add('hidden');
    if (btnLoadAll) btnLoadAll.classList.add('hidden');
  } else {
    const remaining = total - current;
    const nextBatch = Math.min(PAGE_SIZE, remaining);
    if (btnLoadMore) {
      btnLoadMore.classList.remove('hidden');
      if (btnLoadMoreText) btnLoadMoreText.textContent = `Load More (+${nextBatch})`;
    }
    if (btnLoadAll) btnLoadAll.classList.remove('hidden');
  }
}

function setupScrollObserver() {
  const sentinel = document.getElementById('experiences-scroll-sentinel');
  if (!sentinel) return;

  const observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting && state.activeTab === 'experiences') {
      if (state.displayedCount < state.filteredExperiences.length) {
        loadMoreExperiences();
      }
    }
  }, { rootMargin: '300px' });

  observer.observe(sentinel);
}

// Modal Logic
function openModal(expId) {
  const exp = state.experiences.find(e => String(e.id) === String(expId));
  if (!exp) return;
  state.currentModalExp = exp;

  const modal = document.getElementById('experience-modal');
  if (!modal) return;

  // Title & Header info
  document.getElementById('modal-title').textContent = exp.title;
  document.getElementById('modal-author-name').textContent = exp.author || 'Anonymous';
  document.getElementById('modal-location-text').textContent = exp.location || 'Undisclosed';
  
  const ivDate = exp.interview_date || formatDate(exp.post_date || exp.date);
  const ivDateBadge = document.getElementById('modal-interview-date-text');
  if (ivDateBadge) ivDateBadge.textContent = ivDate;
  const ivDateTile = document.getElementById('modal-interview-date');
  if (ivDateTile) ivDateTile.textContent = ivDate;

  document.getElementById('modal-date-text').textContent = formatDate(exp.post_date || exp.date);
  document.getElementById('modal-role-badge').textContent = `${exp.role || 'Software Engineer'} ${exp.level ? '(' + exp.level + ')' : ''}`;

  // Outcome badge
  const outcomeBadge = document.getElementById('modal-outcome-badge');
  const outcome = exp.outcome || 'Pending';
  outcomeBadge.textContent = outcome;
  if (outcome.toLowerCase() === 'offer') {
    outcomeBadge.className = 'px-2.5 py-0.5 rounded-full text-xs font-bold badge-offer';
  } else if (outcome.toLowerCase() === 'rejected') {
    outcomeBadge.className = 'px-2.5 py-0.5 rounded-full text-xs font-bold badge-rejected';
  } else {
    outcomeBadge.className = 'px-2.5 py-0.5 rounded-full text-xs font-bold badge-pending';
  }

  // YOE & Comp
  document.getElementById('modal-yoe').textContent = exp.yoe || 'Not mentioned';
  document.getElementById('modal-company').textContent = exp.current_company || 'Not mentioned';
  document.getElementById('modal-comp').textContent = exp.compensation || 'Not disclosed';

  // Stats
  document.getElementById('modal-upvotes').textContent = exp.votes ?? exp.upvotes ?? 0;
  document.getElementById('modal-views').textContent = exp.views || 0;

  // Executive Summary
  const summaryEl = document.getElementById('modal-summary-text');
  const summaryBox = document.getElementById('modal-summary-box');
  if (summaryEl && summaryBox) {
    if (exp.summary && exp.summary.trim()) {
      summaryEl.textContent = exp.summary;
      summaryBox.classList.remove('hidden');
    } else {
      summaryBox.classList.add('hidden');
    }
  }

  // LeetCode Discuss Link
  const lcLink = document.getElementById('modal-leetcode-link');
  if (lcLink) {
    lcLink.href = exp.url || 'https://leetcode.com/discuss/interview-experience/';
  }

  // Bookmark icon in modal
  updateModalBookmarkIcon(exp.id);

  // Render Rounds
  const roundsContainer = document.getElementById('modal-rounds-container');
  if (roundsContainer) {
    if (!exp.rounds || exp.rounds.length === 0) {
      roundsContainer.innerHTML = '<p class="text-xs text-slate-400 italic">No individual round breakdown provided.</p>';
    } else {
      roundsContainer.innerHTML = exp.rounds.map((round, idx) => {
        const questionsHtml = (round.questions || []).map(q => {
          const isString = typeof q === 'string';
          const qName = isString ? q : (q.name || 'Technical Problem');
          const qDiff = isString ? '' : q.difficulty;
          const qLeetCode = isString ? '' : q.leetcode_equivalent;
          const qDesc = isString ? '' : q.description;
          const qCode = isString ? '' : q.code_snippet;

          // Cross-interview repetition frequency
          const freq = state.questionFreqMap?.get(qName.toLowerCase()) || 
                       (qLeetCode ? state.questionFreqMap?.get(qLeetCode.toLowerCase()) : 0) || 1;

          return `
            <div class="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/90 border border-slate-200 dark:border-slate-700/80 mb-2.5">
              <div class="flex items-center justify-between gap-2 mb-1.5">
                <span class="font-bold text-sm text-slate-900 dark:text-white">${escapeHtml(qName)}</span>
                <div class="flex items-center gap-1.5 shrink-0">
                  ${freq > 1 ? `
                    <span class="px-2 py-0.5 text-[10px] font-black rounded-full bg-amber-500/15 text-amber-600 dark:text-amber-400 border border-amber-500/30 flex items-center gap-1" title="Asked in ${freq} candidate experiences across Amazon">
                      <svg class="w-3 h-3 text-amber-500 fill-amber-500" viewBox="0 0 20 20"><path d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.316.492-.633.991-1.002 1.488-.707.95-1.55 1.89-2.378 2.87-1.127 1.332-2.146 2.766-2.613 4.316-.487 1.615-.406 3.327.35 4.802.753 1.468 2.06 2.593 3.654 3.09 1.594.496 3.327.323 4.79-.508 1.457-.828 2.535-2.145 2.997-3.725.46-1.574.24-3.268-.54-4.707-.38-.702-.87-1.34-1.39-1.94-.48-.553-.98-1.077-1.48-1.583-.24-.243-.48-.483-.71-.722a10.97 10.97 0 00-.85-.78z"/></svg>
                      ${freq}x Repeated
                    </span>
                  ` : ''}
                  ${qDiff ? `<span class="px-2 py-0.5 text-[10px] font-bold rounded-full ${getDifficultyBadgeClass(qDiff)}">${escapeHtml(qDiff)}</span>` : ''}
                </div>
              </div>
              
              ${qLeetCode ? `<div class="text-xs text-amber-600 dark:text-amber-400 font-semibold mb-1 flex items-center gap-1"><i data-lucide="external-link" class="w-3 h-3"></i> LeetCode Equiv: ${escapeHtml(qLeetCode)}</div>` : ''}
              
              ${qDesc ? `<p class="text-xs text-slate-600 dark:text-slate-300 leading-relaxed mb-2">${escapeHtml(qDesc)}</p>` : ''}

              ${qCode ? `
                <div class="relative mt-2">
                  <div class="flex justify-between items-center bg-slate-200 dark:bg-slate-950 px-3 py-1 rounded-t-lg text-[10px] text-slate-400 border border-b-0 border-slate-300 dark:border-slate-700">
                    <span>Code Snippet</span>
                    <button onclick="copyCode(this)" class="hover:text-white flex items-center gap-1"><i data-lucide="copy" class="w-3 h-3"></i> Copy</button>
                  </div>
                  <pre class="bg-slate-900 text-slate-200 p-3 rounded-b-lg text-xs overflow-x-auto border border-slate-300 dark:border-slate-700 font-mono"><code>${escapeHtml(qCode)}</code></pre>
                </div>
              ` : ''}
            </div>
          `;
        }).join('');

        const lpQuestionsHtml = (round.lp_questions || []).map(lpq => {
          return `
            <li class="flex items-start gap-2 text-xs text-slate-700 dark:text-slate-300">
              <i data-lucide="award" class="w-3.5 h-3.5 text-amber-500 shrink-0 mt-0.5"></i>
              <span>${escapeHtml(lpq)}</span>
            </li>
          `;
        }).join('');

        const roundDetails = round.details || round.notes || '';

        return `
          <div class="p-4 rounded-xl bg-slate-100 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-700/60">
            <div class="flex items-center justify-between pb-2 mb-3 border-b border-slate-200 dark:border-slate-800">
              <div class="flex items-center gap-2">
                <span class="w-6 h-6 rounded-full bg-amber-500 text-white font-black text-xs flex items-center justify-center">${idx + 1}</span>
                <h5 class="font-bold text-sm text-slate-900 dark:text-white">${escapeHtml(round.round_name || round.round_type)}</h5>
              </div>
              <div class="flex items-center gap-2 text-xs text-slate-400">
                ${round.duration ? `<span><i data-lucide="clock" class="w-3 h-3 inline mr-1"></i>${escapeHtml(round.duration)}</span>` : ''}
                ${round.interviewer ? `<span>• ${escapeHtml(round.interviewer)}</span>` : ''}
              </div>
            </div>

            ${questionsHtml ? `<div class="mb-3"><div class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Technical Problems:</div>${questionsHtml}</div>` : ''}

            ${lpQuestionsHtml ? `<div class="mb-3"><div class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1.5">Leadership Principle Probes:</div><ul class="space-y-1.5 bg-amber-500/5 p-3 rounded-lg border border-amber-500/20">${lpQuestionsHtml}</ul></div>` : ''}

            ${roundDetails ? `<div class="text-xs text-slate-600 dark:text-slate-300 bg-slate-200/50 dark:bg-slate-800/60 p-3 rounded-xl border border-slate-300/40 dark:border-slate-700/50 leading-relaxed"><strong class="not-italic font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5 mb-1"><i data-lucide="align-left" class="w-3.5 h-3.5 text-amber-500"></i> Round Details & Walkthrough:</strong> ${escapeHtml(roundDetails)}</div>` : ''}
          </div>
        `;
      }).join('');
    }
  }

  // Leadership Principles Chips
  const lpChipsContainer = document.getElementById('modal-lp-chips');
  if (lpChipsContainer) {
    const lps = exp.leadership_principles || [];
    if (lps.length === 0) {
      lpChipsContainer.innerHTML = '<span class="text-xs text-slate-400 italic">Not explicitly mentioned</span>';
    } else {
      lpChipsContainer.innerHTML = lps.map(lp => {
        return `<span class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/30 flex items-center gap-1.5"><i data-lucide="award" class="w-3.5 h-3.5"></i> ${escapeHtml(lp)}</span>`;
      }).join('');
    }
  }

  // Tips Box
  const tipsContainer = document.getElementById('modal-tips-text');
  if (tipsContainer) {
    if (Array.isArray(exp.tips) && exp.tips.length > 0) {
      tipsContainer.innerHTML = exp.tips.map(t => `
        <div class="flex items-start gap-2 text-xs">
          <i data-lucide="check-circle" class="w-3.5 h-3.5 text-amber-500 shrink-0 mt-0.5"></i>
          <span>${escapeHtml(t)}</span>
        </div>
      `).join('');
    } else if (typeof exp.tips === 'string' && exp.tips.trim()) {
      tipsContainer.innerHTML = `<p class="text-xs">${escapeHtml(exp.tips)}</p>`;
    } else {
      tipsContainer.innerHTML = '<p class="text-xs text-slate-400">No specific tips recorded. Focus on clean coding, clarifying ambiguity, and preparing 2 STAR stories for every LP.</p>';
    }
  }

  // Full Text / Transcript
  const fullTextEl = document.getElementById('modal-full-text-content');
  const fullTextSection = document.getElementById('modal-full-text-section');
  if (fullTextEl && fullTextSection) {
    if (exp.full_text && exp.full_text.trim()) {
      fullTextEl.textContent = exp.full_text;
      fullTextSection.classList.remove('hidden');
    } else {
      fullTextSection.classList.add('hidden');
    }
  }

  modal.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
  if (window.lucide) lucide.createIcons({ root: modal });
}

function closeModal() {
  const modal = document.getElementById('experience-modal');
  if (modal) modal.classList.add('hidden');
  document.body.style.overflow = '';
  state.currentModalExp = null;
}

// Bookmarks in LocalStorage
function toggleBookmark(expId, event) {
  if (event) event.stopPropagation();

  if (state.bookmarkedIds.has(expId)) {
    state.bookmarkedIds.delete(expId);
    showToast('Removed from saved experiences', 'bookmark-minus', 'rose');
  } else {
    state.bookmarkedIds.add(expId);
    showToast('Saved to your bookmarks', 'bookmark-check', 'amber');
  }

  localStorage.setItem('amz_bookmarked_ids', JSON.stringify(Array.from(state.bookmarkedIds)));
  updateResultsCount();
  renderExperiences();

  if (state.currentModalExp && state.currentModalExp.id === expId) {
    updateModalBookmarkIcon(expId);
  }
}

function toggleModalBookmark() {
  if (!state.currentModalExp) return;
  toggleBookmark(state.currentModalExp.id);
}

function updateModalBookmarkIcon(expId) {
  const btn = document.getElementById('modal-bookmark-btn');
  if (!btn) return;
  const isBookmarked = state.bookmarkedIds.has(expId);
  btn.innerHTML = `<i data-lucide="bookmark" class="w-4 h-4 ${isBookmarked ? 'fill-amber-500 text-amber-500' : ''}"></i>`;
  if (window.lucide) lucide.createIcons({ root: btn });
}

// Tab Navigation
function switchTab(tabName) {
  state.activeTab = tabName;

  const tabs = ['experiences', 'questions', 'lp', 'analytics'];
  tabs.forEach(t => {
    const view = document.getElementById(`view-${t}`);
    const navBtn = document.getElementById(`nav-tab-${t}`);
    const mobileBtn = document.getElementById(`mobile-tab-${t}`);

    if (t === tabName) {
      if (view) view.classList.remove('hidden');
      if (navBtn) {
        navBtn.className = 'px-3.5 py-1.5 rounded-lg transition-all flex items-center gap-2 bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm';
      }
      if (mobileBtn) {
        mobileBtn.className = 'px-2.5 py-1 rounded-md bg-white dark:bg-slate-700 text-slate-900 dark:text-white';
      }
    } else {
      if (view) view.classList.add('hidden');
      if (navBtn) {
        navBtn.className = 'px-3.5 py-1.5 rounded-lg transition-all flex items-center gap-2 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white';
      }
      if (mobileBtn) {
        mobileBtn.className = 'px-2.5 py-1 rounded-md text-slate-600 dark:text-slate-400';
      }
    }
  });

  // Lazy-render tabs on first visit only (instant zero-lag switching afterwards)
  if (tabName === 'questions' && !renderedTabs.questions) {
    renderQuestionBank();
    renderedTabs.questions = true;
  } else if (tabName === 'lp' && !renderedTabs.lp) {
    renderLpGuide();
    renderedTabs.lp = true;
  } else if (tabName === 'analytics' && !renderedTabs.analytics) {
    renderAnalytics();
    renderedTabs.analytics = true;
  }
}

// QUESTION BANK VIEW
function renderQuestionBank() {
  const container = document.getElementById('questions-list-container');
  const countLabel = document.getElementById('qb-count-label');
  const paginationBar = document.getElementById('qb-pagination-bar');
  const paginationInfo = document.getElementById('qb-pagination-info');
  const loadMoreBtn = document.getElementById('btn-load-more-qb');
  if (!container) return;

  const isFilteredByDate = state.qbDatePreset !== 'all';
  const dateLabel = getDatePresetLabel(state.qbDatePreset, state.qbDateFrom, state.qbDateTo);

  // Map each question with active occurrences filtered by date
  let list = state.questions.map(q => {
    const activeOccurrences = isFilteredByDate
      ? q.occurrences.filter(o => isDateInFilter(o.date, state.qbDatePreset, state.qbDateFrom, state.qbDateTo))
      : q.occurrences;
    return {
      ...q,
      activeOccurrences
    };
  });

  // Filter by date: exclude questions that didn't appear in the active date period
  if (isFilteredByDate) {
    list = list.filter(q => q.activeOccurrences.length > 0);
  }

  // Category filter
  if (state.qbCategory !== 'all') {
    list = list.filter(q => (q.category || '').toLowerCase().includes(state.qbCategory.toLowerCase()));
  }

  // Difficulty filter
  if (state.qbDifficulty !== 'all') {
    list = list.filter(q => (q.difficulty || '').toLowerCase().includes(state.qbDifficulty.toLowerCase()));
  }

  // Search filter
  if (state.qbSearchQuery.trim()) {
    const s = state.qbSearchQuery.toLowerCase();
    list = list.filter(q => {
      return (q.name || '').toLowerCase().includes(s) ||
             (q.leetcodeEquivalent || '').toLowerCase().includes(s) ||
             (q.description || '').toLowerCase().includes(s) ||
             (q.category || '').toLowerCase().includes(s);
    });
  }

  // Sort Question Bank
  if (state.qbSort === 'frequency-desc') {
    list.sort((a, b) => (b.activeOccurrences.length - a.activeOccurrences.length) || (b.occurrences.length - a.occurrences.length));
  } else if (state.qbSort === 'frequency-asc') {
    list.sort((a, b) => (a.activeOccurrences.length - b.activeOccurrences.length) || (a.occurrences.length - b.occurrences.length));
  } else if (state.qbSort === 'name-asc') {
    list.sort((a, b) => a.name.localeCompare(b.name));
  } else if (state.qbSort === 'diff-hard') {
    const rank = { 'Hard': 3, 'Medium': 2, 'Easy': 1 };
    list.sort((a, b) => (rank[b.difficulty] || 0) - (rank[a.difficulty] || 0));
  } else if (state.qbSort === 'diff-easy') {
    const rank = { 'Easy': 1, 'Medium': 2, 'Hard': 3 };
    list.sort((a, b) => (rank[a.difficulty] || 0) - (rank[b.difficulty] || 0));
  }

  state.filteredQuestions = list;
  const total = list.length;
  if (countLabel) {
    const dateSuffix = isFilteredByDate ? ` in ${dateLabel}` : '';
    countLabel.textContent = `Showing ${Math.min(state.qbDisplayedCount, total)} of ${total} questions${dateSuffix}`;
  }

  if (total === 0) {
    container.innerHTML = `
      <div class="col-span-2 text-center py-12 text-slate-400">
        <svg class="w-10 h-10 mx-auto mb-2 opacity-50 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 18l6-6-6-6M8 6l-6 6 6 6"/></svg>
        <p class="font-bold">No questions found matching your filter${isFilteredByDate ? ` in ${escapeHtml(dateLabel)}` : ''}.</p>
      </div>
    `;
    if (paginationBar) paginationBar.classList.add('hidden');
    return;
  }

  // Slice to displayed count
  const slice = list.slice(0, state.qbDisplayedCount);

  container.innerHTML = slice.map(q => {
    const diffClass = getDifficultyBadgeClass(q.difficulty);
    const activeCount = q.activeOccurrences.length;
    const totalCount = q.occurrences.length;
    const maxVisible = 2;
    const visibleOccurrences = q.activeOccurrences.slice(0, maxVisible);
    const remainingCount = activeCount - maxVisible;

    const seenLinks = visibleOccurrences.map(occ => {
      const dateTag = occ.date ? ` <span class="text-[10px] text-slate-400 font-normal">[${escapeHtml(occ.date)}]</span>` : '';
      return `<button onclick="openModal('${occ.expId}')" class="text-[11px] text-amber-600 dark:text-amber-400 hover:underline font-semibold flex items-center gap-1 text-left truncate max-w-full">• ${escapeHtml(occ.expTitle)} (${escapeHtml(occ.role || 'SDE')})${dateTag}</button>`;
    }).join('');

    const moreTag = remainingCount > 0 
      ? `<button onclick="openModal('${q.activeOccurrences[0].expId}')" class="text-[10px] text-slate-400 hover:text-amber-400 font-medium transition-colors">+${remainingCount} more candidate loop(s)</button>` 
      : '';

    const badgeLabel = isFilteredByDate
      ? `${activeCount}x in ${dateLabel}`
      : `${totalCount}x Repeated`;

    const subTotalBadge = isFilteredByDate && totalCount > activeCount
      ? `<span class="text-[9px] opacity-75 font-normal ml-0.5">(${totalCount}x total)</span>`
      : '';

    return `
      <div class="glass-card rounded-2xl p-4 flex flex-col justify-between border border-slate-200 dark:border-slate-800 transition-all duration-150 hover:border-amber-500/30">
        <div>
          <div class="flex items-center justify-between gap-2 mb-2">
            <div class="flex items-center gap-1.5 flex-wrap">
              <span class="px-2 py-0.5 text-[10px] font-bold rounded-full ${diffClass}">${escapeHtml(q.difficulty)}</span>
              <span class="px-2 py-0.5 text-[10px] rounded font-medium bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-300/60 dark:border-slate-700">${escapeHtml(q.category)}</span>
            </div>

            <!-- Prominent Repetition Count Badge -->
            <span class="px-2.5 py-0.5 text-[11px] font-black rounded-full ${activeCount > 1 ? 'bg-amber-500/20 text-amber-600 dark:text-amber-400 border border-amber-500/40 shadow-xs' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700'} flex items-center gap-1 shrink-0" title="Encountered in ${activeCount} candidate interview loop(s)${isFilteredByDate ? ` during ${dateLabel} (${totalCount}x all-time)` : ''}">
              <svg class="w-3.5 h-3.5 ${activeCount > 1 ? 'text-amber-500 fill-amber-500' : 'text-slate-400'}" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.316.492-.633.991-1.002 1.488-.707.95-1.55 1.89-2.378 2.87-1.127 1.332-2.146 2.766-2.613 4.316-.487 1.615-.406 3.327.35 4.802.753 1.468 2.06 2.593 3.654 3.09 1.594.496 3.327.323 4.79-.508 1.457-.828 2.535-2.145 2.997-3.725.46-1.574.24-3.268-.54-4.707-.38-.702-.87-1.34-1.39-1.94-.48-.553-.98-1.077-1.48-1.583-.24-.243-.48-.483-.71-.722a10.97 10.97 0 00-.85-.78z" clip-rule="evenodd"/></svg>
              <span>${badgeLabel}</span>
              ${subTotalBadge}
            </span>
          </div>

          <h4 class="font-bold text-sm text-slate-900 dark:text-white mb-1 leading-snug">${escapeHtml(q.name)}</h4>
          
          ${q.leetcodeEquivalent ? `
            <div class="text-xs font-semibold text-amber-600 dark:text-amber-400 mb-2 flex items-center gap-1">
              <svg class="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71m-2.12 5.66a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg>
              <span>${escapeHtml(q.leetcodeEquivalent)}</span>
            </div>
          ` : ''}

          ${q.description ? `<p class="text-xs text-slate-600 dark:text-slate-300 leading-relaxed mb-3 line-clamp-3">${escapeHtml(q.description)}</p>` : ''}

          ${q.codeSnippet ? `
            <div class="relative mb-3">
              <pre class="bg-slate-900 text-slate-300 p-2.5 rounded-lg text-[11px] overflow-x-auto border border-slate-800 font-mono"><code>${escapeHtml(q.codeSnippet)}</code></pre>
            </div>
          ` : ''}
        </div>

        <div class="pt-3 border-t border-slate-200 dark:border-slate-800">
          <div class="text-[11px] font-semibold text-slate-400 mb-1 flex items-center justify-between">
            <span>Seen in ${activeCount} candidate interview loop${activeCount > 1 ? 's' : ''}${isFilteredByDate ? ` in ${dateLabel}` : ''}:</span>
            <span class="text-[10px] font-bold text-amber-500">${activeCount} post${activeCount > 1 ? 's' : ''}</span>
          </div>
          <div class="space-y-1">${seenLinks}</div>
          ${moreTag ? `<div class="mt-1">${moreTag}</div>` : ''}
        </div>
      </div>
    `;
  }).join('');

  // Update Pagination / Load More UI
  if (paginationBar) {
    if (total <= state.qbDisplayedCount) {
      paginationBar.classList.add('hidden');
    } else {
      paginationBar.classList.remove('hidden');
      if (paginationInfo) {
        paginationInfo.textContent = `Showing 1 to ${slice.length} of ${total} questions`;
      }
      if (loadMoreBtn) {
        loadMoreBtn.innerHTML = `<span>Load More Questions (${total - slice.length} remaining)</span>`;
      }
    }
  }
}

function loadMoreQuestions() {
  state.qbDisplayedCount += 24;
  renderQuestionBank();
}

let qbSearchDebounceTimer = null;
function onQuestionSearch(val) {
  clearTimeout(qbSearchDebounceTimer);
  qbSearchDebounceTimer = setTimeout(() => {
    state.qbSearchQuery = val;
    state.qbDisplayedCount = 24;
    renderQuestionBank();
  }, 150);
}

function onQuestionCategoryFilter(val) {
  state.qbCategory = val;
  state.qbDisplayedCount = 24;
  renderQuestionBank();
}

function onQuestionDifficultyFilter(val) {
  state.qbDifficulty = val;
  state.qbDisplayedCount = 24;
  renderQuestionBank();
}

function onQuestionDatePresetChange(val) {
  state.qbDatePreset = val;
  const container = document.getElementById('qb-custom-date-container');
  if (container) {
    if (val === 'custom') {
      container.classList.remove('hidden');
      container.classList.add('flex');
    } else {
      container.classList.remove('flex');
      container.classList.add('hidden');
    }
  }
  state.qbDisplayedCount = 24;
  renderQuestionBank();
}

function onQuestionCustomDateChange() {
  const f = document.getElementById('qb-filter-date-from');
  const t = document.getElementById('qb-filter-date-to');
  state.qbDateFrom = f ? f.value : '';
  state.qbDateTo = t ? t.value : '';
  state.qbDisplayedCount = 24;
  renderQuestionBank();
}

function onQuestionSortFilter(val) {
  state.qbSort = val;
  state.qbDisplayedCount = 24;
  renderQuestionBank();
}

function resetQuestionBankFilters() {
  state.qbSearchQuery = '';
  state.qbCategory = 'all';
  state.qbDifficulty = 'all';
  state.qbDatePreset = 'all';
  state.qbDateFrom = '';
  state.qbDateTo = '';
  state.qbSort = 'frequency-desc';
  state.qbDisplayedCount = 24;

  const sInput = document.getElementById('qb-search-input');
  if (sInput) sInput.value = '';
  const catSelect = document.getElementById('qb-filter-category');
  if (catSelect) catSelect.value = 'all';
  const diffSelect = document.getElementById('qb-filter-difficulty');
  if (diffSelect) diffSelect.value = 'all';
  const datePreset = document.getElementById('qb-filter-date-preset');
  if (datePreset) datePreset.value = 'all';
  const sortSelect = document.getElementById('qb-filter-sort');
  if (sortSelect) sortSelect.value = 'frequency-desc';

  const cContainer = document.getElementById('qb-custom-date-container');
  if (cContainer) {
    cContainer.classList.remove('flex');
    cContainer.classList.add('hidden');
  }
  const dFrom = document.getElementById('qb-filter-date-from');
  if (dFrom) dFrom.value = '';
  const dTo = document.getElementById('qb-filter-date-to');
  if (dTo) dTo.value = '';

  renderQuestionBank();
}

// 16 LEADERSHIP PRINCIPLES VIEW
function renderLpGuide() {
  const container = document.getElementById('lp-grid-container');
  if (!container) return;

  let lps = [...LEADERSHIP_PRINCIPLES];
  if (state.lpSearchQuery.trim()) {
    const s = state.lpSearchQuery.toLowerCase();
    lps = lps.filter(lp => {
      return lp.name.toLowerCase().includes(s) ||
             lp.tagline.toLowerCase().includes(s) ||
             lp.description.toLowerCase().includes(s) ||
             lp.sampleQuestions.some(sq => sq.toLowerCase().includes(s));
    });
  }

  container.innerHTML = lps.map(lp => {
    const questionsList = lp.sampleQuestions.map(q => `
      <li class="flex items-start gap-2 text-xs text-slate-700 dark:text-slate-300">
        <svg class="w-3.5 h-3.5 text-amber-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        <span>"${escapeHtml(q)}"</span>
      </li>
    `).join('');

    return `
      <div class="glass-card rounded-2xl p-5 flex flex-col justify-between border border-slate-200 dark:border-slate-800">
        <div>
          <!-- Header -->
          <div class="flex items-start justify-between gap-3 mb-2">
            <div>
              <span class="text-[10px] font-black uppercase tracking-wider text-amber-500">Principle #${lp.num}</span>
              <h3 class="text-lg font-black text-slate-900 dark:text-white">${escapeHtml(lp.name)}</h3>
            </div>
            <div class="w-8 h-8 rounded-xl bg-amber-500/10 text-amber-600 dark:text-amber-400 font-black text-sm flex items-center justify-center border border-amber-500/30">
              ${lp.num}
            </div>
          </div>

          <p class="text-xs font-semibold text-amber-600 dark:text-amber-400 italic mb-2">"${escapeHtml(lp.tagline)}"</p>
          <p class="text-xs text-slate-600 dark:text-slate-300 leading-relaxed mb-4">${escapeHtml(lp.description)}</p>

          <!-- Sample Behavioral Questions -->
          <div class="mb-4">
            <h5 class="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
              <svg class="w-3.5 h-3.5 text-amber-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>
              <span>Top Interview Questions Asked:</span>
            </h5>
            <ul class="space-y-2 bg-slate-100 dark:bg-slate-900/60 p-3 rounded-xl border border-slate-200 dark:border-slate-800">
              ${questionsList}
            </ul>
          </div>
        </div>

        <!-- Signals Footer -->
        <div class="pt-3 border-t border-slate-200 dark:border-slate-800 space-y-2 text-xs">
          <div class="flex items-start gap-1.5 text-emerald-600 dark:text-emerald-400">
            <svg class="w-3.5 h-3.5 text-emerald-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
            <span><strong class="font-bold">What interviewers love:</strong> ${escapeHtml(lp.goodSignals)}</span>
          </div>
          <div class="flex items-start gap-1.5 text-rose-600 dark:text-rose-400">
            <svg class="w-3.5 h-3.5 text-rose-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
            <span><strong class="font-bold">Red flags:</strong> ${escapeHtml(lp.badSignals)}</span>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

let lpSearchDebounceTimer = null;
function onLpSearch(val) {
  clearTimeout(lpSearchDebounceTimer);
  lpSearchDebounceTimer = setTimeout(() => {
    state.lpSearchQuery = val;
    renderLpGuide();
  }, 150);
}

// INTERVIEW ANALYTICS VIEW
function renderAnalytics() {
  const total = state.experiences.length;
  if (total === 0) return;

  let offers = 0;
  let rejections = 0;
  let pending = 0;
  const lpCountMap = {};
  const roleCountMap = {};
  const topicCountMap = {};

  state.experiences.forEach(exp => {
    const outcome = (exp.outcome || '').toLowerCase();
    if (outcome === 'offer') offers++;
    else if (outcome === 'rejected') rejections++;
    else pending++;

    const role = exp.role || 'Other';
    roleCountMap[role] = (roleCountMap[role] || 0) + 1;

    if (exp.leadership_principles) {
      exp.leadership_principles.forEach(lp => {
        lpCountMap[lp] = (lpCountMap[lp] || 0) + 1;
      });
    }

    if (exp.rounds) {
      exp.rounds.forEach(r => {
        if (r.questions) {
          r.questions.forEach(q => {
            const cat = q.category || 'General Algorithms';
            topicCountMap[cat] = (topicCountMap[cat] || 0) + 1;
          });
        }
      });
    }
  });

  // Progress Bars
  const offerPct = Math.round((offers / total) * 100);
  const rejPct = Math.round((rejections / total) * 100);
  const pendPct = Math.round((pending / total) * 100);

  document.getElementById('analytics-bar-offer').style.width = `${offerPct}%`;
  document.getElementById('analytics-bar-offer-label').textContent = `${offerPct}% (${offers})`;

  document.getElementById('analytics-bar-rejected').style.width = `${rejPct}%`;
  document.getElementById('analytics-bar-rejected-label').textContent = `${rejPct}% (${rejections})`;

  document.getElementById('analytics-bar-pending').style.width = `${pendPct}%`;
  document.getElementById('analytics-bar-pending-label').textContent = `${pendPct}% (${pending})`;

  // LP Frequency List
  const lpListEl = document.getElementById('analytics-lp-list');
  if (lpListEl) {
    const sortedLPs = Object.entries(lpCountMap).sort((a, b) => b[1] - a[1]).slice(0, 6);
    lpListEl.innerHTML = sortedLPs.map(([lp, count]) => {
      const pct = Math.round((count / total) * 100);
      return `
        <div>
          <div class="flex justify-between mb-1">
            <span class="font-semibold text-slate-800 dark:text-slate-200">${escapeHtml(lp)}</span>
            <span class="text-slate-400 font-bold">${count} (${pct}% of candidates)</span>
          </div>
          <div class="w-full h-2 rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden">
            <div class="h-full bg-amber-500 rounded-full" style="width: ${pct}%"></div>
          </div>
        </div>
      `;
    }).join('');
  }

  // Roles List
  const rolesListEl = document.getElementById('analytics-roles-list');
  if (rolesListEl) {
    const sortedRoles = Object.entries(roleCountMap).sort((a, b) => b[1] - a[1]);
    rolesListEl.innerHTML = sortedRoles.map(([role, count]) => {
      const pct = Math.round((count / total) * 100);
      return `
        <div>
          <div class="flex justify-between mb-1">
            <span class="font-semibold text-slate-800 dark:text-slate-200">${escapeHtml(role)}</span>
            <span class="text-slate-400 font-bold">${count} experiences</span>
          </div>
          <div class="w-full h-2 rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden">
            <div class="h-full bg-blue-500 rounded-full" style="width: ${pct}%"></div>
          </div>
        </div>
      `;
    }).join('');
  }

  // Topics List
  const topicsListEl = document.getElementById('analytics-topics-list');
  if (topicsListEl) {
    const sortedTopics = Object.entries(topicCountMap).sort((a, b) => b[1] - a[1]).slice(0, 6);
    topicsListEl.innerHTML = sortedTopics.map(([topic, count]) => {
      return `
        <div class="flex items-center justify-between p-2.5 rounded-xl bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/60">
          <span class="font-semibold text-slate-800 dark:text-slate-200">${escapeHtml(topic)}</span>
          <span class="px-2 py-0.5 rounded-md text-[10px] font-bold bg-purple-500/10 text-purple-600 dark:text-purple-400 border border-purple-500/20">${count} questions</span>
        </div>
      `;
    }).join('');
  }

  const analyticsContainer = document.getElementById('view-analytics');
  if (window.lucide && analyticsContainer) lucide.createIcons({ root: analyticsContainer });
}

// Data Export (JSON or CSV)
function toggleExportMenu() {
  const menu = document.getElementById('export-menu');
  if (menu) menu.classList.toggle('hidden');
}

// Close export menu when clicking outside
document.addEventListener('click', (e) => {
  const btn = document.getElementById('btn-export');
  const menu = document.getElementById('export-menu');
  if (menu && !menu.contains(e.target) && btn && !btn.contains(e.target)) {
    menu.classList.add('hidden');
  }
});

function exportData(format) {
  toggleExportMenu();
  const data = state.filteredExperiences.length > 0 ? state.filteredExperiences : state.experiences;

  if (format === 'json') {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    downloadBlob(blob, `amazon-interview-experiences-${new Date().toISOString().slice(0, 10)}.json`);
    showToast('Exported filtered data as JSON', 'download', 'emerald');
  } else if (format === 'csv') {
    const headers = ['id', 'title', 'role', 'level', 'location', 'outcome', 'date', 'yoe', 'upvotes', 'views', 'url'];
    const rows = data.map(item => {
      return headers.map(h => {
        let val = item[h] || '';
        if (typeof val === 'string') val = `"${val.replace(/"/g, '""')}"`;
        return val;
      }).join(',');
    });
    const csvContent = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    downloadBlob(blob, `amazon-interview-experiences-${new Date().toISOString().slice(0, 10)}.csv`);
    showToast('Exported filtered data as CSV', 'table', 'emerald');
  }
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function copyExperienceSummary() {
  if (!state.currentModalExp) return;
  const exp = state.currentModalExp;
  const text = `${exp.title}\nOutcome: ${exp.outcome}\nLocation: ${exp.location}\nYOE: ${exp.yoe || 'N/A'}\nCompensation: ${exp.compensation || 'N/A'}\nURL: ${exp.url}\nTips: ${exp.tips || ''}`;
  navigator.clipboard.writeText(text).then(() => {
    showToast('Experience summary copied to clipboard!', 'check', 'emerald');
  });
}

function copyCode(btn) {
  const pre = btn.closest('.relative').querySelector('code');
  if (pre) {
    navigator.clipboard.writeText(pre.textContent).then(() => {
      showToast('Code snippet copied to clipboard', 'copy', 'emerald');
    });
  }
}

// Keyboard Shortcuts
function setupKeyboardShortcuts() {
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeModal();
    } else if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
      e.preventDefault();
      const sInput = document.getElementById('search-input');
      if (sInput) {
        switchTab('experiences');
        sInput.focus();
      }
    }
  });
}

// Toast Notification
function showToast(message, iconName = 'check', color = 'emerald') {
  const toast = document.getElementById('toast-notification');
  const msgEl = document.getElementById('toast-message');
  const iconWrapper = document.getElementById('toast-icon-wrapper');
  if (!toast || !msgEl) return;

  msgEl.textContent = message;
  iconWrapper.className = `w-6 h-6 rounded-lg flex items-center justify-center shrink-0 bg-${color}-500/10 text-${color}-500`;
  iconWrapper.innerHTML = `<i data-lucide="${iconName}" class="w-3.5 h-3.5"></i>`;

  toast.classList.remove('translate-y-20', 'opacity-0');
  toast.classList.add('translate-y-0', 'opacity-100');

  if (window.lucide) lucide.createIcons({ root: iconWrapper });

  setTimeout(() => {
    toast.classList.remove('translate-y-0', 'opacity-100');
    toast.classList.add('translate-y-20', 'opacity-0');
  }, 3000);
}

// Helpers
function renderAllViews() {
  renderExperiences();
  renderedTabs.questions = false;
  renderedTabs.lp = false;
  renderedTabs.analytics = false;
  if (state.activeTab === 'questions') {
    renderQuestionBank();
    renderedTabs.questions = true;
  } else if (state.activeTab === 'lp') {
    renderLpGuide();
    renderedTabs.lp = true;
  } else if (state.activeTab === 'analytics') {
    renderAnalytics();
    renderedTabs.analytics = true;
  }
}

function getDifficultyBadgeClass(diff) {
  const d = (diff || '').toLowerCase();
  if (d.includes('hard')) return 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/30';
  if (d.includes('medium')) return 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/30';
  return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30';
}

function formatDate(dateStr) {
  if (!dateStr) return 'Recently';
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  } catch (e) {
    return dateStr;
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
