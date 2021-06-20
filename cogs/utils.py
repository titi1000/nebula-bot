import discord
from discord.ext import commands
import datetime
from main import MAINCOLOR
from core.others import is_blacklisted_cogs
import disputils

class Utils(commands.Cog):

    def __init__(self, client):
        self.client = client
        print("Utils cog well loaded.")

    # bot's latency
    @commands.command()
    @is_blacklisted_cogs
    async def ping(self, ctx):
        await ctx.send(f"Pong ! {round(self.client.latency * 1000)}ms")

    # clone emoji in your server
    @commands.command()
    @is_blacklisted_cogs
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
    @is_blacklisted_cogs
    async def emojiinfo(self, ctx, emoji:discord.PartialEmoji=None):
        if emoji is None:
            await ctx.send("Please provid an emoji.")
            return
        infos_e = discord.Embed(
            title=emoji.name,
            #url=emoji.url,
            description=f"`{emoji.id}`\nAnimated : {emoji.animated}"
        )
        infos_e.set_thumbnail(url=emoji.url)

        await ctx.send(embed=infos_e)

    # user profile
    @commands.command()
    @is_blacklisted_cogs
    async def profile(self, ctx, user:discord.User=None):
        if user is None:
            profile_e = discord.Embed(
                title=f"{ctx.author.name}#{ctx.author.discriminator} • {ctx.author.id}",
                color=ctx.message.author.color
            )
            flags = ""
            for flag in ctx.author.public_flags.all():
                flags += f"{flag.name} "
            if flags == "":
                flags = "no flags"

            roles = ""
            for role in ctx.author.roles:
                if role.name == "@everyone":
                    continue
                roles += f"<@&{role.id}> "

            created = ctx.author.created_at.strftime("%b %d %Y")
            joined = ctx.author.joined_at.strftime("%b %d %Y")

            profile_e.add_field(name="Roles", value=roles, inline=False)
            profile_e.add_field(name="Flags", value=flags, inline=False)
            profile_e.add_field(name="Bot", value=ctx.author.bot, inline=False)
            profile_e.add_field(name="Avatar URL", value="[link here]({})".format(ctx.author.avatar_url), inline=False)
            profile_e.set_footer(text=f"Account created the {created} • Joined server the {joined}")
            profile_e.set_thumbnail(url=ctx.author.avatar_url)

        if user is not None:
            member = await ctx.guild.fetch_member(user.id)
            profile_e = discord.Embed(
                title=f"{member.name}#{member.discriminator} • {member.id}",
                color=member.color
            )
            flags = ""
            for flag in member.public_flags.all():
                flags += f"{flag.name} "
            if flags == "":
                flags = "no flags"

            roles = ""
            for role in member.roles:
                if role.name == "@everyone":
                    continue
                roles += f"<@&{role.id}> "

            created = member.created_at.strftime("%b %d %Y")
            joined = member.joined_at.strftime("%b %d %Y")

            profile_e.add_field(name="Roles", value=roles, inline=False)
            profile_e.add_field(name="Flags", value=flags, inline=False)
            profile_e.add_field(name="Bot", value=member.bot, inline=False)
            profile_e.add_field(name="Avatar URL", value=f"[link here]({member.avatar_url})", inline=False)
            profile_e.set_footer(text=f"Account created at {created} • Joined server at {joined}")
            profile_e.set_thumbnail(url=member.avatar_url)

        await ctx.send(embed=profile_e)

    # guild infos
    @commands.command()
    @is_blacklisted_cogs
    async def guild(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("You cannot use this command in DM Channel.")
            return

        guild_e = discord.Embed(
            title=f"{ctx.guild.name} • {ctx.guild.id}",
            color=MAINCOLOR
        )
        created = ctx.guild.created_at.strftime("%d %b %Y")
        features = ""
        for feature in ctx.guild.features:
            features += f"{feature} "
        if features == "":
            features = "No features"

        guild_e.set_thumbnail(url=ctx.guild.icon_url)
        guild_e.add_field(name="Owner", value=f"<@{ctx.guild.owner_id}>", inline=True)
        guild_e.add_field(name="Owner's ID", value=ctx.guild.owner_id, inline=True)
        guild_e.add_field(name="Member count", value=ctx.guild.member_count, inline=False)
        guild_e.add_field(name="Channels", value=len(ctx.guild.channels), inline=True)
        guild_e.add_field(name="Roles", value=len(ctx.guild.roles), inline=True)
        guild_e.add_field(name="Boosts", value=ctx.guild.premium_subscription_count, inline=False)
        guild_e.add_field(name=f"Emojis ({len(ctx.guild.emojis)})", value=f"Use command `{ctx.prefix}emojis` to see all emojis.", inline=True)
        guild_e.add_field(name="Features", value=features, inline=False)
        guild_e.set_footer(text=f"Created the {created}")
        guild_e.set_image(url=ctx.guild.banner_url)

        await ctx.send(embed=guild_e)

    # guild emojis
    @commands.command(aliases=["emoji"])
    @is_blacklisted_cogs
    async def emojis(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("You cannot use this command in DM Channel.")
            return
        
        emojis = ""
        for emoji in ctx.guild.emojis:
            if emoji.animated == True:
                emojis += f"<a:{emoji.name}:{emoji.id}> "
            else:
                emojis += f"<:{emoji.name}:{emoji.id}> "

        emojis_e = discord.Embed(
            title=f"{ctx.guild.name}'s emojis • {len(ctx.guild.emojis)} emojis",
            description=emojis
        )
        await ctx.send(embed=emojis_e)      

    # guild membercount
    @commands.command(aliases=["mc"])
    @is_blacklisted_cogs
    async def membercount(self, ctx):
        await ctx.send(f"There is {ctx.guild.member_count} members in {ctx.guild.name}!")
    
    # color
    @commands.command(aliases=["colour"])
    @is_blacklisted_cogs
    async def color(self, ctx, color:discord.Color=None):
        if color is None:
            return await ctx.send("Please provid a color.")

        color_string = str(color)
        color_string = color_string[1:]
        
        color_e = discord.Embed(
            color=color
        )
        color_e.add_field(name="Hex", value=color, inline=False)
        color_e.add_field(name="RGB", value=color.to_rgb(), inline=False)
        color_e.set_thumbnail(url=f"https://dummyimage.com/400x400/{color_string}/{color_string}")

        await ctx.send(embed=color_e)

    # role
    @commands.command(aliases=["ri", "roleinfo"])
    @is_blacklisted_cogs
    async def role(self, ctx, role:discord.Role=None):
        if role is None:
            return await ctx.send("Please provid a role.")

        permissions = ""
        for permission in role.permissions:
            if permission[1] == True:
                the_permission = str(permission[0]).split("_")
                the_permission = " ".join(the_permission)
                the_permission = the_permission.title()
                permissions += f"{the_permission}, "

        created = role.created_at.strftime("%d %b %Y")

        role_e = discord.Embed(
            title="{}'s infos".format(role.name),
            color=role.color
        )
        role_e.add_field(name="ID", value=role.id, inline=True)
        role_e.add_field(name="Color", value=role.color, inline=True)
        role_e.add_field(name="Mention", value=role.mention, inline=True)
        role_e.add_field(name="Members with role", value=len(role.members), inline=True)
        role_e.add_field(name="Position", value=role.position, inline=True)
        role_e.add_field(name="Hoist", value=role.hoist, inline=True)
        role_e.add_field(name="Mentionable", value=role.mentionable, inline=True)
        role_e.add_field(name="Permission(s)", value=permissions, inline=False)

        role_e.set_footer(text=f"Created the {created}")

        await ctx.send(embed=role_e)

    # search for members
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @is_blacklisted_cogs
    async def search(self, ctx, *, text=None):
        if text is None:
            return await ctx.send("Please provid something to search!")

        searching = await ctx.send("Searching... Please wait")
        result = ""
        found = 0
        count = 0
        pages = []

        async for member in ctx.guild.fetch_members(limit=None):
            if count == 10:
                pages.append(discord.Embed(title="Here are the results :", description=f"```js\n{result}\n```", color=0x406da2))
                count = 0
                result = ""

            if text.lower() in member.name.lower():
                count += 1
                if member.nick is not None:
                    result += f"{member.id} {member} ({member.nick})\n"
                    continue
                result += f"{member.id} {member}\n"
                continue

            if member.nick is not None:
                if text.lower() in member.nick.lower():
                    count += 1
                    result += f"{member.id} {member} ({member.nick})\n"

        if result == "" and len(pages) == 0:
            return await searching.edit(content="No member found...")

        if result != "":
            pages.append(discord.Embed(title="Here are the results :", description=f"```js\n{result}\n```", color=0x406da2))

        await searching.delete()
        paginator = disputils.BotEmbedPaginator(ctx, pages)
        await paginator.run()


    # search user by discriminator
    @commands.command(aliases=["discrim"])
    @commands.has_permissions(manage_messages=True)
    @is_blacklisted_cogs
    async def discriminator(self, ctx, discrim=None):
        if discrim is None:
            return await ctx.send("Please provid a discriminator to search!")

        searching = await ctx.send("Searching... Please wait")
        result = ""
        count = 0
        pages = []

        async for member in ctx.guild.fetch_members(limit=None):
            if count == 10:
                pages.append(discord.Embed(title="Here are the results :", description=f"```js\n{result}\n```", color=0x406da2))
                count = 0
                result = ""

            if discrim == member.discriminator:
                count += 1
                result += f"{member.id} {member}\n"
                continue

        if result == "" and len(pages) == 0:
            return await searching.edit(content="No member found...")

        if result != "":
            pages.append(discord.Embed(title="Here are the results :", description=f"```js\n{result}\n```", color=0x406da2))

        await searching.delete()
        paginator = disputils.BotEmbedPaginator(ctx, pages)
        await paginator.run()

    # quotation
    @commands.Cog.listener()
    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel):
            return
        message_splited = message.content.split(" ")
        for word in message_splited:
            if word.startswith(f"https://discord.com/channels/{message.guild.id}"):
                try:
                    link = word.split("/")

                    guild_id = int(link[4])
                    channel_id = int(link[5])
                    message_id = int(link[6])

                    guild = await self.client.fetch_guild(guild_id)
                    channel = self.client.get_channel(channel_id)
                    quoted_message = await channel.fetch_message(message_id)
                    if quoted_message.content == "":
                        return await message.channel.send("Cannot quote an empty message...")
                    
                    quoted_e = discord.Embed(
                        description=quoted_message.content,
                        timestamp=datetime.datetime.utcnow()
                    )
                    quoted_e.set_author(name=f"{quoted_message.author.name}#{quoted_message.author.discriminator}", url=word, icon_url=quoted_message.author.avatar_url)
                    quoted_e.set_footer(text=f"Quoted by {message.author.name}#{message.author.discriminator} in #{message.channel.name}")

                    await message.channel.send(embed=quoted_e)
                except:
                    return

    # quote with command
    @commands.command()
    @is_blacklisted_cogs
    async def quote(self, ctx, link=None):
        if link is None:
            return await ctx.send("You need to provid a link to quote...")
        try:
            link = link.split("/")

            guild_id = int(link[4])
            channel_id = int(link[5])
            message_id = int(link[6])

            guild = await self.client.fetch_guild(guild_id)
            channel = self.client.get_channel(channel_id)
            quoted_message = await channel.fetch_message(message_id)
            if quoted_message.content == "":
                return await ctx.send("Cannot quote an empty message...")
            
            quoted_e = discord.Embed(
                description=quoted_message.content,
                timestamp=datetime.datetime.utcnow()
            )
            quoted_e.set_author(name=f"{quoted_message.author.name}#{quoted_message.author.discriminator}", url=link, icon_url=quoted_message.author.avatar_url)
            quoted_e.set_footer(text=f"Quoted by {ctx.author.name}#{ctx.author.discriminator} in #{ctx.channel.name}")

            await ctx.send(embed=quoted_e)
        except discord.HTTPException:
            return
        except:
            return await ctx.send("Failed to quote...")

    # calculate something
    @commands.command(aliases=["calc", "calculation"])
    @is_blacklisted_cogs
    async def calculate(self, ctx, text=None):
        if text is None:
            return await ctx.send("Please provid a calculation!")

        try:
            await ctx.send(f"Calculation: `{text}`\n\nResult: `{eval(text)}`")
        except:
            return await ctx.send("Please provid a valid calculation!")

def setup(client):
    client.add_cog(Utils(client))