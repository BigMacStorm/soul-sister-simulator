import random
from .config import ESPER_PAY_RATE, CHANCE_NON_BASIC_LAND

def gain_life_action(card, game_state, amount=1, **kwargs):
    game_state.gain_life(amount, source_card=card)

def explore_action(card, game_state, **kwargs):
    # Look at the top card of the deck
    if len(game_state.deck.cards) > 0:
        top_card = game_state.deck.cards[0]
        game_state.deck.cards = game_state.deck.cards[1:]  # Remove from deck
        if top_card.is_land():
            # If it's a land, put it into hand
            game_state.hand.add(top_card)
        else:
            # If it's not a land, put it into graveyard and increase the triggering card's power/toughness
            game_state.graveyard.append(top_card)
            # The card parameter should be the actual card instance from the battlefield
            # Just verify it's on the battlefield and increase its stats
            if card in game_state.battlefield.cards:
                if card.power is not None:
                    card.power += 1
                if card.toughness is not None:
                    card.toughness += 1

def draw_card_action(card, game_state, amount=1, **kwargs):
    game_state.draw_card(amount)

def creature_dies_action(card, game_state, **kwargs):
    # When a creature dies, gain 1 life
    game_state.gain_life(1)

def lose_life_generic_action(card, game_state, amount=1, all_opponents=False, **kwargs):
    # Simulate one or all opponents losing life
    if 'opponent_life_lost' not in game_state.properties:
        game_state.properties['opponent_life_lost'] = 0
    if all_opponents:
        # Assume 3 opponents for simulation
        game_state.properties['opponent_life_lost'] += amount * 3
    else:
        game_state.properties['opponent_life_lost'] += amount

def scry_action(card, game_state, amount=1, **kwargs):
    # Simplified scry - just draw a card for now
    game_state.draw_card(1)

def add_counter_action(card, game_state, counter_type="+1/+1", amount=1, **kwargs):
    # Add +1/+1 counters: increase power and toughness by amount
    if card.power is not None:
        card.power += amount
    if card.toughness is not None:
        card.toughness += amount

def add_counter_to_all_creatures_action(card, game_state, counter_type="+1/+1", amount=1, **kwargs):
    # Add +1/+1 counter to every creature you control
    for c in game_state.battlefield.cards:
        if c.card_type == "Creature":
            if c.power is not None:
                c.power += amount
            if c.toughness is not None:
                c.toughness += amount

def create_token_action(card, game_state, name="token", power=1, toughness=1, **kwargs):
    from .card import Card
    token = Card(name, "Creature", power=power, toughness=toughness)
    # Store existing battlefield cards before adding the token
    existing_cards = list(game_state.battlefield.cards)
    game_state.battlefield.add(token)
    # Trigger ETB for the token
    for trig in token.get_triggers('my_creature_etb'):
        game_state.push_trigger(trig['action'], token, 'my_creature_etb', trig.get('params', {}))
    for c in existing_cards:  # Only trigger existing cards, not the token
        for trig in c.get_triggers('any_creature_etb'):
            params = dict(trig.get('params', {}))
            params['entering_card'] = token
            game_state.push_trigger(trig['action'], c, 'any_creature_etb', params)

def maybe_create_token_action(card, game_state, **kwargs):
    # 15% chance to create a 1/1 'token' creature
    if random.random() < 0.15:
        create_token_action(card, game_state)

def dark_confidant_draw_action(card, game_state, **kwargs):
    # Draw a card, then lose life equal to its total mana cost (lands cost 0)
    drawn = game_state.deck.draw(1)
    if drawn:
        drawn_card = drawn[0]
        game_state.hand.add(drawn_card)
        if drawn_card.card_type == "Land":
            life_loss = 0
        else:
            cost = drawn_card.get_cost() if hasattr(drawn_card, 'get_cost') else {}
            life_loss = sum(cost.values()) if cost else 0
        game_state.life -= life_loss

def elenda_death_token_action(card, game_state, **kwargs):
    # Create X 1/1 Vampire tokens, where X is Elenda's current power
    num_tokens = card.power if card.power is not None else 0
    from .card import Card
    for _ in range(num_tokens):
        token = Card("Vampire", "Creature", power=1, toughness=1)
        # Store existing battlefield cards before adding the token
        existing_cards = list(game_state.battlefield.cards)
        game_state.battlefield.add(token)
        # Trigger ETB for the token
        for trig in token.get_triggers('my_creature_etb'):
            game_state.push_trigger(trig['action'], token, 'my_creature_etb', trig.get('params', {}))
        for c in existing_cards:  # Only trigger existing cards, not the token
            for trig in c.get_triggers('any_creature_etb'):
                params = dict(trig.get('params', {}))
                params['entering_card'] = token
                game_state.push_trigger(trig['action'], c, 'any_creature_etb', params)

def esper_sentinel_draw_action(card, game_state, esper_pay_rate=None, **kwargs):
    if esper_pay_rate is None:
        esper_pay_rate = ESPER_PAY_RATE
    if random.random() < esper_pay_rate:
        game_state.draw_card(1)

def essence_channeler_death_action(card, game_state, **kwargs):
    # Calculate number of +1/+1 counters (current power - base power)
    num_counters = 0
    if card.power is not None and card.base_power is not None:
        num_counters = max(0, card.power - card.base_power)
    if num_counters == 0:
        return
    # Try to find Amalia on the battlefield
    amalia = next((c for c in game_state.battlefield.cards if c.name == "Amalia Benavides Aguirre"), None)
    target = amalia
    # If Amalia is not present, pick a random creature you control
    if not target:
        creatures = [c for c in game_state.battlefield.cards if c.card_type == "Creature" and c is not card]
        if creatures:
            target = random.choice(creatures)
    # Add counters to the target
    if target and target.power is not None and target.toughness is not None:
        target.power += num_counters
        target.toughness += num_counters

def kambal_life_gain_action(card, game_state, **kwargs):
    if random.random() < 0.2:
        game_state.gain_life(2)

def leonin_elder_life_gain_action(card, game_state, **kwargs):
    if random.random() < 0.1:
        game_state.gain_life(1)

def mother_of_runes_counter_removal_action(card, game_state, **kwargs):
    # Remove the top removal spell from the stack (simulate by removing the top 'opp_plays_removal' event)
    for i in range(len(game_state.stack)-1, -1, -1):
        item = game_state.stack[i]
        if item['event'] == 'opp_plays_removal':
            del game_state.stack[i]
            break


def ocelot_pride_end_of_turn_action(card, game_state, **kwargs):
    # If life was gained this turn, create a 1/1 token
    if getattr(game_state, 'life_gained_this_turn', 0) > 0:
        create_token_action(card, game_state)


def selfless_spirit_counter_action(card, game_state, **kwargs):
    # Destroy self and counter the removal/boardwipe (remove top removal/boardwipe from stack)
    game_state.creature_dies(card, mine=True)
    for i in range(len(game_state.stack)-1, -1, -1):
        item = game_state.stack[i]
        if item['event'] in ['opp_plays_removal', 'opp_plays_boardwipe']:
            del game_state.stack[i]
            break


def sorin_life_gain_action(card, game_state, **kwargs):
    # Spend any mana to gain 1 life when I play any card
    mana = game_state.available_mana()
    for color in ['W', 'B', 'C']:
        if mana[color] > 0:
            # Simulate spending one mana
            for land in game_state.battlefield.cards:
                if land.is_land() and not land.is_tapped() and color in land.get_colors():
                    land.tap()
                    break
            game_state.gain_life(1)
            break


def spectrum_sentinel_land_action(card, game_state, **kwargs):
    # Percent chance to gain 1 life when opponent plays a land
    if random.random() < CHANCE_NON_BASIC_LAND:
        game_state.gain_life(1) 

def aetherflux_reservoir_life_gain_action(card, game_state, **kwargs):
    # Gain life equal to the number of nonland cards played this turn so far
    n = getattr(game_state, 'nonland_cards_played_this_turn', 0)
    if n > 0:
        game_state.gain_life(n) 

def cleric_class_extra_life_action(card, game_state, **kwargs):
    # Gain 1 life, but do not trigger life gain triggers
    game_state.life += 1 