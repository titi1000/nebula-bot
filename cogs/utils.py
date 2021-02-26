import discord
from discord.ext import commands
import datetime
from main import MAINCOLOR


class Utils(commands.Cog):

    def __init__(self, client):
        self.client = client
        print("Utils cog well loaded.")

    # bot's latency
    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong ! {}ms".format(round(self.client.latency * 1000)))

    # clone emoji in your server
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

    # user profile
    @commands.command()
    async def profile(self, ctx, user:discord.User=None):
        if user is None:
            profile_e = discord.Embed(
                title="{}#{} • {}".format(ctx.author.name, ctx.author.discriminator, ctx.author.id),
                color=ctx.message.author.color
            )
            flags = ""
            for flag in ctx.author.public_flags.all():
                flags += "{} ".format(flag.name)
            if flags == "":
                flags = "no flags"

            roles = ""
            for role in ctx.author.roles:
                if role.name == "@everyone":
                    continue
                roles += "<@&{}> ".format(role.id)

            created = ctx.author.created_at.strftime("%b %d %Y")
            joined = ctx.author.joined_at.strftime("%b %d %Y")

            profile_e.add_field(name="Roles", value=roles, inline=False)
            profile_e.add_field(name="Flags", value=flags, inline=False)
            profile_e.add_field(name="Bot", value=ctx.author.bot, inline=False)
            profile_e.add_field(name="Avatar URL", value="[link here]({})".format(ctx.author.avatar_url), inline=False)
            profile_e.set_footer(text="Account created at {} • Joined server at {}".format(created, joined))
            profile_e.set_thumbnail(url=ctx.author.avatar_url)

        if user is not None:
            member = await ctx.guild.fetch_member(user.id)
            profile_e = discord.Embed(
                title="{}#{} • {}".format(member.name, member.discriminator, member.id),
                color=member.color
            )
            flags = ""
            for flag in member.public_flags.all():
                flags += "{} ".format(flag.name)
            if flags == "":
                flags = "no flags"

            roles = ""
            for role in member.roles:
                if role.name == "@everyone":
                    continue
                roles += "<@&{}> ".format(role.id)

            created = member.created_at.strftime("%b %d %Y")
            joined = member.joined_at.strftime("%b %d %Y")

            profile_e.add_field(name="Roles", value=roles, inline=False)
            profile_e.add_field(name="Flags", value=flags, inline=False)
            profile_e.add_field(name="Bot", value=member.bot, inline=False)
            profile_e.add_field(name="Avatar URL", value="[link here]({})".format(member.avatar_url), inline=False)
            profile_e.set_footer(text="Account created at {} • Joined server at {}".format(created, joined))
            profile_e.set_thumbnail(url=member.avatar_url)

        await ctx.send(embed=profile_e)

    # guild infos
    @commands.command()
    async def guild(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("You cannot use this command in DM Channel.")
            return

        guild_e = discord.Embed(
            title="{} • {}".format(ctx.guild.name, ctx.guild.id),
            color=MAINCOLOR
        )
        created = ctx.guild.created_at.strftime("%d %b %Y")
        features = ""
        for feature in ctx.guild.features:
            features += "{} ".format(feature)
        if features == "":
            features = "No features"

        guild_e.set_thumbnail(url=ctx.guild.icon_url)
        guild_e.add_field(name="Owner", value="<@{}>".format(ctx.guild.owner_id), inline=True)
        guild_e.add_field(name="Owner's ID", value="{}".format(ctx.guild.owner_id), inline=True)
        guild_e.add_field(name="Member count", value="{}".format(ctx.guild.member_count), inline=False)
        guild_e.add_field(name="Channels", value="{}".format(len(ctx.guild.channels)), inline=True)
        guild_e.add_field(name="Roles", value="{}".format(len(ctx.guild.roles)), inline=True)
        guild_e.add_field(name="Boosts", value="{}".format(ctx.guild.premium_subscription_count), inline=False)
        guild_e.add_field(name="Emojis ({})".format(len(ctx.guild.emojis)), value="Use command `{}emojis` to see all emojis.".format(ctx.prefix), inline=True)
        guild_e.add_field(name="Features", value=features, inline=False)
        guild_e.set_footer(text="Created the {}".format(created))
        guild_e.set_image(url=ctx.guild.banner_url)

        await ctx.send(embed=guild_e)

    # guild emojis
    @commands.command()
    async def emojis(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("You cannot use this command in DM Channel.")
            return
        
        emojis = ""
        for emoji in ctx.guild.emojis:
            if emoji.animated == True:
                emojis += "<a:{}:{}> ".format(emoji.name, emoji.id)
            else:
                emojis += "<:{}:{}> ".format(emoji.name, emoji.id)

        emojis_e = discord.Embed(
            title="{}'s emojis • {} emojis".format(ctx.guild.name, len(ctx.guild.emojis)),
            description=emojis
        )
        await ctx.send(embed=emojis_e)      

    # guild membercount
    @commands.command(aliases=["mc"])
    async def membercount(self, ctx):
        await ctx.send("There is {} members in {}!".format(ctx.guild.member_count, ctx.guild.name))

    # quotation
    @commands.Cog.listener()
    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel):
            return
        message_splited = message.content.split(" ")
        for word in message_splited:
            if word.startswith("https://discord.com/channels/{}".format(message.guild.id)):
                try:
                    link = word.split("/")

                    guild_id = int(link[4])
                    channel_id = int(link[5])
                    message_id = int(link[6])

                    guild = await self.client.fetch_guild(guild_id)
                    channel = self.client.get_channel(channel_id)
                    quoted_message = await channel.fetch_message(message_id)
                    
                    quoted_e = discord.Embed(
                        description=quoted_message.content,
                        timestamp=datetime.datetime.now()
                    )
                    quoted_e.set_author(name="{}#{}".format(quoted_message.author.name, quoted_message.author.discriminator), url=word, icon_url=quoted_message.author.avatar_url)
                    quoted_e.set_footer(text="Quoted by {}#{} in #{}".format(message.author.name, message.author.discriminator, message.channel.name))

                    await message.channel.send(embed=quoted_e)
                except:
                    return

def setup(client):
    client.add_cog(Utils(client))