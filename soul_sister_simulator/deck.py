from .card import Card
import random
from typing import List

class Deck:
    def __init__(self, cards: List[Card]):
        self.original_cards = list(cards)
        self.cards = list(cards)

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, n=1):
        drawn = self.cards[:n]
        self.cards = self.cards[n:]
        return drawn

    def reset(self):
        self.cards = list(self.original_cards)

    def __len__(self):
        return len(self.cards)

    def __str__(self):
        return f"Deck({len(self.cards)} cards remaining)"

    def __repr__(self):
        return f"Deck(cards={self.cards!r})" 