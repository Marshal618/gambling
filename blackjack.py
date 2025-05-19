

import random, itertools, time, sys


SUITS  = ["♠", "♥", "♦", "♣"]
RANKS  = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
SCORES = {**{str(n): n for n in range(2,11)},
          **{f: 10 for f in ("J","Q","K")},
          "A": 11}

class Card:
    __slots__ = ("rank","suit")
    def __init__(self, rank:str, suit:str):
        self.rank, self.suit = rank, suit
    @property
    def value(self): return SCORES[self.rank]
    def __str__(self): return f"{self.rank}{self.suit}"
    __repr__ = __str__

class Deck:
    def __init__(self): self.cards=[Card(r,s) for s,r in itertools.product(SUITS,RANKS)]; self.shuffle()
    def shuffle(self): random.shuffle(self.cards)
    def draw(self): return self.cards.pop() if self.cards else RuntimeError("Empty deck")
    def remaining(self): return len(self.cards)


_CARD_HIDDEN = [
    "┌─────────┐",
    "│░░░░░░░░░│",
    "│░░░░░░░░░│",
    "│░░░░░░░░░│",
    "│░░░░░░░░░│",
    "│░░░░░░░░░│",
    "└─────────┘",
]
def _card_lines(card:Card):
    rank,suit = card.rank, card.suit
    top  = rank.ljust(2) if rank!="10" else "10"
    bot  = rank.rjust(2) if rank!="10" else "10"
    return [
        "┌─────────┐",
        f"│{top}       │",
        "│         │",
        f"│    {suit}    │",
        "│         │",
        f"│       {bot}│",
        "└─────────┘",
    ]

def join_ascii(cards, hide_first=False):
    rows=[]
    for i,c in enumerate(cards):
        rows.append(_CARD_HIDDEN if hide_first and i==0 else _card_lines(c))
    # transpose rows -> joined string
    return "\n".join(" ".join(col) for col in zip(*rows))


class Hand:
    def __init__(self): self.cards=[]
    def add(self,card): self.cards.append(card)
    def clear(self): self.cards.clear()
    def score(self):
        total=sum(c.value for c in self.cards); aces=sum(c.rank=="A" for c in self.cards)
        while total>21 and aces: total-=10; aces-=1
        return total
    def is_blackjack(self): return len(self.cards)==2 and self.score()==21
    def is_bust(self): return self.score()>21
    # >>> new ascii method
    def ascii(self, hide_first=False): return join_ascii(self.cards, hide_first)
    def __str__(self): return " ".join(map(str,self.cards))+f"  (={self.score()})"

class Player:
    def __init__(self,name): self.name=name; self.hand=Hand()
    def reset_hand(self): self.hand.clear()

class Dealer(Player):
    def __init__(self): super().__init__("Dealer")
    def play(self,deck):
        while self.hand.score()<17:
            time.sleep(1)
            self.hand.add(deck.draw())


class BlackjackGame:
    def __init__(self):
        self.deck=Deck(); self.player=Player("You"); self.dealer=Dealer()
    def _deal_new_round(self):
        if self.deck.remaining()<15: print("\n>>> Reshuffling <<<\n"); self.deck=Deck()
        self.player.reset_hand(); self.dealer.reset_hand()
        for _ in range(2): self.player.hand.add(self.deck.draw()); self.dealer.hand.add(self.deck.draw())

    def _player_turn(self):
        while True:
            print("\nYour hand:\n"+self.player.hand.ascii())               # <<< show ASCII
            if self.player.hand.is_blackjack(): print("Blackjack!"); return
            if self.player.hand.is_bust():     print("Bust!"); return
            move=input("Hit or stand? (h/s) > ").strip().lower()
            if move=="h": self.player.hand.add(self.deck.draw())
            elif move=="s": return
            else: print("Please enter h or s.")

    def _dealer_turn(self):
        print("\nDealer reveals:\n"+self.dealer.hand.ascii())              # full hand
        self.dealer.play(self.deck)
        print("Dealer stands with:\n"+self.dealer.hand.ascii())

    def _settle(self):
        p,d=self.player.hand.score(),self.dealer.hand.score()
        if self.player.hand.is_bust():                outcome="Dealer wins – you bust."
        elif self.dealer.hand.is_bust():              outcome="You win – dealer busts!"
        elif self.player.hand.is_blackjack() and not self.dealer.hand.is_blackjack():
                                                     outcome="You win with a Blackjack!"
        elif self.dealer.hand.is_blackjack() and not self.player.hand.is_blackjack():
                                                     outcome="Dealer wins with a Blackjack."
        elif p>d: outcome="You win!"
        elif d>p: outcome="Dealer wins."
        else:    outcome="Push – tie."
        print(f"\nFinal: You {p} vs Dealer {d} → {outcome}\n")

    def play_round(self):
        self._deal_new_round()
        print("Dealer shows:\n"+self.dealer.hand.ascii(hide_first=True))   # hole card hidden
        self._player_turn()
        if not self.player.hand.is_bust(): self._dealer_turn()
        self._settle()

    def loop(self):
        print("\n=== ASCII Blackjack ===")
        while True:
            self.play_round()
            if input("Play again? (y/n) > ").lower()!="y": break


if __name__=="__main__":
    try: BlackjackGame().loop()
    except KeyboardInterrupt: print("\nBye!"); sys.exit(0)
