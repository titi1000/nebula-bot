import discord
from discord.ext import commands
import datetime


class Utils(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong ! {}ms".format(round(self.client.latency * 1000)))

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def cloneemoji(self, ctx, emoji:discord.PartialEmoji=None):
        if emoji is None:
            await ctx.send("Please provid an emoji.")
            return
        try:
            image = await emoji.url.read() # convert the url to bytes object
            await ctx.guild.create_custom_emoji(
                name=emoji.name,
                image=image
            )
        except:
            await ctx.send("Failed... Please retry!")

    @commands.command()
    async def emojiinfo(self, ctx, emoji:discord.PartialEmoji=None):
        if emoji is None:
            await ctx.send("Please provid an emoji.")
            return
        infos_e = discord.Embed(
            title=emoji.name,
            #url=emoji.url,
            description="`{}`\nAnimated : {}".format(emoji.id, emoji.animated)
        )
        infos_e.set_thumbnail(url=emoji.url)

        await ctx.send(embed=infos_e)

    @commands.command()
    async def profile(self, ctx, member:discord.Member=None):
        if member is None:
            profile_e = discord.Embed(
                title="{}#{} • {}".format(ctx.author.name, ctx.author.discriminator, ctx.author.id),
                color=ctx.message.author.color
            )
            roles = ""
            for role in ctx.author.roles:
                if role.name == "@everyone":
                    continue
                roles += "<@&{}> ".format(role.id)

            created = ctx.author.created_at.strftime("%b %d %Y")
            joined = ctx.author.joined_at.strftime("%b %d %Y")

            profile_e.add_field(name="Roles", value=roles, inline=False)
            profile_e.add_field(name="Bot", value=ctx.author.bot, inline=False)
            profile_e.add_field(name="Avatar URL", value="[link here]({})".format(ctx.author.avatar_url), inline=False)
            profile_e.set_footer(text="Account created at {} • Joined server at {}".format(created, joined))
            profile_e.set_thumbnail(url=ctx.author.avatar_url)

        if member is not None:
            profile_e = discord.Embed(
                title="{}#{} • {}".format(member.name, member.discriminator, member.id),
                color=member.color
            )
            roles = ""
            for role in member.roles:
                if role.name == "@everyone":
                    continue
                roles += "<@&{}> ".format(role.id)

            created = member.created_at.strftime("%b %d %Y")
            joined = member.joined_at.strftime("%b %d %Y")

            profile_e.add_field(name="Roles", value=roles, inline=False)
            profile_e.add_field(name="Bot", value=member.bot, inline=False)
            profile_e.add_field(name="Avatar URL", value="[link here]({})".format(member.avatar_url), inline=False)
            profile_e.set_footer(text="Account created at {} • Joined server at {}".format(created, joined))
            profile_e.set_thumbnail(url=member.avatar_url)

        await ctx.send(embed=profile_e)

def setup(client):
    client.add_cog(Utils(client))