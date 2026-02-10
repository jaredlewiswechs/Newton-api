from Kernel.runtime.responder import NSResponder
from Kernel.runtime.event import NSEvent, NSEventType

class T(NSResponder):
    def handle_mouse_move(self, event):
        print('T handling', event.location)
        return True

r2 = T()
print('r2.send_event ->', r2.send_event(NSEvent(type=NSEventType.MOUSE_MOVE, location=(1,2))))
print('r2 has method handle_mouse_move?', hasattr(r2, 'handle_mouse_move'))
print('r2 handlers:', [name for name in dir(r2) if name.startswith('handle_')])
