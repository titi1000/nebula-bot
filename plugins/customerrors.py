import discord
import json
import traceback
import datetime
from discord.ext import commands
from main import owner_id

with open("plugins/plugins.json") as data:
    data = json.load(data)

channel_id = int(data["customerrors"]["channel_id"])

# Thanks to MaRtIn (https://github.com/MaRtIn-9202) for the help
class CustomErrors(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
 
        if isinstance(error, (commands.errors.UserInputError, commands.errors.CheckFailure, commands.errors.ConversionError)):
            trace = error.__traceback__
            final = traceback.format_exception(error, error.__cause__, trace)
        else:
            trace = error.original.__traceback__
            typ = error.original
            final = traceback.format_exception(typ, error.__cause__, trace)

        final = " ".join(final)

        try:
            channel = await self.client.fetch_channel(channel_id)
        except:
            return

        error_e = discord.Embed(
            title="Error", 
            description=f"```py\n{final}```", 
            colour=0xff0000
        )
        error_e.add_field(name="Precise error", value=str(error), inline=False)
        error_e.add_field(name="Command", value=ctx.command.name, inline=False)
        error_e.add_field(name="Channel", value = f"<#{ctx.channel.id}> | {ctx.channel} | {ctx.channel.id}", inline=False)
        error_e.add_field(name="Message", value = ctx.message.content, inline=False)
        error_e.add_field(name ="Author", value = f"{ctx.author} | {ctx.author.id}", inline=False)
        error_e.set_footer(text=f"Error occurred at {datetime.datetime.now().strftime('%H:%M')}")
        await channel.send(embed=error_e)
        

def setup(client):
    client.add_cog(CustomErrors(client))