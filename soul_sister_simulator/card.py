class Card:
    # Triggers are a list of dicts with keys: 'event' (str), 'action' (callable or str), and optional 'params'.
    def __init__(self, name: str, card_type: str, **kwargs):
        self.name = name
        self.card_type = card_type
        self.properties = kwargs
        # Land-specific
        self.colors = kwargs.get('colors', [])  # e.g., ['W'], ['B'], ['W', 'B']
        self.tapped = kwargs.get('tapped', False)
        # Spell-specific
        self.cost = kwargs.get('cost', {'W': 0, 'B': 0, 'C': 0})
        # Creature-specific
        self.power = kwargs.get('power', None)
        self.toughness = kwargs.get('toughness', None)
        self.base_power = self.power
        self.base_toughness = self.toughness
        # Triggers
        self.triggers = kwargs.get('triggers', [])  # List of dicts: {'event': str, 'action': callable, 'params': dict}

    def is_land(self):
        return self.card_type == 'Land'

    def is_tapped(self):
        return self.tapped

    def tap(self):
        self.tapped = True

    def untap(self):
        self.tapped = False

    def get_colors(self):
        return self.colors

    def get_cost(self):
        return self.cost

    def has_trigger(self, event: str) -> bool:
        return any(trig['event'] == event for trig in self.triggers)

    def get_triggers(self, event: str):
        return [trig for trig in self.triggers if trig['event'] == event]

    def execute_triggers(self, event: str, game_state, **kwargs):
        for trig in self.get_triggers(event):
            action = trig['action']
            params = trig.get('params', {})
            if callable(action):
                action(self, game_state, **params, **kwargs)
            # else: could support string-based actions for scripting

    def __str__(self):
        if self.is_land():
            tapped = ' (tapped)' if self.tapped else ''
            return f"{self.name} (Land: {self.colors}){tapped}"
        elif self.card_type == 'Creature':
            return f"{self.name} (Creature {self.power}/{self.toughness}, Cost: {self.cost})"
        else:
            return f"{self.name} ({self.card_type}, Cost: {self.cost})"

    def __repr__(self):
        return (f"Card(name={self.name!r}, card_type={self.card_type!r}, colors={self.colors!r}, "
                f"tapped={self.tapped!r}, cost={self.cost!r}, power={self.power!r}, toughness={self.toughness!r}, "
                f"triggers={self.triggers!r}, properties={self.properties!r})") 