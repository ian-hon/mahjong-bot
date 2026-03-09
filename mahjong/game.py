from .tile import Tile
import random

class Game:
    def __init__(self, players):
        self.turn = 0
        self.max_turn = len(players)
        self.players = players
        # assume player[0] is the first
        
        self.deck = Tile.get_full()
        # i dont know why but with only one shuffle() theres a lot of pairs at the start
        random.shuffle(self.deck)
        random.shuffle(self.deck)
        random.shuffle(self.deck)
        self.hands:list[list[Tile]] = [[] for _ in players]
        
        self.discard = []
        
        self.distribute_tiles()
        
        # print(self.hands)
    
        for h in self.hands:
            print(' '.join([t.as_string() for t in h]))
            print('\n')
        if Tile.is_winning(self.hands[0]):
            exit()
    
    
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
        return self.deck.pop(0)
    