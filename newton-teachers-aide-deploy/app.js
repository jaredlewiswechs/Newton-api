/**
 * Newton Teacher's Aide - Application
 * The Ultimate Teaching Assistant for HISD NES
 * © 2026 Jared Lewis · Ada Computing Company
 * Last Updated: February 1, 2026
 *
 * NEW: Newton AI Chat + MOAD Integration + Web Search
 */

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIGURATION - OFFLINE MODE
// ═══════════════════════════════════════════════════════════════════════════════

const CONFIG = {
  MODE: 'offline',
  MOAD_ENABLED: false,
  WEB_SEARCH_ENABLED: false
};

// Store for current lesson plan (for slide generation)
let currentLessonPlan = null;

// Chat message history
let chatHistory = [];

// MOAD state
let moadConnected = true;

// Current view context for assistant
let currentViewContext = 'lesson';

// ═══════════════════════════════════════════════════════════════════════════════
// OFFLINE ENGINE - No server needed
// All computation runs locally via NewtonOffline (newton-offline-engine.js)
// ═══════════════════════════════════════════════════════════════════════════════

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

function checkStatus() {
  const statusEl = document.getElementById('status');
  // Always online in offline mode - everything runs locally
  statusEl.classList.add('online');
  statusEl.querySelector('.status-text').textContent = 'Offline Ready';
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
      const result = NewtonOffline.generateLesson(
        grade,
        subject,
        teks_codes,
        topic,
        Object.keys(student_needs).length > 0 ? student_needs : null
      );

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
      const result = NewtonOffline.generateSlides(lessonPlan, style);

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
      const result = NewtonOffline.analyzeAssessment(
        assessment_name,
        teks_codes,
        total_points,
        mastery_threshold,
        students
      );

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
      const result = NewtonOffline.generatePLCReport(
        team_name,
        reporting_period,
        teks_codes,
        assessment_data
      );

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

function loadTEKS() {
  const resultsEl = document.getElementById('teks-results');
  // Load all TEKS from local offline database
  const standards = NewtonOffline.getAllTEKS();
  displayTEKS(standards);
}

function searchTEKS() {
  const query = document.getElementById('teks-search').value.trim();
  if (!query) {
    loadTEKS();
    return;
  }

  // Search local offline database
  const results = NewtonOffline.searchTEKS(query);
  displayTEKS(results);
}

function filterTEKS() {
  const grade = document.getElementById('teks-grade-filter').value;
  const subject = document.getElementById('teks-subject-filter').value;

  // Filter local offline database
  const results = NewtonOffline.filterTEKS(grade, subject);
  displayTEKS(results);
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

  // Set offline status indicator
  checkStatus();

  // Load initial TEKS from local database
  loadTEKS();

  // Search on Enter
  document.getElementById('teks-search').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') searchTEKS();
  });

  console.log(`Newton Teacher's Aide - Offline Mode (${NewtonOffline.VERSION})`);
  console.log(`TEKS Database: ${NewtonOffline.TEKS_DATABASE.length} standards loaded`);
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

// ═══════════════════════════════════════════════════════════════════════════════
// NEWTON AI CHAT SYSTEM
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Initialize Newton Chat
 */
function initNewtonChat() {
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input');

  if (chatForm) {
    chatForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const message = chatInput.value.trim();
      if (!message) return;

      // Clear input
      chatInput.value = '';

      // Send message
      await askNewton(message);
    });
  }

  // Auto-resize textarea
  if (chatInput) {
    chatInput.addEventListener('input', () => {
      chatInput.style.height = 'auto';
      chatInput.style.height = Math.min(chatInput.scrollHeight, 150) + 'px';
    });

    // Handle Enter key
    chatInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
      }
    });
  }

  console.log('✅ Newton Chat initialized');
}

/**
 * Ask Newton a question
 */
async function askNewton(message) {
  const messagesContainer = document.getElementById('chat-messages');
  const suggestionsContainer = document.getElementById('chat-suggestions');
  const useWebSearch = document.getElementById('use-web-search')?.checked ?? true;
  const useMoad = document.getElementById('use-moad')?.checked ?? true;

  // Hide suggestions after first message
  if (suggestionsContainer) {
    suggestionsContainer.style.display = 'none';
  }

  // Add user message to chat
  addChatMessage('user', message);

  // Add loading indicator
  const loadingId = addChatMessage('newton', '...', true);

  // Generate offline response (no server needed)
  const offlineResponse = generateOfflineResponse(message);

  // Remove loading indicator
  removeChatMessage(loadingId);

  // Add Newton's response
  addChatMessage('newton', offlineResponse, false, { offline: true });

  // Update chat history
  chatHistory.push({ role: 'user', content: message });
  chatHistory.push({ role: 'assistant', content: offlineResponse });
}

/**
 * Build context for Newton based on current app state
 */
function buildNewtonContext() {
  const context = {
    current_view: currentViewContext,
    timestamp: new Date().toISOString()
  };

  // Add lesson plan context if available
  if (currentLessonPlan) {
    context.lesson_plan = {
      title: currentLessonPlan.title,
      grade: currentLessonPlan.grade,
      subject: currentLessonPlan.subject,
      teks_codes: currentLessonPlan.teks_alignment?.map(t => t.code) || []
    };
  }

  // Add form data from current view
  const currentView = document.querySelector('.view.active');
  if (currentView) {
    const form = currentView.querySelector('form');
    if (form) {
      const formData = new FormData(form);
      context.form_data = Object.fromEntries(formData);
    }
  }

  return context;
}

/**
 * Add a message to the chat
 */
function addChatMessage(role, content, isLoading = false, meta = {}) {
  const messagesContainer = document.getElementById('chat-messages');
  if (!messagesContainer) return null;

  const messageId = 'msg-' + Date.now();
  const messageDiv = document.createElement('div');
  messageDiv.id = messageId;
  messageDiv.className = `chat-message ${role}${isLoading ? ' loading' : ''}`;

  const avatarIcon = role === 'newton' ? 'N' : '👤';
  const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  let metaHTML = '';
  if (meta.verified) {
    metaHTML += '<span class="message-badge verified">Verified by Newton</span>';
  }
  if (meta.sources && meta.sources.length > 0) {
    metaHTML += '<span class="message-badge web">🌐 Web sources</span>';
  }
  if (meta.moad_domains && meta.moad_domains.length > 0) {
    metaHTML += `<span class="message-badge moad">◈ ${meta.moad_domains.join(', ')}</span>`;
  }
  if (meta.offline) {
    metaHTML += '<span class="message-badge offline">Local response</span>';
  }

  let contentHTML = content;
  if (isLoading) {
    contentHTML = `
      <div class="typing-indicator">
        <span></span><span></span><span></span>
      </div>
    `;
  } else {
    // Convert markdown-like formatting
    contentHTML = formatNewtonResponse(content);
  }

  // Add sources if available
  let sourcesHTML = '';
  if (meta.sources && meta.sources.length > 0) {
    sourcesHTML = `
      <div class="message-sources">
        <span class="sources-label">Sources:</span>
        ${meta.sources.map(s => `<a href="${s.url}" target="_blank" class="source-link">${s.title}</a>`).join('')}
      </div>
    `;
  }

  messageDiv.innerHTML = `
    <div class="message-avatar">${avatarIcon}</div>
    <div class="message-content">
      <div class="message-text">${contentHTML}</div>
      ${sourcesHTML}
      <div class="message-meta">
        <span class="message-time">${time}</span>
        ${metaHTML}
      </div>
    </div>
  `;

  messagesContainer.appendChild(messageDiv);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;

  return messageId;
}

/**
 * Remove a message from chat
 */
function removeChatMessage(messageId) {
  const message = document.getElementById(messageId);
  if (message) {
    message.remove();
  }
}

/**
 * Format Newton's response with markdown-like styling
 */
function formatNewtonResponse(text) {
  if (!text) return '';

  // Convert **bold** to <strong>
  text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

  // Convert *italic* to <em>
  text = text.replace(/\*(.+?)\*/g, '<em>$1</em>');

  // Convert `code` to <code>
  text = text.replace(/`(.+?)`/g, '<code>$1</code>');

  // Convert line breaks to <br>
  text = text.replace(/\n/g, '<br>');

  // Convert bullet points
  text = text.replace(/^- (.+)$/gm, '<li>$1</li>');
  text = text.replace(/(<li>.*<\/li>)+/g, '<ul>$&</ul>');

  // Convert numbered lists
  text = text.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');

  return text;
}

/**
 * Generate offline response when API is unavailable
 */
function generateOfflineResponse(message) {
  const lowerMessage = message.toLowerCase();

  // TEKS-related questions
  if (lowerMessage.includes('teks') || lowerMessage.includes('standard')) {
    return `I can help you find TEKS standards! Here's how to search:

1. Go to the **TEKS Browser** tab
2. Use the search bar to find standards by keyword
3. Filter by grade level and subject
4. Click on any standard to copy its code

Common TEKS codes:
- **5.3A** - Add/subtract fractions with unlike denominators
- **5.4B** - Multiplication with decimals
- **5.NF.1** - Add/subtract fractions (CCSS equivalent)

Would you like me to help you find specific standards?`;
  }

  // Lesson planning questions
  if (lowerMessage.includes('lesson') || lowerMessage.includes('plan')) {
    return `Here's how to create a great NES-compliant lesson plan:

**5 Essential Phases:**
1. **Opening (5 min)** - Hook and objective
2. **Direct Instruction (15 min)** - Teacher modeling ("I Do")
3. **Guided Practice (15 min)** - Collaborative work ("We Do")
4. **Independent Practice (10 min)** - Student work ("You Do")
5. **Closing (5 min)** - Exit ticket

**Tips:**
- Start with clear TEKS alignment
- Include differentiation strategies
- Plan formative checks every 5 minutes

Go to **Lesson Planner** to get started!`;
  }

  // Differentiation questions
  if (lowerMessage.includes('differentiat') || lowerMessage.includes('ell') || lowerMessage.includes('accommodat')) {
    return `**Differentiation Strategies:**

**For ELL Students:**
- Provide visual supports and manipulatives
- Use sentence stems and vocabulary walls
- Allow extra processing time
- Pair with bilingual peers

**For Students with 504/IEP:**
- Provide extended time as needed
- Use graphic organizers
- Break tasks into smaller steps
- Offer alternative assessments

**For Gifted Students:**
- Provide extension activities
- Allow for independent research
- Increase depth and complexity
- Offer leadership roles

The Lesson Planner includes automatic accommodation suggestions!`;
  }

  // Default response
  return `I'm Newton, your teaching assistant running in offline mode! All features work without a server:

- **TEKS Standards** - Browse ${NewtonOffline.TEKS_DATABASE.length}+ Texas standards
- **Lesson Planning** - Create NES-compliant lessons instantly
- **Differentiation** - Strategies for diverse learners
- **Assessments** - Analyze scores and group students
- **PLC Reports** - Data-driven team insights

Try the **Lesson Planner** or **TEKS Browser** to get started!`;
}

/**
 * Clear chat history
 */
function clearChat() {
  const messagesContainer = document.getElementById('chat-messages');
  const suggestionsContainer = document.getElementById('chat-suggestions');

  if (messagesContainer) {
    // Keep only the welcome message
    messagesContainer.innerHTML = `
      <div class="chat-message newton">
        <div class="message-avatar">N</div>
        <div class="message-content">
          <div class="message-text">
            Hello! I'm Newton, your AI teaching assistant. I can help you with:
            <ul>
              <li><strong>TEKS Standards</strong> - Find and understand Texas standards</li>
              <li><strong>Lesson Planning</strong> - Create NES-compliant lessons</li>
              <li><strong>Pedagogy</strong> - Best practices for instruction</li>
              <li><strong>Web Search</strong> - Find current resources and research</li>
              <li><strong>MOAD Integration</strong> - Access the Model of All Domains</li>
            </ul>
            What can I help you with today?
          </div>
          <div class="message-meta">
            <span class="message-time">Just now</span>
            <span class="message-badge verified">Verified by Newton</span>
          </div>
        </div>
      </div>
    `;
  }

  if (suggestionsContainer) {
    suggestionsContainer.style.display = 'flex';
  }

  chatHistory = [];
  showNotification('Chat cleared', 'info');
}

/**
 * Toggle web search
 */
function toggleWebSearch() {
  const checkbox = document.getElementById('use-web-search');
  if (checkbox) {
    checkbox.checked = !checkbox.checked;
    showNotification(checkbox.checked ? 'Web search enabled' : 'Web search disabled', 'info');
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// NEWTON FLOATING ASSISTANT
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Toggle the Newton assistant panel
 */
function toggleNewtonAssistant() {
  const panel = document.getElementById('newton-assistant-panel');
  const fab = document.getElementById('newton-fab');

  if (panel) {
    panel.classList.toggle('open');
    if (fab) {
      fab.classList.toggle('active');
    }

    // Update context when opening
    if (panel.classList.contains('open')) {
      updateAssistantContext();
    }
  }
}

/**
 * Update the assistant context based on current view
 */
function updateAssistantContext() {
  const contextValue = document.getElementById('context-value');
  const currentView = document.querySelector('.view.active');

  if (contextValue && currentView) {
    const viewId = currentView.id.replace('view-', '');
    const contextNames = {
      'lesson': 'Lesson Planner',
      'slides': 'Slide Deck',
      'assess': 'Assessment Analyzer',
      'plc': 'PLC Report',
      'teks': 'TEKS Browser',
      'guide': 'User Guide',
      'newton-chat': 'Newton Chat',
      'docs': 'Documentation'
    };
    contextValue.textContent = contextNames[viewId] || viewId;
    currentViewContext = viewId;
  }
}

/**
 * Handle quick actions from assistant
 */
function newtonQuickAction(action) {
  const currentView = document.querySelector('.view.active');
  const viewId = currentView?.id.replace('view-', '') || 'lesson';

  const actions = {
    help: {
      lesson: 'How do I create an effective lesson plan for my students?',
      slides: 'How can I make my slides more engaging for students?',
      assess: 'What makes a good exit ticket assessment?',
      plc: 'How do I interpret PLC report data effectively?',
      teks: 'How do I find the right TEKS standards for my lesson?'
    },
    improve: {
      lesson: 'Can you suggest improvements for my current lesson plan?',
      slides: 'How can I improve my slide content for better learning?',
      assess: 'What are some ways to improve my assessment questions?',
      plc: 'How can I make my PLC report more actionable?'
    },
    explain: {
      lesson: 'Explain the 5 NES phases in detail',
      slides: 'Explain how to structure presentation slides for learning',
      assess: 'Explain the difference between formative and summative assessment',
      plc: 'Explain how to analyze student performance data'
    },
    search: {
      lesson: 'Search for lesson planning best practices 2026',
      slides: 'Search for engaging presentation techniques for students',
      assess: 'Search for formative assessment strategies',
      plc: 'Search for PLC meeting facilitation tips'
    }
  };

  const message = actions[action]?.[viewId] || actions[action]?.lesson || 'How can I help?';

  // Navigate to chat and ask the question
  document.querySelector('[data-view="newton-chat"]')?.click();
  setTimeout(() => askNewton(message), 300);

  // Close the assistant panel
  toggleNewtonAssistant();
}

/**
 * Submit assistant query
 */
function submitAssistantQuery(event) {
  event.preventDefault();
  const input = document.getElementById('assistant-input');
  const message = input?.value.trim();

  if (message) {
    // Navigate to chat
    document.querySelector('[data-view="newton-chat"]')?.click();
    setTimeout(() => askNewton(message), 300);
    input.value = '';
    toggleNewtonAssistant();
  }

  return false;
}

// ═══════════════════════════════════════════════════════════════════════════════
// MOAD INTEGRATION
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Initialize MOAD - offline mode, no server connection
 */
function initMOAD() {
  moadConnected = false;
  const moadStatus = document.getElementById('moad-status');
  if (moadStatus) {
    moadStatus.classList.remove('connected');
    moadStatus.querySelector('.moad-text').textContent = 'Offline Mode';
  }
}

/**
 * Query MOAD - returns null in offline mode
 */
function queryMOAD(domain, concept) {
  return null;
}

// ═══════════════════════════════════════════════════════════════════════════════
// ENHANCED SLIDE GENERATION WITH NEWTON DRAWING
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Display slides with Newton-drawn content
 */
function displaySlidesWithNewtonDrawing(result) {
  const container = document.getElementById('slides-result');
  const content = document.getElementById('slides-content');
  const deck = result.slide_deck;

  document.getElementById('slides-time').textContent = `${result.elapsed_us}μs`;
  document.getElementById('slides-count').textContent = `${deck.total_slides} slides`;

  // Generate rich slide previews with Newton-drawn content
  content.innerHTML = deck.slides.map(slide => {
    const slideContent = generateSlideContent(slide);
    const slideClass = getSlideTypeClass(slide.type);

    return `
      <div class="slide-card ${slideClass}" data-slide="${slide.slide_number}">
        <div class="slide-header">
          <span class="slide-number">Slide ${slide.slide_number}</span>
          <span class="slide-type">${formatSlideType(slide.type)}</span>
          <div class="slide-actions">
            <button class="slide-action-btn" onclick="editSlideWithNewton(${slide.slide_number})" title="Edit with Newton">
              ✨
            </button>
            <button class="slide-action-btn" onclick="regenerateSlide(${slide.slide_number})" title="Regenerate">
              🔄
            </button>
          </div>
        </div>
        <div class="slide-content">
          ${slideContent}
        </div>
        <div class="slide-footer">
          <span class="newton-badge">Newton-drawn</span>
          ${slide.teks_codes?.length ? `<span class="teks-mini">${slide.teks_codes.join(', ')}</span>` : ''}
        </div>
      </div>
    `;
  }).join('');

  // Add export actions
  content.innerHTML += `
    <div class="slides-export-actions">
      <button class="btn-primary" onclick="exportSlidesToPPTX()">
        <span class="btn-icon">📊</span>
        Export to PowerPoint
      </button>
      <button class="btn-secondary" onclick="exportSlidesToPDF()">
        <span class="btn-icon">📄</span>
        Export to PDF
      </button>
      <button class="btn-secondary" onclick="exportSlidesToGoogleSlides()">
        <span class="btn-icon">🔗</span>
        Open in Google Slides
      </button>
    </div>
  `;

  container.classList.remove('hidden');
}

/**
 * Generate rich content for a slide based on its type
 */
function generateSlideContent(slide) {
  switch (slide.type) {
    case 'title':
      return `
        <div class="slide-title-content">
          <h2 class="slide-main-title">${slide.title || 'Lesson Title'}</h2>
          <p class="slide-subtitle">${slide.subtitle || ''}</p>
          <div class="slide-meta-info">
            <span>${slide.footer || ''}</span>
          </div>
        </div>
      `;

    case 'objective':
      return `
        <div class="slide-objective-content">
          <div class="objective-icon">🎯</div>
          <h3>Learning Objective</h3>
          <p class="objective-text">${slide.content || ''}</p>
          ${slide.teks_codes?.length ? `
            <div class="teks-alignment">
              <span class="teks-label">TEKS:</span>
              ${slide.teks_codes.map(t => `<span class="teks-tag">${t}</span>`).join('')}
            </div>
          ` : ''}
        </div>
      `;

    case 'vocabulary':
      return `
        <div class="slide-vocab-content">
          <h3>📚 Key Vocabulary</h3>
          <div class="vocab-grid">
            ${(slide.content || '').split('\n').filter(v => v.trim()).map(vocab => {
              const [term, def] = vocab.split(':').map(s => s.trim());
              return `
                <div class="vocab-item">
                  <span class="vocab-term">${term || vocab}</span>
                  ${def ? `<span class="vocab-def">${def}</span>` : ''}
                </div>
              `;
            }).join('')}
          </div>
        </div>
      `;

    case 'phase_header':
      const phaseIcons = {
        'Opening': '🎯',
        'I Do': '📖',
        'We Do': '👥',
        'You Do': '✏️',
        'Closing': '📝'
      };
      const phaseIcon = Object.entries(phaseIcons).find(([key]) =>
        (slide.title || '').includes(key))?.[1] || '📌';

      return `
        <div class="slide-phase-content">
          <div class="phase-icon-large">${phaseIcon}</div>
          <h2 class="phase-title">${slide.title || 'Phase'}</h2>
          <p class="phase-subtitle">${slide.subtitle || ''}</p>
        </div>
      `;

    case 'example':
      return `
        <div class="slide-example-content">
          <div class="example-header">
            <span class="example-badge">Example</span>
            <h3>${slide.title || 'Worked Example'}</h3>
          </div>
          <div class="example-body">
            <p>${slide.content || ''}</p>
          </div>
          <div class="example-footer">
            <span class="think-aloud-hint">💭 Think aloud while solving</span>
          </div>
        </div>
      `;

    case 'practice':
      return `
        <div class="slide-practice-content">
          <div class="practice-header">
            <h3>${slide.title || "Let's Practice Together"}</h3>
            <span class="practice-badge">We Do</span>
          </div>
          <div class="practice-problems">
            <p>${slide.content || ''}</p>
          </div>
          <div class="practice-tip">
            <span class="tip-icon">💡</span>
            <span>Work with your partner. Share your thinking!</span>
          </div>
        </div>
      `;

    case 'exit_ticket':
      return `
        <div class="slide-exit-content">
          <div class="exit-header">
            <span class="exit-icon">🎫</span>
            <h3>Exit Ticket</h3>
          </div>
          <div class="exit-body">
            <p>${slide.content || ''}</p>
          </div>
          <div class="exit-footer">
            <span class="exit-instruction">Complete independently. Turn in before you leave!</span>
          </div>
        </div>
      `;

    default:
      return `
        <div class="slide-default-content">
          <h3 class="slide-title">${slide.title || ''}</h3>
          <p class="slide-body">${slide.subtitle || slide.content || ''}</p>
        </div>
      `;
  }
}

/**
 * Get CSS class for slide type
 */
function getSlideTypeClass(type) {
  const classes = {
    'title': 'slide-type-title',
    'objective': 'slide-type-objective',
    'vocabulary': 'slide-type-vocab',
    'phase_header': 'slide-type-phase',
    'example': 'slide-type-example',
    'practice': 'slide-type-practice',
    'exit_ticket': 'slide-type-exit'
  };
  return classes[type] || 'slide-type-default';
}

/**
 * Format slide type for display
 */
function formatSlideType(type) {
  const names = {
    'title': 'Title',
    'objective': 'Objective',
    'vocabulary': 'Vocabulary',
    'phase_header': 'Phase',
    'example': 'Example',
    'practice': 'Practice',
    'exit_ticket': 'Exit Ticket'
  };
  return names[type] || type.replace(/_/g, ' ');
}

/**
 * Edit a slide with Newton's help (offline - prompt-based)
 */
function editSlideWithNewton(slideNumber) {
  showNotification('Slide editing is available in online mode. Use Print/PDF export to edit slides.', 'info');
}

/**
 * Regenerate a single slide (offline - regenerate entire deck)
 */
function regenerateSlide(slideNumber) {
  if (!currentLessonPlan) {
    showNotification('No lesson plan available for regeneration', 'warning');
    return;
  }
  const result = NewtonOffline.generateSlides(currentLessonPlan, 'modern');
  if (result.verified) {
    displaySlides(result);
    showNotification('Slides regenerated!', 'success');
  }
}

/**
 * Export slides to PowerPoint (offline - use print)
 */
function exportSlidesToPPTX() {
  showNotification('Use Print (Ctrl+P) and save as PDF for export', 'info');
  window.print();
}

/**
 * Export slides to PDF
 */
async function exportSlidesToPDF() {
  showNotification('Generating PDF...', 'info');
  window.print();
  showNotification('Use print dialog to save as PDF', 'info');
}

/**
 * Export to Google Slides
 */
async function exportSlidesToGoogleSlides() {
  showNotification('Google Slides export coming soon!', 'info');
}

// ═══════════════════════════════════════════════════════════════════════════════
// DOCUMENTATION SYSTEM
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Load documentation page
 */
function loadDoc(docId) {
  const docsContent = document.getElementById('docs-content');
  const docsLinks = document.querySelectorAll('.docs-link');

  // Update active link
  docsLinks.forEach(link => link.classList.remove('active'));
  event.target.classList.add('active');

  // Load doc content
  const docs = getDocumentation();
  const doc = docs[docId];

  if (doc) {
    docsContent.innerHTML = `
      <article class="doc-article">
        <h2>${doc.title}</h2>
        <p class="doc-lead">${doc.lead}</p>
        ${doc.content}
      </article>
    `;
  }
}

/**
 * Get documentation content
 */
function getDocumentation() {
  return {
    'overview': {
      title: 'Newton Education System Overview',
      lead: 'Newton is a constraint-verified computation system that ensures every educational artifact is mathematically proven correct before delivery.',
      content: document.getElementById('docs-content')?.innerHTML || ''
    },
    'quickstart': {
      title: 'Quick Start Guide',
      lead: 'Get started with Newton Teacher\'s Aide in 5 minutes.',
      content: `
        <section class="doc-section">
          <h3>1. Create Your First Lesson Plan</h3>
          <ol>
            <li>Select your grade level (3-8)</li>
            <li>Choose your subject area</li>
            <li>Enter TEKS codes for your lesson</li>
            <li>Add a specific topic (optional)</li>
            <li>Click "Generate Lesson Plan"</li>
          </ol>

          <div class="doc-callout info">
            <div class="callout-icon">💡</div>
            <div class="callout-content">
              <strong>Tip:</strong> Use the TEKS Browser to find the right standards for your lesson.
            </div>
          </div>
        </section>

        <section class="doc-section">
          <h3>2. Generate Slides</h3>
          <p>After creating a lesson plan, click "Generate Slides" to create a presentation deck. Newton will draw each slide with:</p>
          <ul>
            <li>Title slide with lesson metadata</li>
            <li>Objective slide with TEKS alignment</li>
            <li>Phase headers (I Do, We Do, You Do)</li>
            <li>Example slides with worked problems</li>
            <li>Exit ticket for assessment</li>
          </ul>
        </section>
      `
    },
    'moad-overview': {
      title: 'MOAD: Model of All Domains',
      lead: 'MOAD is Anthropic\'s comprehensive domain knowledge system that powers Newton\'s educational intelligence.',
      content: `
        <section class="doc-section">
          <h3>What is MOAD?</h3>
          <p>MOAD (Model of All Domains) is a structured knowledge graph that represents academic concepts, their relationships, and learning progressions across all subjects.</p>

          <h4>Key Capabilities</h4>
          <ul>
            <li><strong>Concept Mapping</strong> - Understand how ideas connect across subjects</li>
            <li><strong>Prerequisite Chains</strong> - Know what students need to learn first</li>
            <li><strong>Cross-Domain Links</strong> - Connect math to science, history to literature</li>
            <li><strong>Difficulty Calibration</strong> - Match content to student readiness</li>
          </ul>
        </section>

        <section class="doc-section">
          <h3>MOAD + Newton Integration</h3>
          <p>When you create lesson plans or ask Newton for help, MOAD provides:</p>

          <div class="doc-grid">
            <div class="doc-card">
              <div class="doc-card-icon">🎯</div>
              <h5>Precise Alignment</h5>
              <p>Standards are mapped to specific domain concepts</p>
            </div>
            <div class="doc-card">
              <div class="doc-card-icon">📊</div>
              <h5>Learning Paths</h5>
              <p>Optimal sequences for teaching concepts</p>
            </div>
            <div class="doc-card">
              <div class="doc-card-icon">🔗</div>
              <h5>Connections</h5>
              <p>Related concepts for deeper understanding</p>
            </div>
            <div class="doc-card">
              <div class="doc-card-icon">✅</div>
              <h5>Verification</h5>
              <p>All knowledge is constraint-checked</p>
            </div>
          </div>
        </section>
      `
    }
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// UPDATED INITIALIZATION
// ═══════════════════════════════════════════════════════════════════════════════

// Update the navigation initialization to track context
const originalInitNavigation = initNavigation;
initNavigation = function() {
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

      // Update context for assistant
      currentViewContext = viewId;
      updateAssistantContext();
    });
  });
};

// Override displaySlides to use enhanced version
const originalDisplaySlides = displaySlides;
displaySlides = displaySlidesWithNewtonDrawing;

// Initialize new features on load
document.addEventListener('DOMContentLoaded', () => {
  initNewtonChat();
  initMOAD();
  updateAssistantContext();
  console.log('✅ Newton Teacher\'s Aide 2.0 ready');
  console.log('   - Newton AI Chat');
  console.log('   - MOAD Integration');
  console.log('   - Web Search');
  console.log('   - Enhanced Slide Generation');
});

// Make new functions global
window.askNewton = askNewton;
window.clearChat = clearChat;
window.toggleWebSearch = toggleWebSearch;
window.toggleNewtonAssistant = toggleNewtonAssistant;
window.newtonQuickAction = newtonQuickAction;
window.submitAssistantQuery = submitAssistantQuery;
window.loadDoc = loadDoc;
window.editSlideWithNewton = editSlideWithNewton;
window.regenerateSlide = regenerateSlide;
window.exportSlidesToPPTX = exportSlidesToPPTX;
window.exportSlidesToPDF = exportSlidesToPDF;
window.exportSlidesToGoogleSlides = exportSlidesToGoogleSlides;


// ═══════════════════════════════════════════════════════════════════════════════
// WILD GARDEN - Offline Mode
// ═══════════════════════════════════════════════════════════════════════════════

function initWildGarden() {
  const status = document.getElementById('wg-status');
  if (status) {
    status.innerHTML = `
      <span class="status-dot"></span>
      <span class="status-text">Offline Mode - Wild Garden requires a server</span>
    `;
  }
}

function refreshWildGarden() {
  initWildGarden();
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Initialize Wild Garden when view is shown
document.addEventListener('DOMContentLoaded', () => {
  const wildGardenNav = document.querySelector('[data-view="wild-garden"]');
  if (wildGardenNav) {
    wildGardenNav.addEventListener('click', () => {
      initWildGarden();
    });
  }
});

window.refreshWildGarden = refreshWildGarden;
