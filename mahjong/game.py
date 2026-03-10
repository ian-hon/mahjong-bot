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
        
        self.hands: dict[str, list[Tile]] = {p:[] for p in players}
        self.opened: dict[str, list[list[Tile]]] = {p:[] for p in players}
        
        self.discard_pile: list[Tile] = []
        
        self.distribute_tiles()
        
        self.update_gamestate() # just in case
        
    def update_gamestate(self):
        if self.get_winner() != None: # incase 0 evals to False
            self.state = Game.GameState.Won
        elif len(self.deck) <= 0:
            self.state = Game.GameState.Stalemate
    
    
    def get_winner(self) -> None | str:
        for k, h in self.hands.items():
            if Tile.is_winning(h):
                return k
        return None
    
    
    def discard(self, player: str, n: int):
        # n is the index of tile to discard
        # if (player >= len(self.players)) or (player < 0):
        #     return
        if not (player in self.hands):
            return
        
        t = self.hands[player].pop(n)
        self.discard_pile.append(t)
        
    
    def player_can_chi(self, player: str):
        return Tile.can_chi(self.discard_pile[-1], self.hands[player])
    
    
    def player_can_pong(self, player: str):
        return Tile.can_pong(self.discard_pile[-1], self.hands[player])
    
    
    def player_can_kang(self, player: str):
        return Tile.can_kang(self.discard_pile[-1], self.hands[player])
    
    
    def chi(self, player: str, pattern: list[int] | None):
        # TODO: implement
        # if the player has 23_, 3_5, 3_5, _56 and chi a 4,
        # we use pattern to determine which pattern they actually want to 'chi'
        # pattern = [2, 3] -> 23_
        # pattern = [3, 5] -> 3_5
        if (pattern != None) and (len(pattern) != 2):
            return
        
        hand = self.hands[player]
        
        chi_patterns = Tile.available_chi_patterns(self.discard_pile[-1], hand)
        if not chi_patterns:
            return
        
        targeted_pattern = None
        if len(chi_patterns) == 1:
            targeted_pattern = chi_patterns[0]
        elif pattern != None:            
            pattern.sort()
            if not (pattern in chi_patterns):
                return
            targeted_pattern = pattern
        
        if targeted_pattern == None:
            return
        
        t = self.discard_pile.pop()
        # take the tiles from pattern and add to opened
        result = []
        indices = []
        for item in targeted_pattern:
            for index, tile in enumerate([i for i in self.hands[player]]):
                if (tile.suit == t.suit) and (tile.value == item):
                    result.append(tile)
                    indices.append(index)
                    break
        result.append(t)
        self.hands[player] = [i for i_index, i in enumerate(self.hands[player]) if i_index not in indices]
        self.opened[player] += [result]
        
        self.update_gamestate()
        
    
    def pong(self, player: str):
        hand = self.hands[player]
        if not Tile.can_pong(self.discard_pile[-1], hand):
            return
        
        t = self.discard_pile.pop()
        self.hands[player].append(t)
        
        # Tile.can_pong only allows 3 in hand (2 before appending)
        # thus, dont need to worry about appending 4 * tile into the opened dict
        self.opened[player] += [[i for i in self.hands[player] if (i.suit == t.suit) and (i.value == t.value)]]
        self.hands[player] = [i for i in self.hands[player] if (i.suit != t.suit) or (i.value != t.value)]
        
        self.update_gamestate()
    
    
    def kang(self, player: str):
        hand = self.hands[player]
        if not Tile.can_kang(self.discard_pile[-1], hand):
            return
        
        t = self.discard_pile.pop()
        self.hands[player].append(t)
        self.opened[player] += [[i for i in self.hands[player] if (i.suit == t.suit) and (i.value == t.value)]]
        self.hands[player] = [i for i in self.hands[player] if (i.suit != t.suit) or (i.value != t.value)]
        
        self.update_gamestate()

    
    def distribute_tiles(self):
        # at start of the game only
        self.hands = {
            p:[self.take_tile() for _ in range(13)]
            for p in self.players
        }
        self.hands[self.players[0]].append(self.take_tile())
        
        self.sort_hands()
    
    
    def sort_hands(self):
        self.hands = {k:Tile.sort_tiles(v) for k, v in self.hands.items()}
    
        
    def take_tile(self):
        # removes one tile from deck and returns it
        t = self.deck.pop(0)
        self.discard_pile.append(t)
        return t
    
    class GameState(Enum):
        Ongoing = 0
        Won = 1
        Stalemate = 2
    
    
    