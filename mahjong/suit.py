from __future__ import annotations
from enum import Enum


class Dragons(Enum):
    # Fa = '發'
    # Zhong = '中'
    # Ban = '□'
    Fa = '🀅'
    Ban = '🀆'
    Zhong = '🀄'
    # 🀄🀅🀆

    def as_string(self, value):
        return str(self.value)
    
    def sort_key(self):
        dragon_order = {d: i for i, d in enumerate(Dragons)}
        return (4, dragon_order.get(self, 0))
    

class Winds(Enum):
    # Bei = '北'
    # Nan = '南'
    # Dong = '東'
    # Xi = '西'
    Bei = '🀃'
    Nan = '🀁'
    Dong = '🀀'
    Xi = '🀂'
    # 🀀🀁🀂🀃
    
    def as_string(self, value):
        return str(self.value)
    
    def sort_key(self):
        wind_order = {w: i for i, w in enumerate(Winds)}
        return (3, wind_order.get(self, 0))
    

class Suit(Enum):
    Characters = 'C'
    Bamboo = 'B'
    Dots = 'D'
    Dragon = Dragons
    Wind = Winds
    # Flower = 5
    # 🀢🀣🀤🀥🀦🀧🀨🀩
    # 🀪
    
    def is_consecutive(self):
        return {
            Suit.Characters: True,
            Suit.Bamboo: True,
            Suit.Dots: True,
            Suit.Dragon: False,
            Suit.Wind: False,
        }[self]
    
    # def title(self):
    #     return self.value
    
    def as_string(self, value):
        return {
            Suit.Characters: '🀇🀈🀉🀊🀋🀌🀍🀎🀏',
            Suit.Bamboo: '🀐🀑🀒🀓🀔🀕🀖🀗🀘',
            Suit.Dots: '🀙🀚🀛🀜🀝🀞🀟🀠🀡',
        }.get(self, '')[value]
    
    @staticmethod
    def as_string_dyn(suit: Suit | Dragons | Winds, value):
        if isinstance(suit, Suit):
            return suit.as_string(value)
        elif isinstance(suit, (Dragons, Winds)):
            return suit.as_string(value)
        return str('')
    
    def sort_key(self):
        suit_order = {
            Suit.Bamboo: 0,
            Suit.Characters: 1,
            Suit.Dots: 2,
            Suit.Dragon: 3,
            Suit.Wind: 4,
        }
        return (suit_order.get(self, 99),) # default just in case