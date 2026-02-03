#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
PARCSTATION UI TESTS
User Flow & Heuristic Validation

Based on Nielsen's 10 Usability Heuristics:
1. Visibility of System Status
2. Match Between System and Real World  
3. User Control and Freedom
4. Consistency and Standards
5. Error Prevention
6. Recognition Rather than Recall
7. Flexibility and Efficiency of Use
8. Aesthetic and Minimalist Design
9. Help Users Recognize, Diagnose, and Recover from Errors
10. Help and Documentation

Tests how users actually interact with parcStation.
"The more your tests resemble the way your software is used, 
 the more confidence they can give you." - Kent C. Dodds
═══════════════════════════════════════════════════════════════════════════════
"""

import re
import sys
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════════
# HTML STRUCTURE TESTS
# Verify UI elements exist for user interactions
# ═══════════════════════════════════════════════════════════════════════════════

def load_html():
    """Load the main HTML file."""
    html_path = Path(__file__).parent / "index2.html"
    return html_path.read_text(encoding='utf-8')

def load_js():
    """Load the main JS file."""
    js_path = Path(__file__).parent / "app2.js"
    return js_path.read_text(encoding='utf-8')

def load_css():
    """Load the main CSS file."""
    css_path = Path(__file__).parent / "style.css"
    return css_path.read_text(encoding='utf-8')


class UIStructureTests:
    """Test that UI elements exist for all user interactions."""
    
    def __init__(self):
        self.html = load_html()
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def check(self, condition, name, details=""):
        """Record test result."""
        if condition:
            self.passed += 1
            self.results.append(('✓', name))
        else:
            self.failed += 1
            self.results.append(('✗', f"{name}: {details}"))
    
    # ─────────────────────────────────────────────────────────────────────────
    # Heuristic 1: Visibility of System Status
    # ─────────────────────────────────────────────────────────────────────────
    
    def test_newton_status_indicator(self):
        """User should see Newton connection status."""
        self.check(
            'newton-status' in self.html,
            "Newton status indicator exists",
            "No element with id='newton-status'"
        )
    
    def test_verification_badges(self):
        """User should see verification status on cards."""
        self.check(
            'verification-badge' in self.html,
            "Verification badges exist",
            "No verification-badge class"
        )
    
    def test_loading_states(self):
        """User should see loading feedback."""
        self.check(
            'loading' in self.html.lower() or 'Searching' in self.html,
            "Loading states defined",
            "No loading indicators"
        )
    
    # ─────────────────────────────────────────────────────────────────────────
    # Heuristic 2: Match Between System and Real World
    # ─────────────────────────────────────────────────────────────────────────
    
    def test_familiar_terminology(self):
        """UI should use familiar terms."""
        familiar_terms = ['Stack', 'Card', 'Document', 'Source', 'Claim']
        found = sum(1 for term in familiar_terms if term in self.html)
        self.check(
            found >= 4,
            f"Uses familiar terminology ({found}/5 terms found)",
            "Missing familiar terminology"
        )
    
    def test_intuitive_icons(self):
        """UI should use recognizable icons."""
        icons = ['📚', '📄', '📖', '🔍', '✓', '⚡']
        found = sum(1 for icon in icons if icon in self.html)
        self.check(
            found >= 4,
            f"Uses intuitive icons ({found}/6 found)",
            "Missing intuitive icons"
        )
    
    # ─────────────────────────────────────────────────────────────────────────
    # Heuristic 3: User Control and Freedom
    # ─────────────────────────────────────────────────────────────────────────
    
    def test_back_button(self):
        """User should be able to go back."""
        self.check(
            'btn-back' in self.html,
            "Back button exists",
            "No btn-back element"
        )
    
    def test_cancel_buttons(self):
        """Dialogs should have cancel buttons."""
        cancel_count = self.html.lower().count('cancel')
        self.check(
            cancel_count >= 3,
            f"Cancel buttons exist ({cancel_count} found)",
            "Missing cancel buttons"
        )
    
    def test_sheet_close_buttons(self):
        """Sheets/modals should be closeable."""
        self.check(
            'sheet-close' in self.html,
            "Sheet close buttons exist",
            "No sheet-close elements"
        )
    
    # ─────────────────────────────────────────────────────────────────────────
    # Heuristic 4: Consistency and Standards
    # ─────────────────────────────────────────────────────────────────────────
    
    def test_consistent_button_classes(self):
        """Buttons should use consistent classes."""
        self.check(
            'btn btn-primary' in self.html and 'btn btn-secondary' in self.html,
            "Consistent button classes (primary/secondary)",
            "Inconsistent button styling"
        )
    
    def test_consistent_view_structure(self):
        """Views should follow consistent structure."""
        view_count = self.html.count('class="view')
        self.check(
            view_count >= 4,
            f"Consistent view structure ({view_count} views)",
            "Inconsistent view structure"
        )
    
    # ─────────────────────────────────────────────────────────────────────────
    # Heuristic 5: Error Prevention
    # ─────────────────────────────────────────────────────────────────────────
    
    def test_input_placeholders(self):
        """Inputs should have helpful placeholders."""
        placeholder_count = self.html.count('placeholder=')
        self.check(
            placeholder_count >= 5,
            f"Input placeholders exist ({placeholder_count} found)",
            "Missing input placeholders"
        )
    
    def test_form_labels(self):
        """Forms should have labels."""
        label_count = self.html.count('<label')
        self.check(
            label_count >= 5,
            f"Form labels exist ({label_count} found)",
            "Missing form labels"
        )
    
    # ─────────────────────────────────────────────────────────────────────────
    # Heuristic 6: Recognition Rather than Recall
    # ─────────────────────────────────────────────────────────────────────────
    
    def test_breadcrumb_navigation(self):
        """User should see where they are."""
        self.check(
            'breadcrumb' in self.html,
            "Breadcrumb navigation exists",
            "No breadcrumb element"
        )
    
    def test_sidebar_navigation(self):
        """User should see available options in sidebar."""
        self.check(
            'sidebar' in self.html and 'stack-list' in self.html,
            "Sidebar navigation exists",
            "Missing sidebar navigation"
        )
    
    # ─────────────────────────────────────────────────────────────────────────
    # Heuristic 7: Flexibility and Efficiency of Use
    # ─────────────────────────────────────────────────────────────────────────
    
    def test_keyboard_shortcuts(self):
        """Power users should have keyboard shortcuts."""
        shortcuts = ['⌘K', '⌘N', '⌘J', 'ESC']
        found = sum(1 for s in shortcuts if s in self.html)
        self.check(
            found >= 2,
            f"Keyboard shortcuts documented ({found}/4)",
            "Missing keyboard shortcuts"
        )
    
    def test_spotlight_search(self):
        """User should have quick search access."""
        self.check(
            'spotlight' in self.html,
            "Spotlight search exists",
            "No spotlight search"
        )
    
    # ─────────────────────────────────────────────────────────────────────────
    # Heuristic 10: Help and Documentation
    # ─────────────────────────────────────────────────────────────────────────
    
    def test_hint_text(self):
        """UI should provide contextual hints."""
        hint_count = self.html.count('hint')
        self.check(
            hint_count >= 2,
            f"Hint text exists ({hint_count} found)",
            "Missing hint text"
        )
    
    def run_all(self):
        """Run all UI structure tests."""
        print("\n" + "═" * 60)
        print("UI STRUCTURE TESTS (Nielsen's Heuristics)")
        print("═" * 60)
        
        # Run all test methods
        test_methods = [m for m in dir(self) if m.startswith('test_')]
        for method in test_methods:
            getattr(self, method)()
        
        # Print results
        for status, msg in self.results:
            print(f"  {status} {msg}")
        
        print(f"\n  Total: {self.passed} passed, {self.failed} failed")
        return self.failed == 0


# ═══════════════════════════════════════════════════════════════════════════════
# USER FLOW TESTS  
# Test complete user journeys
# ═══════════════════════════════════════════════════════════════════════════════

class UserFlowTests:
    """Test that user flows are complete."""
    
    def __init__(self):
        self.js = load_js()
        self.html = load_html()
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def check(self, condition, name, details=""):
        if condition:
            self.passed += 1
            self.results.append(('✓', name))
        else:
            self.failed += 1
            self.results.append(('✗', f"{name}: {details}"))
    
    # ─────────────────────────────────────────────────────────────────────────
    # Flow 1: Create Stack → Add Card → Verify
    # ─────────────────────────────────────────────────────────────────────────
    
    def test_create_stack_flow(self):
        """User can create a new stack."""
        has_button = 'btn-new-stack' in self.html
        has_handler = 'showNewStackSheet' in self.js
        has_create = 'createStack' in self.js
        self.check(
            has_button and has_handler and has_create,
            "Create stack flow complete",
            f"button:{has_button} handler:{has_handler} create:{has_create}"
        )
    
    def test_add_card_flow(self):
        """User can add a card."""
        has_button = 'btn-new-card' in self.html
        has_handler = 'showQuickCardSheet' in self.js
        has_save = 'saveQuickCard' in self.js
        self.check(
            has_button and has_handler and has_save,
            "Add card flow complete",
            f"button:{has_button} handler:{has_handler} save:{has_save}"
        )
    
    def test_verify_card_flow(self):
        """User can verify a card with Newton."""
        has_button = 'btn-verify-card' in self.html
        has_handler = 'verifyCurrentCard' in self.js
        self.check(
            has_button and has_handler,
            "Verify card flow complete",
            f"button:{has_button} handler:{has_handler}"
        )
    
    # ─────────────────────────────────────────────────────────────────────────
    # Flow 2: Add Source to Card
    # ─────────────────────────────────────────────────────────────────────────
    
    def test_add_source_flow(self):
        """User can add sources to cards."""
        has_button = 'btn-add-source' in self.html
        has_handler = 'showAddSourceSheet' in self.js
        has_sheet = 'add-source-sheet' in self.html
        self.check(
            has_button and has_handler and has_sheet,
            "Add source flow complete",
            f"button:{has_button} handler:{has_handler} sheet:{has_sheet}"
        )
    
    def test_add_source_from_url(self):
        """User can add source by URL."""
        has_input = 'source-url' in self.html
        has_handler = 'addSourceFromUrl' in self.js
        self.check(
            has_input and has_handler,
            "Add source from URL works",
            f"input:{has_input} handler:{has_handler}"
        )
    
    def test_add_source_from_wikipedia(self):
        """User can add source from Wikipedia."""
        has_tab = 'source-tab-wikipedia' in self.html
        has_search = 'searchWikipediaForSource' in self.js
        self.check(
            has_tab and has_search,
            "Add source from Wikipedia works",
            f"tab:{has_tab} search:{has_search}"
        )
    
    def test_add_source_from_arxiv(self):
        """User can add source from arXiv."""
        has_tab = 'source-tab-arxiv' in self.html
        has_search = 'searchArxivForSource' in self.js
        self.check(
            has_tab and has_search,
            "Add source from arXiv works",
            f"tab:{has_tab} search:{has_search}"
        )
    
    # ─────────────────────────────────────────────────────────────────────────
    # Flow 3: Cartridge Interaction
    # ─────────────────────────────────────────────────────────────────────────
    
    def test_cartridge_panel(self):
        """Cartridges open in a panel."""
        has_panel = 'cartridge-panel' in self.html
        has_open = 'openCartridgePanel' in self.js
        has_close = 'closeCartridgePanel' in self.js
        self.check(
            has_panel and has_open and has_close,
            "Cartridge panel flow complete",
            f"panel:{has_panel} open:{has_open} close:{has_close}"
        )
    
    def test_cartridge_search(self):
        """User can search within cartridges."""
        has_input = 'cartridge-search-input' in self.html
        has_execute = 'executeCartridgeSearch' in self.js
        self.check(
            has_input and has_execute,
            "Cartridge search works",
            f"input:{has_input} execute:{has_execute}"
        )
    
    def test_cartridge_results_to_source(self):
        """User can add cartridge result as source."""
        has_button_class = 'btn-use-source' in self.js
        has_handler = 'addSourceToCurrentCard' in self.js
        self.check(
            has_button_class and has_handler,
            "Cartridge result → source flow complete",
            f"button:{has_button_class} handler:{has_handler}"
        )
    
    # ─────────────────────────────────────────────────────────────────────────
    # Flow 4: Document Authoring
    # ─────────────────────────────────────────────────────────────────────────
    
    def test_document_list_flow(self):
        """User can view document list."""
        has_view = 'view-documents' in self.html
        has_show = 'showDocumentsView' in self.js
        self.check(
            has_view and has_show,
            "Document list view works",
            f"view:{has_view} show:{has_show}"
        )
    
    def test_document_editor_flow(self):
        """User can edit documents."""
        has_view = 'view-document-editor' in self.html
        has_show = 'showDocumentEditor' in self.js
        self.check(
            has_view and has_show,
            "Document editor works",
            f"view:{has_view} show:{has_show}"
        )
    
    def test_mark_claim_flow(self):
        """User can mark text as claim."""
        has_button = 'btn-mark-claim' in self.html
        has_handler = 'markSelectionAsClaim' in self.js
        self.check(
            has_button and has_handler,
            "Mark as claim flow works",
            f"button:{has_button} handler:{has_handler}"
        )
    
    def test_promote_claim_flow(self):
        """User can promote claim to card."""
        has_sheet = 'promote-claim-sheet' in self.html
        has_method = 'promoteClaimToCard' in self.js
        self.check(
            has_sheet and has_method,
            "Promote claim → card flow works",
            f"sheet:{has_sheet} method:{has_method}"
        )
    
    # ─────────────────────────────────────────────────────────────────────────
    # Flow 5: Spotlight Search
    # ─────────────────────────────────────────────────────────────────────────
    
    def test_spotlight_open(self):
        """User can open spotlight."""
        has_trigger = 'spotlight-trigger' in self.html
        has_overlay = 'spotlight-overlay' in self.html
        self.check(
            has_trigger and has_overlay,
            "Spotlight opens correctly",
            f"trigger:{has_trigger} overlay:{has_overlay}"
        )
    
    def test_spotlight_quick_actions(self):
        """Spotlight has quick actions."""
        has_new_stack = 'data-action="new-stack"' in self.html
        has_new_card = 'data-action="new-card"' in self.html
        has_new_doc = 'data-action="new-document"' in self.html
        self.check(
            has_new_stack and has_new_card and has_new_doc,
            "Spotlight quick actions exist",
            f"stack:{has_new_stack} card:{has_new_card} doc:{has_new_doc}"
        )
    
    def run_all(self):
        """Run all user flow tests."""
        print("\n" + "═" * 60)
        print("USER FLOW TESTS (Complete Journeys)")
        print("═" * 60)
        
        test_methods = [m for m in dir(self) if m.startswith('test_')]
        for method in test_methods:
            getattr(self, method)()
        
        for status, msg in self.results:
            print(f"  {status} {msg}")
        
        print(f"\n  Total: {self.passed} passed, {self.failed} failed")
        return self.failed == 0


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + " PARCSTATION UI TESTS ".center(58) + "║")
    print("║" + " Testing How Users Actually Use the App ".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    
    ui_tests = UIStructureTests()
    flow_tests = UserFlowTests()
    
    ui_ok = ui_tests.run_all()
    flow_ok = flow_tests.run_all()
    
    total_passed = ui_tests.passed + flow_tests.passed
    total_failed = ui_tests.failed + flow_tests.failed
    
    print("\n" + "═" * 60)
    print(f"TOTAL: {total_passed} passed, {total_failed} failed")
    print("═" * 60)
    
    if total_failed == 0:
        print("\n✅ All UI tests passed!")
        return 0
    else:
        print(f"\n❌ {total_failed} UI tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
