from __future__ import annotations
from mahjong.game import Game, Tile
import time
from datetime import datetime
import discord
from discord import CategoryChannel, TextChannel, Message
from discord.ui import View, Button
from typing import cast
import utils


# class TileButton(Button):
#     def __init__(self, func, player: str, label: str):
#         super().__init__(label=label, style=discord.ButtonStyle.primary)
#         self.func = func
#         self.player = player
    
#     async def callback(self, interaction: discord.Interaction):
#         # await interaction.response.send_message(f"Discarded {Tile.as_string(self.tile)}", ephemeral=True)
#         self.func(self.player)3


class ActionButton(Button):
    def __init__(self, title: str, func, player: str, style: discord.ButtonStyle, enabled: bool, index: int):
        super().__init__(label=title, style=style, disabled=not enabled)
        self.func = func
        self.player = player
        self.index = index
    
    
    async def callback(self, interaction: discord.Interaction):
        await self.func(self.player, interaction, self.index)
        


class TileView(View):
    def __init__(self, handler: GameHandler, player: str):
        super().__init__(timeout=None)
        
        # self.add_item(ActionButton('Chi', lambda x:game.chi(x, None), player, discord.ButtonStyle.green, game.player_can_chi(player)))
        # self.add_item(ActionButton('Pong', lambda x:game.pong(x), player, discord.ButtonStyle.green, game.player_can_pong(player)))
        # self.add_item(ActionButton('Kang', lambda x:game.kang(x), player, discord.ButtonStyle.green, game.player_can_kang(player)))
        
        self.add_item(ActionButton('Chi', handler.handle_chi, player, discord.ButtonStyle.green, handler.game.player_can_chi(player), 0))
        self.add_item(ActionButton('Pong', handler.handle_pong, player, discord.ButtonStyle.green, handler.game.player_can_pong(player), 0))
        self.add_item(ActionButton('Kang', handler.handle_kang, player, discord.ButtonStyle.green, handler.game.player_can_kang(player), 0))
        
        for index, tile in enumerate(handler.game.hands[player]):
            self.add_item(ActionButton(Tile.as_string(tile), handler.handle_discard, player, discord.ButtonStyle.primary, True, index))


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
            embed = self.construct_player_embed(p)
            # view = TileView(self.game.hands[p], p)
            # message = await c.send(embed=embed, view=view)
            message = await c.send(embed=embed)
            if message == None:
                return None
            self.messages[p] = message
            r[p] = c
        
        await self.populate_interactions(ctx)
        
        return r
    
    
    def construct_player_embed(self, player: str):
        result = discord.Embed(
            title=f'{player}\'s hand',
            description=f"{Tile.tiles_to_string(self.game.hands[player])}",
            colour=utils.get_embed_colour()
        )
        
        result.set_footer(text=f'last updated at {datetime.now().strftime(utils.get_time_format())}')
        
        [result.add_field(name=f"{p}'s opened tiles", value='  '.join([
            ' '.join([Tile.as_string(i) for i in t])
            for t in opened_tiles
        ]), inline=False) for p, opened_tiles in self.game.opened.items() if len(opened_tiles) != 0]
        
        return result
    
    
    async def update_messages(self, ctx: discord.ApplicationContext):
        for k, v in self.messages.items():
            embed = self.construct_player_embed(k)
            # view = TileView(self.game.hands[k], k)
            await v.edit(embed=embed)
        await self.populate_interactions(ctx)
    
    
    async def populate_interactions(self, ctx: discord.ApplicationContext):
        for k, v in self.messages.items():
            view = TileView(self, k)
            await v.edit(view=view)
    
    
    async def handle_chi(self, player: str, interaction: discord.Interaction, _: int):
        await interaction.respond(f'{player} attempt to handle_chi')
    
    
    async def handle_pong(self, player: str, interaction: discord.Interaction, _: int):
        await interaction.respond(f'{player} attempt to handle_pong')
    
    
    async def handle_kang(self, player: str, interaction: discord.Interaction, _: int):
        await interaction.respond(f'{player} attempt to handle_kang')
    
    
    async def handle_discard(self, player: str, interaction: discord.Interaction, index: int):
        await interaction.respond(f'{player} attempt to handle_discard {index}')