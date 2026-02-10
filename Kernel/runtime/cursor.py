class NSCursor:
    def __init__(self, name: str = 'arrow'):
        self.name = name

    def set(self):
        # No-op in the demo environment
        pass

    @classmethod
    def arrow(cls):
        return cls('arrow')

    @classmethod
    def pointing_hand(cls):
        return cls('pointing_hand')
