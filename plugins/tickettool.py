import discord
import re
import os
import datetime
from discord.ext import commands
from main import MAINCOLOR
from core.db import db

class Tickettool(commands.Cog):

    def __init__(self, client):
        self.client = client

    async def gen_html_close(self, channel, closer):
        logs_channel_id = db.get_tickettool_logs(channel.guild.id)
        if logs_channel_id is False:
            return

        member_name = channel.name.replace("-", "#")
        
        f = open(f"{channel.name}_{channel.guild.id}.html", "w", encoding="utf-8")
        f.write("<html>\r\n<link rel=\"stylesheet\" href=\"https://meyerweb.com/eric/tools/css/reset/reset200802.css\"><link rel=\"preconnect\" href=\"https://fonts.googleapis.com\"><link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin><link href=\"https://fonts.googleapis.com/css2?family=Open+Sans&display=swap\" rel=\"stylesheet\">\r\n<style>body{font-family: 'Open Sans', sans-serif;background-color:#36393f;color:#ffffff;width:98%;padding:15px 15px}</style>\r\n")
        f.write(f"<header style=\"display:flex;flex-direction:row;margin-bottom:20px\"><img src=\"{channel.guild.icon_url}\" width=\"60\" height=\"60\"><span style=\"font-size:34px;padding:15px 8px\">{channel.guild.name} - {member_name}</span></header>\r\n<body>")
        
        messages = 0
        
        async for message in channel.history(limit=1000, oldest_first=True):
            messages += 1
            if len(message.embeds) != 0:
                continue

            for mention in message.mentions:
                message.content = message.content.replace(f"<@!{mention.id}>", f"@{mention.name}")
                message.content = message.content.replace(f"<@{mention.id}>", f"@{mention.name}")

            for mention in message.channel_mentions:
                message.content = message.content.replace(f"<#{mention.id}>", f"#{mention.name}")

            for mention in message.role_mentions:
                message.content = message.content.replace(f"<@&{mention.id}>", f"@{mention.name}")
            
            time = message.created_at.strftime("%m/%d/%Y, %H:%M")

            if message.content != "":
                try:
                    f.write(f"<div style=\"padding:15px 0 20px 0;border-bottom:1px solid #9f9f9f;width:100%\"><span style=\"font-size:20px;color:#a4a4a4;padding-bottom:10px;\">{message.author.name}#{message.author.discriminator}:</span><span style=\"margin: 0 8px; font-size:15px;color:#b0b0b0\">{time}</span><br><span>{message.content}</span></div>")
                except:
                    pass

            for attachment in message.attachments:
                if attachment.content_type.startswith("image"):
                    try:
                        f.write(f"<div style=\"padding:15px 0 20px 0;border-bottom:1px solid #9f9f9f;width:100%\"><span style=\"font-size:20px;color:#a4a4a4;padding-bottom:10px;\">{message.author.name}#{message.author.discriminator}:</span><span style=\"margin: 0 8px; font-size:15px;color:#b0b0b0\">{time}</span><br><img src=\"{attachment.url}\" style=\"max-width:500;max-height:800;padding-top:15px\"></div>")
                    except:
                        pass

        f.write("\r\n</body>\r\n</html>")
        f.close()

        closed_e = discord.Embed(
            title=f"Ticket #{channel.name} closed",
            color=MAINCOLOR,
            timestamp=datetime.datetime.now()
        )
        closed_e.add_field(name="Member", value=member_name, inline=False)
        closed_e.add_field(name="Messages (max 1000)", value=messages, inline=False)
        closed_e.add_field(name="Closed by", value=f"{closer.name}#{closer.discriminator}", inline=False)

        try:
            logs_channel = channel.guild.get_channel(logs_channel_id)
            await logs_channel.send(embed=closed_e, file=discord.File(f"{channel.name}_{channel.guild.id}.html"))
            os.remove(f"{channel.name}_{channel.guild.id}.html")
        except:
            return os.remove(f"{channel.name}_{channel.guild.id}.html")
        

    @commands.group(invoke_without_command=True, aliases=["ticket_tool", "ticket-tool"])
    @commands.has_permissions(administrator=True)
    async def tickettool(self, ctx):
        message_id = db.get_tickettool(ctx.guild.id)

        if message_id is False:
            return await ctx.send(f"You don't have any ticket tool set in this server...\nUse `{ctx.prefix}tickettool setup` to interactively set a ticket tool message!")

        try:
            message = await ctx.fetch_message(message_id)
        except:
            return await ctx.send(f"You don't have any ticket tool set in this server...\nUse `{ctx.prefix}tickettool setup` to interactively set a ticket tool message!")

        await ctx.send(f"Ticket tool set in {message.channel.mention} ({message.jump_url})")


    @tickettool.command()
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx):

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        def check_title(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and len(msg.content) < 256

        def check_footer(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and len(msg.content) < 2048

        def check_description(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and len(msg.content) < 2048

        def cancel_check(msg):
            if msg.content == "cancel":
                return True
            return False

        await ctx.send("Interactive ticket tool setup started! You can cancel it at any time by typing \"cancel\".\nWhere should the ticket-tool message go?\nPlease provid a valid channel")

        setup_e = discord.Embed()

        channel = await self.client.wait_for("message", check=check)
        if cancel_check(channel) is True:
            return await ctx.send("Cancelled!")
        if len(channel.channel_mentions) == 0:
            return await ctx.send("Cancelled as no valid channel was provided")
        channel = channel.channel_mentions[0]

        await ctx.send("Do you want a copy of the tickets to be sent in a log channel? [y/n]")
        response = await self.client.wait_for("message", check=check)
        if cancel_check(response) is True:
            return await ctx.send("Cancelled!")
        if response.content.lower() == "y":
            await ctx.send("What should be the log channel? Please provid a valid channel")
            logs_channel = await self.client.wait_for("message", check=check)
            if len(logs_channel.channel_mentions) == 0:
                return await ctx.send("Cancelled as no valid channel was provided")
            logs_channel = logs_channel.channel_mentions[0]

        await ctx.send("Should the embed have a title? [y/n]")
        response = await self.client.wait_for("message", check=check)
        if cancel_check(response) is True:
            return await ctx.send("Cancelled!")
        if response.content.lower() == "y":
            await ctx.send("What should be the title?")
            title = await self.client.wait_for("message", check=check_title)
            setup_e.title = title.content

        await ctx.send("Should the embed have a footer? [y/n]")
        response = await self.client.wait_for("message", check=check)
        if cancel_check(response) is True:
            return await ctx.send("Cancelled!")
        if response.content.lower() == "y":
            await ctx.send("What should be the footer?")
            footer = await self.client.wait_for("message", check=check_footer)
            setup_e.set_footer(text=footer.content)

        await ctx.send("Should the embed have a description? [y/n]")
        response = await self.client.wait_for("message", check=check)
        if cancel_check(response) is True:
            return await ctx.send("Cancelled!")
        if response.content.lower() == "y":
            await ctx.send("What should be the description?")
            description = await self.client.wait_for("message", check=check_description)
            setup_e.description = description.content

        await ctx.send("Should the embed have a thumbnail? [y/n]")
        response = await self.client.wait_for("message", check=check)
        if cancel_check(response) is True:
            return await ctx.send("Cancelled!")
        if response.content.lower() == "y":
            await ctx.send("What should be the thumbnail?\nPlease enter a valid url")
            thumbnail = await self.client.wait_for("message", check=check)
            if len(thumbnail.attachments) >= 1:
                url = thumbnail.attachments[0].url
            else:
                url = thumbnail.content
            setup_e.set_thumbnail(url=url)

        await ctx.send("Should the embed have a custom color? [y/n]")
        response = await self.client.wait_for("message", check=check)
        if cancel_check(response) is True:
            return await ctx.send("Cancelled!")
        if response.content.lower() == "y":
            await ctx.send("What should be the color?\nPlease enter a valid hex color (with `#` before)")
            color = await self.client.wait_for("message", check=check)
            match = re.search(r"^#(?:[0-9a-fA-F]{3}){1,2}$", color.content) # thx github for the 3 next lines lol 
            if match:
                setup_e.colour = int(color.content.replace("#", "0x"), 0)
            else:
                await ctx.send("Not a valid hex color. Embed will have the default color. Restart if you want a custom color!")

        try:
            await ctx.send("Do you want to send the following ticket tool message in {}? [y/n]".format(channel.mention), embed=setup_e)
        except discord.errors.HTTPException:
            return await ctx.send("Embed cannot be empty... Please retry")

        response = await self.client.wait_for("message", check=check)
        if cancel_check(response) is True:
            return await ctx.send("Cancelled!")
        if response.content.lower() == "y":
            message = await channel.send(embed=setup_e)
            await message.add_reaction("📩")
            await ctx.send("Ready!")
        else:
            return await ctx.send("Cancelled!")

        db.cursor.execute("UPDATE guilds SET tickettool_id = ? WHERE guild_id = ?", (message.id, ctx.guild.id))
        db.cursor.execute("UPDATE guilds SET tickettool_logs = ? WHERE guild_id = ?", (logs_channel.id, ctx.guild.id))
        db.commit()

    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        tickettool_id = db.get_tickettool(payload.guild_id)
        channel = await self.client.fetch_channel(payload.channel_id)
        if payload.message_id == tickettool_id and str(payload.emoji) == "📩" and payload.member != self.client.user:
            for existing_channel in channel.category.text_channels:
                if existing_channel.name == f"{payload.member.name}-{payload.member.discriminator}" and existing_channel.topic == f"{payload.member.id}":
                    return await payload.member.send(f"Hi! You tried to contact the {existing_channel.guild.name} server staff but you already have an open ticket.\nHere is your ticket: {existing_channel.mention}")

            guild = await self.client.fetch_guild(payload.guild_id)
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                payload.member: discord.PermissionOverwrite(read_messages=True)
            }
            channel = await channel.category.create_text_channel(f"{payload.member.name}-{payload.member.discriminator}", overwrites=overwrites, topic=payload.member.id)
            await channel.send(payload.member.mention)
            tickettool_e = discord.Embed(
                title="New ticket created!",
                description="Moderators can close the ticket by adding the :lock: reaction to this message.\nPlease don't change the name of the channel and his topic :warning:",
                color=MAINCOLOR
            )
            message = await channel.send(embed=tickettool_e)
            return await message.add_reaction("🔒")

        message = await channel.fetch_message(payload.message_id)
        if str(payload.emoji) == "🔒" and payload.member != self.client.user and len(message.embeds) > 0:
            if message.embeds[0].title == "New ticket created!" and message.embeds[0].description == "Moderators can close the ticket by adding the :lock: reaction to this message.\nPlease don't change the name of the channel and his topic :warning:" and message.embeds[0].colour == discord.Color(MAINCOLOR):
                await self.gen_html_close(channel, payload.member)
                await channel.delete()


def setup(client):
    client.add_cog(Tickettool(client))