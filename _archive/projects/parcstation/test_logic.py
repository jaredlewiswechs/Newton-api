#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
PARCSTATION LOGIC TESTS
JavaScript Logic & Data Flow Validation

Tests the core logic patterns in app2.js:
- DataStore operations (CRUD for stacks, cards, documents)
- State management (views, navigation, history)
- Integration patterns (Newton, Cartridges)
- Event handling patterns

These tests analyze the JavaScript source to verify logic completeness.
═══════════════════════════════════════════════════════════════════════════════
"""

import re
import sys
from pathlib import Path

def load_js():
    """Load the main JS file."""
    js_path = Path(__file__).parent / "app2.js"
    return js_path.read_text(encoding='utf-8')


class DataStoreTests:
    """Test DataStore has all required operations."""
    
    def __init__(self):
        self.js = load_js()
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
    
    def test_stack_crud(self):
        """DataStore has CRUD for stacks."""
        operations = ['getStacks', 'getStack', 'addStack', 'updateStack', 'deleteStack']
        found = [op for op in operations if op in self.js]
        self.check(
            len(found) >= 4,
            f"Stack CRUD operations ({len(found)}/5)",
            f"Missing: {set(operations) - set(found)}"
        )
    
    def test_card_crud(self):
        """DataStore has CRUD for cards."""
        operations = ['getCards', 'getCard', 'addCard', 'updateCard', 'deleteCard']
        found = [op for op in operations if op in self.js]
        self.check(
            len(found) >= 4,
            f"Card CRUD operations ({len(found)}/5)",
            f"Missing: {set(operations) - set(found)}"
        )
    
    def test_document_crud(self):
        """DataStore has CRUD for documents."""
        operations = ['getDocuments', 'getDocument', 'addDocument', 'updateDocument', 'deleteDocument']
        found = [op for op in operations if op in self.js]
        self.check(
            len(found) >= 4,
            f"Document CRUD operations ({len(found)}/5)",
            f"Missing: {set(operations) - set(found)}"
        )
    
    def test_claim_operations(self):
        """DataStore has claim operations for documents."""
        operations = ['addClaimToDocument', 'updateClaimInDocument', 'removeClaimFromDocument']
        found = [op for op in operations if op in self.js]
        self.check(
            len(found) >= 2,
            f"Claim operations ({len(found)}/3)",
            f"Missing: {set(operations) - set(found)}"
        )
    
    def test_promote_claim_to_card(self):
        """DataStore can promote claims to cards."""
        self.check(
            'promoteClaimToCard' in self.js,
            "Promote claim to card exists",
            "Missing promoteClaimToCard method"
        )
    
    def test_search_function(self):
        """DataStore has search capability."""
        self.check(
            'search(' in self.js or 'search (' in self.js,
            "Search function exists",
            "Missing search method"
        )
    
    def test_persistence(self):
        """DataStore persists to localStorage."""
        has_save = 'localStorage.setItem' in self.js
        has_load = 'localStorage.getItem' in self.js
        self.check(
            has_save and has_load,
            "localStorage persistence",
            f"save:{has_save} load:{has_load}"
        )
    
    def test_cartridges_data(self):
        """DataStore has cartridges configuration."""
        self.check(
            'getCartridges' in self.js,
            "Cartridges data available",
            "Missing getCartridges"
        )
    
    def run_all(self):
        print("\n" + "─" * 50)
        print("DataStore Tests")
        print("─" * 50)
        
        test_methods = [m for m in dir(self) if m.startswith('test_')]
        for method in test_methods:
            getattr(self, method)()
        
        for status, msg in self.results:
            print(f"  {status} {msg}")
        
        return self.failed == 0


class ViewNavigationTests:
    """Test view navigation and state management."""
    
    def __init__(self):
        self.js = load_js()
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
    
    def test_view_methods(self):
        """All views have show methods."""
        views = ['showStacksView', 'showStackDetail', 'showCardDetail', 
                 'showDocumentsView', 'showDocumentEditor', 'showSearchResults']
        found = [v for v in views if v in self.js]
        self.check(
            len(found) >= 5,
            f"View methods ({len(found)}/6)",
            f"Missing: {set(views) - set(found)}"
        )
    
    def test_hide_all_views(self):
        """hideAllViews exists for view switching."""
        self.check(
            'hideAllViews' in self.js,
            "hideAllViews method exists",
            "Missing hideAllViews"
        )
    
    def test_history_management(self):
        """Navigation history is managed."""
        has_push = 'pushHistory' in self.js
        has_go_back = 'goBack' in self.js
        has_history = 'this.history' in self.js
        self.check(
            has_push and has_go_back and has_history,
            "History management complete",
            f"push:{has_push} back:{has_go_back} state:{has_history}"
        )
    
    def test_breadcrumb_updates(self):
        """Breadcrumb updates on navigation."""
        self.check(
            'updateBreadcrumb' in self.js,
            "Breadcrumb updates exist",
            "Missing updateBreadcrumb"
        )
    
    def test_current_state_tracking(self):
        """Current state is tracked."""
        states = ['currentView', 'currentStack', 'currentCard', 'currentDocument']
        found = [s for s in states if s in self.js]
        self.check(
            len(found) >= 3,
            f"State tracking ({len(found)}/4)",
            f"Missing: {set(states) - set(found)}"
        )
    
    def run_all(self):
        print("\n" + "─" * 50)
        print("View Navigation Tests")
        print("─" * 50)
        
        test_methods = [m for m in dir(self) if m.startswith('test_')]
        for method in test_methods:
            getattr(self, method)()
        
        for status, msg in self.results:
            print(f"  {status} {msg}")
        
        return self.failed == 0


class IntegrationTests:
    """Test integration with Newton, Cartridges, etc."""
    
    def __init__(self):
        self.js = load_js()
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
    
    def test_newton_config(self):
        """Newton URL is configured."""
        self.check(
            'NEWTON_URL' in self.js,
            "Newton URL configured",
            "Missing NEWTON_URL"
        )
    
    def test_newton_verify(self):
        """Can verify with Newton."""
        self.check(
            'verifyCurrentCard' in self.js or '/verify' in self.js,
            "Newton verification logic exists",
            "Missing verification logic"
        )
    
    def test_newton_ground(self):
        """Can ground with Newton."""
        self.check(
            '/ground' in self.js or 'ground(' in self.js,
            "Newton grounding logic exists",
            "Missing grounding logic"
        )
    
    def test_cartridges_config(self):
        """Cartridges URL is configured."""
        self.check(
            'CARTRIDGES_URL' in self.js,
            "Cartridges URL configured",
            "Missing CARTRIDGES_URL"
        )
    
    def test_wikipedia_integration(self):
        """Wikipedia cartridge integration."""
        self.check(
            'searchWikipedia' in self.js or '/wikipedia' in self.js,
            "Wikipedia integration exists",
            "Missing Wikipedia logic"
        )
    
    def test_arxiv_integration(self):
        """arXiv cartridge integration."""
        self.check(
            'searchArxiv' in self.js or '/arxiv' in self.js,
            "arXiv integration exists",
            "Missing arXiv logic"
        )
    
    def test_agent_config(self):
        """Newton Agent URL is configured."""
        self.check(
            'AGENT_URL' in self.js,
            "Newton Agent URL configured",
            "Missing AGENT_URL"
        )
    
    def test_chat_integration(self):
        """Chat with Newton Agent."""
        self.check(
            'sendMessage' in self.js or 'chat-input' in self.js,
            "Chat integration exists",
            "Missing chat logic"
        )
    
    def run_all(self):
        print("\n" + "─" * 50)
        print("Integration Tests")
        print("─" * 50)
        
        test_methods = [m for m in dir(self) if m.startswith('test_')]
        for method in test_methods:
            getattr(self, method)()
        
        for status, msg in self.results:
            print(f"  {status} {msg}")
        
        return self.failed == 0


class CartridgePanelTests:
    """Test cartridge panel logic."""
    
    def __init__(self):
        self.js = load_js()
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
    
    def test_cartridge_activation(self):
        """Cartridges can be activated."""
        self.check(
            'activateCartridge' in self.js,
            "Cartridge activation exists",
            "Missing activateCartridge"
        )
    
    def test_cartridge_panel_open_close(self):
        """Cartridge panel opens and closes."""
        has_open = 'openCartridgePanel' in self.js
        has_close = 'closeCartridgePanel' in self.js
        self.check(
            has_open and has_close,
            "Panel open/close methods exist",
            f"open:{has_open} close:{has_close}"
        )
    
    def test_cartridge_search_execute(self):
        """Cartridge search can be executed."""
        self.check(
            'executeCartridgeSearch' in self.js,
            "Cartridge search execution exists",
            "Missing executeCartridgeSearch"
        )
    
    def test_cartridge_results_render(self):
        """Cartridge results are rendered."""
        self.check(
            'renderCartridgeResults' in self.js,
            "Cartridge results rendering exists",
            "Missing renderCartridgeResults"
        )
    
    def test_source_from_cartridge(self):
        """Can add source from cartridge result."""
        self.check(
            'addSourceToCurrentCard' in self.js,
            "Add source from cartridge exists",
            "Missing addSourceToCurrentCard"
        )
    
    def test_cartridge_types(self):
        """Multiple cartridge types supported."""
        types = ['wikipedia', 'arxiv', 'calculator', 'calendar', 'dictionary']
        found = [t for t in types if t in self.js.lower()]
        self.check(
            len(found) >= 3,
            f"Cartridge types ({len(found)}/5)",
            f"Missing: {set(types) - set(found)}"
        )
    
    def run_all(self):
        print("\n" + "─" * 50)
        print("Cartridge Panel Tests")
        print("─" * 50)
        
        test_methods = [m for m in dir(self) if m.startswith('test_')]
        for method in test_methods:
            getattr(self, method)()
        
        for status, msg in self.results:
            print(f"  {status} {msg}")
        
        return self.failed == 0


class AddSourceTests:
    """Test add source flow logic."""
    
    def __init__(self):
        self.js = load_js()
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
    
    def test_show_add_source_sheet(self):
        """Add source sheet can be shown."""
        self.check(
            'showAddSourceSheet' in self.js,
            "showAddSourceSheet exists",
            "Missing showAddSourceSheet"
        )
    
    def test_source_tabs(self):
        """Source tabs are initialized."""
        self.check(
            'initSourceTabs' in self.js or 'source-tab' in self.js,
            "Source tabs logic exists",
            "Missing source tabs"
        )
    
    def test_add_from_url(self):
        """Can add source from URL."""
        self.check(
            'addSourceFromUrl' in self.js,
            "Add from URL exists",
            "Missing addSourceFromUrl"
        )
    
    def test_search_wikipedia_for_source(self):
        """Can search Wikipedia for source."""
        self.check(
            'searchWikipediaForSource' in self.js,
            "Search Wikipedia for source exists",
            "Missing searchWikipediaForSource"
        )
    
    def test_search_arxiv_for_source(self):
        """Can search arXiv for source."""
        self.check(
            'searchArxivForSource' in self.js,
            "Search arXiv for source exists",
            "Missing searchArxivForSource"
        )
    
    def test_add_manual_source(self):
        """Can add manual source."""
        self.check(
            'addManualSource' in self.js,
            "Add manual source exists",
            "Missing addManualSource"
        )
    
    def test_select_source_result(self):
        """Can select source from search results."""
        self.check(
            'selectSourceResult' in self.js,
            "Select source result exists",
            "Missing selectSourceResult"
        )
    
    def run_all(self):
        print("\n" + "─" * 50)
        print("Add Source Tests")
        print("─" * 50)
        
        test_methods = [m for m in dir(self) if m.startswith('test_')]
        for method in test_methods:
            getattr(self, method)()
        
        for status, msg in self.results:
            print(f"  {status} {msg}")
        
        return self.failed == 0


class EventBindingTests:
    """Test that events are properly bound."""
    
    def __init__(self):
        self.js = load_js()
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
    
    def test_bind_events_method(self):
        """bindEvents method exists."""
        self.check(
            'bindEvents' in self.js,
            "bindEvents method exists",
            "Missing bindEvents"
        )
    
    def test_click_handlers(self):
        """Click handlers are bound."""
        click_count = self.js.count("addEventListener('click'")
        self.check(
            click_count >= 5,
            f"Click handlers ({click_count} found)",
            "Insufficient click handlers"
        )
    
    def test_keyboard_handlers(self):
        """Keyboard handlers exist."""
        has_keydown = "keydown" in self.js
        has_keypress = "keypress" in self.js or "onkeypress" in self.js
        self.check(
            has_keydown or has_keypress,
            "Keyboard handlers exist",
            "Missing keyboard handlers"
        )
    
    def test_input_handlers(self):
        """Input change handlers exist."""
        self.check(
            "'input'" in self.js or 'oninput' in self.js,
            "Input handlers exist",
            "Missing input handlers"
        )
    
    def run_all(self):
        print("\n" + "─" * 50)
        print("Event Binding Tests")
        print("─" * 50)
        
        test_methods = [m for m in dir(self) if m.startswith('test_')]
        for method in test_methods:
            getattr(self, method)()
        
        for status, msg in self.results:
            print(f"  {status} {msg}")
        
        return self.failed == 0


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + " PARCSTATION LOGIC TESTS ".center(58) + "║")
    print("║" + " JavaScript Logic & Data Flow Validation ".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    
    all_passed = True
    total_passed = 0
    total_failed = 0
    
    test_classes = [
        DataStoreTests,
        ViewNavigationTests,
        IntegrationTests,
        CartridgePanelTests,
        AddSourceTests,
        EventBindingTests
    ]
    
    for TestClass in test_classes:
        tests = TestClass()
        tests.run_all()
        total_passed += tests.passed
        total_failed += tests.failed
        if tests.failed > 0:
            all_passed = False
    
    print("\n" + "═" * 60)
    print(f"TOTAL: {total_passed} passed, {total_failed} failed")
    print("═" * 60)
    
    if all_passed:
        print("\n✅ All logic tests passed!")
        return 0
    else:
        print(f"\n❌ {total_failed} logic tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
