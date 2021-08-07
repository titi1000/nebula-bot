import discord
from discord.ext import commands
import datetime
from main import MAINCOLOR
from core.others import is_blacklisted_cogs
import disputils
import json

class Utils(commands.Cog):

    def __init__(self, client):
        self.client = client
        print("Utils cog well loaded.")

        # import discord flags 
        with open("others.json") as discord_flags:
            self.discord_flags = json.load(discord_flags)["flags"]

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
        if emoji is None: return await ctx.send("Please provid an emoji.")
        try:
            image = await emoji.url.read() # convert the url to bytes object
            await ctx.guild.create_custom_emoji(
                name=emoji.name,
                image=image
            )
        except: await ctx.send("Failed... Please retry!")

    @commands.command()
    @is_blacklisted_cogs
    async def emojiinfo(self, ctx, emoji:discord.PartialEmoji=None):
        if emoji is None: return await ctx.send("Please provid an emoji.")
        infos_e = discord.Embed(
            title=emoji.name,
            #url=emoji.url,
            description=f"`{emoji.id}`\nAnimated : {emoji.animated}"
        )
        infos_e.set_thumbnail(url=emoji.url)

        await ctx.send(embed=infos_e)

    # member profile
    @commands.command()
    @is_blacklisted_cogs
    async def profile(self, ctx, member:discord.Member=None):
        if member is None: member=ctx.author
        else: member = await ctx.guild.fetch_member(member.id)
    
        flags = []
        for flag in member.public_flags.all(): flags.append(self.discord_flags[flag.name])
        if flags != []: flags = " ".join(flags)
        else: flags = "No flags"

        roles = []
        for role in member.roles:
            if role.name == "@everyone": continue
            roles.append(role.mention)
        if roles != []: roles = " ".join(roles)
        else: roles = "No roles"

        created = member.created_at.strftime("%b %d %Y")
        joined = member.joined_at.strftime("%b %d %Y")
        
        account_type = "Human"
        if member.bot: account_type = "Bot"
            
        profile_e = discord.Embed(
            title=f"{member} • {member.id}",
            description=flags,
            color=member.color
        )
        
        profile_e.add_field(name= "Account type", value=account_type, inline = False)
        profile_e.add_field(name="Roles", value=roles, inline=False)
        profile_e.add_field(name="Avatar URL", value=f"[link here]({member.avatar_url})", inline=False)
        profile_e.set_footer(text=f"Account created at {created} • Joined server at {joined}")
        profile_e.set_thumbnail(url=member.avatar_url)

        await ctx.send(embed=profile_e)

    # guild infos
    @commands.command()
    @is_blacklisted_cogs
    async def guild(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel): return await ctx.send("You cannot use this command in DM Channel.")

        guild_e = discord.Embed(
            title=f"{ctx.guild.name} • {ctx.guild.id}",
            color=MAINCOLOR
        )
        created = ctx.guild.created_at.strftime("%d %b %Y")
        features = ""
        for feature in ctx.guild.features: features += f"{feature} "
        if features == "": features = "No features"

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
        if isinstance(ctx.channel, discord.DMChannel): return await ctx.send("You cannot use this command in DM Channel.")
        
        emojis = ""
        for emoji in ctx.guild.emojis:
            if emoji.animated: emojis += f"<a:{emoji.name}:{emoji.id}> "
            else: emojis += f"<:{emoji.name}:{emoji.id}> "
        if emojis == "": emojis = "No emojis"

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
        if color is None: return await ctx.send("Please provid a color.")

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
        if role is None: return await ctx.send("Please provid a role.")

        permissions = ""
        for permission in role.permissions:
            if permission[1]:
                the_permission = str(permission[0]).split("_")
                the_permission = " ".join(the_permission)
                the_permission = the_permission.title()
                permissions += f"{the_permission}, "
        if permissions == "": permissions = "No permissions"

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
        if text is None: return await ctx.send("Please provid something to search!")

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

        if result == "" and len(pages) == 0: return await searching.edit(content="No member found...")
        if result != "": pages.append(discord.Embed(title="Here are the results :", description=f"```js\n{result}\n```", color=0x406da2))

        await searching.delete()
        paginator = disputils.BotEmbedPaginator(ctx, pages)
        await paginator.run()


    # search user by discriminator
    @commands.command(aliases=["discrim"])
    @commands.has_permissions(manage_messages=True)
    @is_blacklisted_cogs
    async def discriminator(self, ctx, discrim=None):
        if discrim is None: return await ctx.send("Please provid a discriminator to search!")

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

        if result == "" and len(pages) == 0: return await searching.edit(content="No member found...")
        if result != "": pages.append(discord.Embed(title="Here are the results :", description=f"```js\n{result}\n```", color=0x406da2))

        await searching.delete()
        paginator = disputils.BotEmbedPaginator(ctx, pages)
        await paginator.run()

    # quotation
    @commands.Cog.listener()
    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel): return
        message_splited = message.content.split(" ")
        for word in message_splited:
            if word.startswith(f"https://discord.com/channels/{message.guild.id}") or word.startswith(f"https://canary.discord.com/channels/{message.guild.id}"):

                try:
                    link = word.split("/")

                    guild_id = int(link[4])
                    channel_id = int(link[5])
                    message_id = int(link[6])

                    guild = await self.client.fetch_guild(guild_id)
                    channel = self.client.get_channel(channel_id)
                    quoted_message = await channel.fetch_message(message_id)
                    if quoted_message.content == "": return await message.channel.send("Cannot quote an empty message...")
                    
                    quoted_e = discord.Embed(
                        description=quoted_message.content,
                        timestamp=datetime.datetime.utcnow()
                    )
                    quoted_e.set_author(name=f"{quoted_message.author.name}#{quoted_message.author.discriminator}", url=word, icon_url=quoted_message.author.avatar_url)
                    quoted_e.set_footer(text=f"Quoted by {message.author.name}#{message.author.discriminator} in #{message.channel.name}")

                    await message.channel.send(embed=quoted_e)
                except: return

    # quote with command
    @commands.command()
    @is_blacklisted_cogs
    async def quote(self, ctx, link=None):
        if link is None: return await ctx.send("You need to provid a link to quote...")
        try:
            link = link.split("/")

            guild_id = int(link[4])
            channel_id = int(link[5])
            message_id = int(link[6])

            channel = self.client.get_channel(channel_id)
            quoted_message = await channel.fetch_message(message_id)
            if quoted_message.content == "": return await ctx.send("Cannot quote an empty message...")
            
            quoted_e = discord.Embed(
                description=quoted_message.content,
                timestamp=datetime.datetime.utcnow()
            )
            quoted_e.set_author(name=f"{quoted_message.author.name}#{quoted_message.author.discriminator}", url=link, icon_url=quoted_message.author.avatar_url)
            quoted_e.set_footer(text=f"Quoted by {ctx.author.name}#{ctx.author.discriminator} in #{ctx.channel.name}")

            await ctx.send(embed=quoted_e)
        except discord.HTTPException: return
        except: return await ctx.send("Failed to quote...")

    # calculate something
    @commands.command(aliases=["calc", "calculation"])
    @is_blacklisted_cogs
    async def calculate(self, ctx, text=None):
        if text is None: return await ctx.send("Please provid a calculation!")
        try: await ctx.send(f"Calculation: `{text}`\n\nResult: `{eval(text)}`")
        except: return await ctx.send("Please provid a valid calculation!")

def setup(client):
    client.add_cog(Utils(client))