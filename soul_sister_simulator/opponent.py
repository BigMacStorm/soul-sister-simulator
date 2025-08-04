"""
Simplified opponent simulation module for the Soul Sisters simulator.

This module provides a minimal opponent system that focuses only on triggering
player deck effects. Opponents are just simple counters that perform basic actions.
"""

import random
from typing import List, Dict, Any
from .config import OPPONENT_CONFIG
from .scaling_utils import get_action_scaling


class SimpleOpponent:
    """A simple opponent that just maintains creature count and performs basic actions."""
    
    def __init__(self, opponent_id: int):
        self.opponent_id = opponent_id
        self.creature_count = 0
        self.max_creatures = OPPONENT_CONFIG['max_creatures']
    
    def add_creature(self) -> bool:
        """Add a creature if under the limit."""
        if self.creature_count < self.max_creatures:
            self.creature_count += 1
            return True
        return False
    
    def remove_creature(self) -> bool:
        """Remove a creature if any exist."""
        if self.creature_count > 0:
            self.creature_count -= 1
            return True
        return False
    
    def get_creature_count(self) -> int:
        """Get the number of creatures."""
        return self.creature_count
    
    def reset(self) -> None:
        """Reset the opponent's state."""
        self.creature_count = 0


class OpponentAction:
    """Base class for opponent actions."""
    
    def __init__(self, name: str, probability: float):
        self.name = name
        self.probability = probability
    
    def should_execute(self) -> bool:
        """Determine if this action should be executed based on probability."""
        return random.random() < self.probability
    
    def execute(self, opponents: List[SimpleOpponent], player_game_state, **kwargs) -> Dict[str, Any]:
        """Execute the action and return results."""
        raise NotImplementedError("Subclasses must implement execute()")


class PlayCreatureAction(OpponentAction):
    """Action for an opponent to play a creature."""
    
    def __init__(self):
        super().__init__("play_creature", OPPONENT_CONFIG['creature_play_probability'])
    
    def execute(self, opponents: List[SimpleOpponent], player_game_state, **kwargs) -> Dict[str, Any]:
        if not self.should_execute():
            return {"action": self.name, "executed": False}
        
        # Choose a random opponent that can add a creature
        available_opponents = [opp for opp in opponents if opp.creature_count < opp.max_creatures]
        if not available_opponents:
            return {"action": self.name, "executed": False, "reason": "all_opponents_full"}
        
        opponent = random.choice(available_opponents)
        success = opponent.add_creature()
        
        if success:
            # Trigger any_creature_etb effects on player's creatures
            for card in player_game_state.battlefield.cards:
                for trigger in card.get_triggers('any_creature_etb'):
                    player_game_state.push_trigger(trigger['action'], card, 'any_creature_etb', trigger.get('params', {}))
            player_game_state.process_stack()
        
        return {
            "action": self.name,
            "executed": success,
            "opponent_id": opponent.opponent_id if success else None
        }
    
    def execute_single_opponent(self, opponent: SimpleOpponent, player_game_state, **kwargs) -> Dict[str, Any]:
        if not self.should_execute():
            return {"action": self.name, "executed": False}
        
        if opponent.creature_count >= opponent.max_creatures:
            return {"action": self.name, "executed": False, "reason": "opponent_full"}
        
        success = opponent.add_creature()
        
        if success:
            # Trigger any_creature_etb effects on player's creatures
            for card in player_game_state.battlefield.cards:
                for trigger in card.get_triggers('any_creature_etb'):
                    player_game_state.push_trigger(trigger['action'], card, 'any_creature_etb', trigger.get('params', {}))
            player_game_state.process_stack()
        
        return {
            "action": self.name,
            "executed": success,
            "opponent_id": opponent.opponent_id if success else None
        }
    
    def force_execute_single_opponent(self, opponent: SimpleOpponent, player_game_state, **kwargs) -> Dict[str, Any]:
        """Force execute this action regardless of probability (for testing)."""
        if opponent.creature_count >= opponent.max_creatures:
            return {"action": self.name, "executed": False, "reason": "opponent_full"}
        
        success = opponent.add_creature()
        
        if success:
            # Trigger any_creature_etb effects on player's creatures
            for card in player_game_state.battlefield.cards:
                for trigger in card.get_triggers('any_creature_etb'):
                    player_game_state.push_trigger(trigger['action'], card, 'any_creature_etb', trigger.get('params', {}))
            player_game_state.process_stack()
        
        return {
            "action": self.name,
            "executed": success,
            "opponent_id": opponent.opponent_id if success else None
        }


class CreatureDeathAction(OpponentAction):
    """Action for an opponent creature to die."""
    
    def __init__(self):
        super().__init__("creature_death", OPPONENT_CONFIG['creature_death_probability'])
    
    def execute(self, opponents: List[SimpleOpponent], player_game_state, **kwargs) -> Dict[str, Any]:
        if not self.should_execute():
            return {"action": self.name, "executed": False}
        
        # Choose a random opponent that has creatures
        available_opponents = [opp for opp in opponents if opp.creature_count > 0]
        if not available_opponents:
            return {"action": self.name, "executed": False, "reason": "no_creatures"}
        
        opponent = random.choice(available_opponents)
        success = opponent.remove_creature()
        
        if success:
            # Trigger creature_dies effects on player's creatures
            for card in player_game_state.battlefield.cards:
                for trigger in card.get_triggers('creature_dies'):
                    player_game_state.push_trigger(trigger['action'], card, 'creature_dies', trigger.get('params', {}))
            player_game_state.process_stack()
        
        return {
            "action": self.name,
            "executed": success,
            "opponent_id": opponent.opponent_id if success else None
        }
    
    def execute_single_opponent(self, opponent: SimpleOpponent, player_game_state, **kwargs) -> Dict[str, Any]:
        if not self.should_execute():
            return {"action": self.name, "executed": False}
        
        if opponent.creature_count == 0:
            return {"action": self.name, "executed": False, "reason": "no_creatures"}
        
        success = opponent.remove_creature()
        
        if success:
            # Trigger creature_dies effects on player's creatures
            for card in player_game_state.battlefield.cards:
                for trigger in card.get_triggers('creature_dies'):
                    player_game_state.push_trigger(trigger['action'], card, 'creature_dies', trigger.get('params', {}))
            player_game_state.process_stack()
        
        return {
            "action": self.name,
            "executed": success,
            "opponent_id": opponent.opponent_id if success else None
        }
    
    def force_execute_single_opponent(self, opponent: SimpleOpponent, player_game_state, **kwargs) -> Dict[str, Any]:
        """Force execute this action regardless of probability (for testing)."""
        if opponent.creature_count == 0:
            return {"action": self.name, "executed": False, "reason": "no_creatures"}
        
        success = opponent.remove_creature()
        
        if success:
            # Trigger creature_dies effects on player's creatures
            for card in player_game_state.battlefield.cards:
                for trigger in card.get_triggers('creature_dies'):
                    player_game_state.push_trigger(trigger['action'], card, 'creature_dies', trigger.get('params', {}))
            player_game_state.process_stack()
        
        return {
            "action": self.name,
            "executed": success,
            "opponent_id": opponent.opponent_id if success else None
        }


class PlayRemovalAction(OpponentAction):
    """Action for an opponent to play removal targeting our creatures."""
    
    def __init__(self):
        super().__init__("play_removal", OPPONENT_CONFIG['removal_play_probability'])
    
    def execute(self, opponents: List[SimpleOpponent], player_game_state, **kwargs) -> Dict[str, Any]:
        if not self.should_execute():
            return {"action": self.name, "executed": False}
        
        # Check if we have creatures to target
        our_creatures = [c for c in player_game_state.battlefield.cards if c.card_type == "Creature"]
        if not our_creatures:
            return {"action": self.name, "executed": False, "reason": "no_targets"}
        
        # Target a random creature
        target = random.choice(our_creatures)
        player_game_state.creature_dies(target, mine=True)
        
        return {
            "action": self.name,
            "executed": True,
            "target": target.name
        }
    
    def execute_single_opponent(self, opponent: SimpleOpponent, player_game_state, **kwargs) -> Dict[str, Any]:
        # Same logic as execute() since removal doesn't depend on opponent state
        return self.execute([opponent], player_game_state, **kwargs)


class PlayBoardWipeAction(OpponentAction):
    """Action for an opponent to play a board wipe."""
    
    def __init__(self):
        super().__init__("play_board_wipe", OPPONENT_CONFIG['board_wipe_probability'])
    
    def execute(self, opponents: List[SimpleOpponent], player_game_state, **kwargs) -> Dict[str, Any]:
        if not self.should_execute():
            return {"action": self.name, "executed": False}
        
        # Kill all our creatures
        our_creatures = [c for c in player_game_state.battlefield.cards if c.card_type == "Creature"]
        creatures_killed = []
        
        for creature in our_creatures[:]:  # Copy list to avoid modification during iteration
            player_game_state.creature_dies(creature, mine=True)
            creatures_killed.append(creature.name)
        
        return {
            "action": self.name,
            "executed": True,
            "creatures_killed": creatures_killed
        }
    
    def execute_single_opponent(self, opponent: SimpleOpponent, player_game_state, **kwargs) -> Dict[str, Any]:
        # Same logic as execute() since board wipe doesn't depend on opponent state
        return self.execute([opponent], player_game_state, **kwargs)


class OpponentSimulator:
    """Main class for simulating multiple simple opponents."""
    
    def __init__(self):
        self.opponents = []
        self.num_opponents = OPPONENT_CONFIG['num_opponents']
        self.actions = [
            PlayCreatureAction(),
            CreatureDeathAction(),
            PlayRemovalAction(),
            PlayBoardWipeAction(),
        ]
        self._initialize_opponents()
    
    def _initialize_opponents(self) -> None:
        """Initialize the opponent list."""
        self.opponents = [SimpleOpponent(i) for i in range(self.num_opponents)]
    
    def take_turn(self, player_game_state, turn_number: int = 1) -> Dict[str, Any]:
        """Simulate all opponents' turns and return results."""
        turn_results = {
            "actions_executed": [],
            "opponent_states": [],
            "turn_number": turn_number
        }
        
        # Get scaled actions for this turn
        scaling = get_action_scaling()
        scaled_actions = scaling.get_scaled_actions(turn_number)
        
        # Execute scaled actions
        for action_name, event_count in scaled_actions.items():
            for _ in range(event_count):
                # Find the appropriate action
                action = next((a for a in self.actions if a.name == action_name), None)
                if action:
                    result = action.execute(self.opponents, player_game_state)
                    if result["executed"]:
                        turn_results["actions_executed"].append(result)
        
        # Record opponent states
        for opponent in self.opponents:
            turn_results["opponent_states"].append({
                "opponent_id": opponent.opponent_id,
                "creatures": opponent.get_creature_count()
            })
        
        return turn_results
    
    def take_single_opponent_turn(self, opponent_id: int, player_game_state, turn_number: int = 1) -> Dict[str, Any]:
        """Simulate a single opponent's turn and return results."""
        if opponent_id >= len(self.opponents):
            return {"actions_executed": [], "error": "Invalid opponent ID"}
        
        opponent = self.opponents[opponent_id]
        turn_results = {
            "actions_executed": [],
            "opponent_id": opponent_id,
            "turn_number": turn_number
        }
        
        # Get scaled actions for this turn
        scaling = get_action_scaling()
        scaled_actions = scaling.get_scaled_actions(turn_number)
        
        # Execute scaled actions for this specific opponent
        for action_name, event_count in scaled_actions.items():
            for _ in range(event_count):
                # Find the appropriate action
                action = next((a for a in self.actions if a.name == action_name), None)
                if action:
                    result = action.execute_single_opponent(opponent, player_game_state)
                    if result["executed"]:
                        turn_results["actions_executed"].append(result)
        
        return turn_results
    
    def force_opponent_action(self, opponent_id: int, action_name: str, player_game_state, turn_number: int = 1) -> Dict[str, Any]:
        """Force a specific opponent to perform a specific action (for testing)."""
        if opponent_id >= len(self.opponents):
            return {"actions_executed": [], "error": "Invalid opponent ID"}
        
        opponent = self.opponents[opponent_id]
        turn_results = {
            "actions_executed": [],
            "opponent_id": opponent_id
        }
        
        # Find the specific action and force execute it
        for action in self.actions:
            if action.name == action_name:
                result = action.force_execute_single_opponent(opponent, player_game_state)
                if result["executed"]:
                    turn_results["actions_executed"].append(result)
                break
        
        return turn_results
    
    def get_opponent_state(self, opponent_id: int) -> Dict[str, Any]:
        """Get the current state of a specific opponent."""
        if opponent_id >= len(self.opponents):
            return {"error": "Invalid opponent ID"}
        
        opponent = self.opponents[opponent_id]
        return {
            "opponent_id": opponent.opponent_id,
            "creatures": opponent.get_creature_count(),
            "max_creatures": opponent.max_creatures
        }
    
    def reset(self) -> None:
        """Reset all opponents' states."""
        for opponent in self.opponents:
            opponent.reset()
    
    def get_total_creatures(self) -> int:
        """Get the total number of creatures across all opponents."""
        return sum(opp.get_creature_count() for opp in self.opponents)
    
    def get_opponent_states(self) -> List[Dict[str, Any]]:
        """Get the current state of all opponents."""
        return [
            {
                "opponent_id": opp.opponent_id,
                "creatures": opp.get_creature_count(),
                "max_creatures": opp.max_creatures
            }
            for opp in self.opponents
        ] 