#!/usr/bin/env python3
"""
Test to show scaling factors per opponent per turn.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from soul_sister_simulator.scaling_utils import get_action_scaling
from soul_sister_simulator.opponent import OpponentSimulator
from soul_sister_simulator.game_state import GameState
from soul_sister_simulator.deck import Deck
from soul_sister_simulator.decklist import build_deck
from soul_sister_simulator.cards_def import get_card

def test_scaling_per_opponent():
    """Test scaling factors per opponent per turn."""
    print("Scaling Factors Per Opponent Per Turn")
    print("=" * 50)
    
    # Set up game state
    deck = Deck(build_deck())
    commander = get_card("Amalia Benavides Aguirre")
    game_state = GameState(deck, commander=commander, verbose=False)
    game_state.new_game()
    
    # Set up opponent simulator with 3 opponents
    opponent_sim = OpponentSimulator()
    opponent_sim.num_opponents = 3
    opponent_sim._initialize_opponents()
    
    scaling = get_action_scaling()
    
    print(f"Configuration: {opponent_sim.num_opponents} opponents")
    print(f"Base scaling factor: {scaling.scaling_config['base_scaling_factor']}")
    print(f"Max scaling factor: {scaling.scaling_config['max_scaling_factor']}")
    print()
    
    # Test scaling over 10 turns
    num_turns = 10
    
    print("Turn | Scaling Factor | Opponent Actions Summary")
    print("-----|----------------|-------------------------")
    
    for turn in range(1, num_turns + 1):
        # Get scaling factor for this turn
        scaling_factor = scaling.calculate_scaling_factor(turn)
        
        # Get expected actions for this turn
        scaled_actions = scaling.get_scaled_actions(turn)
        
        # Simulate opponent turns to see actual results
        opponent_results = []
        for opponent_id in range(opponent_sim.num_opponents):
            results = opponent_sim.take_single_opponent_turn(opponent_id, game_state, turn)
            actions_executed = len(results["actions_executed"])
            opponent_results.append(actions_executed)
        
        # Calculate total actions across all opponents
        total_actions = sum(opponent_results)
        
        # Show results
        print(f"  {turn:2d} | {scaling_factor:13.3f} | "
              f"Expected: {scaled_actions['play_creature']} creatures, "
              f"Actual: {total_actions} total actions "
              f"(Opponents: {opponent_results})")
    
    print("\nFinal Opponent States:")
    for opponent_id in range(opponent_sim.num_opponents):
        state = opponent_sim.get_opponent_state(opponent_id)
        print(f"  Opponent {opponent_id}: {state['creatures']} creatures")
    
    print(f"\nTotal creatures across all opponents: {opponent_sim.get_total_creatures()}")

if __name__ == "__main__":
    test_scaling_per_opponent() 