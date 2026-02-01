/**
 * Newton Teacher's Aide - Application
 * The Ultimate Teaching Assistant for HISD NES
 * © 2026 Jared Lewis · Ada Computing Company
 * Last Updated: January 6, 2026
 */

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════════

const CONFIG = {
  // API endpoint - Newton API backend
  API_BASE: window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : window.location.origin,
  TIMEOUT: 60000
};

// Store for current lesson plan (for slide generation)
let currentLessonPlan = null;

// ═══════════════════════════════════════════════════════════════════════════════
// API CLIENT
// ═══════════════════════════════════════════════════════════════════════════════

async function apiRequest(endpoint, method = 'GET', data = null) {
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json'
    }
  };

  if (data) {
    options.body = JSON.stringify(data);
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), CONFIG.TIMEOUT);
  options.signal = controller.signal;

  try {
    const response = await fetch(`${CONFIG.API_BASE}${endpoint}`, options);
    clearTimeout(timeout);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'API request failed');
    }

    return await response.json();
  } catch (error) {
    clearTimeout(timeout);
    if (error.name === 'AbortError') {
      throw new Error('Request timed out');
    }
    throw error;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// VIEW NAVIGATION
// ═══════════════════════════════════════════════════════════════════════════════

function initNavigation() {
  const navItems = document.querySelectorAll('.nav-item');
  const views = document.querySelectorAll('.view');

  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const viewId = item.dataset.view;

      // Update nav state
      navItems.forEach(nav => nav.classList.remove('active'));
      item.classList.add('active');

      // Show view
      views.forEach(view => view.classList.remove('active'));
      document.getElementById(`view-${viewId}`).classList.add('active');
    });
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// STATUS INDICATOR
// ═══════════════════════════════════════════════════════════════════════════════

async function checkStatus() {
  const statusEl = document.getElementById('status');

  try {
    const response = await apiRequest('/health');
    statusEl.classList.add('online');
    statusEl.querySelector('.status-text').textContent = 'Connected';
  } catch (error) {
    statusEl.classList.remove('online');
    statusEl.querySelector('.status-text').textContent = 'Offline';
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// LESSON PLANNER
// ═══════════════════════════════════════════════════════════════════════════════

function initLessonPlanner() {
  const form = document.getElementById('lesson-form');

  // Accommodation checkbox toggles
  ['ell', '504', 'sped', 'gt'].forEach(type => {
    const checkbox = document.getElementById(`acc-${type}`);
    const input = document.getElementById(`acc-${type}-names`);

    checkbox.addEventListener('change', () => {
      input.disabled = !checkbox.checked;
      if (checkbox.checked) input.focus();
    });
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const grade = parseInt(document.getElementById('lesson-grade').value);
    const subject = document.getElementById('lesson-subject').value;
    const teksInput = document.getElementById('lesson-teks').value;
    const topic = document.getElementById('lesson-topic').value || null;

    const teks_codes = teksInput.split(',').map(t => t.trim().toUpperCase()).filter(t => t);

    // Collect accommodations
    const student_needs = {};
    ['ell', '504', 'sped', 'gt'].forEach(type => {
      const checkbox = document.getElementById(`acc-${type}`);
      const input = document.getElementById(`acc-${type}-names`);
      if (checkbox.checked && input.value.trim()) {
        student_needs[type] = input.value.split(',').map(n => n.trim()).filter(n => n);
      }
    });

    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<div class="spinner"></div> Generating...';

    try {
      const result = await apiRequest('/education/lesson', 'POST', {
        grade,
        subject,
        teks_codes,
        topic,
        student_needs: Object.keys(student_needs).length > 0 ? student_needs : null
      });

      if (result.verified) {
        currentLessonPlan = result.lesson_plan;
        displayLessonPlan(result);
      } else {
        alert('Error: ' + (result.error || 'Failed to generate lesson plan'));
      }
    } catch (error) {
      alert('Error: ' + error.message);
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<span class="btn-icon">✨</span> Generate Lesson Plan';
    }
  });
}

function displayLessonPlan(result) {
  const container = document.getElementById('lesson-result');
  const content = document.getElementById('lesson-content');
  const lesson = result.lesson_plan;

  document.getElementById('lesson-time').textContent = `${result.elapsed_us}μs`;
  document.getElementById('lesson-fingerprint').textContent = result.fingerprint;

  const teksBadges = lesson.teks_alignment.map(t =>
    `<span class="teks-badge">${t.code}</span>`
  ).join('');

  const phasesHTML = lesson.phases.map(phase => {
    const phaseClass = phase.phase;
    const icon = getPhaseIcon(phase.phase);

    return `
      <div class="lesson-phase">
        <div class="phase-header">
          <div class="phase-icon ${phaseClass}">${icon}</div>
          <div class="phase-title">
            <h4>${phase.title}</h4>
            <span>${phase.phase.charAt(0).toUpperCase() + phase.phase.slice(1)} Phase</span>
          </div>
          <div class="phase-duration">${phase.duration_minutes} min</div>
        </div>

        <div class="phase-activities">
          <h5>Activities</h5>
          <ul>
            ${phase.activities.map(a => `<li>${a}</li>`).join('')}
          </ul>
        </div>

        <div class="phase-sections">
          <div class="phase-section">
            <h5>Teacher Actions</h5>
            <ul>
              ${phase.teacher_actions.map(a => `<li>${a}</li>`).join('')}
            </ul>
          </div>
          <div class="phase-section">
            <h5>Student Actions</h5>
            <ul>
              ${phase.student_actions.map(a => `<li>${a}</li>`).join('')}
            </ul>
          </div>
        </div>

        ${phase.formative_checks && phase.formative_checks.length > 0 ? `
          <div class="phase-section" style="margin-top: 1rem; background: #FEF3C7; border-left: 3px solid #F59E0B;">
            <h5>Checks for Understanding</h5>
            <ul>
              ${phase.formative_checks.map(c => `<li>${c}</li>`).join('')}
            </ul>
          </div>
        ` : ''}
      </div>
    `;
  }).join('');

  content.innerHTML = `
    <h3 class="lesson-title">${lesson.title}</h3>

    <div class="lesson-meta">
      <div class="meta-item">
        <strong>Grade:</strong> ${lesson.grade}
      </div>
      <div class="meta-item">
        <strong>Subject:</strong> ${lesson.subject}
      </div>
      <div class="meta-item">
        <strong>Date:</strong> ${lesson.date}
      </div>
      <div class="meta-item">
        <strong>Duration:</strong> ${lesson.total_duration_minutes} minutes
      </div>
    </div>

    <div class="teks-badges">
      ${teksBadges}
    </div>

    <div class="lesson-objective">
      <strong>Learning Objective</strong>
      ${lesson.objective}
    </div>

    ${lesson.vocabulary && lesson.vocabulary.length > 0 ? `
      <div class="lesson-phase">
        <h4>Key Vocabulary</h4>
        <ul>
          ${lesson.vocabulary.map(v => `<li><strong>${v.term}</strong>: ${v.definition}</li>`).join('')}
        </ul>
      </div>
    ` : ''}

    ${phasesHTML}

    ${lesson.differentiation ? `
      <div class="lesson-phase">
        <h4>Differentiation Strategies</h4>
        <div class="phase-sections">
          <div class="phase-section">
            <h5>Below Level</h5>
            <p>${lesson.differentiation.below_level}</p>
          </div>
          <div class="phase-section">
            <h5>On Level</h5>
            <p>${lesson.differentiation.on_level}</p>
          </div>
          <div class="phase-section">
            <h5>Above Level</h5>
            <p>${lesson.differentiation.above_level}</p>
          </div>
        </div>
      </div>
    ` : ''}

    ${lesson.accommodations ? `
      <div class="lesson-phase">
        <h4>Student Accommodations</h4>
        ${Object.entries(lesson.accommodations).map(([key, items]) => `
          <div class="phase-section">
            <h5>${key}</h5>
            <ul>
              ${items.map(item => `<li>${item}</li>`).join('')}
            </ul>
          </div>
        `).join('')}
      </div>
    ` : ''}
  `;

  container.classList.remove('hidden');
  container.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function getPhaseIcon(phase) {
  const icons = {
    opening: '🎯',
    instruction: '📖',
    guided: '👥',
    independent: '✏️',
    closing: '📝'
  };
  return icons[phase] || '📌';
}

function generateSlidesFromLesson() {
  if (!currentLessonPlan) {
    alert('Please generate a lesson plan first.');
    return;
  }

  // Switch to slides view
  document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
  document.querySelector('[data-view="slides"]').classList.add('active');
  document.querySelectorAll('.view').forEach(view => view.classList.remove('active'));
  document.getElementById('view-slides').classList.add('active');

  // Fill in the lesson plan JSON
  document.getElementById('slides-json').value = JSON.stringify(currentLessonPlan, null, 2);
}

function printLesson() {
  window.print();
}

function exportLesson() {
  if (!currentLessonPlan) {
    alert('No lesson plan to export.');
    return;
  }

  const blob = new Blob([JSON.stringify(currentLessonPlan, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `lesson-plan-${currentLessonPlan.date || 'export'}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SLIDE DECK GENERATOR
// ═══════════════════════════════════════════════════════════════════════════════

function initSlideGenerator() {
  const form = document.getElementById('slides-form');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const style = document.getElementById('slides-style').value;
    const jsonInput = document.getElementById('slides-json').value;

    let lessonPlan;
    try {
      lessonPlan = JSON.parse(jsonInput);
    } catch (error) {
      alert('Invalid JSON. Please paste a valid lesson plan.');
      return;
    }

    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<div class="spinner"></div> Generating...';

    try {
      const result = await apiRequest('/education/slides', 'POST', {
        lesson_plan: lessonPlan,
        style
      });

      if (result.verified) {
        displaySlides(result);
      } else {
        alert('Error generating slides');
      }
    } catch (error) {
      alert('Error: ' + error.message);
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<span class="btn-icon">📊</span> Generate Slides';
    }
  });
}

function displaySlides(result) {
  const container = document.getElementById('slides-result');
  const content = document.getElementById('slides-content');
  const deck = result.slide_deck;

  document.getElementById('slides-time').textContent = `${result.elapsed_us}μs`;
  document.getElementById('slides-count').textContent = `${deck.total_slides} slides`;

  content.innerHTML = deck.slides.map(slide => `
    <div class="slide-card">
      <div class="slide-header">Slide ${slide.slide_number} - ${slide.type}</div>
      <div class="slide-content">
        <div class="slide-title">${slide.title || ''}</div>
        <div class="slide-body">${slide.subtitle || slide.content || ''}</div>
      </div>
    </div>
  `).join('');

  container.classList.remove('hidden');
}

// ═══════════════════════════════════════════════════════════════════════════════
// ASSESSMENT ANALYZER
// ═══════════════════════════════════════════════════════════════════════════════

function initAssessmentAnalyzer() {
  const form = document.getElementById('assess-form');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const assessment_name = document.getElementById('assess-name').value;
    const teksInput = document.getElementById('assess-teks').value;
    const total_points = parseFloat(document.getElementById('assess-total').value);
    const mastery_threshold = parseFloat(document.getElementById('assess-threshold').value);
    const dataInput = document.getElementById('assess-data').value;

    const teks_codes = teksInput.split(',').map(t => t.trim().toUpperCase()).filter(t => t);

    // Parse student data
    const students = dataInput.trim().split('\n').map((line, idx) => {
      const [name, score] = line.split(',').map(s => s.trim());
      return {
        id: String(idx + 1),
        name: name || `Student ${idx + 1}`,
        score: parseFloat(score) || 0
      };
    }).filter(s => s.name);

    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<div class="spinner"></div> Analyzing...';

    try {
      const result = await apiRequest('/education/assess', 'POST', {
        assessment_name,
        teks_codes,
        total_points,
        mastery_threshold,
        students
      });

      if (result.verified) {
        displayAssessment(result);
      } else {
        alert('Error analyzing assessment');
      }
    } catch (error) {
      alert('Error: ' + error.message);
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<span class="btn-icon">✅</span> Analyze Assessment';
    }
  });
}

function displayAssessment(result) {
  const container = document.getElementById('assess-result');
  const statsEl = document.getElementById('assess-stats');
  const groupsEl = document.getElementById('assess-groups');
  const analysis = result.analysis;
  const stats = analysis.statistics;
  const groups = analysis.groups;

  document.getElementById('assess-time').textContent = 'Analysis complete';

  statsEl.innerHTML = `
    <div class="stat-card">
      <div class="stat-value">${stats.class_average}%</div>
      <div class="stat-label">Class Average</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">${stats.class_median}%</div>
      <div class="stat-label">Class Median</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">${stats.mastery_rate}%</div>
      <div class="stat-label">Mastery Rate</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">${stats.total_students}</div>
      <div class="stat-label">Total Students</div>
    </div>
  `;

  groupsEl.innerHTML = `
    <div class="group-card reteach">
      <div class="group-header">
        <div class="group-icon">⚠️</div>
        <div>
          <div class="group-title">Needs Reteach</div>
          <div class="group-count">${groups.needs_reteach.count} students</div>
        </div>
      </div>
      <ul class="student-list">
        ${groups.needs_reteach.students.map(s => `
          <li>
            <span>${s.student_name}</span>
            <span class="student-score">${s.percentage}%</span>
          </li>
        `).join('') || '<li>No students in this group</li>'}
      </ul>
      <div class="group-recommendation">${groups.needs_reteach.recommendation}</div>
    </div>

    <div class="group-card approaching">
      <div class="group-header">
        <div class="group-icon">📊</div>
        <div>
          <div class="group-title">Approaching</div>
          <div class="group-count">${groups.approaching.count} students</div>
        </div>
      </div>
      <ul class="student-list">
        ${groups.approaching.students.map(s => `
          <li>
            <span>${s.student_name}</span>
            <span class="student-score">${s.percentage}%</span>
          </li>
        `).join('') || '<li>No students in this group</li>'}
      </ul>
      <div class="group-recommendation">${groups.approaching.recommendation}</div>
    </div>

    <div class="group-card mastery">
      <div class="group-header">
        <div class="group-icon">⭐</div>
        <div>
          <div class="group-title">At Mastery</div>
          <div class="group-count">${groups.mastery.count} students</div>
        </div>
      </div>
      <ul class="student-list">
        ${groups.mastery.students.map(s => `
          <li>
            <span>${s.student_name}</span>
            <span class="student-score">${s.percentage}%</span>
          </li>
        `).join('') || '<li>No students in this group</li>'}
      </ul>
      <div class="group-recommendation">${groups.mastery.recommendation}</div>
    </div>
  `;

  container.classList.remove('hidden');
  container.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ═══════════════════════════════════════════════════════════════════════════════
// PLC REPORT GENERATOR
// ═══════════════════════════════════════════════════════════════════════════════

function initPLCGenerator() {
  const form = document.getElementById('plc-form');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const team_name = document.getElementById('plc-team').value;
    const reporting_period = document.getElementById('plc-period').value || null;
    const teksInput = document.getElementById('plc-teks').value;
    const dataInput = document.getElementById('plc-data').value;

    const teks_codes = teksInput.split(',').map(t => t.trim().toUpperCase()).filter(t => t);

    // Parse student data
    const assessment_data = dataInput.trim().split('\n').map((line, idx) => {
      const [name, score] = line.split(',').map(s => s.trim());
      return {
        id: String(idx + 1),
        name: name || `Student ${idx + 1}`,
        score: parseFloat(score) || 0
      };
    }).filter(s => s.name);

    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<div class="spinner"></div> Generating...';

    try {
      const result = await apiRequest('/education/plc', 'POST', {
        team_name,
        reporting_period,
        teks_codes,
        assessment_data
      });

      if (result.verified) {
        displayPLCReport(result);
      } else {
        alert('Error generating PLC report');
      }
    } catch (error) {
      alert('Error: ' + error.message);
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<span class="btn-icon">📈</span> Generate PLC Report';
    }
  });
}

function displayPLCReport(result) {
  const container = document.getElementById('plc-result');
  const content = document.getElementById('plc-content');
  const report = result.plc_report;

  document.getElementById('plc-time').textContent = `${result.elapsed_us}μs`;

  content.innerHTML = `
    <div class="plc-section">
      <h3>📊 Summary</h3>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-value">${report.summary.class_average}%</div>
          <div class="stat-label">Class Average</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">${report.summary.mastery_rate}%</div>
          <div class="stat-label">Mastery Rate</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">${report.summary.needs_reteach}</div>
          <div class="stat-label">Need Reteach</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">${report.summary.total_students}</div>
          <div class="stat-label">Total Students</div>
        </div>
      </div>
    </div>

    <div class="plc-section">
      <h3>💡 Data Insights</h3>
      ${report.insights.map(insight => `
        <div class="insight-card ${insight.type}">
          <div class="insight-title">${insight.title}</div>
          <div class="insight-description">${insight.description}</div>
        </div>
      `).join('')}
    </div>

    <div class="plc-section">
      <h3>✅ Action Items</h3>
      ${report.action_items.map(item => `
        <div class="action-item">
          <div class="action-header">
            <span class="action-priority ${item.priority}">${item.priority}</span>
            <span>${item.timeline}</span>
          </div>
          <div class="action-content">${item.action}</div>
          <div class="action-meta">
            <span><strong>Owner:</strong> ${item.owner}</span>
            <span><strong>Resources:</strong> ${item.resources}</span>
          </div>
        </div>
      `).join('')}
    </div>

    <div class="plc-section">
      <h3>🎯 Next Steps</h3>
      <div class="steps">
        <div class="step">
          <div class="step-number">1</div>
          <div class="step-content">
            <h4>Immediate</h4>
            <p>${report.next_steps.immediate}</p>
          </div>
        </div>
        <div class="step">
          <div class="step-number">2</div>
          <div class="step-content">
            <h4>Short-Term</h4>
            <p>${report.next_steps.short_term}</p>
          </div>
        </div>
        <div class="step">
          <div class="step-number">3</div>
          <div class="step-content">
            <h4>Long-Term</h4>
            <p>${report.next_steps.long_term}</p>
          </div>
        </div>
      </div>
    </div>

    <div class="plc-section">
      <h3>💬 Discussion Points</h3>
      <ul class="tips-list">
        ${report.plc_discussion_points.map(point => `<li>${point}</li>`).join('')}
      </ul>
    </div>
  `;

  container.classList.remove('hidden');
  container.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function printPLC() {
  window.print();
}

// ═══════════════════════════════════════════════════════════════════════════════
// TEKS BROWSER
// ═══════════════════════════════════════════════════════════════════════════════

async function loadTEKS() {
  const resultsEl = document.getElementById('teks-results');
  resultsEl.innerHTML = '<div class="loading"><div class="spinner"></div> Loading TEKS...</div>';

  try {
    const result = await apiRequest('/education/teks');
    displayTEKS(result.standards);
  } catch (error) {
    resultsEl.innerHTML = `<p>Error loading TEKS: ${error.message}</p>`;
  }
}

async function searchTEKS() {
  const query = document.getElementById('teks-search').value.trim();
  if (!query) {
    loadTEKS();
    return;
  }

  const resultsEl = document.getElementById('teks-results');
  resultsEl.innerHTML = '<div class="loading"><div class="spinner"></div> Searching...</div>';

  try {
    const result = await apiRequest('/education/teks/search', 'POST', { query });
    displayTEKS(result.results);
  } catch (error) {
    resultsEl.innerHTML = `<p>Error searching TEKS: ${error.message}</p>`;
  }
}

async function filterTEKS() {
  const grade = document.getElementById('teks-grade-filter').value;
  const subject = document.getElementById('teks-subject-filter').value;

  const resultsEl = document.getElementById('teks-results');
  resultsEl.innerHTML = '<div class="loading"><div class="spinner"></div> Loading...</div>';

  try {
    let endpoint = '/education/teks';
    const params = new URLSearchParams();
    if (grade) params.append('grade', grade);
    if (subject) params.append('subject', subject);
    if (params.toString()) endpoint += '?' + params.toString();

    const result = await apiRequest(endpoint);
    displayTEKS(result.standards);
  } catch (error) {
    resultsEl.innerHTML = `<p>Error loading TEKS: ${error.message}</p>`;
  }
}

function displayTEKS(standards) {
  const resultsEl = document.getElementById('teks-results');

  if (!standards || standards.length === 0) {
    resultsEl.innerHTML = '<p>No TEKS standards found.</p>';
    return;
  }

  resultsEl.innerHTML = standards.map(s => `
    <div class="teks-card" onclick="selectTEKS('${s.code}')">
      <div class="teks-code">${s.code}</div>
      <div class="teks-meta">
        <span>Grade ${s.grade}</span>
        <span>${s.subject.replace('_', ' ')}</span>
        <span>Bloom: ${s.cognitive_level}</span>
      </div>
      <div class="teks-skill">${s.skill}</div>
      <div class="teks-keywords">
        ${s.keywords.slice(0, 5).map(k => `<span class="teks-keyword">${k}</span>`).join('')}
      </div>
    </div>
  `).join('');
}

function selectTEKS(code) {
  // Copy to clipboard
  navigator.clipboard.writeText(code).then(() => {
    alert(`TEKS code ${code} copied to clipboard!`);
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initLessonPlanner();
  initSlideGenerator();
  initAssessmentAnalyzer();
  initPLCGenerator();

  // Check server status
  checkStatus();
  setInterval(checkStatus, 30000);

  // Load initial TEKS
  loadTEKS();

  // Search on Enter
  document.getElementById('teks-search').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') searchTEKS();
  });
});

// Make functions available globally
window.generateSlidesFromLesson = generateSlidesFromLesson;
window.printLesson = printLesson;
window.exportLesson = exportLesson;
window.printPLC = printPLC;
window.searchTEKS = searchTEKS;
window.filterTEKS = filterTEKS;
window.selectTEKS = selectTEKS;

// ═══════════════════════════════════════════════════════════════════════════════
// ENHANCED FEATURES - JANUARY 2026
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Keyboard Navigation
 * Alt+1-6 for quick view switching
 * Cmd/Ctrl+S for save
 * Cmd/Ctrl+E for export
 */
function initKeyboardNavigation() {
  document.addEventListener('keydown', (e) => {
    // View switching: Alt + Number
    if (e.altKey && !e.ctrlKey && !e.metaKey) {
      const viewMap = {
        '1': 'lesson',
        '2': 'slides',
        '3': 'assess',
        '4': 'plc',
        '5': 'teks',
        '6': 'guide'
      };
      
      if (viewMap[e.key]) {
        e.preventDefault();
        const navItem = document.querySelector(`[data-view="${viewMap[e.key]}"]`);
        if (navItem) navItem.click();
      }
    }

    // Save: Cmd/Ctrl+S
    if ((e.metaKey || e.ctrlKey) && e.key === 's') {
      e.preventDefault();
      autoSave();
    }

    // Export: Cmd/Ctrl+E
    if ((e.metaKey || e.ctrlKey) && e.key === 'e') {
      e.preventDefault();
      exportCurrentView();
    }

    // Print: Cmd/Ctrl+P (enhanced)
    if ((e.metaKey || e.ctrlKey) && e.key === 'p') {
      e.preventDefault();
      enhancedPrint();
    }
  });
}

/**
 * Auto-save functionality
 */
let autoSaveTimer = null;
const AUTO_SAVE_DELAY = 3000; // 3 seconds

function setupAutoSave() {
  // Watch all form inputs
  document.querySelectorAll('input, textarea, select').forEach(input => {
    input.addEventListener('input', () => {
      clearTimeout(autoSaveTimer);
      autoSaveTimer = setTimeout(autoSave, AUTO_SAVE_DELAY);
      showAutoSaveIndicator('saving');
    });
  });
}

function autoSave() {
  const currentView = document.querySelector('.view.active');
  if (!currentView) return;

  const viewId = currentView.id.replace('view-', '');
  const formData = gatherFormData(viewId);
  
  // Save to localStorage
  localStorage.setItem(`newton-aide-${viewId}`, JSON.stringify({
    data: formData,
    timestamp: Date.now()
  }));
  
  showAutoSaveIndicator('saved');
  setTimeout(() => showAutoSaveIndicator('idle'), 2000);
}

function gatherFormData(viewId) {
  const form = document.querySelector(`#view-${viewId} form`);
  if (!form) return {};

  const formData = {};
  new FormData(form).forEach((value, key) => {
    formData[key] = value;
  });
  return formData;
}

function showAutoSaveIndicator(state) {
  let indicator = document.getElementById('auto-save-indicator');
  if (!indicator) {
    indicator = document.createElement('div');
    indicator.id = 'auto-save-indicator';
    indicator.className = 'auto-save-indicator';
    document.body.appendChild(indicator);
  }

  const messages = {
    saving: '💾 Saving...',
    saved: '✅ Saved',
    idle: ''
  };

  indicator.textContent = messages[state] || '';
  indicator.className = `auto-save-indicator ${state}`;
}

/**
 * Enhanced export functionality
 */
function exportCurrentView() {
  const currentView = document.querySelector('.view.active');
  if (!currentView) return;

  const viewId = currentView.id.replace('view-', '');
  
  // Check for current result data
  if (viewId === 'lesson' && currentLessonPlan) {
    exportLesson();
  } else if (viewId === 'plc') {
    exportPLCReport();
  } else if (viewId === 'assess') {
    exportAssessment();
  } else {
    showNotification('No data to export', 'warning');
  }
}

/**
 * Export PLC report as PDF/CSV
 */
function exportPLCReport() {
  const content = document.getElementById('plc-content');
  if (!content || !content.innerHTML) {
    showNotification('No PLC report to export', 'warning');
    return;
  }

  // For now, trigger browser print (can be enhanced with PDF library)
  window.print();
  showNotification('Use browser print dialog to save as PDF', 'info');
}

/**
 * Export assessment data
 */
function exportAssessment() {
  const statsEl = document.getElementById('assess-stats');
  if (!statsEl || !statsEl.innerHTML) {
    showNotification('No assessment data to export', 'warning');
    return;
  }

  // Create CSV from visible data
  const rows = [['Metric', 'Value']];
  statsEl.querySelectorAll('.stat-card').forEach(card => {
    const label = card.querySelector('.stat-label')?.textContent || '';
    const value = card.querySelector('.stat-value')?.textContent || '';
    rows.push([label, value]);
  });

  const csv = rows.map(row => row.join(',')).join('\n');
  downloadFile(csv, 'assessment-analysis.csv', 'text/csv');
  showNotification('Assessment data exported as CSV', 'success');
}

/**
 * Download file helper
 */
function downloadFile(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/**
 * Enhanced print with better formatting
 */
function enhancedPrint() {
  // Add print-specific classes before printing
  document.body.classList.add('printing');
  window.print();
  setTimeout(() => document.body.classList.remove('printing'), 100);
}

/**
 * Show notification/toast
 */
function showNotification(message, type = 'info') {
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.textContent = message;
  notification.style.cssText = `
    position: fixed;
    top: 80px;
    right: 20px;
    padding: 16px 24px;
    background: ${type === 'success' ? '#10B981' : type === 'warning' ? '#F59E0B' : type === 'error' ? '#EF4444' : '#3B82F6'};
    color: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    z-index: 10000;
    animation: slideIn 0.3s ease-out;
  `;
  document.body.appendChild(notification);
  setTimeout(() => {
    notification.style.animation = 'slideOut 0.3s ease-out';
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

/**
 * CSV Import for student data
 */
function initCSVImport() {
  // Create file input
  const importBtn = document.createElement('button');
  importBtn.className = 'btn-secondary btn-sm';
  importBtn.innerHTML = '<span class="btn-icon">📁</span> Import CSV';
  importBtn.onclick = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.csv';
    input.onchange = handleCSVImport;
    input.click();
  };

  // Add to assessment view
  const assessForm = document.querySelector('#view-assess .form-container');
  if (assessForm) {
    const btnContainer = document.createElement('div');
    btnContainer.style.marginTop = '10px';
    btnContainer.appendChild(importBtn);
    assessForm.appendChild(btnContainer);
  }
}

/**
 * Handle CSV file import
 */
async function handleCSVImport(event) {
  const file = event.target.files[0];
  if (!file) return;

  const text = await file.text();
  const lines = text.trim().split('\n');
  
  // Parse CSV (simple parser, assumes Name, Score format)
  const data = lines.slice(1).map(line => {
    const [name, score] = line.split(',').map(s => s.trim());
    return `${name}, ${score}`;
  }).join('\n');

  // Populate the assessment data textarea
  const textarea = document.getElementById('assess-data');
  if (textarea) {
    textarea.value = data;
    showNotification('CSV imported successfully', 'success');
  }
}

/**
 * Search and filter functionality
 */
function initSearchAndFilter() {
  // Add search box to TEKS browser (already exists, enhance it)
  const searchInput = document.getElementById('teks-search');
  if (searchInput) {
    // Debounced search
    let searchTimer = null;
    searchInput.addEventListener('input', () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => {
        if (searchInput.value.trim()) {
          searchTEKS();
        }
      }, 500);
    });
  }
}

/**
 * Undo/Redo functionality
 */
let historyStack = [];
let historyIndex = -1;
const MAX_HISTORY = 50;

function saveToHistory() {
  const currentView = document.querySelector('.view.active');
  if (!currentView) return;

  const viewId = currentView.id.replace('view-', '');
  const formData = gatherFormData(viewId);
  
  // Remove any history after current index
  historyStack = historyStack.slice(0, historyIndex + 1);
  
  // Add new state
  historyStack.push({
    viewId,
    data: formData,
    timestamp: Date.now()
  });
  
  // Limit history size
  if (historyStack.length > MAX_HISTORY) {
    historyStack.shift();
  } else {
    historyIndex++;
  }
}

function undo() {
  if (historyIndex <= 0) {
    showNotification('Nothing to undo', 'info');
    return;
  }

  historyIndex--;
  restoreFromHistory(historyStack[historyIndex]);
  showNotification('Undo successful', 'success');
}

function redo() {
  if (historyIndex >= historyStack.length - 1) {
    showNotification('Nothing to redo', 'info');
    return;
  }

  historyIndex++;
  restoreFromHistory(historyStack[historyIndex]);
  showNotification('Redo successful', 'success');
}

function restoreFromHistory(state) {
  // Switch to the view
  const navItem = document.querySelector(`[data-view="${state.viewId}"]`);
  if (navItem) navItem.click();

  // Restore form data
  setTimeout(() => {
    Object.entries(state.data).forEach(([key, value]) => {
      const input = document.querySelector(`[name="${key}"]`);
      if (input) input.value = value;
    });
  }, 100);
}

// Add keyboard shortcuts for undo/redo
document.addEventListener('keydown', (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'z' && !e.shiftKey) {
    e.preventDefault();
    undo();
  } else if ((e.metaKey || e.ctrlKey) && (e.key === 'y' || (e.key === 'z' && e.shiftKey))) {
    e.preventDefault();
    redo();
  }
});

/**
 * Initialize all enhanced features
 */
function initEnhancedFeatures() {
  initKeyboardNavigation();
  setupAutoSave();
  initCSVImport();
  initSearchAndFilter();
  
  // Save to history on form changes
  document.querySelectorAll('input, textarea, select').forEach(input => {
    input.addEventListener('change', saveToHistory);
  });

  console.log('✅ Enhanced features initialized (January 2026)');
  console.log('Keyboard shortcuts:');
  console.log('  Alt+1-6: Switch views');
  console.log('  Cmd/Ctrl+S: Save');
  console.log('  Cmd/Ctrl+E: Export');
  console.log('  Cmd/Ctrl+Z: Undo');
  console.log('  Cmd/Ctrl+Y: Redo');
}

// Initialize enhanced features on load
document.addEventListener('DOMContentLoaded', initEnhancedFeatures);
