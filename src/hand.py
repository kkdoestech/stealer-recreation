"""src/hand.py - Milestone 1: Card & Preflop Hand Representation.

This module provides:
    - Rank, Suit enums
    - Card dataclass (frozen)
    - HandCategory enum (PAIR, SUITED, OFFSUIT)
    - classify_hand(card1, card2) -> canonical hand string
    - generate_all_169_hands() -> list of all canonical preflop hand strings
"""

from enum import Enum
from dataclasses import dataclass
from typing import List


class Rank(Enum):
    """Card ranks from TWO (2) to ACE (14)."""
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

    @property
    def short(self) -> str:
        """One‑character representation: 'A', 'K', ..., '2'."""
        return {
            2: '2', 3: '3', 4: '4', 5: '5', 6: '6',
            7: '7', 8: '8', 9: '9', 10: 'T',
            11: 'J', 12: 'Q', 13: 'K', 14: 'A'
        }[self.value]


class Suit(Enum):
    """The four card suits."""
    SPADES = 1
    HEARTS = 2
    DIAMONDS = 3
    CLUBS = 4

    @property
    def short(self) -> str:
        """One‑character representation: 's', 'h', 'd', 'c'."""
        return {
            Suit.SPADES: 's',
            Suit.HEARTS: 'h',
            Suit.DIAMONDS: 'd',
            Suit.CLUBS: 'c',
        }[self]


@dataclass(frozen=True)
class Card:
    """An immutable card with a rank and a suit."""
    rank: Rank
    suit: Suit

    def __str__(self) -> str:
        return f"{self.rank.short}{self.suit.short}"


class HandCategory(Enum):
    """Preflop hand category."""
    PAIR = 1
    SUITED = 2
    OFFSUIT = 3

    @property
    def suffix(self) -> str:
        """Notation suffix: '' for pairs, 's' for suited, 'o' for offsuit."""
        return {
            HandCategory.PAIR: '',
            HandCategory.SUITED: 's',
            HandCategory.OFFSUIT: 'o',
        }[self]


def classify_hand(card1: Card, card2: Card) -> str:
    """Return the canonical string for two cards.

    Raises ValueError if the same card object is passed twice.
    """
    if card1 is card2:
        raise ValueError("Cannot classify a card with itself.")

    # Determine rank order (higher first)
    if card1.rank.value > card2.rank.value:
        high, low = card1.rank, card2.rank
    else:
        high, low = card2.rank, card1.rank

    # Determine category
    if high == low:
        category = HandCategory.PAIR
    elif card1.suit == card2.suit:
        category = HandCategory.SUITED
    else:
        category = HandCategory.OFFSUIT

    return f"{high.short}{low.short}{category.suffix}"


def generate_all_169_hands() -> List[str]:
    """Return a list of all 169 canonical preflop hand strings."""
    ranks = list(Rank)
    hands = set()

    # Pair hands: AA ... 22
    for r in ranks:
        hands.add(f"{r.short}{r.short}")

    # Suited & Offsuit for every unordered pair of distinct ranks
    for i, r1 in enumerate(ranks):
        for r2 in ranks[i+1:]:  # only unique pairs (r1 > r2 in value)
            high, low = (r1, r2) if r1.value > r2.value else (r2, r1)
            suited = f"{high.short}{low.short}s"
            offsuit = f"{high.short}{low.short}o"
            hands.add(suited)
            hands.add(offsuit)

    # The set is unordered; we return a sorted list for determinism.
    # The test only cares about content, not order.
    return sorted(hands)