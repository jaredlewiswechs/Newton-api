from typing import Optional

class NSResponder:
    """Base class for objects that handle events. Supports a responder chain."""

    def __init__(self):
        self.next_responder: Optional[NSResponder] = None

    def become_first_responder(self):
        return True

    def resign_first_responder(self):
        return True

    def send_event(self, event):
        """Attempt to handle an event; returns True if handled."""
        name = f"handle_{event.type.name.lower()}"
        handler = getattr(self, name, None)
        # temporary debug logging (removed after debugging)
        # If we have a handler, call it. If it returns True, the event is handled.
        if handler:
            res = handler(event)
            if res:
                return True
            # if handler didn't handle (returned False), fall through to next responder
        # fallback to next responder
        if self.next_responder:
            return self.next_responder.send_event(event)
        return False

    def handle_mouse_down(self, event):
        return False

    def handle_mouse_up(self, event):
        return False

    def handle_mouse_move(self, event):
        return False

    def handle_key_down(self, event):
        return False

    def handle_key_up(self, event):
        return False
