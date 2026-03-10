from mahjong.game import Game, Tile
import time
from datetime import datetime
import discord
from discord import CategoryChannel, TextChannel, Message
from typing import cast
import utils


class GameHandler:
    # discord wrapper for mahjong.game.Game
    def __init__(self, players):
        # https://stackoverflow.com/questions/33128325/how-to-set-class-attribute-with-await-in-init
        self.game = Game(players)
        self.timestamp = time.time()
        self.channels: dict[str, TextChannel] | None = None
        self.category: CategoryChannel | None = None
        self.messages: dict[str, Message] = {}
        
        self.last_update = time.time()
        
        
    async def construct(self, ctx):    
        self.channels = await self.create_channels(ctx)
        if self.channels == None:
            return False
        if self.messages == {}:
            return False
        return True
    
    
    async def create_channels(self, ctx: discord.ApplicationContext):
        if ctx.guild is None:
            return None
        self.category = await ctx.guild.create_category(f'Mahjong Table ({datetime.fromtimestamp(self.timestamp).strftime(utils.get_time_format())})')
        
        participant_overwrite = discord.PermissionOverwrite(view_channel=False)
        player_overwrite = discord.PermissionOverwrite(send_messages=True, view_channel=True)
        base_overwrite =  {
            ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(send_messages=True, view_channel=True)
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
            message = await c.send(embed=self.construct_player_embed(p))
            if message == None:
                return None
            self.messages[p] = message
            r[p] = c
            
        return r
    
    
    def construct_player_embed(self, player: str):
        result = discord.Embed(
            title=f'{player}\'s hand',
            description=f"{Tile.tiles_to_string(self.game.hands[player])}",
            colour=utils.get_embed_colour(),
            footer=discord.EmbedFooter(text=f'last updated at {datetime.now().strftime(utils.get_time_format())}')
        )
        
        [result.add_field(name=f"{player}'s opened tiles", value='  '.join([
            ' '.join([Tile.as_string(i) for i in t])
            for t in opened_tiles
        ]
            )) for player, opened_tiles in self.game.opened.items() if len(opened_tiles) != 0]
        
        return result
    
    
    async def update_messages(self, ctx: discord.ApplicationContext):
        for k, v in self.messages.items():
            await v.edit(embed=self.construct_player_embed(k))
