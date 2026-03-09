from __future__ import annotations
from .suit import *

class Tile:
    def __init__(self, suit, value=-1):
        self.suit = suit
        self.value = value
    
    @staticmethod
    def get_full():
        # no flowers and no seasons
        # return [
        #     n
        #     for m in (
        #         [
        #             [
        #                 Tile(s, v) for v in range(9)
        #             ]
        #             for s in (
        #                 x
        #                 for y in 
        #                 ([
        #                     Suit.Bamboo,
        #                     # Suit.Characters,
        #                     # Suit.Dots
        #                 ] for _ in range(4))
        #                 for x in y
        #             )
        #         ]
        #         # + [
        #         #     [
        #         #         Tile(s, j)
        #         #         for j in range(4)
        #         #     ]
        #         #     for s in Winds
        #         # ]
        #         # + [
        #         #     [
        #         #         Tile(s, j)
        #         #         for j in range(4)
        #         #     ]
        #         #     for s in Dragons
        #         # ]
        #     )
        #     for n in m
        # ]
        return [
            n
            for m in (
                [
                    [
                        Tile(s, v) for v in range(9)
                    ]
                    for s in (
                        x
                        for y in 
                        ([
                            Suit.Bamboo,
                            Suit.Characters,
                            Suit.Dots
                        ] for _ in range(4))
                        for x in y
                    )
                ]
                + [
                    [
                        Tile(s, j)
                        for j in range(4)
                    ]
                    for s in Winds
                ]
                + [
                    [
                        Tile(s, j)
                        for j in range(4)
                    ]
                    for s in Dragons
                ]
            )
            for n in m
        ]
    
    def as_string(self):
        # return f'{self.suit.as_string()} ({self.value})'
        return self.suit.as_string(self.value)
    
    def _sort_key(self):
        return self.suit.sort_key() + (self.value,)

    @staticmethod
    def is_winning(tiles: list[Tile]):
        # dfs backtrack, find if can assign till theres no tiles left
        # group the tiles by their suits first
        f = lambda s:{i:len([n for n in tiles if (n.suit == s) and (n.value == i)]) for i in range(9)} 
        # characters = {i:len([n for n in tiles if (n.suit == Suit.Characters) and (n.value == i)]) for i in range(9)}
        # bamboo = {i:len([n for n in tiles if (n.suit == Suit.Bamboo) and (n.value == i)]) for i in range(9)}
        # dots = {i:len([n for n in tiles if (n.suit == Suit.Dots) and (n.value == i)]) for i in range(9)}
        characters = f(Suit.Characters)
        bamboo = f(Suit.Bamboo)
        dots = f(Suit.Dots)
        
        results = [Tile.can_be_grouped(l, Tile.Grouping.empty_stats()) for l in
            [
                characters,
                bamboo,
                dots,
            ]
        ] + [
            Tile.can_be_grouped(
                {0:len([n for n in tiles if n.suit == k])},
                Tile.Grouping.empty_stats(),
                consecutive=False
            )
            for k in [s for s in Dragons] + [s for s in Winds]
        ]
        
        if all([r[0] for r in results]):
            suit_list = [Suit.Characters, Suit.Bamboo, Suit.Dots] + [s for s in Dragons] + [s for s in Winds]
            for suit, stats in zip(suit_list, [r[1].values() for r in results]):                
                spacing = '  '
                print(f'{suit} :', spacing.join([
                    spacing.join([
                        ' '.join([
                            Suit.as_string_dyn(suit, n)
                            for n in m
                        ])
                        for m in stat
                    ])
                    for stat in stats
                ]))
        return all([r[0] for r in results])
        
    @staticmethod
    def can_be_grouped(tiles: dict[int, int], stats: dict[Grouping, list[list[int]]], consecutive=True):
        # print(f'\tattempt with {tiles}')
        
        # returns True if all groups are formed; aka no more tiles are left
        s = sum(tiles.values())
        if s == 0: # tiles empty, criteria fulfilled
            print('empty')
            return [True, stats]
        if s == 1: # cant match
            print('cant match')
            return [False, stats]
        if s <= 3: # pong
            print('pong')
            # easiest way to find non-duplicates ig
            if len(set([k for k, v in tiles.items() if v != 0])) == 1:
                # stats[Tile.Grouping.Pong if s == 3 else Tile.Grouping.Kang] += 1
                # stats[
                #     [
                #         Tile.Grouping.Pair,
                #         Tile.Grouping.Pong,
                #         Tile.Grouping.Kang
                #     ][s - 2]
                # ] += 1
                stats[
                    [
                        Tile.Grouping.Pair,
                        Tile.Grouping.Pong,
                        Tile.Grouping.Kang
                    ][s - 2]
                ].append([[k for k, v in tiles.items() if v != 0][0]] * s)
                return [True, stats]
        # 4 onwards, can form 2 + 2 (pair + pair)
        
        # get first non-empty tile
        # then check for chi, using sliding window (?)
        # 3 -> 4 & 5
        # OR
        # 3 -> 1 & 2, 2 & 4, 4 & 5?
        # will this be fulfilled by the previous dfs cycle?
        
        (e_k, e_v) = [(k, v) for k, v in tiles.items() if v >= 1][0]
        # check chi first
        if consecutive and (e_k <= 6):
            if (tiles[e_k + 1] >= 1) and (tiles[e_k + 2] >= 1):
                # we can change in-place also without cloning but im too lazy
                t = {k:v for k, v in tiles.items()} # clone
                t[e_k] -= 1
                t[e_k + 1] -= 1
                t[e_k + 2] -= 1
                r = Tile.can_be_grouped(t, stats)
                if r[0]:
                    # stats[Tile.Grouping.Chi] += 1
                    stats[Tile.Grouping.Chi].append([e_k, e_k + 1, e_k + 2])
                    return [True, r[1]]
        # check pair, pong, and kong
        if e_v >= 2:
            # max e_v is 4
            # we try all 3?
            for i in range(2, e_v + 1):
                t = {k:v for k, v in tiles.items()} # clone
                t[e_k] -= i
                # if Tile.can_be_grouped(t):
                #     return True
                r = Tile.can_be_grouped(t, stats)
                if r[0]:
                    # stats[
                    #     [
                    #         Tile.Grouping.Pair,
                    #         Tile.Grouping.Pong,
                    #         Tile.Grouping.Kang
                    #     ][e_v - 2]
                    # ] += 1
                    # stats[
                    #     [
                    #         Tile.Grouping.Pair,
                    #         Tile.Grouping.Pong,
                    #         Tile.Grouping.Kang
                    #     ][e_v - 2]
                    # ] += 1
                    
                    stats[
                        [
                            Tile.Grouping.Pair,
                            Tile.Grouping.Pong,
                            Tile.Grouping.Kang
                        ][e_v - 2]
                    ].append([[k for k, v in tiles.items() if v != 0][0]] * e_v)
                    print(f'stats index: {e_v} {[
                            Tile.Grouping.Pair,
                            Tile.Grouping.Pong,
                            Tile.Grouping.Kang
                        ][e_v - 2]}')
                    return [True, r[1]]
        return [False, stats] # or what here?
        

    @staticmethod
    def sort_tiles(tiles: list[Tile]):
        tiles.sort(key=lambda t: t._sort_key())
        return tiles
    
    
    class Grouping(Enum):
        Chi = 0
        Pair = 1
        Pong = 2
        Kang = 3
        
        @staticmethod
        def empty_stats():
            return {
                s:[] for s in Tile.Grouping
            }