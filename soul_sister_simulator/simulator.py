from .deck import Deck
from .card import Card
from .game_state import GameState
from typing import List, Dict, Any
import copy

class Simulator:
    def __init__(self, deck_list: List[Card], num_simulations: int = 1000, max_turns: int = 6):
        self.deck_list = deck_list
        self.num_simulations = num_simulations
        self.max_turns = max_turns
        self.stats = []

    def run_single_game(self) -> List[Dict[str, Any]]:
        deck = Deck(copy.deepcopy(self.deck_list))
        state = GameState(deck)
        state.new_game()
        per_turn_stats = []
        for turn in range(1, self.max_turns + 1):
            # In Commander, always draw at the start of every turn, including turn 1
            state.draw_card()
            turn_stats = {
                'turn': turn,
                'life': state.life,
                'hand': len(state.hand),
                'lands_played': 0,
                'cards_played': 0,
                'life_gained': 0,
            }
            # Play a land if available
            land_in_hand = next((c for c in state.hand.cards if c.card_type == 'Land'), None)
            if land_in_hand:
                state.play_land(land_in_hand)
                turn_stats['lands_played'] += 1
                turn_stats['cards_played'] += 1
            # Play all nonland cards (simplified logic)
            nonlands = [c for c in state.hand.cards if c.card_type != 'Land']
            for card in nonlands:
                state.play_card(card)
                turn_stats['cards_played'] += 1
                # Placeholder: Soul Sisters effects would go here
            # Placeholder: Calculate life gained this turn (to be expanded)
            turn_stats['life_gained'] = 0
            per_turn_stats.append(turn_stats)
            state.end_turn()
        return per_turn_stats

    def run(self) -> Dict[str, Any]:
        all_stats = []
        for _ in range(self.num_simulations):
            game_stats = self.run_single_game()
            all_stats.append(game_stats)
        # Aggregate statistics
        summary = self.aggregate_stats(all_stats)
        return summary

    def aggregate_stats(self, all_stats: List[List[Dict[str, Any]]]) -> Dict[str, Any]:
        # Calculate averages per turn
        num_games = len(all_stats)
        max_turns = self.max_turns
        turn_summaries = []
        for turn in range(max_turns):
            turn_data: Dict[str, Any] = {'turn': turn + 1, 'life': 0.0, 'hand': 0.0, 'lands_played': 0.0, 'cards_played': 0.0, 'life_gained': 0.0}
            for game in all_stats:
                stats = game[turn]
                for key in ['life', 'hand', 'lands_played', 'cards_played', 'life_gained']:
                    turn_data[key] += stats[key]
            for key in ['life', 'hand', 'lands_played', 'cards_played', 'life_gained']:
                turn_data[key] = float(turn_data[key]) / num_games
            turn_data['turn'] = turn + 1  # Ensure 'turn' stays int
            turn_summaries.append(turn_data)
        return {'per_turn': turn_summaries, 'num_games': num_games} 