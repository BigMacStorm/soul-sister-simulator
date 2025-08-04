import random
import argparse
from .decklist import build_deck
from .cards_def import get_card
from .game_state import GameState
from .deck import Deck
from .config import NUM_SIMULATIONS
from .opponent import OpponentSimulator

LOG = []
VERBOSE = True

def log_action(action):
    if VERBOSE:
        LOG.append(action)
        print(action)

def log_board_state(state, note=None):
    if not VERBOSE:
        return
    board = []
    if note:
        board.append(f"{note}")
    board.append(f"Life: {state.life}\n")
    # Show available untapped mana instead of listing lands
    available_mana = state.available_mana()
    board.append(f"Available Mana: {available_mana}\n")
    # Group battlefield cards by type (except lands)
    creatures = [c for c in state.battlefield.cards if c.card_type == "Creature"]
    others = [c for c in state.battlefield.cards if c.card_type not in ("Land", "Creature")]
    if creatures:
        board.append("Creatures:")
        for c in creatures:
            board.append(f"  - {c.name} (Creature {c.power}/{c.toughness})")
    if others:
        board.append("Other Permanents:")
        for c in others:
            board.append(f"  - {c.name} ({c.card_type})")
    board.append("\nHand:")
    for c in state.hand.cards:
        board.append(f"  - {str(c)}")
    # Print graveyard summary
    num_gy = len(state.graveyard)
    num_gy_creatures = sum(1 for c in state.graveyard if c.card_type == "Creature")
    board.append(f"\nGraveyard: {num_gy} cards ({num_gy_creatures} creatures)")
    board_str = "\n".join(board)
    LOG.append(board_str)
    print(board_str)

def print_silent_summary(state):
    life = state.life
    creatures = [c for c in state.battlefield.cards if c.card_type == "Creature"]
    num_creatures = len(creatures)
    total_power = sum(c.power for c in creatures if c.power is not None)
    total_toughness = sum(c.toughness for c in creatures if c.toughness is not None)
    print(f"Game ended. Life: {life} - Creatures: {num_creatures} - Total power/toughness: {total_power}/{total_toughness}")

def run_single_simulation(num_turns=10, verbose=True):
    global VERBOSE
    VERBOSE = verbose
    deck = Deck(build_deck())
    commander = get_card("Amalia Benavides Aguirre")
    state = GameState(deck, commander=commander, verbose=verbose)
    state.new_game()
    
    # Initialize opponent simulator
    opponent = OpponentSimulator()
    
    if verbose:
        log_board_state(state, note="Initial State")
        log_action(f"Opponents: {opponent.num_opponents} opponents")
    
    per_turn_stats = []
    for turn in range(1, num_turns + 1):
        # Player's turn
        log_action(f"\n=== Turn {turn} (Player) ===")
        state.start_turn()
        drawn = state.draw_card(1)
        if drawn:
            # Get the last card added to hand for logging
            drawn_card = state.hand.cards[-1]
            log_action(f"Drew a card at start of turn: {drawn_card.name} ({drawn_card.card_type})")
        else:
            log_action("No card drawn (deck empty)")
        if verbose:
            log_board_state(state, note="Start of turn state (after draw)")
        land_played = False
        hand_cards = list(state.hand.cards)
        random.shuffle(hand_cards)
        for card in hand_cards:
            if card.is_land() and not land_played and card.card_type == "Land":
                try:
                    state.play_land(card)
                    log_action(f"Played land: {card}")
                    land_played = True
                except Exception as e:
                    log_action(f"Failed to play land: {card} ({e})")
            elif card.is_land() and card.card_type == "Artifact":
                try:
                    state.play_land(card)
                    log_action(f"Played artifact land: {card}")
                except Exception as e:
                    log_action(f"Failed to play artifact land: {card} ({e})")
        if state.command_zone and state.can_cast_commander():
            try:
                state.cast_commander()
                log_action(f"Cast commander: {commander}")
            except Exception as e:
                log_action(f"Failed to cast commander: {e}")
        hand_cards = [c for c in state.hand.cards if not c.is_land() and c.card_type not in ("Instant", "Sorcery")]
        random.shuffle(hand_cards)
        for card in hand_cards:
            try:
                state.play_card(card)
                log_action(f"Played card: {card}")
            except Exception as e:
                log_action(f"Failed to play card: {card} ({e})")
        for c in state.battlefield.cards:
            for trig in c.get_triggers('end_of_turn'):
                state.push_trigger(trig['action'], c, 'end_of_turn', trig.get('params', {}))
        state.process_stack()
        while len(state.hand.cards) > 7:
            discard = random.choice(state.hand.cards)
            state.hand.remove(discard)
            state.graveyard.append(discard)
            log_action(f"Discarded: {discard}")
        
        # Each opponent takes their turn in order
        for opponent_id in range(opponent.num_opponents):
            log_action(f"\n=== Turn {turn} (Opponent {opponent_id}) ===")
            opponent_results = opponent.take_single_opponent_turn(opponent_id, state, turn)
            if verbose and opponent_results["actions_executed"]:
                log_action(f"Opponent {opponent_id} actions:")
                for action in opponent_results["actions_executed"]:
                    log_action(f"  - {action['action']}: {action}")
            if verbose:
                opponent_state = opponent.get_opponent_state(opponent_id)
                log_action(f"Opponent {opponent_id}: {opponent_state['creatures']} creatures")
        
        # Record stats for this turn
        creatures = [c for c in state.battlefield.cards if c.card_type == "Creature"]
        num_creatures = len(creatures)
        total_power = sum(c.power for c in creatures if c.power is not None)
        total_toughness = sum(c.toughness for c in creatures if c.toughness is not None)
        damage_to_enemies = state.properties.get('opponent_life_lost', 0)
        hand_size = len(state.hand.cards)
        graveyard_size = len(state.graveyard)
        graveyard_creatures = sum(1 for c in state.graveyard if c.card_type == "Creature")
        
        # Add opponent stats
        total_opponent_creatures = opponent.get_total_creatures()
        per_turn_stats.append({
            'life': state.life,
            'num_creatures': num_creatures,
            'total_power': total_power,
            'total_toughness': total_toughness,
            'damage_to_enemies': damage_to_enemies,
            'hand_size': hand_size,
            'graveyard_size': graveyard_size,
            'graveyard_creatures': graveyard_creatures,
            'opponent_creatures': total_opponent_creatures,
            'opponent_actions': len(opponent_results["actions_executed"]),
            'cards_drawn': state.cards_drawn_this_turn,
        })
    
    if verbose:
        log_board_state(state, note="Final State")
        final_opponent_states = opponent.get_opponent_states()
        total_creatures = opponent.get_total_creatures()
        log_action(f"Final opponent states: {total_creatures} total creatures")
        for opp_state in final_opponent_states:
            log_action(f"  Opponent {opp_state['opponent_id']}: {opp_state['creatures']} creatures")
    
    return per_turn_stats

def simulate_turns(num_turns=10, verbose=True):
    stats = run_single_simulation(num_turns=num_turns, verbose=verbose)
    if not verbose:
        # Print silent summary
        last = stats[-1]
        print(f"Game ended. Life: {last['life']} - Creatures: {last['num_creatures']} - Total power/toughness: {last['total_power']}/{last['total_toughness']}")

def run_many_simulations(num_turns=10, num_simulations=None):
    if num_simulations is None:
        from .config import NUM_SIMULATIONS
        num_simulations = NUM_SIMULATIONS
    stats_per_turn = []
    for _ in range(num_turns):
        stats_per_turn.append({
            'life': [],
            'num_creatures': [],
            'total_power': [],
            'total_toughness': [],
            'damage_to_enemies': [],
            'hand_size': [],
            'graveyard_size': [],
            'graveyard_creatures': [],
            'opponent_creatures': [],
            'opponent_actions': [],
            'cards_drawn': [],
        })
    for sim in range(num_simulations):
        stats = run_single_simulation(num_turns=num_turns, verbose=False)
        for turn, stat in enumerate(stats):
            stats_per_turn[turn]['life'].append(stat['life'])
            stats_per_turn[turn]['num_creatures'].append(stat['num_creatures'])
            stats_per_turn[turn]['total_power'].append(stat['total_power'])
            stats_per_turn[turn]['total_toughness'].append(stat['total_toughness'])
            stats_per_turn[turn]['damage_to_enemies'].append(stat['damage_to_enemies'])
            stats_per_turn[turn]['hand_size'].append(stat['hand_size'])
            stats_per_turn[turn]['graveyard_size'].append(stat['graveyard_size'])
            stats_per_turn[turn]['graveyard_creatures'].append(stat['graveyard_creatures'])
            stats_per_turn[turn]['opponent_creatures'].append(stat['opponent_creatures'])
            stats_per_turn[turn]['opponent_actions'].append(stat['opponent_actions'])
            stats_per_turn[turn]['cards_drawn'].append(stat['cards_drawn'])
    
    # Print summary table for player
    print("\n=== Player Simulation Averages ({} games) ===".format(num_simulations))
    print("Turn | Life | Creatures | Total P/T | Damage to Enemies | Hand | Graveyard | GY Creatures | Cards Drawn")
    print("-----|------|-----------|-----------|-------------------|------|-----------|--------------|------------")
    for turn, stats in enumerate(stats_per_turn, 1):
        avg_life = sum(stats['life']) / len(stats['life'])
        avg_creatures = sum(stats['num_creatures']) / len(stats['num_creatures'])
        avg_power = sum(stats['total_power']) / len(stats['total_power'])
        avg_toughness = sum(stats['total_toughness']) / len(stats['total_toughness'])
        avg_damage = sum(stats['damage_to_enemies']) / len(stats['damage_to_enemies'])
        avg_hand = sum(stats['hand_size']) / len(stats['hand_size'])
        avg_gy = sum(stats['graveyard_size']) / len(stats['graveyard_size'])
        avg_gy_creatures = sum(stats['graveyard_creatures']) / len(stats['graveyard_creatures'])
        avg_cards_drawn = sum(stats['cards_drawn']) / len(stats['cards_drawn'])
        print(f"{turn:>4} | {avg_life:>4.1f} | {avg_creatures:>9.2f} | {avg_power:.2f}/{avg_toughness:.2f} | {avg_damage:>17.2f} | {avg_hand:>4.2f} | {avg_gy:>9.2f} | {avg_gy_creatures:>12.2f} | {avg_cards_drawn:>10.2f}")
    
    # Print summary table for opponent
    print("\n=== Opponent Simulation Averages ({} games) ===".format(num_simulations))
    print("Turn | Total Creatures | Actions")
    print("-----|----------------|---------")
    for turn, stats in enumerate(stats_per_turn, 1):
        avg_creatures = sum(stats['opponent_creatures']) / len(stats['opponent_creatures'])
        avg_actions = sum(stats['opponent_actions']) / len(stats['opponent_actions'])
        print(f"{turn:>4} | {avg_creatures:>14.2f} | {avg_actions:>7.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate a number of turns of Soul Sister deck.")
    parser.add_argument('--turns', type=int, default=10, help='Number of turns to simulate (default: 10)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose simulation output')
    parser.add_argument('--many', action='store_true', help='Run many simulations and print averages')
    parser.add_argument('--opponents', type=int, help='Number of opponents to simulate (overrides config)')
    args = parser.parse_args()
    
    # Override config if opponents flag is set
    if args.opponents is not None:
        from .config import OPPONENT_CONFIG
        OPPONENT_CONFIG['num_opponents'] = args.opponents
    
    if args.many:
        run_many_simulations(num_turns=args.turns)
    else:
        simulate_turns(num_turns=args.turns, verbose=args.verbose) 