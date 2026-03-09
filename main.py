import discord
from dotenv import load_dotenv
import os

import commands

load_dotenv()

bot = discord.Bot()

commands.init(bot)

bot.run(os.getenv("BOT_TOKEN"))

# from mahjong.game import Game

# from mahjong.tile import Tile

# print(Tile.can_be_grouped({
#     0:1,
#     1:1,
#     2:1
# }))

# Game([0])

# for i in range(1_000_000):
#     print(i)
#     g = Game([0])
    
#     if g.state == Game.GameState.Won:
#         print('won')
#         break
    

