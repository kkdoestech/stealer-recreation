Poker (NLHE):
    Before the flop, when you face an opponent’s “steal” raise, which starting hands are profitable to re‑raise (3‑bet)?

In poker, “stealing” means that a player in a late position (like the Button or Small Blind) raises to win the blinds and antes after everyone else has folded. A “3‑bet” is a re‑raise against that initial raise. This tool calculates, using mathematics, a list of hands that you can 3‑bet with and still make money in the long run. That list is your optimal 3‑bet steal range.



A simple real‑world analogy

Imagine you are a street vendor, and your “hands” are the items you sell. A customer (your opponent) tries to buy your cheapest trinkets (the blinds) at a very low price (the steal raise).

    You must decide: Which items should I counter‑offer with (3‑bet) so that I don’t lose money, and ideally make a profit?

    You can’t use your worst items, because if the customer accepts, you lose money (–EV).

    You also can’t use only your best items, because you’d miss too many opportunities.

This project is like a smart calculator: you tell it the customer’s offer (raise size), your budget (stack depth), and other details, and it computes a list showing which items (starting hands) are profitable to counter‑offer with over many repetitions.










=============================================================================================



1. Expected Value (EV) in Poker
    Imagine you're playing a game where you can bet $1 on a coin flip.
    If it lands heads, you win $2, if tails you lose your $1.
        -> Expected value is the average value -> you'll win (or lose) per bet if you repeat the
        same situation many times.

        Let's calculate:
            + Probability of heads = 1/2 -> you win $2
            + Probability of tails = 1/2 -> you lose your $1

            EV = (1/2 * $2) + (1/2 * -$1) = +$0.5
                -> that means on average you make 50 cent profit every time you take the bet.
                  -> that's positive EV play -> you can do it.

            In Poker -> EV is the same idea:
                EV = (chance you win) * (amount you win) - (chance you lose) * (amount you lose)

        
        But Poker is more complex because there are multiple opponents, different bet sizes, and you might not see all cards.
            -> We'll build a simplified model where we pre-compute the equity (win probability) of every possible 2-card hand against
            a random opponent hand.
                -> then, given a bet size and pot size -> we can calculate the EV of making a certain play (like raising or folding).
                    -> Milestone 4 will handle that math.

        -> For now we're just building the foundation: representing cards and hands.


2. How did the Senior Developers Represent Cards and Hands?
    The original code (in the /src folder of the (stealer) project) had:
        + hand.py (545 lines) -> a massive file that handled everything:
            + Card representation (rank and suit)
            + Hand ranking (eg: straight, flush, etc.)
            + Pre-flop equity calculations (win rates for all 169 possible starting hands).

        + ranking.py -> a tiny file that probably just imported enums or helpers.
        + hand_eval.py -> likely evaluated a full 5-card or 7-card hand -> to determine its rank (eg: pair, 2 pair, etc).
        + hands/ ->  a directory full of JSON file, one for each starting hand (like AA.json, AKs.json).
            -> each file contained a 2D array of win probabilities against other hands.


    What data structures did they use?
        + Dictionaries (hash maps) -> to map hand names -> to their equity values.
        + Nested lists (2D arrays) -> inside the JSON equity files -> to store win-rates for every possible opponent hand.

            + Pros of their approach:
                + Simple and fast - dictionaries give 0(1) lookup for equity
                + Precomputation - all equity numbers are pre-calculated -> so actual poker bot runs very quickly.
                + Human-readable - hand names like "AKs" are easy to understand.

            + Cons:
                + Hard-coded strings: if you mistype a hand name -> KeyError.
                + No explicit card objects: used integers or strings to represent individual cards -> less safe and less expressive.
                + Monolithic - everything was crammed into 1 huge file -> making it hard to test.


3. Our Workspace Structure for Milestone 1 (in ./recreation)
    -> We're building a clean, modular, test-driven version.
        ->
        recreation/
        |-- pyproject.toml   # Configure for pytest (tells it where it find code)
        |-- src/
        |   |-- __init__.py  # makes python treat src/ -> as a package
        |   |-- hand.py      # Our card and hand representation (Milestone 1)
        |-- test/
            |-- __init__.py  # make tests/ a package
            |-- test_hand.py # 30 quality-gate tests for Milestone 1



Suits vs. Ranks: Every card has a rank (13 possibilities) and a suit (4 possibilities: Clubs, Diamonds, Hearts, Spades), producing a full deck of $13 \times 4 = 52$ unique cards.


Dual Value of Ace: While Ace is officially the highest rank (13 or 14 depending on indexing), it can also act as the lowest rank (1) to complete a 5-high straight (A-2-3-4-5, known as the wheel).
4. Understand the Quality-Gate Tests (the "Contract")
    -> Your contract - what the code must do.

    Section 1: (Rank) Enum
        + (test_rank_has_13_members) - we need exactly 13 ranks (2 through Ace) 
            