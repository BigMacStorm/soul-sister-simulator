from .card import Card
from typing import List

class Hand:
    def __init__(self):
        self.cards: List[Card] = []

    def add(self, card: Card):
        self.cards.append(card)

    def add_many(self, cards: List[Card]):
        self.cards.extend(cards)

    def remove(self, card: Card):
        self.cards.remove(card)

    def show(self):
        return [str(card) for card in self.cards]

    def __len__(self):
        return len(self.cards)

    def __str__(self):
        return f"Hand({len(self.cards)} cards: {[card.name for card in self.cards]})"

    def __repr__(self):
        return f"Hand(cards={self.cards!r})" 