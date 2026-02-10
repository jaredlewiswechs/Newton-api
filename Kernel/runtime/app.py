"""Minimal application and run loop for Kernel demo."""
from typing import Optional, List
from .event import NSEvent
from .responder import NSResponder
import threading
import time


class NSApplication:
    _shared = None

    def __init__(self):
        self._event_queue: List[NSEvent] = []
        self._running = False
        self._delegate = None
        self._main_responder: Optional[NSResponder] = None
        self._lock = threading.Lock()

    @classmethod
    def shared_application(cls):
        if cls._shared is None:
            cls._shared = cls()
        return cls._shared

    def set_delegate(self, d):
        self._delegate = d

    def set_main_responder(self, r: NSResponder):
        self._main_responder = r

    def post_event(self, event: NSEvent):
        with self._lock:
            self._event_queue.append(event)

    def run_once(self, timeout: float = 0.0):
        """Process at most one event if available."""
        ev = None
        with self._lock:
            if self._event_queue:
                ev = self._event_queue.pop(0)
        if ev and self._main_responder:
            handled = self._main_responder.send_event(ev)
            return handled
        return False

    def run(self, poll_interval: float = 0.01):
        self._running = True
        while self._running:
            processed = self.run_once()
            time.sleep(poll_interval)

    def stop(self):
        self._running = False


class NSRunningApplication:
    pass


class NSWorkspace:
    pass
