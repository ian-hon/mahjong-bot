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
        # self.add_item(ActionButton('Chi', handler.handle_chi, player, discord.ButtonStyle.green, ((handler.game.turn == player_turn) and handler.game.player_can_chi(player)), 0))
        # self.add_item(ActionButton('Chi', handler.handle_chi, player, discord.ButtonStyle.green, ((handler.game.turn == player_turn) and handler.game.player_can_chi(player)), 0))
        
        flag = False
        if (len(handler.game.discard_pile) != 0) and handler.game.is_player_turn(player) and ((len(handler.game.hands[player]) + sum([len(n) for n in handler.game.opened[player]])) == 13):
            for index, patterns in enumerate(Tile.available_chi_patterns(handler.game.discard_pile[-1], handler.game.hands[player])):
                self.add_item(ActionButton(f'Chi ( {' '.join([
                    Tile.as_string(Tile(handler.game.discard_pile[-1].suit, p))
                    for p in sorted(patterns + [handler.game.discard_pile[-1].value])
                    ]
                )} )', handler.handle_chi, player, discord.ButtonStyle.green, True, index))
                flag = True
        
        # self.add_item(ActionButton('Pong', handler.handle_pong, player, discord.ButtonStyle.green, handler.game.player_can_pong(player), 0))
        # self.add_item(ActionButton('Kang', handler.handle_kang, player, discord.ButtonStyle.green, handler.game.player_can_kang(player), 0))
        
        if handler.game.player_can_pong(player):
            self.add_item(ActionButton('Pong', handler.handle_pong, player, discord.ButtonStyle.green, True, 0))
            flag = True
        if handler.game.player_can_kang(player):
            self.add_item(ActionButton('Kang', handler.handle_kang, player, discord.ButtonStyle.green, True, 0))
            flag = True
        
        for index, tile in enumerate(handler.game.hands[player]):
            self.add_item(ActionButton(Tile.as_string(tile), handler.handle_discard, player, discord.ButtonStyle.primary, handler.game.is_player_turn(player) and (not flag), index))
        if flag and handler.game.is_player_turn(player):
            self.add_item(ActionButton('Pass and take a tile', handler.take_tile, player, discord.ButtonStyle.grey, True, 0))


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
            # description=f"{Tile.tiles_to_string(self.game.hands[player])}",
            colour=utils.get_embed_colour()
        )
        
        result.add_field(name='Discard pile', value=f"`{Tile.tiles_to_string(self.game.discard_pile)} `", inline=False)
        result.add_field(name='', value=f"{Tile.tiles_to_string(self.game.hands[player])}", inline=False)
        result.set_footer(text=f'last updated at {datetime.now().strftime(utils.get_time_format())}')
        [result.add_field(name=f"{p}'s opened tiles", value='  '.join([
            ' '.join([Tile.as_string(i) for i in t])
            for t in opened_tiles
        ]), inline=False) for p, opened_tiles in self.game.opened.items() if len(opened_tiles) != 0]
        
        return result
    
    
    async def update_messages(self, ctx: discord.ApplicationContext):
        self.game.update_gamestate()
        
        if self.game.state == Game.GameState.Won:
            for k, v in self.messages.items():
                await v.edit(embed=discord.Embed(
                    colour=utils.get_embed_colour(),
                    title=f'{self.game.get_winner()} has won!'
                ), view=None)
            return
        
        for k, v in self.messages.items():
            embed = self.construct_player_embed(k)
            # view = TileView(self.game.hands[k], k)
            await v.edit(embed=embed)
        await self.populate_interactions(ctx)
    
    
    async def populate_interactions(self, ctx: discord.ApplicationContext):
        for k, v in self.messages.items():
            view = TileView(self, k)
            await v.edit(view=view)
    
    
    async def handle_chi(self, player: str, interaction: discord.Interaction, pattern_index: int):
        if not self.game.is_player_turn(player):
            await interaction.respond('It is not your turn!', ephemeral=True)
            return
        self.game.chi(player, Tile.available_chi_patterns(self.game.discard_pile[-1], self.game.hands[player])[pattern_index])
        self.game.sort_hands()
        await self.update_messages(cast(discord.ApplicationContext, interaction.context))
        await interaction.response.defer()
    
    
    async def handle_pong(self, player: str, interaction: discord.Interaction, _: int):
        if not self.game.player_can_pong(player):
            return
        self.game.turn = self.game.players.index(player)
        self.game.pong(player)
        
        self.game.sort_hands()
        await self.update_messages(cast(discord.ApplicationContext, interaction.context))
        await interaction.response.defer()
    
    
    async def handle_kang(self, player: str, interaction: discord.Interaction, _: int):
        if not self.game.player_can_kang(player):
            return
        self.game.turn = self.game.players.index(player)        
        self.game.kang(player)
        
        self.game.sort_hands()
        await self.update_messages(cast(discord.ApplicationContext, interaction.context))
        await interaction.response.defer()
    
    
    async def handle_discard(self, player: str, interaction: discord.Interaction, index: int):
        if not self.game.is_player_turn(player):
            await interaction.respond('It is not your turn!', ephemeral=True)
            return
        self.game.discard(player, index)
        # self.game.hands[player].append(self.game.take_tile())
        # if self.game.next_tile:
        #     self.game.hands[player].append(self.game.next_tile)
        # self.game.next_tile = self.game.take_tile()
        self.game.sort_hands()
        self.game.increment_turn()
        
        await self.update_messages(cast(discord.ApplicationContext, interaction.context))
        await interaction.response.defer()
        
    async def take_tile(self, player: str, interaction: discord.Interaction, _: int):
        self.game.hands[player].append(self.game.take_tile())
        self.game.turn = self.game.get_player_turn(player)
        
        await self.update_messages(cast(discord.ApplicationContext, interaction.context))
        await interaction.response.defer()