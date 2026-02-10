import time
from Kernel.runtime.app import NSApplication
from Kernel.runtime.responder import NSResponder
from Kernel.runtime.event import NSEvent, NSEventType


class TestResponder(NSResponder):
    def __init__(self):
        super().__init__()
        self.events = []

    def handle_mouse_down(self, event):
        self.events.append(('down', event.location))
        return True

    def handle_mouse_move(self, event):
        self.events.append(('move', event.location))
        return True


def test_event_queue_and_dispatch():
    app = NSApplication.shared_application()
    # reset the queue
    app._event_queue.clear()
    resp = TestResponder()
    app.set_main_responder(resp)
    ev = NSEvent(type=NSEventType.MOUSE_DOWN, location=(10,20))
    app.post_event(ev)
    handled = app.run_once()
    assert handled is True
    assert resp.events == [('down', (10,20))]


def test_chain_to_next_responder_if_not_handled():
    app = NSApplication.shared_application()
    app._event_queue.clear()
    r1 = NSResponder()
    r2 = TestResponder()
    r1.next_responder = r2
    app.set_main_responder(r1)
    ev = NSEvent(type=NSEventType.MOUSE_MOVE, location=(5,6))
    app.post_event(ev)
    handled = app.run_once()
    assert handled is True


def test_direct_send_event_chaining():
    r1 = NSResponder()
    r2 = TestResponder()
    r1.next_responder = r2
    ev = NSEvent(type=NSEventType.MOUSE_MOVE, location=(7,8))
    assert r1.send_event(ev) is True
    assert r2.events[-1] == ('move', (7,8))


def test_run_loop_stop():
    app = NSApplication.shared_application()
    app._event_queue.clear()
    # run in background and then stop
    def run_and_stop():
        app.post_event(NSEvent(type=NSEventType.MOUSE_DOWN, location=(1,2)))
        app.stop()
    t = None
    try:
        import threading
        t = threading.Thread(target=run_and_stop)
        t.start()
        app.run(poll_interval=0.001)
    finally:
        if t:
            t.join(timeout=1)
