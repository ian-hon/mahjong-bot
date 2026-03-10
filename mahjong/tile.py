from __future__ import annotations
from typing import cast
from .suit import *

class Tile:
    def __init__(self, suit, value=-1):
        self.suit = suit
        self.value = value
        
    
    @staticmethod
    def tiles_to_string(tiles):
        return ' '.join([t.as_string() for t in tiles])
    
    
    @staticmethod
    def get_full():
        # no flowers and no seasons
        # return [n for m in [[Tile(Suit.Bamboo, v) for v in range(9)] for _ in range(4)] for n in m]
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
        return self.suit.as_string(self.value)
    
    def _sort_key(self):
        return self.suit.sort_key() + (self.value,)
    
    @staticmethod
    def get_tile_freq(suit: Suit, tiles: list[Tile]):
        return {i:len([n for n in tiles if (n.suit == suit) and (n.value == i)]) for i in range(9)}

    @staticmethod
    def is_winning(tiles: list[Tile]):
        # dfs backtrack, find if can assign till theres no tiles left
        # group the tiles by their suits first
        characters = Tile.get_tile_freq(Suit.Characters, tiles)
        bamboo = Tile.get_tile_freq(Suit.Bamboo, tiles)
        dots = Tile.get_tile_freq(Suit.Dots, tiles)
        
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
        
        return all([r[0] for r in results])
    
    
    @staticmethod
    def group_tiles(results):
        # UNUSED
        suit_list = [Suit.Characters, Suit.Bamboo, Suit.Dots] + [s for s in Dragons] + [s for s in Winds]
        spacing = '  '
        return spacing.join([
            spacing.join([
                spacing.join([
                    ' '.join([
                        Suit.as_string_dyn(suit, n)
                        for n in m
                    ])
                    for m in stat
                ])
                for stat in stats
            ])
            for suit, stats in zip(suit_list, [r[1].values() for r in results])
        ])
    
    
    @staticmethod
    def can_chi(tile: Tile, tiles: list[Tile]):
        if not Suit.is_consecutive(tile.suit):
            return False
        
        # check in a 3-wide sliding window
        suit = cast(Suit, tile.suit)
        relevant = Tile.get_tile_freq(suit, tiles)
        
        if (tile.value < 0) or (tile.value >= 9):
            return False
        
        return any([
            all([
                (
                    (index + tile.value >= 0) and
                    (index + tile.value < 9) and
                    (relevant[tile.value + index] >= 1)
                )
                for index in candidates
            ])
            for candidates in
            [
                [-2, -1],
                [-1, 1],
                [1, 2]
            ]
        ])
    
    
    @staticmethod
    def available_chi_patterns(tile: Tile, tiles: list[Tile]):        
        # check in a 3-wide sliding window
        suit = cast(Suit, tile.suit)
        relevant = Tile.get_tile_freq(suit, tiles)
        
        if (tile.value < 0) or (tile.value >= 9):
            return []
        
        return [
            [
                tile.value + index
                for index in candidates
            ]
            for candidates in
            [
                [-2, -1],
                [-1, 1],
                [1, 2]
            ]
            if all([
                (
                    (index + tile.value >= 0) and
                    (index + tile.value < 9) and
                    (relevant[tile.value + index] >= 1)
                )
                for index in candidates
            ])
        ]
    
    
    @staticmethod
    def can_pong(tile: Tile, tiles: list[Tile]):
        return len([i for i in tiles if (i.suit == tile.suit) and (i.value == tile.value)]) == 2
    
    @staticmethod
    def can_kang(tile: Tile, tiles: list[Tile]):
        return len([i for i in tiles if (i.suit == tile.suit) and (i.value == tile.value)]) == 3
        
    @staticmethod
    def can_be_grouped(tiles: dict[int, int], stats: dict[Grouping, list[list[int]]], consecutive=True):        
        # returns True if all groups are formed; aka no more tiles are left
        s = sum(tiles.values())
        if s == 0: # tiles empty, criteria fulfilled
            return [True, stats]
        if s == 1: # cant match
            return [False, stats]
        if s <= 3: # pong
            # easiest way to find non-duplicates ig
            if len(set([k for k, v in tiles.items() if v != 0])) == 1:
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
                    stats[Tile.Grouping.Chi].append([e_k, e_k + 1, e_k + 2])
                    return [True, r[1]]
        # check pair, pong, and kang
        if e_v >= 2:
            # max e_v is 4
            # we try all 3?
            for i in range(2, e_v + 1):
                t = {k:v for k, v in tiles.items()} # clone
                t[e_k] -= i
                r = Tile.can_be_grouped(t, stats)
                if r[0]:
                    stats[
                        [
                            Tile.Grouping.Pair,
                            Tile.Grouping.Pong,
                            Tile.Grouping.Kang
                        ][e_v - 2]
                    ].append([[k for k, v in tiles.items() if v != 0][0]] * e_v)
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