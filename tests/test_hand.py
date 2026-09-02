"""
Quality Gate Tests for Milestone 1: Card & Preflop Hand Representation
======================================================================

These tests define the CONTRACT that our src/hand.py module must fulfill.
We write tests FIRST (TDD) — the implementation does not exist yet, so
running `pytest` right now should give us ImportErrors or failures.

Once we implement src/hand.py and ALL tests pass, Milestone 1 is complete.

DSA concepts tested:
    - Enum       → Rank (13 values), Suit (4 values), HandCategory (3 values)
    - Dataclass  → Card (frozen record of Rank + Suit)
    - List       → 169 distinct preflop hand categories
    - Hash Map   → classify(card1, card2) → canonical hand string
"""

import pytest

# ---------------------------------------------------------------------------
# We import from src.hand — this module doesn't exist yet!
# When you run `pytest` now, every test will fail with ImportError.
# That's the point: the tests define what we NEED to build.
# ---------------------------------------------------------------------------
from src.hand import (
    Rank,
    Suit,
    Card,
    HandCategory,
    classify_hand,
    generate_all_169_hands,
)


# ===================================================================
# SECTION 1: Rank Enum
# ===================================================================
# Rank represents card ranks 2 through Ace.
# Internally each rank stores an integer value so we can compare/sort.
#   2=2, 3=3, ..., 10=10, Jack=11, Queen=12, King=13, Ace=14
#
# DSA note: An Enum is essentially a FIXED ARRAY of named constants.
#   - Lookup by name:  Rank["ACE"]  → O(1) via internal hash map
#   - Lookup by value: Rank(14)     → O(1) via internal hash map
#   - Total members:   13 (constant)
# ===================================================================

class TestRank:
    """Tests for the Rank enum — 13 members from TWO(2) to ACE(14)."""

    def test_rank_has_13_members(self):
        """There are exactly 13 ranks in a standard deck."""
        assert len(Rank) == 13

    def test_lowest_rank_is_two(self):
        """The lowest rank is TWO with integer value 2."""
        assert Rank.TWO.value == 2

    def test_highest_rank_is_ace(self):
        """The highest rank is ACE with integer value 14."""
        assert Rank.ACE.value == 14

    def test_face_card_values(self):
        """Jack=11, Queen=12, King=13 — standard poker ordering."""
        assert Rank.JACK.value == 11
        assert Rank.QUEEN.value == 12
        assert Rank.KING.value == 13

    def test_ranks_are_ordered(self):
        """Ranks can be compared: TWO < THREE < ... < ACE.

        This is essential later when we sort hands by strength.
        Comparison uses the integer .value under the hood.
        """
        assert Rank.TWO.value < Rank.THREE.value
        assert Rank.TEN.value < Rank.JACK.value
        assert Rank.KING.value < Rank.ACE.value

    def test_rank_short_name(self):
        """Each Rank must have a .short property returning its 1-char label.

        We need this for display: 'A' not 'ACE', 'T' not 'TEN', etc.
        These short names are used to build canonical hand strings like 'AKs'.
        """
        assert Rank.ACE.short == "A"
        assert Rank.KING.short == "K"
        assert Rank.QUEEN.short == "Q"
        assert Rank.JACK.short == "J"
        assert Rank.TEN.short == "T"
        assert Rank.NINE.short == "9"
        assert Rank.TWO.short == "2"


# ===================================================================
# SECTION 2: Suit Enum
# ===================================================================
# Suit represents the 4 card suits.
# We don't need ordering for suits (poker suits are equal in Texas
# Hold'em), but we need them to distinguish cards in a deck.
#
# DSA note: Another small fixed Enum — 4 members, O(1) everything.
# ===================================================================

class TestSuit:
    """Tests for the Suit enum — 4 members."""

    def test_suit_has_4_members(self):
        """Standard deck has exactly 4 suits."""
        assert len(Suit) == 4

    def test_suit_members_exist(self):
        """All four suits must be defined."""
        suits = {s.name for s in Suit}
        assert suits == {"SPADES", "HEARTS", "DIAMONDS", "CLUBS"}

    def test_suit_short_name(self):
        """Each Suit must have a .short property: s, h, d, c."""
        assert Suit.SPADES.short == "s"
        assert Suit.HEARTS.short == "h"
        assert Suit.DIAMONDS.short == "d"
        assert Suit.CLUBS.short == "c"


# ===================================================================
# SECTION 3: Card Dataclass
# ===================================================================
# A Card is a frozen (immutable) record: Card(rank=Rank.ACE, suit=Suit.SPADES)
#
# DSA note: A dataclass is a STRUCT/RECORD — a fixed-size container
#   for a known set of fields. "frozen" means immutable, which lets
#   Python hash it (so we can put Cards in sets and use them as dict keys).
#   - Create:  O(1)
#   - Compare: O(1)  (field-by-field)
#   - Hash:    O(1)
# ===================================================================

class TestCard:
    """Tests for the Card dataclass — a (Rank, Suit) pair."""

    def test_card_creation(self):
        """We can create a Card with a rank and a suit."""
        card = Card(rank=Rank.ACE, suit=Suit.SPADES)
        assert card.rank == Rank.ACE
        assert card.suit == Suit.SPADES

    def test_card_is_immutable(self):
        """Cards are frozen dataclasses — you cannot change their fields.

        Immutability matters because we'll use Cards as dictionary keys
        and set members. Mutable objects can't be hashed safely.
        """
        card = Card(rank=Rank.ACE, suit=Suit.SPADES)
        with pytest.raises(AttributeError):
            card.rank = Rank.KING  # type: ignore[misc]

    def test_card_equality(self):
        """Two Cards with the same rank and suit are equal.

        Python dataclasses auto-generate __eq__ based on fields.
        """
        card_a = Card(rank=Rank.ACE, suit=Suit.SPADES)
        card_b = Card(rank=Rank.ACE, suit=Suit.SPADES)
        assert card_a == card_b

    def test_card_inequality(self):
        """Cards with different rank OR suit are not equal."""
        ace_spades = Card(rank=Rank.ACE, suit=Suit.SPADES)
        ace_hearts = Card(rank=Rank.ACE, suit=Suit.HEARTS)
        king_spades = Card(rank=Rank.KING, suit=Suit.SPADES)
        assert ace_spades != ace_hearts
        assert ace_spades != king_spades

    def test_card_is_hashable(self):
        """Frozen dataclasses are hashable — we can store Cards in a set.

        This is critical for O(1) membership checks later when we
        track which cards are already dealt.
        """
        card = Card(rank=Rank.ACE, suit=Suit.SPADES)
        card_set = {card}
        assert card in card_set

    def test_card_str_representation(self):
        """Card should have a readable string like 'As' (Ace of spades).

        Combines Rank.short + Suit.short → 'As', 'Kh', '2d', etc.
        """
        card = Card(rank=Rank.ACE, suit=Suit.SPADES)
        assert str(card) == "As"

        card2 = Card(rank=Rank.TEN, suit=Suit.HEARTS)
        assert str(card2) == "Th"

    def test_full_deck_has_52_cards(self):
        """A full deck is every (Rank, Suit) combination = 13 × 4 = 52.

        DSA note: This is the Cartesian product of two sets.
        Time to generate: O(13 × 4) = O(52) = O(1) since it's constant.
        """
        deck = [Card(rank=r, suit=s) for r in Rank for s in Suit]
        assert len(deck) == 52
        # All cards should be unique
        assert len(set(deck)) == 52


# ===================================================================
# SECTION 4: HandCategory Enum
# ===================================================================
# In Texas Hold'em, a preflop hand is two cards. We categorize them:
#   - PAIR:    same rank, e.g. AA, KK, 77       → 13 categories
#   - SUITED:  different rank, same suit, e.g. AKs → 78 categories
#   - OFFSUIT: different rank, different suit, e.g. AKo → 78 categories
#                                         Total: 169 categories
#
# Why 78? Choose(13,2) = 13! / (2! × 11!) = 78
# ===================================================================

class TestHandCategory:
    """Tests for the HandCategory enum — PAIR, SUITED, OFFSUIT."""

    def test_has_three_categories(self):
        """There are exactly 3 preflop hand categories."""
        assert len(HandCategory) == 3

    def test_category_names(self):
        """The categories are PAIR, SUITED, and OFFSUIT."""
        names = {c.name for c in HandCategory}
        assert names == {"PAIR", "SUITED", "OFFSUIT"}

    def test_category_suffixes(self):
        """Each category has a .suffix used in notation: '', 's', 'o'.

        Pairs have no suffix (e.g., 'AA' not 'AAp').
        Suited hands get 's' (e.g., 'AKs').
        Offsuit hands get 'o' (e.g., 'AKo').
        """
        assert HandCategory.PAIR.suffix == ""
        assert HandCategory.SUITED.suffix == "s"
        assert HandCategory.OFFSUIT.suffix == "o"


# ===================================================================
# SECTION 5: classify_hand() function
# ===================================================================
# Given two Card objects, classify_hand returns a CANONICAL hand string.
#
# "Canonical" means the higher rank always comes first:
#   Card(K♠), Card(A♥) → "AKo"  (not "KAo")
#   Card(7♦), Card(7♠) → "77"   (not "77o" — pairs have no suit suffix)
#
# DSA note: This function does O(1) work — compare two Rank values,
# check if Suits match, build a short string. No loops, no searching.
# ===================================================================

class TestClassifyHand:
    """Tests for classify_hand(card1, card2) → canonical hand string."""

    def test_pair(self):
        """Two cards of the same rank → a pair, e.g., 'AA'."""
        c1 = Card(rank=Rank.ACE, suit=Suit.SPADES)
        c2 = Card(rank=Rank.ACE, suit=Suit.HEARTS)
        assert classify_hand(c1, c2) == "AA"

    def test_suited(self):
        """Different rank, same suit → suited hand, e.g., 'AKs'."""
        c1 = Card(rank=Rank.ACE, suit=Suit.SPADES)
        c2 = Card(rank=Rank.KING, suit=Suit.SPADES)
        assert classify_hand(c1, c2) == "AKs"

    def test_offsuit(self):
        """Different rank, different suit → offsuit hand, e.g., 'AKo'."""
        c1 = Card(rank=Rank.ACE, suit=Suit.SPADES)
        c2 = Card(rank=Rank.KING, suit=Suit.HEARTS)
        assert classify_hand(c1, c2) == "AKo"

    def test_canonical_order_higher_rank_first(self):
        """The higher-ranked card always comes first in the string.

        If we pass (King, Ace), the result is still 'AKo' not 'KAo'.
        This ensures every hand has ONE canonical representation.
        """
        c1 = Card(rank=Rank.KING, suit=Suit.HEARTS)
        c2 = Card(rank=Rank.ACE, suit=Suit.SPADES)
        assert classify_hand(c1, c2) == "AKo"

    def test_low_pair(self):
        """Lowest pair: '22'."""
        c1 = Card(rank=Rank.TWO, suit=Suit.DIAMONDS)
        c2 = Card(rank=Rank.TWO, suit=Suit.CLUBS)
        assert classify_hand(c1, c2) == "22"

    def test_low_suited(self):
        """Low suited connector: '32s'."""
        c1 = Card(rank=Rank.TWO, suit=Suit.CLUBS)
        c2 = Card(rank=Rank.THREE, suit=Suit.CLUBS)
        assert classify_hand(c1, c2) == "32s"

    def test_same_card_raises_error(self):
        """Passing the exact same card twice is physically impossible.

        Our function should raise a ValueError to catch bugs early.
        """
        c1 = Card(rank=Rank.ACE, suit=Suit.SPADES)
        with pytest.raises(ValueError):
            classify_hand(c1, c1)


# ===================================================================
# SECTION 6: generate_all_169_hands()
# ===================================================================
# This function returns a list of all 169 canonical preflop hands.
#
# Breakdown:
#   - 13 pairs:   AA, KK, QQ, ..., 22
#   - 78 suited:  AKs, AQs, ..., 32s   (C(13,2) = 78)
#   - 78 offsuit: AKo, AQo, ..., 32o   (C(13,2) = 78)
#   Total: 13 + 78 + 78 = 169
#
# DSA note:
#   Time:  O(13²) = O(169) to iterate all rank pairs — constant.
#   Space: O(169) to store the result list — constant.
#   We use a nested loop: for each rank_i, for each rank_j >= rank_i.
# ===================================================================

class TestGenerate169Hands:
    """Tests for generate_all_169_hands() → list of canonical hand strings."""

    def test_returns_169_hands(self):
        """There are exactly 169 distinct preflop hand categories."""
        hands = generate_all_169_hands()
        assert len(hands) == 169

    def test_no_duplicates(self):
        """All 169 hands must be unique — no repeated strings.

        We verify by converting to a set (hash set, O(n) insert)
        and checking the size is unchanged.
        """
        hands = generate_all_169_hands()
        assert len(set(hands)) == 169

    def test_contains_all_pairs(self):
        """Must include all 13 pairs: AA, KK, QQ, ..., 22."""
        hands = set(generate_all_169_hands())
        expected_pairs = {"AA", "KK", "QQ", "JJ", "TT",
                          "99", "88", "77", "66", "55",
                          "44", "33", "22"}
        assert expected_pairs.issubset(hands)

    def test_pair_count_is_13(self):
        """Exactly 13 of the 169 hands are pairs (no suffix)."""
        hands = generate_all_169_hands()
        pairs = [h for h in hands if len(h) == 2]
        assert len(pairs) == 13

    def test_suited_count_is_78(self):
        """Exactly 78 hands are suited (end with 's')."""
        hands = generate_all_169_hands()
        suited = [h for h in hands if h.endswith("s")]
        assert len(suited) == 78

    def test_offsuit_count_is_78(self):
        """Exactly 78 hands are offsuit (end with 'o')."""
        hands = generate_all_169_hands()
        offsuit = [h for h in hands if h.endswith("o")]
        assert len(offsuit) == 78

    def test_contains_specific_suited_hand(self):
        """Spot-check: 'AKs' (best suited hand) must be in the list."""
        hands = set(generate_all_169_hands())
        assert "AKs" in hands

    def test_contains_specific_offsuit_hand(self):
        """Spot-check: '72o' (the notorious worst hand) must be in the list."""
        hands = set(generate_all_169_hands())
        assert "72o" in hands

    def test_hands_are_strings(self):
        """Every element in the returned list is a string."""
        hands = generate_all_169_hands()
        assert all(isinstance(h, str) for h in hands)

