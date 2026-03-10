import discord
from discord import CategoryChannel, TextChannel
from typing import cast
# from mahjong.game import Game
from handler import GameHandler
import time

def init(bot: discord.Bot):
    handler: GameHandler | None = None
    
    @bot.event
    async def on_ready():
        print('mahjong bot at your service')
        
    @bot.slash_command()
    async def hmm(ctx: discord.ApplicationContext):
        message = await ctx.respond('hmmm')
        for i in range(30):
            await message.edit(content=f'{i}')
            time.sleep(0.1)
    
    
    @bot.slash_command()
    async def start_game(ctx: discord.commands.ApplicationContext,
                        player2: discord.Option(discord.Member, "Player 2", required=True),
                        player3: discord.Option(discord.Member, "Player 3", required=False),
                        player4: discord.Option(discord.Member, "Player 4", required=False)
                        ):
        nonlocal handler
        players: list[discord.member.Member] = [p for p in [ctx.author, player2, player3, player4] if p is not None]
        
        if len(players) == 1:
            await ctx.respond('how even')
            return
        
        if len(players) != len(set([p.id for p in players])):
            await ctx.respond('No duplicate players allowed.')
            return
        
        if handler != None:
            await ctx.respond('There is currently an ongoing game. Due to Discord\'s rate limits, only one game can run at any time.')
            return
        
        await ctx.respond(f"Starting game with: {', '.join([p.mention for p in players])}")
        h = GameHandler([p.name for p in players])
        if not (await h.construct(ctx)):
            await ctx.respond('Unable to setup game')
            return
        handler = h
    
    @bot.slash_command()
    async def end_game(ctx: discord.commands.ApplicationContext):
        nonlocal handler
        if handler == None:
            await ctx.respond('No active game at the moment.')
            return
    
        for channel in cast(dict[str, TextChannel], handler.channels).values():
            await channel.delete()
        await cast(CategoryChannel, handler.category).delete()
        
        handler = None
        
        await ctx.respond('Succesfully ended game')
    
    
    @bot.slash_command()
    async def proceed(ctx: discord.ApplicationContext):
        if handler == None:
            await ctx.respond('No active game at the moment.')
            return
        await handler.update_messages(ctx)
        
    # discard
    #   choose index
    
    # chi
    #   discard
    
    # pong
    #   discard
    
    # kang
    #   discard
    

