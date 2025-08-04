"""
Utility functions for scaling opponent actions based on turn number.
"""

import random
import math
from typing import Dict, List, Tuple
from .config import OPPONENT_CONFIG


class ActionScaling:
    """Handles scaling of opponent actions based on turn number."""
    
    def __init__(self):
        self.scaling_config = OPPONENT_CONFIG['scaling']
    
    def calculate_scaling_factor(self, turn: int) -> float:
        """Calculate the scaling factor for a given turn."""
        if turn < self.scaling_config['scaling_start_turn']:
            return 1.0
        
        turns_since_start = turn - self.scaling_config['scaling_start_turn'] + 1
        base_factor = self.scaling_config['base_scaling_factor']
        max_factor = self.scaling_config['max_scaling_factor']
        
        if self.scaling_config['scaling_formula'] == 'linear':
            scaling_factor = 1.0 + (base_factor * turns_since_start)
        elif self.scaling_config['scaling_formula'] == 'exponential':
            # Use exponential growth: 1 + base_factor * (e^(turns_since_start * 0.5) - 1)
            # This gives exponential growth that starts slow and accelerates
            scaling_factor = 1.0 + (base_factor * (math.exp(turns_since_start * 0.5) - 1))
        elif self.scaling_config['scaling_formula'] == 'logarithmic':
            scaling_factor = 1.0 + (base_factor * math.log(turns_since_start + 1))
        else:
            scaling_factor = 1.0
        
        return min(scaling_factor, max_factor)
    
    def calculate_event_count(self, base_probability: float, action_name: str, turn: int) -> int:
        """
        Calculate how many events should occur for a given action on a given turn.
        
        Args:
            base_probability: Base probability of the action occurring
            action_name: Name of the action (e.g., 'play_creature')
            turn: Current turn number
            
        Returns:
            Number of events that should occur (0 or more)
        """
        scaling_factor = self.calculate_scaling_factor(turn)
        max_events = self.scaling_config['max_events_per_turn'].get(action_name, 1)
        
        # Calculate the probability of each event count
        event_probabilities = []
        
        for event_count in range(max_events + 1):
            if event_count == 0:
                # Probability of no events
                prob = 1.0 - (base_probability * scaling_factor)
            else:
                # Probability of exactly this many events
                # Use a decreasing probability for higher event counts
                prob = (base_probability * scaling_factor) * (0.5 ** (event_count - 1))
            
            event_probabilities.append((event_count, prob))
        
        # Normalize probabilities
        total_prob = sum(prob for _, prob in event_probabilities)
        if total_prob > 0:
            event_probabilities = [(count, prob / total_prob) for count, prob in event_probabilities]
        
        # Choose event count based on probabilities
        rand = random.random()
        cumulative_prob = 0.0
        
        for event_count, prob in event_probabilities:
            cumulative_prob += prob
            if rand <= cumulative_prob:
                return event_count
        
        return 0
    
    def get_scaled_actions(self, turn: int) -> Dict[str, int]:
        """
        Get the number of each action type that should occur on a given turn.
        
        Args:
            turn: Current turn number
            
        Returns:
            Dictionary mapping action names to event counts
        """
        actions = {
            'play_creature': self.calculate_event_count(
                OPPONENT_CONFIG['creature_play_probability'], 'play_creature', turn
            ),
            'creature_death': self.calculate_event_count(
                OPPONENT_CONFIG['creature_death_probability'], 'creature_death', turn
            ),
            'play_removal': self.calculate_event_count(
                OPPONENT_CONFIG['removal_play_probability'], 'play_removal', turn
            ),
            'play_board_wipe': self.calculate_event_count(
                OPPONENT_CONFIG['board_wipe_probability'], 'play_board_wipe', turn
            ),
        }
        
        return actions


def get_action_scaling() -> ActionScaling:
    """Get a singleton instance of ActionScaling."""
    if not hasattr(get_action_scaling, '_instance'):
        get_action_scaling._instance = ActionScaling()
    return get_action_scaling._instance 