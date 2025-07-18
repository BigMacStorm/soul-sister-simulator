from .card import Card
from typing import List

class Battlefield:
    def __init__(self):
        self.cards: List[Card] = []

    def add(self, card: Card):
        self.cards.append(card)

    def add_many(self, cards: List[Card]):
        self.cards.extend(cards)

    def remove(self, card: Card):
        self.cards.remove(card)

    def get_by_name(self, name: str) -> List[Card]:
        return [card for card in self.cards if card.name == name]

    def get_by_type(self, card_type: str) -> List[Card]:
        return [card for card in self.cards if card.card_type == card_type]

    def __len__(self):
        return len(self.cards)

    def __str__(self):
        return f"Battlefield({len(self.cards)} cards: {[card.name for card in self.cards]})"

    def __repr__(self):
        return f"Battlefield(cards={self.cards!r})" 