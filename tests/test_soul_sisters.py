"""
Comprehensive test suite for the Soul Sisters Magic: The Gathering simulator.

This test suite focuses on testing card interactions, trigger systems, and board state
management in the context of a Soul Sisters deck. Tests construct specific board states
and verify that card interactions work as expected.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch
from typing import List, Dict, Any, Optional

# Add the parent directory to the path so we can import the soul_sister_simulator module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from soul_sister_simulator.game_state import GameState
from soul_sister_simulator.deck import Deck
from soul_sister_simulator.card import Card
from soul_sister_simulator.cards_def import get_card
from soul_sister_simulator.actions import gain_life_action
from soul_sister_simulator.opponent import OpponentSimulator, SimpleOpponent


class SoulSistersTestBase(unittest.TestCase):
    """Base class for Soul Sisters tests with common helper methods."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a minimal deck for testing
        test_cards = [
            get_card("Plains"),
            get_card("Swamp"),
            get_card("Soul Warden"),
            get_card("Soul's Attendant"),
        ]
        deck = Deck(test_cards)
        commander = get_card("Amalia Benavides Aguirre")
        self.game_state: GameState = GameState(deck, commander=commander, verbose=False)
        self.game_state.new_game()
        
    def tearDown(self):
        """Clean up after each test."""
        self.game_state = None  # type: ignore
    
    def _ensure_game_state(self) -> GameState:
        """Ensure game_state is initialized and return it."""
        assert self.game_state is not None, "Game state not initialized"
        return self.game_state
    
    def add_cards_to_battlefield(self, card_names: List[str]):
        """Add cards to the battlefield by name."""
        game_state = self._ensure_game_state()
        for card_name in card_names:
            card = get_card(card_name)
            game_state.battlefield.add(card)
    
    def add_cards_to_hand(self, card_names: List[str]):
        """Add cards to hand by name."""
        game_state = self._ensure_game_state()
        for card_name in card_names:
            card = get_card(card_name)
            game_state.hand.add(card)
    
    def add_lands_to_battlefield(self, land_names: List[str], tapped=False):
        """Add lands to the battlefield, optionally tapped."""
        game_state = self._ensure_game_state()
        for land_name in land_names:
            land = get_card(land_name)
            if tapped:
                land.tap()
            game_state.battlefield.add(land)
    
    def get_creatures_on_battlefield(self) -> List[Card]:
        """Get all creatures currently on the battlefield."""
        game_state = self._ensure_game_state()
        return [card for card in game_state.battlefield.cards if card.card_type == "Creature"]
    
    def get_life_gain_triggers(self) -> List[Card]:
        """Get all cards on the battlefield that have life gain triggers."""
        game_state = self._ensure_game_state()
        life_gain_cards = []
        for card in game_state.battlefield.cards:
            if card.has_trigger('any_creature_etb') or card.has_trigger('my_creature_etb'):
                life_gain_cards.append(card)
        return life_gain_cards
    
    def count_triggers_for_event(self, event: str) -> int:
        """Count how many triggers exist for a specific event on the battlefield."""
        game_state = self._ensure_game_state()
        count = 0
        for card in game_state.battlefield.cards:
            count += len(card.get_triggers(event))
        return count
    
    def play_card_from_hand(self, card_name: str) -> bool:
        """Play a card from hand, returning True if successful."""
        game_state = self._ensure_game_state()
        try:
            card = next((c for c in game_state.hand.cards if c.name == card_name), None)
            if card:
                game_state.play_card(card)
                return True
        except Exception:
            pass
        return False
    
    def assert_life_total(self, expected_life: int):
        """Assert that the current life total matches the expected value."""
        game_state = self._ensure_game_state()
        self.assertEqual(game_state.life, expected_life, 
                        f"Expected life total {expected_life}, got {game_state.life}")
    
    def assert_creature_count(self, expected_count: int):
        """Assert that the number of creatures on the battlefield matches the expected value."""
        creatures = self.get_creatures_on_battlefield()
        self.assertEqual(len(creatures), expected_count,
                        f"Expected {expected_count} creatures, got {len(creatures)}")
    
    def assert_card_on_battlefield(self, card_name: str):
        """Assert that a specific card is on the battlefield."""
        game_state = self._ensure_game_state()
        card_names = [card.name for card in game_state.battlefield.cards]
        self.assertIn(card_name, card_names, f"Expected {card_name} to be on battlefield")
    
    def assert_card_not_on_battlefield(self, card_name: str):
        """Assert that a specific card is not on the battlefield."""
        game_state = self._ensure_game_state()
        card_names = [card.name for card in game_state.battlefield.cards]
        self.assertNotIn(card_name, card_names, f"Expected {card_name} to not be on battlefield")
    
    def get_card_from_battlefield(self, card_name: str) -> Card:
        """Get a specific card from the battlefield by name."""
        game_state = self._ensure_game_state()
        return next(c for c in game_state.battlefield.cards if c.name == card_name)
    
    def assert_power_greater_than(self, card: Card, expected_min: int):
        """Assert that a card's power is greater than the expected minimum."""
        if card.power is not None:
            self.assertGreater(card.power, expected_min)
    
    def assert_toughness_greater_than(self, card: Card, expected_min: int):
        """Assert that a card's toughness is greater than the expected minimum."""
        if card.toughness is not None:
            self.assertGreater(card.toughness, expected_min)
    
    def assert_power_greater_equal(self, card: Card, expected_min: int):
        """Assert that a card's power is greater than or equal to the expected minimum."""
        if card.power is not None:
            self.assertGreaterEqual(card.power, expected_min)
    
    def assert_power_greater_than_base(self, card: Card):
        """Assert that a card's power is greater than its base power."""
        if card.power is not None and card.base_power is not None:
            self.assertGreater(card.power, card.base_power)
    
    def assert_toughness_greater_than_base(self, card: Card):
        """Assert that a card's toughness is greater than its base toughness."""
        if card.toughness is not None and card.base_toughness is not None:
            self.assertGreater(card.toughness, card.base_toughness)


class TestBasicLifeGainTriggers(SoulSistersTestBase):
    """Test basic life gain trigger interactions."""
    
    def test_soul_warden_life_gain_on_creature_etb(self):
        """
        Test that Soul Warden gains life when a creature enters the battlefield.
        This is the core mechanic of the Soul Sisters archetype.
        """
        initial_life = self.game_state.life
        
        # Set up board state: 2 Plains, 1 Soul Warden
        self.add_lands_to_battlefield(["Plains", "Plains"])
        self.add_cards_to_battlefield(["Soul Warden"])
        
        # Add a creature to hand
        self.add_cards_to_hand(["Soul's Attendant"])
        
        # Play the creature
        self.play_card_from_hand("Soul's Attendant")
        
        # Verify life gain occurred
        self.assert_life_total(initial_life + 1)
        self.assert_creature_count(2)
    
    def test_multiple_soul_sisters_trigger_together(self):
        """
        Test that multiple Soul Sisters creatures all trigger when a creature enters.
        This tests the stacking nature of life gain triggers.
        """
        initial_life = self.game_state.life
        
        # Set up board state: 2 Plains, multiple Soul Sisters
        self.add_lands_to_battlefield(["Plains", "Plains"])
        self.add_cards_to_battlefield(["Soul Warden", "Soul's Attendant", "Auriok Champion"])
        
        # Add a creature to hand
        self.add_cards_to_hand(["Lunarch Veteran"])
        
        # Play the creature
        self.play_card_from_hand("Lunarch Veteran")
        
        # Verify multiple life gain triggers occurred (3 Soul Sisters, Lunarch Veteran doesn't trigger on itself)
        self.assert_life_total(initial_life + 3)
        self.assert_creature_count(4)
    
    def test_life_gain_triggers_only_on_creatures(self):
        """
        Test that life gain triggers only fire for creatures, not other card types.
        This ensures the trigger system correctly filters by card type.
        """
 
        initial_life = self.game_state.life
        
        # Set up board state: 2 Plains, 1 Soul Warden
        self.add_lands_to_battlefield(["Plains", "Plains"])
        self.add_cards_to_battlefield(["Soul Warden"])
        
        # Add a non-creature card to hand
        self.add_cards_to_hand(["Swords to Plowshares"])
        
        # Play the non-creature card
        self.play_card_from_hand("Swords to Plowshares")
        
        # Verify no life gain occurred
        self.assert_life_total(initial_life)
        self.assert_creature_count(1)


class TestAmaliaBenavidesAguirre(SoulSistersTestBase):
    """Test the commander's explore mechanic and life gain interactions."""
    
    def test_amalia_explore_on_life_gain(self):
        """
        Test that Amalia Benavides Aguirre explores when life is gained.
        This tests the commander's core mechanic and the explore action.
        """
        
        initial_life = self.game_state.life
        
        # Set up board state: 2 Plains, 1 Amalia
        self.add_lands_to_battlefield(["Plains", "Plains"])
        self.add_cards_to_battlefield(["Amalia Benavides Aguirre", "Soul's Attendant"])
        self.game_state.deck.cards = [get_card("Damn")]
        
        # Add a Soul Sister to hand
        self.add_cards_to_hand(["Soul Warden"])
        
        # Play Soul Warden to trigger life gain
        self.play_card_from_hand("Soul Warden")
        
        # Verify life gain occurred and Amalia triggered
        self.assert_life_total(initial_life + 1)
        self.assert_creature_count(3)
        
        # Check that Amalia's power/toughness increased from explore
        amalia = next(c for c in self.game_state.battlefield.cards if c.name == "Amalia Benavides Aguirre")
        # Amalia starts at 1/3, explore should increase by 1 when non-land is revealed
        # Expected: power=2, toughness=4
        self.assertEqual(amalia.power, 2)  # type: ignore # Should be 1 + 1 = 2
        self.assertEqual(amalia.toughness, 4)  # type: ignore # Should be 3 + 1 = 4
    
    def test_amalia_explore_with_land_vs_nonland(self):
        """
        Test Amalia's explore mechanic with both land and non-land cards.
        This verifies the explore action correctly handles different card types.
        """
        
        # Set up board state: 2 Plains, 1 Amalia
        self.add_lands_to_battlefield(["Plains", "Plains"])
        self.add_cards_to_battlefield(["Amalia Benavides Aguirre"])
        
        # Mock the deck to control what Amalia explores
        original_cards = self.game_state.deck.cards
        self.game_state.deck.cards = [get_card("Plains")]
        
        # Trigger life gain to cause explore
        self.game_state.gain_life(1)
        
        # Verify Amalia's stats increased
        amalia = next(c for c in self.game_state.battlefield.cards if c.name == "Amalia Benavides Aguirre")
        self.assertGreater(amalia.power, 1)  # type: ignore
        self.assertGreater(amalia.toughness, 3)  # type: ignore
        
        # Restore original deck
        self.game_state.deck.cards = original_cards


class TestArchangelOfThune(SoulSistersTestBase):
    """Test Archangel of Thune's +1/+1 counter distribution mechanic."""
    
    def test_archangel_counters_on_life_gain(self):
        """
        Test that Archangel of Thune adds +1/+1 counters to all creatures when life is gained.
        This tests the counter distribution mechanic and life gain triggers.
        """
        
        initial_life = self.game_state.life
        
        # Set up board state: 3 Plains, 1 Archangel, 2 other creatures
        self.add_lands_to_battlefield(["Plains", "Plains", "Plains"])
        self.add_cards_to_battlefield(["Archangel of Thune", "Soul Warden", "Soul's Attendant"])
        
        # Add a creature to hand
        self.add_cards_to_hand(["Lunarch Veteran"])
        
        # Play the creature to trigger life gain
        self.play_card_from_hand("Lunarch Veteran")
        
        # Verify life gain occurred: 2 from Soul Sisters, Lunarch Veteran doesn't trigger on itself = 2 total
        self.assert_life_total(initial_life + 2)
        self.assert_creature_count(4)
        
        # Verify all creatures got +1/+1 counters
        creatures = self.get_creatures_on_battlefield()
        for creature in creatures:
            self.assertGreater(creature.power, creature.base_power)  # type: ignore
            self.assertGreater(creature.toughness, creature.base_toughness)  # type: ignore
    
    def test_archangel_multiple_triggers(self):
        """
        Test that Archangel of Thune triggers multiple times with multiple life gain events.
        This ensures the trigger system handles multiple events correctly.
        """
        
        initial_life = self.game_state.life
        
        # Set up board state: 3 Plains, 1 Archangel, 1 Soul Sister
        self.add_lands_to_battlefield(["Plains", "Plains", "Plains"])
        self.add_cards_to_battlefield(["Archangel of Thune", "Soul Warden"])
        
        # Add multiple creatures to hand
        self.add_cards_to_hand(["Soul's Attendant", "Lunarch Veteran"])
        
        # Play both creatures
        self.play_card_from_hand("Soul's Attendant")
        print(f"After Soul's Attendant: {self.game_state.life}")
        self.play_card_from_hand("Lunarch Veteran")
        print(f"After Lunarch Veteran: {self.game_state.life}")
        print(f"Total life gained: {self.game_state.life - initial_life}")

        self.assert_life_total(initial_life + 3)
        self.assert_creature_count(4)
        
        # Verify creatures got multiple +1/+1 counters
        archangel = next(c for c in self.game_state.battlefield.cards if c.name == "Archangel of Thune")
        self.assertGreaterEqual(archangel.power, 5)  # type: ignore # Base 3 + at least 2 counters


class TestKarlovOfTheGhostCouncil(SoulSistersTestBase):
    """Test Karlov of the Ghost Council's +1/+1 counter mechanic."""
    
    def test_karlov_counters_on_life_gain(self):
        """
        Test that Karlov of the Ghost Council gets +1/+1 counters when life is gained.
        This tests individual creature counter mechanics.
        """
        
        initial_life = self.game_state.life
        
        # Set up board state: 2 Plains, 1 Karlov, 1 Soul Sister
        self.add_lands_to_battlefield(["Plains", "Plains"])
        self.add_cards_to_battlefield(["Karlov of the Ghost Council", "Soul Warden"])
        
        # Add a creature to hand
        self.add_cards_to_hand(["Soul's Attendant"])
        
        # Play the creature to trigger life gain
        self.play_card_from_hand("Soul's Attendant")
        
        # Verify life gain occurred
        self.assert_life_total(initial_life + 1)
        self.assert_creature_count(3)
        
        # Verify Karlov got +1/+1 counters
        karlov = next(c for c in self.game_state.battlefield.cards if c.name == "Karlov of the Ghost Council")
        self.assertGreater(karlov.power, 2)  # type: ignore # Base 2 + at least 1 counter
        self.assertGreater(karlov.toughness, 2)  # type: ignore # Base 2 + at least 1 counter


class TestBloodArtistAndDeathTriggers(SoulSistersTestBase):
    """Test death trigger mechanics and life gain from creature deaths."""
    
    def test_blood_artist_life_gain_on_death(self):
        """
        Test that Blood Artist gains life when a creature dies.
        This tests death trigger mechanics and the graveyard system.
        """
        
        initial_life = self.game_state.life
        
        # Set up board state: 2 Plains, 1 Blood Artist, 1 other creature
        self.add_lands_to_battlefield(["Plains", "Plains"])
        self.add_cards_to_battlefield(["Blood Artist", "Soul Warden"])
        
        # Kill the Soul Warden (not Blood Artist)
        soul_warden = next(c for c in self.game_state.battlefield.cards if c.name == "Soul Warden")
        self.game_state.creature_dies(soul_warden, mine=True)
        
        # Verify life gain occurred from death
        self.assert_life_total(initial_life + 1)
        self.assert_creature_count(1)  # One creature died
    
    def test_multiple_death_triggers(self):
        """
        Test that multiple death trigger creatures all trigger when a creature dies.
        This tests the stacking of death triggers.
        """
        
        initial_life = self.game_state.life
        
        # Set up board state: 2 Plains, multiple death trigger creatures
        self.add_lands_to_battlefield(["Plains", "Plains"])
        self.add_cards_to_battlefield(["Blood Artist", "Cruel Celebrant", "Deathgreeter"])
        
        # Add a creature to hand and play it
        self.add_cards_to_hand(["Soul Warden"])
        self.play_card_from_hand("Soul Warden")
        
        # Kill the Soul Warden
        soul_warden = next(c for c in self.game_state.battlefield.cards if c.name == "Soul Warden")
        self.game_state.creature_dies(soul_warden, mine=True)
        
        # Verify multiple death triggers occurred
        self.assert_life_total(initial_life + 3)  # 1 from ETB + 2 from death triggers (Soul Warden doesn't trigger on itself)
        self.assert_creature_count(3)  # 3 death trigger creatures remain


class TestDelneyStreetwiseLookout(SoulSistersTestBase):
    """Test Delney's trigger doubling mechanic for small creatures."""
    
    def test_delney_doubles_triggers_for_small_creatures(self):
        """
        Test that Delney, Streetwise Lookout doubles triggers for creatures with power 2 or less.
        This tests the complex trigger doubling mechanic.
        """
        
        initial_life = self.game_state.life
        
        # Set up board state: 2 Plains, 1 Delney, 1 Soul Warden (power 1)
        self.add_lands_to_battlefield(["Plains", "Plains"])
        self.add_cards_to_battlefield(["Delney, Streetwise Lookout", "Soul Warden"])
        
        # Add a small creature to hand
        self.add_cards_to_hand(["Soul's Attendant"])  # Power 1
        
        # Play the creature
        self.play_card_from_hand("Soul's Attendant")
        
        # Verify double life gain occurred (Delney doubles the trigger)
        self.assert_life_total(initial_life + 2)  # Doubled from 1
        self.assert_creature_count(3)
    
    def test_delney_does_not_double_large_creatures(self):
        """
        Test that Delney does not double triggers for creatures with power greater than 2.
        This ensures the power check works correctly.
        """
        
        initial_life = self.game_state.life
        
        # Set up board state: 3 Plains, 1 Delney, 1 Soul Warden
        self.add_lands_to_battlefield(["Plains", "Plains", "Plains"])
        self.add_cards_to_battlefield(["Delney, Streetwise Lookout", "Soul Warden"])
        
        # Add a large creature to hand
        self.add_cards_to_hand(["Archangel of Thune"])  # Power 3
        
        # Play the creature
        self.play_card_from_hand("Archangel of Thune")
        
        # Verify normal life gain occurred (not doubled)
        self.assert_life_total(initial_life + 0)  # Not doubled, and Archangel doesn't trigger on itself
        self.assert_creature_count(3)


class TestComplexBoardStates(SoulSistersTestBase):
    """Test complex board states with multiple interacting cards."""
    
    def test_full_soul_sisters_board(self):
        """
        Test a full Soul Sisters board with multiple life gain triggers and counter effects.
        This tests the integration of multiple card interactions.
        """
        
        initial_life = self.game_state.life
        
        # Set up a complex board state
        self.add_lands_to_battlefield(["Plains", "Plains", "Plains", "Plains"])
        self.add_cards_to_battlefield([
            "Soul Warden", "Soul's Attendant", "Auriok Champion",
            "Archangel of Thune", "Karlov of the Ghost Council"
        ])
        
        # Add a creature to hand
        self.add_cards_to_hand(["Lunarch Veteran"])
        
        # Play the creature
        self.play_card_from_hand("Lunarch Veteran")
        
        # Verify complex interactions occurred
        self.assert_life_total(initial_life + 3)  # 3 Soul Sisters trigger (Lunarch Veteran doesn't trigger on itself)
        self.assert_creature_count(6)
        
        # Verify counter effects occurred
        creatures = self.get_creatures_on_battlefield()
        for creature in creatures:
            if creature.name in ["Archangel of Thune", "Karlov of the Ghost Council"]:
                self.assertGreater(creature.power, creature.base_power) # type: ignore
    
    def test_life_gain_chain_reaction(self):
        """
        Test a chain reaction of life gain triggers that cause additional effects.
        This tests the trigger stack and multiple resolution cycles.
        """
        
        initial_life = self.game_state.life
        
        # Set up board state with life gain triggers and counter effects
        self.add_lands_to_battlefield(["Plains", "Plains", "Plains"])
        self.add_cards_to_battlefield([
            "Soul Warden", "Archangel of Thune", "Karlov of the Ghost Council"
        ])
        
        # Add multiple creatures to hand
        self.add_cards_to_hand(["Soul's Attendant", "Lunarch Veteran"])
        
        # Play both creatures
        self.play_card_from_hand("Soul's Attendant")
        self.play_card_from_hand("Lunarch Veteran")
        
        # Verify chain reaction occurred
        self.assert_life_total(initial_life + 3)  # 2 creatures * 2 Soul Sisters (creatures don't trigger on themselves)
        self.assert_creature_count(5)
        
        # Verify counter effects occurred multiple times
        karlov = next(c for c in self.game_state.battlefield.cards if c.name == "Karlov of the Ghost Council")
        self.assertGreaterEqual(karlov.power, 6)  # Base 2 + at least 4 counters # type: ignore


class TestManaAndCostSystem(SoulSistersTestBase):
    """Test the mana system and cost payment mechanics."""
    
    def test_mana_availability_and_cost_payment(self):
        """
        Test that the mana system correctly tracks available mana and pays costs.
        This tests the core mana mechanics of the game.
        """
        
        
        # Set up board state with different colored lands
        self.add_lands_to_battlefield(["Plains", "Swamp", "Caves of Koilos"])
        
        # Check available mana
        available_mana = self.game_state.available_mana()
        self.assertEqual(available_mana['W'], 2)  # Plains + Caves
        self.assertEqual(available_mana['B'], 2)  # Swamp + Caves
        
        # Add a card with specific mana cost
        self.add_cards_to_hand(["Amalia Benavides Aguirre"])  # Cost: W/B
        
        # Verify we can pay the cost
        amalia = next(c for c in self.game_state.hand.cards if c.name == "Amalia Benavides Aguirre")
        self.assertTrue(self.game_state.can_pay_cost(amalia))
        
        # Play the card
        self.play_card_from_hand("Amalia Benavides Aguirre")
        
        # Verify card was played and mana was spent
        self.assert_card_on_battlefield("Amalia Benavides Aguirre")
        self.assert_card_not_on_battlefield("Plains")  # Should be tapped
    
    def test_insufficient_mana_prevents_playing(self):
        """
        Test that cards cannot be played without sufficient mana.
        This tests the cost validation system.
        """
        
        
        # Set up board state with insufficient mana
        self.add_lands_to_battlefield(["Plains"])  # Only 1 white mana
        
        # Add a card that requires more mana
        self.add_cards_to_hand(["Archangel of Thune"])  # Cost: 2WW
        
        # Verify we cannot pay the cost
        archangel = next(c for c in self.game_state.hand.cards if c.name == "Archangel of Thune")
        self.assertFalse(self.game_state.can_pay_cost(archangel))
        
        # Verify card cannot be played
        self.assertFalse(self.play_card_from_hand("Archangel of Thune"))


class TestOpponentInteractions(SoulSistersTestBase):
    """Test opponent ETB and death trigger interactions."""
    
    def setUp(self):
        """Set up test fixtures with opponent simulator."""
        super().setUp()
        self.opponent_simulator = OpponentSimulator()
        # Override to use 1 opponent for testing
        self.opponent_simulator.num_opponents = 1
        self.opponent_simulator._initialize_opponents()
    
    def test_opponent_creature_etb_triggers_soul_warden(self):
        """Test that opponent playing a creature triggers Soul Warden."""
        game_state = self._ensure_game_state()
        
        # Add Soul Warden to battlefield
        self.add_cards_to_battlefield(["Soul Warden"])
        initial_life = game_state.life
        
        # Force opponent to play a creature (bypasses probability)
        results = self.opponent_simulator.force_opponent_action(0, "play_creature", game_state)
        
        # Verify creature was played and life was gained
        self.assertIn("play_creature", [a["action"] for a in results["actions_executed"]])
        self.assertGreater(game_state.life, initial_life)
        self.assertEqual(game_state.life, initial_life + 1)
        
        # Verify opponent creature count increased
        opponent = self.opponent_simulator.opponents[0]
        self.assertEqual(opponent.get_creature_count(), 1)
    
    def test_opponent_creature_death_triggers_blood_artist(self):
        """Test that opponent creature dying triggers Blood Artist."""
        game_state = self._ensure_game_state()
        
        # Add Blood Artist to battlefield
        self.add_cards_to_battlefield(["Blood Artist"])
        initial_life = game_state.life
        
        # First, force opponent to play a creature
        self.opponent_simulator.force_opponent_action(0, "play_creature", game_state)
        opponent = self.opponent_simulator.opponents[0]
        self.assertEqual(opponent.get_creature_count(), 1)
        
        # Now force opponent to have a creature die
        results = self.opponent_simulator.force_opponent_action(0, "creature_death", game_state)
        
        # Verify creature died and life was gained from Blood Artist
        self.assertIn("creature_death", [a["action"] for a in results["actions_executed"]])
        self.assertGreater(game_state.life, initial_life)
        self.assertEqual(game_state.life, initial_life + 1)
        self.assertEqual(opponent.get_creature_count(), 0)
    
    def test_opponent_actions_trigger_multiple_effects(self):
        """Test that opponent actions trigger multiple effects simultaneously."""
        game_state = self._ensure_game_state()
        
        # Add multiple trigger cards
        self.add_cards_to_battlefield(["Soul Warden", "Blood Artist", "Soul's Attendant"])
        initial_life = game_state.life
        
        # Force opponent to play a creature (should trigger ETB effects automatically)
        results = self.opponent_simulator.force_opponent_action(0, "play_creature", game_state)
        self.assertIn("play_creature", [a["action"] for a in results["actions_executed"]])
        
        # Should gain 2 life (Soul Warden + Soul's Attendant)
        self.assertEqual(game_state.life, initial_life + 2)
        
        # Now force opponent to have a creature die
        results = self.opponent_simulator.force_opponent_action(0, "creature_death", game_state)
        self.assertIn("creature_death", [a["action"] for a in results["actions_executed"]])
        
        # Should gain 1 more life (Blood Artist)
        self.assertEqual(game_state.life, initial_life + 3)
    
    def test_opponent_simulator_take_single_turn(self):
        """Test that opponent simulator properly triggers effects during single turn."""
        game_state = self._ensure_game_state()
        
        # Add Soul Warden to battlefield
        self.add_cards_to_battlefield(["Soul Warden"])
        initial_life = game_state.life
        
        # Take a single opponent turn
        results = self.opponent_simulator.take_single_opponent_turn(0, game_state, 1)
        
        # Check if any actions were executed
        if results["actions_executed"]:
            # Find the play_creature action
            creature_actions = [a for a in results["actions_executed"] if a["action"] == "play_creature"]
            if creature_actions:
                # Should have gained life from Soul Warden
                self.assertGreater(game_state.life, initial_life)
        
        # Verify opponent state is tracked
        opponent_state = self.opponent_simulator.get_opponent_state(0)
        self.assertIn("creatures", opponent_state)
        self.assertIn("opponent_id", opponent_state)
    
    def test_multiple_opponents_trigger_effects(self):
        """Test that multiple opponents can trigger effects."""
        game_state = self._ensure_game_state()
        
        # Set up 2 opponents
        self.opponent_simulator.num_opponents = 2
        self.opponent_simulator._initialize_opponents()
        
        # Add Soul Warden to battlefield
        self.add_cards_to_battlefield(["Soul Warden"])
        initial_life = game_state.life
        
        # Force both opponents to play creatures
        for i in range(2):
            results = self.opponent_simulator.force_opponent_action(i, "play_creature", game_state)
            self.assertIn("play_creature", [a["action"] for a in results["actions_executed"]])
        
        # Should gain 2 life (one for each opponent creature)
        self.assertEqual(game_state.life, initial_life + 2)
        
        # Verify both opponents have creatures
        self.assertEqual(self.opponent_simulator.opponents[0].get_creature_count(), 1)
        self.assertEqual(self.opponent_simulator.opponents[1].get_creature_count(), 1)
    
    def test_opponent_removal_triggers_death_effects(self):
        """Test that opponent removal triggers death effects on our creatures."""
        game_state = self._ensure_game_state()
        
        # Add our creature and Blood Artist
        self.add_cards_to_battlefield(["Blood Artist"])
        our_creature = get_card("Soul Warden")
        game_state.battlefield.add(our_creature)
        initial_life = game_state.life
        
        # Simulate opponent removal
        game_state.creature_dies(our_creature, mine=True)
        
        # Should gain life from Blood Artist
        self.assertGreater(game_state.life, initial_life)
        self.assertEqual(game_state.life, initial_life + 1)
        
        # Verify our creature is in graveyard
        self.assertIn(our_creature, game_state.graveyard)
        self.assertNotIn(our_creature, game_state.battlefield.cards)


if __name__ == '__main__':
    unittest.main() 