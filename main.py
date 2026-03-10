# import discord
# from dotenv import load_dotenv
# import os

# import commands

# load_dotenv()

# bot = discord.Bot()

# commands.init(bot)

# bot.run(os.getenv("BOT_TOKEN"))

# TODO: use private threads instead
# each participant gets their own private thread
# the mahjong board + opened tiles are all shown in a text channel
# on that embed shown, everyone else can click spectate to view all the participant's threads
#   the bot will invite the users into the thread

# main text channel will also show who's turn it is + time thinking

# the chi, pong, kang can be either inside the main text channel or the thread
# OR
# chi, pong, kang inside main text channel
# discard options inside thread

# participants can forfeit and leave the game
# their tiles (what they opened + hand) will go back into the deck and the deck will be reshuffled
# if theres 2 players and one leaves, the last one is the winner


from mahjong.game import Game

from mahjong.tile import Tile

# Game([0])

for i in range(1_000_000):
    # print(i)
    g = Game(['a'])
    t = g.take_tile()
    print(f'\ndiscarded: {Tile.as_string(t)}')
    print(f'{" ".join([Tile.as_string(i) for i in g.hands['a']])}')
    g.discard_pile.append(t)
    g.chi('a', None)
    
    # if g.state == Game.GameState.Won:
    #     print('won')
    #     break
    

