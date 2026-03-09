from mahjong.game import Game
import time
from datetime import datetime
import discord
from discord import CategoryChannel, TextChannel
from typing import cast


class GameHandler:
    # discord wrapper for mahjong.game.Game
    def __init__(self, players):
        # https://stackoverflow.com/questions/33128325/how-to-set-class-attribute-with-await-in-init
        self.game = Game(players)
        self.timestamp = time.time()
        self.channels: dict[str, TextChannel] | None = None
        self.category: CategoryChannel | None = None
        
        
    async def construct(self, ctx):    
        self.channels = await self.create_channels(ctx)
        if self.channels == None:
            return False
        return True
    
    
    async def create_channels(self, ctx: discord.ApplicationContext):
        if ctx.guild is None:
            return None
        self.category = await ctx.guild.create_category(f'Mahjong Table ({datetime.fromtimestamp(self.timestamp).strftime('%H:%M:%S %d/%m')})')
        
        participant_overwrite = discord.PermissionOverwrite(view_channel=False)
        player_overwrite = discord.PermissionOverwrite(send_messages=True, view_channel=True)
        base_overwrite =  {
            ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(view_channel=True)
        }
        
        members = {
            p:cast(discord.Member, discord.utils.get(ctx.guild.members, name=p))
            for p in self.game.players
        }
        
        r = {}
        for p in self.game.players:
            o:dict[discord.Member | discord.Role, discord.PermissionOverwrite] = {
                v:(participant_overwrite if k != p else player_overwrite)
                for k, v in members.items()
            }
            c = await ctx.guild.create_text_channel(
                f"{p}s-game",
                category=self.category,
                overwrites=o | base_overwrite
            )
            r[p] = c
            
        return r
