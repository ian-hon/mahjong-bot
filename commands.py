import discord

def init(bot: discord.Bot):
    @bot.event
    async def on_ready():
        print('mahjong bot at your service')
        
    @bot.slash_command()
    async def hmm(ctx: discord.ApplicationContext):
        await ctx.respond('test')
    

