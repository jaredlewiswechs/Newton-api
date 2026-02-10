"""Comprehensive tests for the full Kernel 120 implementation.

Covers: view tree, windowing, layout, gesture recognizers, controls,
text system, data views, pasteboard, accessibility, and menus.
"""
import pytest
import time
from Kernel.view.nsview import NSView, NSViewController, NSRect, NSSize
from Kernel.view.nsscrollview import NSScrollView, NSClipView
from Kernel.view.nssplitview import NSSplitView
from Kernel.view.nsstackview import NSStackView, NSGridView
from Kernel.window.nswindow import NSWindow, NSWindowController, NSPanel, NSWindowStyleMask
from Kernel.window.nsscreen import NSScreen
from Kernel.layout.constraint import (
    NSLayoutConstraint, NSLayoutAnchor, NSLayoutXAxisAnchor,
    NSLayoutDimension, NSLayoutGuide, NSLayoutAttribute,
    NSLayoutRelation, solve_constraints,
)
from Kernel.gesture.recognizer import (
    NSGestureRecognizer, NSClickGestureRecognizer,
    NSPanGestureRecognizer, NSGestureRecognizerState,
)
from Kernel.gesture.tracking import NSTrackingArea, NSTrackingAreaOptions
from Kernel.controls.nscontrol import NSControl
from Kernel.controls.nsbutton import NSButton, NSButtonType
from Kernel.controls.nstextfield import NSTextField
from Kernel.controls.nsslider import NSSlider
from Kernel.controls.nssegmented import NSSegmentedControl
from Kernel.text.nsfont import NSFont, NSFontDescriptor, NSFontManager
from Kernel.text.nstextstorage import NSTextStorage
from Kernel.text.nslayoutmanager import NSLayoutManager, NSTextContainer
from Kernel.text.nstextview import NSTextView
from Kernel.data.nstableview import NSTableView, NSTableColumn
from Kernel.data.nsoutlineview import NSOutlineView
from Kernel.data.nscollectionview import NSCollectionView, NSCollectionViewItem
from Kernel.pasteboard.nspasteboard import NSPasteboard, NSPasteboardType, NSPasteboardItem
from Kernel.pasteboard.dragging import NSDraggingInfo, NSDraggingItem, NSDraggingSession, NSDragOperation
from Kernel.accessibility.nsaccessibility import (
    NSAccessibilityElement, NSAccessibilityRole, accessibility_tree_from_view,
)
from Kernel.menu.nsmenu import NSMenu, NSMenuItem
from Kernel.menu.nstoolbar import NSToolbar, NSToolbarItem
from Kernel.runtime.event import NSEvent, NSEventType
from Kernel.gui.nsbezier import NSColor


# ═══════════════════════════════════════════════════════════════════
# VIEW TREE
# ═══════════════════════════════════════════════════════════════════

class TestNSView:
    def test_create_view_with_frame(self):
        v = NSView(NSRect(10, 20, 100, 50))
        assert v.frame.x == 10
        assert v.frame.width == 100
        assert v.bounds.x == 0
        assert v.bounds.width == 100

    def test_add_and_remove_subview(self):
        parent = NSView(NSRect(0, 0, 200, 200))
        child = NSView(NSRect(10, 10, 50, 50))
        parent.add_subview(child)
        assert len(parent.subviews) == 1
        assert child.superview is parent
        assert child.next_responder is parent

        child.remove_from_superview()
        assert len(parent.subviews) == 0
        assert child.superview is None

    def test_hit_testing_deepest_subview(self):
        root = NSView(NSRect(0, 0, 200, 200))
        child = NSView(NSRect(50, 50, 100, 100))
        grandchild = NSView(NSRect(10, 10, 30, 30))
        child.add_subview(grandchild)
        root.add_subview(child)

        # point inside grandchild (root coords: 50+10=60, 50+10=60)
        hit = root.hit_test((65, 65))
        assert hit is grandchild

        # point inside child but outside grandchild
        hit = root.hit_test((55, 55))
        assert hit is child

        # point inside root but outside child
        hit = root.hit_test((10, 10))
        assert hit is root

        # point outside root
        hit = root.hit_test((250, 250))
        assert hit is None

    def test_hidden_view_not_hit(self):
        root = NSView(NSRect(0, 0, 200, 200))
        child = NSView(NSRect(0, 0, 200, 200))
        child.is_hidden = True
        root.add_subview(child)
        hit = root.hit_test((50, 50))
        assert hit is root  # child is hidden, so root is hit

    def test_z_order(self):
        root = NSView(NSRect(0, 0, 200, 200))
        a = NSView(NSRect(0, 0, 100, 100))
        b = NSView(NSRect(0, 0, 100, 100))
        a.identifier = "a"
        b.identifier = "b"
        root.add_subview(a)
        root.add_subview(b)
        # b is on top (added last)
        hit = root.hit_test((50, 50))
        assert hit.identifier == "b"

        # bring a to front
        root.bring_subview_to_front(a)
        hit = root.hit_test((50, 50))
        assert hit.identifier == "a"

    def test_coordinate_conversion(self):
        root = NSView(NSRect(0, 0, 300, 300))
        child = NSView(NSRect(50, 50, 200, 200))
        root.add_subview(child)
        # convert (0,0) in child to root coords
        wx, wy = child.convert_point_to((0, 0), root)
        assert wx == 50
        assert wy == 50

    def test_view_with_tag(self):
        root = NSView(NSRect(0, 0, 200, 200))
        child = NSView(NSRect(0, 0, 100, 100))
        child.tag = 42
        root.add_subview(child)
        found = root.view_with_tag(42)
        assert found is child
        assert root.view_with_tag(99) is None

    def test_render_tree_returns_svg(self):
        root = NSView(NSRect(0, 0, 200, 200))
        root._background_color = NSColor(255, 0, 0)
        child = NSView(NSRect(10, 10, 50, 50))
        child._background_color = NSColor(0, 255, 0)
        root.add_subview(child)
        svg = root.render_tree()
        assert '<g ' in svg
        assert 'data-view-id=' in svg
        assert 'rgb(255,0,0)' in svg


class TestNSViewController:
    def test_load_view(self):
        vc = NSViewController()
        assert vc.view is not None
        assert isinstance(vc.view, NSView)

    def test_child_controllers(self):
        parent = NSViewController()
        child = NSViewController()
        parent.add_child(child)
        assert len(parent.children) == 1
        assert child.parent is parent
        child.remove_from_parent()
        assert len(parent.children) == 0


class TestNSScrollView:
    def test_scroll_view_document(self):
        sv = NSScrollView(NSRect(0, 0, 200, 200))
        doc = NSView(NSRect(0, 0, 500, 500))
        sv.document_view = doc
        assert sv.document_view is doc
        sv.scroll_to(100, 50)
        vis = sv.document_visible_rect
        assert vis.x == 100
        assert vis.y == 50


class TestNSSplitView:
    def test_split_view_arranged(self):
        sv = NSSplitView(NSRect(0, 0, 400, 200))
        a = NSView()
        b = NSView()
        sv.add_arranged_subview(a)
        sv.add_arranged_subview(b)
        assert len(sv.arranged_subviews) == 2
        assert a.frame.width > 0
        assert b.frame.width > 0


class TestNSStackView:
    def test_stack_layout(self):
        stack = NSStackView(NSRect(0, 0, 300, 100))
        a = NSView()
        b = NSView()
        c = NSView()
        stack.add_arranged_subview(a)
        stack.add_arranged_subview(b)
        stack.add_arranged_subview(c)
        assert len(stack.arranged_subviews) == 3
        # check that all three got nonzero width
        assert a.frame.width > 0
        assert b.frame.width > 0
        assert c.frame.width > 0


class TestNSGridView:
    def test_grid_add_row(self):
        grid = NSGridView(NSRect(0, 0, 200, 200), rows=0, columns=2)
        v1 = NSView()
        v2 = NSView()
        grid.add_row([v1, v2])
        assert grid.number_of_rows == 1
        assert grid.number_of_columns == 2
        assert grid.cell_at(0, 0) is v1
        assert grid.cell_at(0, 1) is v2


# ═══════════════════════════════════════════════════════════════════
# WINDOWING
# ═══════════════════════════════════════════════════════════════════

class TestNSWindow:
    def setup_method(self):
        NSWindow._all_windows.clear()

    def test_create_window(self):
        win = NSWindow(NSRect(0, 0, 480, 320), title="Test")
        assert win.title == "Test"
        assert win.content_view is not None
        assert win.frame.width == 480

    def test_make_key_and_order_front(self):
        win = NSWindow(title="Test")
        win.make_key_and_order_front()
        assert win.is_visible
        assert win.is_key_window

    def test_close_window(self):
        win = NSWindow(title="Test")
        win.make_key_and_order_front()
        win.close()
        assert not win.is_visible

    def test_event_routing_to_view(self):
        win = NSWindow(NSRect(0, 0, 200, 200), title="Test")
        child = NSView(NSRect(50, 50, 100, 100))
        child.identifier = "target"
        win.content_view.add_subview(child)
        # send mouse event at (75, 75) — inside child
        ev = NSEvent(type=NSEventType.MOUSE_DOWN, location=(75, 75))
        win.send_event(ev)
        # should hit child (responder chain test)

    def test_first_responder(self):
        win = NSWindow(title="Test")
        from Kernel.runtime.responder import NSResponder
        r = NSResponder()
        assert win.make_first_responder(r)
        assert win.first_responder is r

    def test_window_render_svg(self):
        win = NSWindow(NSRect(0, 0, 300, 200), title="MyWindow")
        svg = win.render_to_svg()
        assert '<svg' in svg
        assert 'MyWindow' in svg
        assert 'circle' in svg  # traffic lights

    def test_center(self):
        win = NSWindow(NSRect(0, 0, 200, 100))
        win.center()
        assert win.frame.x == (1920 - 200) / 2


class TestNSPanel:
    def setup_method(self):
        NSWindow._all_windows.clear()

    def test_panel_is_floating(self):
        p = NSPanel(title="Inspector")
        assert p.is_floating_panel


class TestNSWindowController:
    def setup_method(self):
        NSWindow._all_windows.clear()

    def test_show_window(self):
        win = NSWindow(title="Ctrl Test")
        wc = NSWindowController(win)
        wc.show_window()
        assert win.is_visible


class TestNSScreen:
    def test_main_screen(self):
        s = NSScreen.main_screen()
        assert s.frame.width == 1920
        assert s.backing_scale_factor == 2.0


# ═══════════════════════════════════════════════════════════════════
# LAYOUT
# ═══════════════════════════════════════════════════════════════════

class TestNSLayoutConstraint:
    def test_width_constraint(self):
        v = NSView(NSRect(0, 0, 50, 50))
        anchor = NSLayoutDimension(v, NSLayoutAttribute.WIDTH)
        c = anchor.constraint_equal_to_constant(200.0)
        c.activate()
        assert c.is_active
        solve_constraints([c])
        assert v.frame.width == 200.0

    def test_pin_left_to_parent(self):
        parent = NSView(NSRect(0, 0, 400, 300))
        child = NSView(NSRect(50, 50, 100, 100))
        parent.add_subview(child)

        left_anchor_parent = NSLayoutXAxisAnchor(parent, NSLayoutAttribute.LEFT)
        left_anchor_child = NSLayoutXAxisAnchor(child, NSLayoutAttribute.LEFT)
        c = left_anchor_child.constraint_equal_to(left_anchor_parent, constant=20.0)
        c.activate()
        solve_constraints([c])
        assert abs(child.frame.x - 20.0) < 0.01

    def test_center_x(self):
        parent = NSView(NSRect(0, 0, 400, 300))
        child = NSView(NSRect(0, 0, 100, 100))
        parent.add_subview(child)

        c = NSLayoutConstraint(
            item=child, attribute=NSLayoutAttribute.CENTER_X,
            related_by=NSLayoutRelation.EQUAL,
            to_item=parent, to_attribute=NSLayoutAttribute.CENTER_X,
            multiplier=1.0, constant=0.0,
        )
        c.activate()
        solve_constraints([c])
        expected = (400 - 100) / 2
        assert abs(child.frame.x - expected) < 0.01

    def test_layout_guide(self):
        guide = NSLayoutGuide()
        guide.identifier = "margins"
        v = NSView(NSRect(0, 0, 200, 200))
        v.add_layout_guide(guide)
        assert len(v.layout_guides) == 1
        assert guide.owning_view is v
        # anchors exist
        assert guide.leading_anchor is not None
        assert guide.width_anchor is not None


# ═══════════════════════════════════════════════════════════════════
# GESTURE RECOGNIZERS
# ═══════════════════════════════════════════════════════════════════

class _ClickTarget:
    def __init__(self):
        self.clicked = False
    def on_click(self, recognizer):
        self.clicked = True


class TestNSClickGestureRecognizer:
    def test_single_click(self):
        target = _ClickTarget()
        gr = NSClickGestureRecognizer(target=target, action="on_click")
        ev = NSEvent(type=NSEventType.MOUSE_DOWN, location=(50, 50))
        result = gr.recognize(ev)
        assert result is True
        assert target.clicked
        assert gr.state == NSGestureRecognizerState.RECOGNIZED

    def test_double_click_required(self):
        target = _ClickTarget()
        gr = NSClickGestureRecognizer(target=target, action="on_click")
        gr.number_of_clicks_required = 2
        ev = NSEvent(type=NSEventType.MOUSE_DOWN, location=(50, 50))
        assert gr.recognize(ev) is False
        assert not target.clicked
        # second click immediately
        assert gr.recognize(ev) is True
        assert target.clicked


class _PanTarget:
    def __init__(self):
        self.translations = []
    def on_pan(self, recognizer):
        self.translations.append(recognizer.translation)


class TestNSPanGestureRecognizer:
    def test_pan_sequence(self):
        target = _PanTarget()
        gr = NSPanGestureRecognizer(target=target, action="on_pan")
        gr.recognize(NSEvent(type=NSEventType.MOUSE_DOWN, location=(100, 100)))
        assert gr.state == NSGestureRecognizerState.BEGAN
        gr.recognize(NSEvent(type=NSEventType.MOUSE_MOVE, location=(120, 110)))
        assert gr.state == NSGestureRecognizerState.CHANGED
        assert gr.translation == (20.0, 10.0)
        gr.recognize(NSEvent(type=NSEventType.MOUSE_UP, location=(120, 110)))
        assert gr.state == NSGestureRecognizerState.ENDED


class TestNSTrackingArea:
    def test_enter_exit(self):
        ta = NSTrackingArea(
            rect=NSRect(10, 10, 80, 80),
            options=NSTrackingAreaOptions.MOUSE_ENTERED_AND_EXITED | NSTrackingAreaOptions.ACTIVE_ALWAYS,
        )
        assert ta.check_mouse(50, 50) == 'entered'
        assert ta.check_mouse(50, 60) is None  # still inside, no MOVED option
        assert ta.check_mouse(200, 200) == 'exited'

    def test_mouse_moved(self):
        ta = NSTrackingArea(
            rect=NSRect(0, 0, 100, 100),
            options=NSTrackingAreaOptions.MOUSE_ENTERED_AND_EXITED | NSTrackingAreaOptions.MOUSE_MOVED | NSTrackingAreaOptions.ACTIVE_ALWAYS,
        )
        ta.check_mouse(50, 50)  # enter
        assert ta.check_mouse(60, 60) == 'moved'


# ═══════════════════════════════════════════════════════════════════
# CONTROLS
# ═══════════════════════════════════════════════════════════════════

class _ActionTarget:
    def __init__(self):
        self.received = False
    def on_action(self, sender):
        self.received = True


class TestNSButton:
    def test_button_click(self):
        target = _ActionTarget()
        btn = NSButton(NSRect(0, 0, 100, 30), title="OK")
        btn.target = target
        btn.action = "on_action"
        ev = NSEvent(type=NSEventType.MOUSE_DOWN, location=(50, 15))
        btn.handle_mouse_down(ev)
        assert target.received

    def test_toggle_state(self):
        btn = NSButton(title="Toggle")
        btn.set_button_type(NSButtonType.TOGGLE)
        assert btn.state == 0
        btn.handle_mouse_down(NSEvent(type=NSEventType.MOUSE_DOWN))
        assert btn.state == 1
        btn.handle_mouse_down(NSEvent(type=NSEventType.MOUSE_DOWN))
        assert btn.state == 0

    def test_svg_rendering(self):
        btn = NSButton(NSRect(0, 0, 80, 30), title="Click")
        svg = btn.draw()
        assert 'Click' in svg
        assert '<rect' in svg

    def test_disabled_button(self):
        target = _ActionTarget()
        btn = NSButton(title="Disabled")
        btn.target = target
        btn.action = "on_action"
        btn.is_enabled = False
        btn.handle_mouse_down(NSEvent(type=NSEventType.MOUSE_DOWN))
        assert not target.received


class TestNSTextField:
    def test_label_factory(self):
        label = NSTextField.label_with_string("Hello")
        assert label.string_value == "Hello"
        assert not label.is_editable

    def test_key_input(self):
        tf = NSTextField(NSRect(0, 0, 200, 24), string_value="")
        tf.handle_key_down(NSEvent(type=NSEventType.KEY_DOWN, user_info={'key': 'a'}))
        tf.handle_key_down(NSEvent(type=NSEventType.KEY_DOWN, user_info={'key': 'b'}))
        assert tf.string_value == "ab"
        tf.handle_key_down(NSEvent(type=NSEventType.KEY_DOWN, user_info={'key': 'backspace'}))
        assert tf.string_value == "a"

    def test_svg_rendering(self):
        tf = NSTextField(NSRect(0, 0, 200, 24), string_value="test")
        svg = tf.draw()
        assert 'test' in svg


class TestNSSlider:
    def test_slider_range(self):
        s = NSSlider(NSRect(0, 0, 200, 24), value=0.5, min_value=0.0, max_value=1.0)
        assert s.double_value == 0.5
        s.double_value = 1.5  # exceeds max
        assert s.double_value == 1.0
        s.double_value = -0.5  # below min
        assert s.double_value == 0.0

    def test_tick_marks(self):
        s = NSSlider(value=0.0, min_value=0.0, max_value=10.0)
        s.number_of_tick_marks = 11
        s.allows_tick_mark_values_only = True
        assert s.tick_mark_value_at_index(0) == 0.0
        assert s.tick_mark_value_at_index(10) == 10.0
        s.double_value = 3.7
        assert s.double_value == 4.0  # snaps to nearest tick

    def test_mouse_tracking(self):
        target = _ActionTarget()
        s = NSSlider(NSRect(0, 0, 200, 24), value=0.0, min_value=0.0, max_value=1.0)
        s.target = target
        s.action = "on_action"
        s.is_continuous = True
        s.handle_mouse_down(NSEvent(type=NSEventType.MOUSE_DOWN, location=(100, 12)))
        assert target.received
        assert s.double_value == pytest.approx(0.5, abs=0.01)


class TestNSSegmentedControl:
    def test_segment_selection(self):
        sc = NSSegmentedControl(NSRect(0, 0, 300, 30), labels=["A", "B", "C"])
        assert sc.segment_count == 3
        assert sc.selected_segment == 0
        sc.handle_mouse_down(NSEvent(type=NSEventType.MOUSE_DOWN, location=(200, 15)))
        assert sc.selected_segment == 2  # 200/100 = segment 2


# ═══════════════════════════════════════════════════════════════════
# TEXT SYSTEM
# ═══════════════════════════════════════════════════════════════════

class TestNSFont:
    def test_system_font(self):
        f = NSFont.system_font(14.0)
        assert f.point_size == 14.0
        assert f.line_height > 0

    def test_font_metrics(self):
        f = NSFont("Menlo", 12.0)
        assert f.ascender > 0
        assert f.descender < 0
        assert f.cap_height > 0

    def test_svg_attrs(self):
        f = NSFont("Helvetica", 16.0)
        attrs = f.to_svg_attrs()
        assert 'font-family="Helvetica"' in attrs
        assert 'font-size="16.0"' in attrs


class TestNSTextStorage:
    def test_basic_ops(self):
        ts = NSTextStorage("Hello World")
        assert ts.length == 11
        assert ts.string == "Hello World"
        ts.replace_characters_in_range(5, 1, ", ")
        assert ts.string == "Hello, World"
        ts.delete_characters_in_range(5, 2)
        assert ts.string == "HelloWorld"

    def test_attributes(self):
        ts = NSTextStorage("abcdef")
        ts.add_attribute("bold", True, 0, 3)
        assert ts.attributes_at_index(1) == {"bold": True}
        assert ts.attributes_at_index(4) == {}


class TestNSLayoutManager:
    def test_layout_lines(self):
        ts = NSTextStorage("Hello\nWorld")
        lm = NSLayoutManager()
        tc = NSTextContainer(NSSize(500, 500))
        ts.add_layout_manager(lm)
        lm.add_text_container(tc)
        lm.ensure_layout()
        assert len(lm._lines) == 2

    def test_character_index_for_point(self):
        ts = NSTextStorage("Hello World")
        lm = NSLayoutManager()
        tc = NSTextContainer(NSSize(500, 500))
        ts.add_layout_manager(lm)
        lm.add_text_container(tc)
        lm.ensure_layout()
        idx = lm.character_index_for_point((tc.line_fragment_padding + lm._char_width * 3, 5), tc)
        assert idx == 3

    def test_used_rect(self):
        ts = NSTextStorage("Line one\nLine two\nLine three")
        lm = NSLayoutManager()
        tc = NSTextContainer(NSSize(500, 500))
        ts.add_layout_manager(lm)
        lm.add_text_container(tc)
        rect = lm.used_rect_for_text_container(tc)
        assert rect.height > 0
        assert rect.width > 0


class TestNSTextView:
    def test_insert_and_delete(self):
        tv = NSTextView(NSRect(0, 0, 300, 200), text="Hello")
        assert tv.string == "Hello"
        tv.insert_text(" World")
        assert tv.string == "Hello World"
        tv.delete_backward()
        assert tv.string == "Hello Worl"

    def test_key_input(self):
        tv = NSTextView(NSRect(0, 0, 300, 200), text="")
        tv.handle_key_down(NSEvent(type=NSEventType.KEY_DOWN, user_info={'key': 'H'}))
        tv.handle_key_down(NSEvent(type=NSEventType.KEY_DOWN, user_info={'key': 'i'}))
        assert tv.string == "Hi"

    def test_selection(self):
        tv = NSTextView(text="Hello")
        tv.select_all()
        assert tv.selected_range == (0, 5)


# ═══════════════════════════════════════════════════════════════════
# DATA VIEWS
# ═══════════════════════════════════════════════════════════════════

class _SimpleTableDataSource:
    def __init__(self, data):
        self._data = data
    def number_of_rows(self, tv):
        return len(self._data)
    def object_value_for(self, tv, col, row):
        return self._data[row].get(col.identifier, "")


class TestNSTableView:
    def test_table_columns(self):
        tv = NSTableView(NSRect(0, 0, 400, 200))
        c1 = NSTableColumn("name")
        c1.title = "Name"
        c2 = NSTableColumn("age")
        c2.title = "Age"
        tv.add_table_column(c1)
        tv.add_table_column(c2)
        assert tv.number_of_columns == 2
        assert tv.column_with_identifier("name") is c1

    def test_data_source(self):
        tv = NSTableView(NSRect(0, 0, 400, 200))
        c1 = NSTableColumn("name")
        tv.add_table_column(c1)
        ds = _SimpleTableDataSource([
            {"name": "Alice"},
            {"name": "Bob"},
            {"name": "Charlie"},
        ])
        tv.data_source = ds
        assert tv.number_of_rows == 3
        tv.reload_data()
        assert len(tv._cached_rows) == 3

    def test_selection(self):
        tv = NSTableView()
        tv.select_row_indexes([1, 3])
        assert tv.selected_row_indexes == [1, 3]
        tv.deselect_row(1)
        assert tv.selected_row_indexes == [3]

    def test_svg_rendering(self):
        tv = NSTableView(NSRect(0, 0, 300, 200))
        c = NSTableColumn("x")
        c.title = "X"
        tv.add_table_column(c)
        svg = tv.draw()
        assert 'X' in svg


class _TreeDataSource:
    def __init__(self):
        self.tree = {"Root": {"Child1": {}, "Child2": {"Grandchild": {}}}}

    def number_of_children(self, item, ov):
        if item is None:
            return 1
        if isinstance(item, str) and item in self.tree:
            return len(self.tree[item])
        for parent_dict in self.tree.values():
            if isinstance(parent_dict, dict) and item in parent_dict:
                return len(parent_dict[item]) if isinstance(parent_dict[item], dict) else 0
        return 0

    def child(self, idx, of_item, ov):
        if of_item is None:
            return list(self.tree.keys())[idx]
        if of_item in self.tree:
            return list(self.tree[of_item].keys())[idx]
        for parent_dict in self.tree.values():
            if isinstance(parent_dict, dict) and of_item in parent_dict:
                sub = parent_dict[of_item]
                if isinstance(sub, dict):
                    return list(sub.keys())[idx]
        return None

    def is_item_expandable(self, item, ov):
        return self.number_of_children(item, ov) > 0

    def object_value_for(self, ov, col, item):
        return str(item)


class TestNSOutlineView:
    def test_expand_collapse(self):
        ov = NSOutlineView(NSRect(0, 0, 300, 400))
        ds = _TreeDataSource()
        ov.data_source = ds
        ov.reload_data()
        # initially only root
        assert ov.number_of_rows == 1
        root_item = ov.item_at_row(0)
        assert root_item == "Root"
        ov.expand_item(root_item)
        assert ov.number_of_rows == 3  # Root, Child1, Child2


class TestNSCollectionView:
    def test_collection_basics(self):
        cv = NSCollectionView(NSRect(0, 0, 400, 400))

        class DS:
            def number_of_sections(self, cv): return 1
            def number_of_items_in_section(self, cv, s): return 6
            def item_for(self, cv, ip): return f"Item {ip[1]}"

        cv.data_source = DS()
        cv.item_size = (80, 80)
        cv.reload_data()
        assert len(cv._items) == 6
        assert cv._items[0].represented_object == "Item 0"


# ═══════════════════════════════════════════════════════════════════
# PASTEBOARD
# ═══════════════════════════════════════════════════════════════════

class TestNSPasteboard:
    def test_string_copy_paste(self):
        pb = NSPasteboard("test-pb")
        pb.set_string("Hello, clipboard!")
        assert pb.string_for_type(NSPasteboardType.STRING) == "Hello, clipboard!"

    def test_change_count(self):
        pb = NSPasteboard("test-cc")
        initial = pb.change_count
        pb.set_string("a")
        assert pb.change_count > initial

    def test_multiple_items(self):
        pb = NSPasteboard("test-multi")
        pb.clear_contents()
        pb.write_objects(["one", "two"])
        assert len(pb.pasteboard_items) == 2

    def test_data_types(self):
        pb = NSPasteboard("test-data")
        pb.set_data(b"PNG data", NSPasteboardType.PNG)
        data = pb.data_for_type(NSPasteboardType.PNG)
        assert data == b"PNG data"

    def test_pasteboard_item(self):
        item = NSPasteboardItem()
        item.set_string("hello", NSPasteboardType.STRING)
        item.set_string("<b>hello</b>", NSPasteboardType.HTML)
        assert item.string_for_type(NSPasteboardType.STRING) == "hello"
        assert item.string_for_type(NSPasteboardType.HTML) == "<b>hello</b>"
        assert len(item.types) == 2


class TestDragging:
    def test_drag_operation_flags(self):
        op = NSDragOperation.COPY | NSDragOperation.MOVE
        assert NSDragOperation.COPY in op
        assert NSDragOperation.LINK not in op

    def test_dragging_session(self):
        item = NSDraggingItem("text data")
        session = NSDraggingSession(items=[item])
        assert len(session.dragging_items) == 1


# ═══════════════════════════════════════════════════════════════════
# ACCESSIBILITY
# ═══════════════════════════════════════════════════════════════════

class TestAccessibility:
    def test_element_tree(self):
        elem = NSAccessibilityElement()
        elem.role = NSAccessibilityRole.WINDOW
        elem.label = "Main Window"
        child = NSAccessibilityElement()
        child.role = NSAccessibilityRole.BUTTON
        child.label = "OK"
        elem.add_child(child)
        assert len(elem.children) == 1
        assert child.parent is elem

    def test_to_dict(self):
        elem = NSAccessibilityElement()
        elem.role = NSAccessibilityRole.BUTTON
        elem.label = "Submit"
        d = elem.to_dict()
        assert d['role'] == "AXButton"
        assert d['label'] == "Submit"

    def test_tree_from_view(self):
        root = NSView(NSRect(0, 0, 200, 200))
        btn = NSButton(NSRect(10, 10, 80, 30), title="OK")
        root.add_subview(btn)
        tree = accessibility_tree_from_view(root)
        assert tree.role == NSAccessibilityRole.GROUP
        assert len(tree.children) == 1
        assert tree.children[0].role == NSAccessibilityRole.BUTTON


# ═══════════════════════════════════════════════════════════════════
# MENUS
# ═══════════════════════════════════════════════════════════════════

class TestNSMenu:
    def test_add_items(self):
        menu = NSMenu("File")
        menu.add_item_with_title("New", "new_document", "n")
        menu.add_item_with_title("Open", "open_document", "o")
        menu.add_item(NSMenuItem.separator())
        menu.add_item_with_title("Quit", "quit", "q")
        assert menu.number_of_items == 4
        assert menu.item_with_title("New").key_equivalent == "n"
        assert menu.item_at_index(2).is_separator_item

    def test_key_equivalent(self):
        target = _ActionTarget()
        menu = NSMenu("Edit")
        item = menu.add_item_with_title("Copy", "on_action", "c")
        item.target = target
        result = menu.perform_key_equivalent("c")
        assert result
        assert target.received

    def test_submenu(self):
        main = NSMenu("Main")
        file_item = NSMenuItem("File")
        file_menu = NSMenu("File")
        file_menu.add_item_with_title("New")
        file_item.submenu = file_menu
        main.add_item(file_item)
        assert main.item_at_index(0).has_submenu
        assert main.item_at_index(0).submenu.number_of_items == 1


class TestNSToolbar:
    def test_toolbar_items(self):
        tb = NSToolbar("main-toolbar")
        tb.insert_item("save", 0)
        tb.insert_item("open", 1)
        assert len(tb.items) == 2
        assert tb.item_with_identifier("save") is not None

    def test_visibility(self):
        tb = NSToolbar("test")
        assert tb.is_visible
        tb.is_visible = False
        assert not tb.is_visible


# ═══════════════════════════════════════════════════════════════════
# INTEGRATION: VIEW TREE + EVENT ROUTING
# ═══════════════════════════════════════════════════════════════════

class TestIntegration:
    def setup_method(self):
        NSWindow._all_windows.clear()

    def test_full_event_chain(self):
        """Window → content view → subview hit test → button click → action fires."""
        from Kernel.runtime.app import NSApplication

        target = _ActionTarget()
        win = NSWindow(NSRect(0, 0, 400, 300), title="Integration")
        btn = NSButton(NSRect(50, 50, 100, 30), title="Go")
        btn.target = target
        btn.action = "on_action"
        win.content_view.add_subview(btn)

        app = NSApplication()
        app.set_main_responder(win)
        ev = NSEvent(type=NSEventType.MOUSE_DOWN, location=(100, 65), timestamp=time.time())
        app.post_event(ev)
        app.run_once()
        assert target.received

    def test_gesture_on_view(self):
        """Gesture recognizer on a view catches events before responder chain."""
        target = _ClickTarget()
        v = NSView(NSRect(0, 0, 200, 200))
        gr = NSClickGestureRecognizer(target=target, action="on_click")
        v.add_gesture_recognizer(gr)
        ev = NSEvent(type=NSEventType.MOUSE_DOWN, location=(50, 50))
        handled = v.send_event(ev)
        assert handled
        assert target.clicked

    def test_text_field_in_window(self):
        """TextField receives keyboard events as first responder."""
        NSWindow._all_windows.clear()
        win = NSWindow(NSRect(0, 0, 400, 300))
        tf = NSTextField(NSRect(10, 10, 200, 24), string_value="")
        win.content_view.add_subview(tf)
        win.make_first_responder(tf)

        for ch in "abc":
            ev = NSEvent(type=NSEventType.KEY_DOWN, user_info={'key': ch})
            win.send_event(ev)
        assert tf.string_value == "abc"

    def test_accessibility_tree_for_window(self):
        """Build accessibility tree from a window's content view."""
        NSWindow._all_windows.clear()
        win = NSWindow(NSRect(0, 0, 400, 300), title="Acc Test")
        btn = NSButton(NSRect(10, 10, 80, 30), title="OK")
        tf = NSTextField(NSRect(10, 50, 200, 24), string_value="hello")
        win.content_view.add_subview(btn)
        win.content_view.add_subview(tf)

        tree = accessibility_tree_from_view(win.content_view)
        assert len(tree.children) == 2
        roles = [c.role for c in tree.children]
        assert NSAccessibilityRole.BUTTON in roles
        assert NSAccessibilityRole.TEXT_FIELD in roles
