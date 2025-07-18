from .deck import Deck
from .hand import Hand
from .card import Card
from .battlefield import Battlefield
from typing import List, Dict, Optional, Callable, Any

class GameState:
    starting_life = 40
    
    def __init__(self, deck: Deck, commander: Optional[Card] = None, verbose: bool = True):
        self.deck = deck
        self.hand = Hand()
        self.battlefield = Battlefield()
        self.graveyard: List[Card] = []
        self.life = self.starting_life
        self.lands_played_this_turn = 0
        self.turn = 1
        self.mana_pool = {'W': 0, 'B': 0, 'C': 0}
        # Commander support
        self.commander = commander
        self.command_zone = commander is not None
        self.commander_cast_count = 0
        # Stack for triggers and spells
        self.stack: List[Dict[str, Any]] = []  # Each item: {'action': callable, 'source': Card, 'event': str, 'params': dict}
        # Lurrus effect
        self.lurrus_cast_used = False
        # Simulation-wide properties for actions
        self.properties = {}
        # Verbose flag for logging
        self.verbose = verbose

    def new_game(self):
        self.deck.reset()
        self.deck.shuffle()
        self.hand = Hand()
        self.battlefield = Battlefield()
        self.graveyard = []
        self.life = self.starting_life
        self.lands_played_this_turn = 0
        self.turn = 1
        self.mana_pool = {'W': 0, 'B': 0, 'C': 0}
        self.command_zone = self.commander is not None
        self.commander_cast_count = 0
        self.stack = []
        self.hand.add_many(self.deck.draw(7))

    def untap_all(self):
        for card in self.battlefield.cards:
            if card.is_land():
                card.untap()

    def start_turn(self):
        # Trigger 'start_of_turn' for all cards on the battlefield before anything else
        for c in self.battlefield.cards:
            for trig in c.get_triggers('start_of_turn'):
                self.push_trigger(trig['action'], c, 'start_of_turn', trig.get('params', {}))
        self.process_stack()
        self.untap_all()
        self.lands_played_this_turn = 0
        self.mana_pool = {'W': 0, 'B': 0, 'C': 0}
        self.turn += 1
        self.lurrus_cast_used = False
        self.nonland_cards_played_this_turn = 0

    def draw_card(self, n=1):
        self.hand.add_many(self.deck.draw(n))

    def play_land(self, card: Card):
        if self.lands_played_this_turn >= 1:
            raise Exception("Already played a land this turn.")
        if not card.is_land():
            raise Exception("Card is not a land.")
        self.hand.remove(card)
        # If the land has an etb life cost, pay it
        if hasattr(card, 'properties') and 'etb_cost_life' in card.properties:
            self.life -= card.properties['etb_cost_life']
        # If the land enters tapped, set tapped=True
        if card.properties.get('enters_tapped', False):
            card.tapped = True
        else:
            card.tapped = False
        self.battlefield.add(card)
        self.lands_played_this_turn += 1
        # Process self_etb triggers for the land
        for trig in card.get_triggers('self_etb'):
            self.push_trigger(trig['action'], card, 'self_etb', trig.get('params', {}))
        self.process_stack()

    def available_mana(self) -> Dict[str, int]:
        mana = {'W': 0, 'B': 0, 'C': 0}
        for card in self.battlefield.cards:
            if card.is_land() and not card.is_tapped():
                for color in card.get_colors():
                    mana[color] += 1
        return mana

    def can_pay_cost(self, card: Card, extra_cost: int = 0) -> bool:
        cost = card.get_cost().copy()
        cost['C'] = cost.get('C', 0) + extra_cost
        available = self.available_mana()
        # Check colored mana first
        for color in ['W', 'B']:
            if available[color] < cost.get(color, 0):
                return False
        # Check colorless (generic) mana
        total_available = sum(available.values())
        total_needed = sum(cost.values())
        if total_available < total_needed:
            return False
        # Simulate tapping lands to ensure we can actually pay the cost with the available lands
        lands = [c for c in self.battlefield.cards if c.is_land() and not c.is_tapped()]
        temp_cost = cost.copy()
        used = set()
        # Pay colored mana first
        for color in ['W', 'B']:
            needed = temp_cost.get(color, 0)
            for i, land in enumerate(lands):
                if i in used:
                    continue
                if needed > 0 and color in getattr(land, 'colors', []):
                    used.add(i)
                    needed -= 1
            if needed > 0:
                return False
        # Pay colorless (generic) mana
        needed = temp_cost.get('C', 0)
        for i, land in enumerate(lands):
            if i in used:
                continue
            if needed > 0:
                used.add(i)
                needed -= 1
        if needed > 0:
            return False
        return True

    def tap_lands_for_cost(self, card: Card, extra_cost: int = 0):
        cost = card.get_cost().copy()
        cost['C'] = cost.get('C', 0) + extra_cost
        lands = [c for c in self.battlefield.cards if c.is_land() and not c.is_tapped()]
        used = set()
        # Pay colored mana first
        for color in ['W', 'B']:
            needed = cost.get(color, 0)
            for i, land in enumerate(lands):
                if i in used:
                    continue
                if needed > 0 and color in getattr(land, 'colors', []):
                    # Check if this land costs life to tap
                    if hasattr(land, 'properties') and 'tap_cost_life' in land.properties:
                        self.life -= land.properties['tap_cost_life']
                    land.tap()
                    used.add(i)
                    needed -= 1
                    cost[color] -= 1
        # Pay colorless (generic) mana
        needed = cost.get('C', 0)
        for i, land in enumerate(lands):
            if i in used:
                continue
            if needed > 0:
                # Check if this land costs life to tap
                if hasattr(land, 'properties') and 'tap_cost_life' in land.properties:
                    self.life -= land.properties['tap_cost_life']
                land.tap()
                used.add(i)
                needed -= 1
                cost['C'] -= 1
        # If any cost remains unpaid, raise error
        if any(v > 0 for v in cost.values()):
            raise Exception("Not enough mana to pay cost.")

    def log_trigger(self, source, event, action):
        if not self.verbose:
            return
        msg = f"Trigger: {event} from {getattr(source, 'name', str(source))} (action: {getattr(action, '__name__', str(action))})"
        print(msg)

    def push_trigger(self, action: Callable, source: Card, event: str, params: dict):
        # Check for Delney, Streetwise Lookout on the battlefield
        delney_present = any(
            c.name == "Delney, Streetwise Lookout" for c in self.battlefield.cards
        )
        double_trigger = (
            delney_present and hasattr(source, 'base_power') and source.base_power is not None and source.base_power <= 2
        )
        self.stack.append({'action': action, 'source': source, 'event': event, 'params': params})
        self.log_trigger(source, event, action)
        # If Delney is present and this is a qualifying creature, push the trigger twice
        if double_trigger:
            self.stack.append({'action': action, 'source': source, 'event': event, 'params': params})
            self.log_trigger(source, event, action)

    def process_stack(self):
        while self.stack:
            if len(self.stack) > 200:
                print(self.stack)
                self.stack.clear()
                break
            item = self.stack.pop()
            action = item['action']
            source = item['source']
            event = item['event']
            params = item['params']
            action(source, self, **params)

    def play_card(self, card: Card):
        if not self.can_pay_cost(card):
            raise Exception("Cannot pay cost to play this card.")
        self.tap_lands_for_cost(card)
        self.hand.remove(card)
        self.battlefield.add(card)
        if card.card_type != 'Land':
            if not hasattr(self, 'nonland_cards_played_this_turn'):
                self.nonland_cards_played_this_turn = 0
            self.nonland_cards_played_this_turn += 1
            # Trigger 'my_plays_card' for all your permanents (including the card being played)
            for c in self.battlefield.cards:
                for trig in c.get_triggers('my_plays_card'):
                    self.push_trigger(trig['action'], c, 'my_plays_card', trig.get('params', {}))
        # Stack triggers: my_creature_etb for all your permanents (including the entering creature)
        if card.card_type == 'Creature':
            for c in self.battlefield.cards:
                for trig in c.get_triggers('my_creature_etb'):
                    self.push_trigger(trig['action'], c, 'my_creature_etb', trig.get('params', {}))
        # Stack triggers: any_creature_etb for all other cards on battlefield
        if card.card_type == 'Creature':
            for c in self.battlefield.cards:
                if c is not card:
                    for trig in c.get_triggers('any_creature_etb'):
                        params = dict(trig.get('params', {}))
                        params['entering_card'] = card
                        self.push_trigger(trig['action'], c, 'any_creature_etb', params)
        self.process_stack()

    def gain_life(self, amount: int):
        self.life += amount
        # Track life gained this turn for effects like Ocelot Pride
        if not hasattr(self, 'life_gained_this_turn'):
            self.life_gained_this_turn = 0
        self.life_gained_this_turn += amount
        # Stack 'life_gained' triggers for all cards on battlefield (including the card that caused the gain)
        for c in self.battlefield.cards:
            for trig in c.get_triggers('life_gained'):
                params = dict(trig.get('params', {}))
                params['amount'] = amount
                self.push_trigger(trig['action'], c, 'life_gained', params)
        self.process_stack()

    def can_cast_commander(self) -> bool:
        if not self.command_zone or self.commander is None:
            return False
        extra_cost = 2 * self.commander_cast_count
        return self.can_pay_cost(self.commander, extra_cost=extra_cost)

    def cast_commander(self):
        if not self.command_zone or self.commander is None:
            raise Exception("No commander in the command zone.")
        extra_cost = 2 * self.commander_cast_count
        if not self.can_pay_cost(self.commander, extra_cost=extra_cost):
            raise Exception("Cannot pay cost to cast commander.")
        self.tap_lands_for_cost(self.commander, extra_cost=extra_cost)
        self.battlefield.add(self.commander)
        self.command_zone = False
        self.commander_cast_count += 1
        if self.commander.card_type != 'Land':
            if not hasattr(self, 'nonland_cards_played_this_turn'):
                self.nonland_cards_played_this_turn = 0
            self.nonland_cards_played_this_turn += 1
        # Stack triggers: my_creature_etb for all your permanents (including the commander)
        if self.commander.card_type == 'Creature':
            for c in self.battlefield.cards:
                for trig in c.get_triggers('my_creature_etb'):
                    self.push_trigger(trig['action'], c, 'my_creature_etb', trig.get('params', {}))
        # Stack triggers: any_creature_etb for all other cards on battlefield
        if self.commander.card_type == 'Creature':
            for c in self.battlefield.cards:
                if c is not self.commander:
                    for trig in c.get_triggers('any_creature_etb'):
                        params = dict(trig.get('params', {}))
                        params['entering_card'] = self.commander
                        self.push_trigger(trig['action'], c, 'any_creature_etb', params)
        self.process_stack()

    def commander_destroyed(self):
        if self.commander is not None:
            # Remove from battlefield if present
            if self.commander in self.battlefield.cards:
                self.battlefield.remove(self.commander)
            self.command_zone = True
            # Cost will be increased next time it's cast

    def end_turn(self):
        pass  # No changes needed; untap and mana pool reset at start_turn

    def creature_dies(self, card: Card, mine: bool = True):
        # Remove the creature from the battlefield
        if card in self.battlefield.cards:
            self.battlefield.remove(card)
        # Stack triggers: self_dies for the dying card only
        for trig in card.get_triggers('self_dies'):
            self.push_trigger(trig['action'], card, 'self_dies', trig.get('params', {}))
        # Stack triggers: my_creature_dies for all your permanents (including the dying creature) if it's your creature
        if mine:
            for c in self.battlefield.cards + [card]:
                for trig in c.get_triggers('my_creature_dies'):
                    self.push_trigger(trig['action'], c, 'my_creature_dies', trig.get('params', {}))
        # Stack triggers: creature_dies for all your permanents (including the dying creature) for any creature dying
        for c in self.battlefield.cards + [card]:
            for trig in c.get_triggers('creature_dies'):
                self.push_trigger(trig['action'], c, 'creature_dies', trig.get('params', {}))
        self.process_stack()
        # Only non-token creatures go to graveyard
        is_token = (
            getattr(card, 'cost', None) is None or
            card.name.lower() in ["token", "vampire"]
        )
        if not is_token:
            self.graveyard.append(card)

    def __str__(self):
        return (f"Turn {self.turn}: Life={self.life}, Hand={len(self.hand)}, "
                f"Battlefield={len(self.battlefield)}, Graveyard={len(self.graveyard)}, "
                f"Commander in command zone: {self.command_zone}, Commander casts: {self.commander_cast_count}")

    def __repr__(self):
        return (f"GameState(turn={self.turn}, life={self.life}, hand={self.hand!r}, "
                f"battlefield={self.battlefield!r}, graveyard={self.graveyard!r}, "
                f"commander={self.commander!r}, command_zone={self.command_zone}, commander_cast_count={self.commander_cast_count})") 

    def can_cast_with_lurrus(self, card: Card) -> bool:
        # Lurrus must be on the battlefield, effect not used this turn, card must be in graveyard, must be a creature, and total mana cost <= 2
        lurrus_present = any(c.name == "Lurrus of the Dream-Den" for c in self.battlefield.cards)
        if not lurrus_present or self.lurrus_cast_used:
            return False
        if card not in self.graveyard:
            return False
        if card.card_type != "Creature":
            return False
        cost = card.get_cost()
        total_cost = sum(cost.values())
        return total_cost <= 2

    def cast_with_lurrus(self, card: Card):
        if not self.can_cast_with_lurrus(card):
            raise Exception("Cannot cast this card with Lurrus this turn.")
        if not self.can_pay_cost(card):
            raise Exception("Cannot pay cost to cast this card.")
        self.tap_lands_for_cost(card)
        self.graveyard.remove(card)
        self.battlefield.add(card)
        self.lurrus_cast_used = True
        if card.card_type != 'Land':
            if not hasattr(self, 'nonland_cards_played_this_turn'):
                self.nonland_cards_played_this_turn = 0
            self.nonland_cards_played_this_turn += 1
        for c in self.battlefield.cards:
            for trig in c.get_triggers('my_creature_etb'):
                self.push_trigger(trig['action'], c, 'my_creature_etb', trig.get('params', {}))
        for c in self.battlefield.cards:
            if c is not card:
                for trig in c.get_triggers('any_creature_etb'):
                    params = dict(trig.get('params', {}))
                    params['entering_card'] = card
                    self.push_trigger(trig['action'], c, 'any_creature_etb', params)
        self.process_stack() 