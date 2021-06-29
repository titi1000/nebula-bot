import discord
import datetime
from discord.ext import commands
from main import owner_id, MAINCOLOR, is_it_owner


class OwnerMessage(commands.Cog):

    def __init__(self, client):
        self.client = client


    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        owner = await self.client.fetch_user(owner_id[0])

        created = guild.created_at.strftime("%d %b %Y")

        guild_e = discord.Embed(
            title=f"{self.client.user.name} joined a new server!",
            color=MAINCOLOR
        )
        guild_e.add_field(name="Name", value=guild.name, inline=False)
        guild_e.add_field(name="ID", value=guild.id, inline=False)
        guild_e.add_field(name="Owner", value=f"{guild.owner.name}#{guild.owner.discriminator}", inline=False)
        guild_e.add_field(name="Owner ID", value=guild.owner_id, inline=False)
        guild_e.add_field(name="Member count", value=guild.member_count, inline=False)
        guild_e.add_field(name="Channels", value=len(guild.channels), inline=False)
        guild_e.add_field(name="Roles", value=len(guild.roles), inline=False)
        guild_e.add_field(name="Boosts", value=guild.premium_subscription_count, inline=False)
        guild_e.set_footer(text=f"Server created the {created}")
        guild_e.set_thumbnail(url=guild.icon_url)
        guild_e.set_image(url=guild.banner_url)

        await owner.send(embed=guild_e)

    # get invite from a server
    @commands.command()
    @commands.check(is_it_owner)
    async def get_invite(self, ctx, *, name):
        guild = discord.utils.get(self.client.guilds, name=name)
        if guild:
            invites = await guild.invites()
            max = 0
            for invite in invites:
                if max == 10:
                    return
                await ctx.send(invite.url)
                max += 1
        else:
            return await ctx.send(f"Guild \"{name}\" not found... Please retry")

def setup(client):
    client.add_cog(OwnerMessage(client))