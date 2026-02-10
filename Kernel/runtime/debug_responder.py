from Kernel.runtime.responder import NSResponder
from Kernel.runtime.event import NSEvent, NSEventType

class TestResponder(NSResponder):
    def __init__(self):
        super().__init__()
        self.events=[]
    def handle_mouse_move(self, event):
        self.events.append(event.location)
        return True

r1 = NSResponder()
r2 = TestResponder()
r1.next_responder = r2
print('send_event result:', r1.send_event(NSEvent(type=NSEventType.MOUSE_MOVE, location=(5,6))))
print('r2.events:', r2.events)
