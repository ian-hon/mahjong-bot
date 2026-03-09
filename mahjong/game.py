from .tile import Tile
import random
from enum import Enum

class Game:
    def __init__(self, players):
        self.state = Game.GameState.Ongoing
        
        self.turn = 0
        self.max_turn = len(players)
        self.players: list[str] = players
        # assume player[0] is the first
        
        self.deck = Tile.get_full()
        # i dont know why but with only one shuffle() theres a lot of pairs at the start
        random.shuffle(self.deck)
        random.shuffle(self.deck)
        random.shuffle(self.deck)
        
        self.hands: list[list[Tile]] = [[] for _ in players]
        self.opened: list[list[Tile]] = [[] for _ in players]
        
        self.discard_pile: list[Tile] = []
        
        self.distribute_tiles()
    
        # for h in self.hands:
        #     print(' '.join([t.as_string() for t in h]))
        #     print('\n')
        
        self.update_gamestate() # just in case
        
    def update_gamestate(self):
        if self.get_winner() != None: # incase 0 evals to False
            self.state = Game.GameState.Won
        elif len(self.deck) <= 0:
            self.state = Game.GameState.Stalemate
    
    
    def get_winner(self) -> None | int:
        for index, h in enumerate(self.hands):
            if Tile.is_winning(h):
                return index
        return None
    
    
    def discard(self, player: int, n: int):
        # n is the index of tile to discard
        if (player >= len(self.players)) or (player < 0):
            return
        
        t = self.hands[player].pop(n)
        self.discard_pile.append(t)
    
    
    def chi(self, player: int):
        if self.turn != player:
            return
        hand = self.hands[player]
        
        if not Tile.can_chi(self.discard_pile[-1], hand):
            return
        
        t = self.discard_pile.pop()
        self.hands[player].append(t)
        
        self.update_gamestate()
        
    
    def pong(self, player: int):
        hand = self.hands[player]
        if not Tile.can_pong(self.discard_pile[-1], hand):
            return
        
        t = self.discard_pile.pop()
        self.hands[player].append(t)
        
        self.update_gamestate()
    
    
    def kang(self, player: int):
        hand = self.hands[player]
        if not Tile.can_kang(self.discard_pile[-1], hand):
            return
        
        t = self.discard_pile.pop()
        self.hands[player].append(t)
        
        self.update_gamestate()

    
    def distribute_tiles(self):
        # at start of the game only
        self.hands = [
            [self.take_tile() for _ in range(13)]
            for _ in self.players
        ]
        self.hands[0].append(self.take_tile())
        
        self.hands = [Tile.sort_tiles(h) for h in self.hands]
    
        
    def take_tile(self):
        # removes one tile from deck and returns it
        t = self.deck.pop(0)
        self.discard_pile.append(t)
        return t
    
    class GameState(Enum):
        Ongoing = 0
        Won = 1
        Stalemate = 2
    
    
    