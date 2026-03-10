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
        
        # self.hands: list[list[Tile]] = [[] for _ in players]
        # self.opened: list[list[Tile]] = [[] for _ in players]
        self.hands: dict[str, list[Tile]] = {p:[] for p in players}
        self.opened: dict[str, list[list[Tile]]] = {p:[] for p in players}
        
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
    
    
    def chi(self, player: str, pattern: list[int] | None):
        # TODO: implement
        # if the player has 23_, 3_5, 3_5, _56 and chi a 4,
        # we use pattern to determine which pattern they actually want to 'chi'
        # pattern = [2, 3] -> 23_
        # pattern = [3, 5] -> 3_5
        if (pattern != None) and (len(pattern) != 2):
            return
        
        hand = self.hands[player]
        
        # chi_able, chi_patterns = Tile.can_chi(self.discard_pile[-1], hand)
        # if not chi_able:
        #     return
        
        chi_patterns = Tile.available_chi_patterns(self.discard_pile[-1], hand)
        if not chi_patterns:
            return
        
        # freq = Tile.get_tile_freq(self.discard_pile[-1].suit, self.hands[player])
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
        
        # print('before (chi)')
        # print(f'hand: {[Tile.as_string(i) for i in self.hands[player]]}')
        # print(f'opened: {[''.join([Tile.as_string(n) for n in i]) for i in self.opened[player]]}')
        t = self.discard_pile.pop()
        # take the tiles from pattern and add to opened
        result = []
        indices = []
        for item in targeted_pattern:
            # print(f'\titem: {item}')
            for index, tile in enumerate([i for i in self.hands[player]]):
                # print(f'\t\t{index}: {Tile.as_string(tile)} ({tile.suit}, {tile.value}, {item}, {t.suit})')
                if (tile.suit == t.suit) and (tile.value == item):
                    # result.append(tile)
                    # discarded_tile = self.hands[player].pop(index - len(result))
                    # self.hands[player] = [i for i_index, i in enumerate(self.hands[player]) if i_index != (index + len(result))]
                    result.append(tile)
                    indices.append(index)
                    # result.append(discarded_tile)
                    break
        result.append(t)
        self.hands[player] = [i for i_index, i in enumerate(self.hands[player]) if i_index not in indices]
        
        # print(f'pattern: {chi_patterns}')
        # print(f't: {Tile.as_string(t)} {t.value}')
        # print(f'accrued result: {[Tile.as_string(i) for i in result]}')
        self.opened[player] += [result]
        # print('after')
        # print(f'hand: {[Tile.as_string(i) for i in self.hands[player]]}')
        # print(f'opened: {[''.join([Tile.as_string(n) for n in i]) for i in self.opened[player]]}')
        
        self.update_gamestate()
        
        exit()
        
    
    def pong(self, player: str):
        hand = self.hands[player]
        if not Tile.can_pong(self.discard_pile[-1], hand):
            return
        
        t = self.discard_pile.pop()
        self.hands[player].append(t)
        
        print('before (pong)')
        print([Tile.as_string(i) for i in self.hands[player]])
        print([''.join([Tile.as_string(n) for n in i]) for i in self.opened[player]])
        # Tile.can_pong only allows 3 in hand (2 before appending)
        # thus, dont need to worry about appending 4 * tile into the opened dict
        self.opened[player] += [[i for i in self.hands[player] if i == t]]
        self.hands[player] = [i for i in self.hands[player] if i != t]
        print('after')
        print([Tile.as_string(i) for i in self.hands[player]])
        print([''.join([Tile.as_string(n) for n in i]) for i in self.opened[player]])
        
        self.update_gamestate()
    
    
    def kang(self, player: str):
        hand = self.hands[player]
        if not Tile.can_kang(self.discard_pile[-1], hand):
            return
        
        t = self.discard_pile.pop()
        self.hands[player].append(t)
        print('before (kang)')
        print([Tile.as_string(i) for i in self.hands[player]])
        print([''.join([Tile.as_string(n) for n in i]) for i in self.opened[player]])
        # self.opened[player].append([t] * 4)
        self.opened[player] += [[i for i in self.hands[player] if i == t]]
        self.hands[player] = [i for i in self.hands[player] if i != t]
        print('after')
        print([Tile.as_string(i) for i in self.hands[player]])
        print([''.join([Tile.as_string(n) for n in i]) for i in self.opened[player]])
        
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
    
    
    