from core.nebula_logging import report_error, report_error_no_ctx
import discord
import re
import os
import datetime
from discord.ext import commands
from main import MAINCOLOR
from core.db import db
from core.others import is_it_moderator_member

class Tickettool(commands.Cog):

    def __init__(self, client):
        self.client = client

    async def gen_html_close(self, channel, closer):
        r_logs_channel_id = db.get_tickettool_logs(channel.guild.id)
        if r_logs_channel_id[0] is False: return await report_error_no_ctx(self.client, r_logs_channel_id)
        if r_logs_channel_id[1][0] is None: return
        logs_channel_id = r_logs_channel_id[1][0]

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
        closed_e.add_field(name="Messages", value=messages, inline=False)
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
        r_tickettool_id = db.get_tickettool(ctx.guild.id)
        if r_tickettool_id[0] is False: return await report_error(self.client, ctx, r_tickettool_id)
        if r_tickettool_id[1][0] is None: return await ctx.send(f"You don't have any ticket tool set in this server...\nUse `{ctx.prefix}tickettool setup` to interactively set a ticket tool message!")
        tickettool_id = r_tickettool_id[1][0].split(" ")

        try:
            channel = ctx.guild.get_channel(int(tickettool_id[1]))
            message = await channel.fetch_message(int(tickettool_id[0]))
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

        start_e = discord.Embed(
            title="Interactive ticket tool setup started!",
            description=":warning: Please make sure I have permission to manage the channels on this server, it won't work if I don't have it. :warning:\n\nYou can cancel it at any time by typing 'cancel'.\n\nWhere should the ticket-tool message go?\n**Please provid a valid channel**",
            color=MAINCOLOR
        )

        setup_message = await ctx.send(embed=start_e)

        setup_e = discord.Embed()

        channel = await self.client.wait_for("message", check=check)
        await channel.delete()
        if cancel_check(channel) is True:
            await setup_message.delete()
            return await ctx.send("Cancelled!")
        if len(channel.channel_mentions) == 0:
            return await ctx.send("Cancelled as no valid channel was provided")
        channel = channel.channel_mentions[0]

        e = discord.Embed(title="Do you want a copy of the tickets to be sent in a log channel? [y/n]", description="*Please answer with 'y' (for yes) or 'n' (for no) when asked!*")
        await setup_message.edit(embed=e)
        response = await self.client.wait_for("message", check=check)
        await response.delete()
        if cancel_check(response) is True:
            await setup_message.delete()
            return await ctx.send("Cancelled!")
        if response.content.lower() == "y":
            e = discord.Embed(title="What should be the log channel?", description="*Please provid a valid channel*")
            await setup_message.edit(embed=e)
            logs_channel = await self.client.wait_for("message", check=check)
            await logs_channel.delete()
            if len(logs_channel.channel_mentions) == 0:
                return await ctx.send("Cancelled as no valid channel was provided")
            logs_channel = logs_channel.channel_mentions[0]

        embed = discord.Embed(
            title="Should the embed have a title? [y/n]",
            description="*see the embed image for an example*"
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/858466787762896926/860865452158091264/embed_title.png")
        await setup_message.edit(embed=embed)
        response = await self.client.wait_for("message", check=check)
        await response.delete()
        if cancel_check(response) is True:
            await setup_message.delete()
            return await ctx.send("Cancelled!")
        if response.content.lower() == "y":
            e = discord.Embed(title="What should be the title?", description="*Please provid a valid string*")
            await setup_message.edit(embed=e)
            title = await self.client.wait_for("message", check=check_title)
            await title.delete()
            setup_e.title = title.content

        embed = discord.Embed(
            title="Should the embed have a description? [y/n]",
            description="*see the embed image for an example*"
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/858466787762896926/860866775821713448/embed_description.png")
        await setup_message.edit(embed=embed)
        response = await self.client.wait_for("message", check=check)
        await response.delete()
        if cancel_check(response) is True:
            await setup_message.delete()
            return await ctx.send("Cancelled!")
        if response.content.lower() == "y":
            e = discord.Embed(title="What should be the description?", description="*Please provid a valid string*")
            await setup_message.edit(embed=e)
            description = await self.client.wait_for("message", check=check_description)
            await description.delete()
            setup_e.description = description.content

        embed = discord.Embed(
            title="Should the embed have a footer? [y/n]",
            description="*see the embed image for an example*"
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/858466787762896926/860866713457000458/embed_footer.png")
        await setup_message.edit(embed=embed)
        response = await self.client.wait_for("message", check=check)
        await response.delete()
        if cancel_check(response) is True:
            await setup_message.delete()
            return await ctx.send("Cancelled!")
        if response.content.lower() == "y":
            e = discord.Embed(title="What should be the footer?", description="*Please provid a valid string*")
            await setup_message.edit(embed=e)
            footer = await self.client.wait_for("message", check=check_footer)
            await footer.delete()
            setup_e.set_footer(text=footer.content)

        embed = discord.Embed(
            title="Should the embed have a thumbnail? [y/n]",
            description="*see the embed image for an example*"
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/858466787762896926/860866753139441674/embed_thumbnail.png")
        await setup_message.edit(embed=embed)
        response = await self.client.wait_for("message", check=check)
        await response.delete()
        if cancel_check(response) is True:
            await setup_message.delete()
            return await ctx.send("Cancelled!")
        if response.content.lower() == "y":
            e = discord.Embed(title="What should be the thumbnail?", description="*Please enter a valid url*")
            await setup_message.edit(embed=e)
            thumbnail = await self.client.wait_for("message", check=check)
            await thumbnail.delete()
            if len(thumbnail.attachments) >= 1:
                url = thumbnail.attachments[0].url
            else:
                url = thumbnail.content
            setup_e.set_thumbnail(url=url)

        embed = discord.Embed(
            title="Should the embed have a custom color? (If no, the color will be the default) [y/n]",
            description="*see the embed image for an example*"
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/858466787762896926/860866691894738945/embed_color.png")
        await setup_message.edit(embed=embed)
        response = await self.client.wait_for("message", check=check)
        await response.delete()
        if cancel_check(response) is True:
            await setup_message.delete()
            return await ctx.send("Cancelled!")
        if response.content.lower() == "y":
            e = discord.Embed(title="What should be the color?", description="*Please enter a valid hex color (with `#` before)*")
            await setup_message.edit(embed=e)
            color = await self.client.wait_for("message", check=check)
            await color.delete()
            match = re.search(r"^#(?:[0-9a-fA-F]{3}){1,2}$", color.content) # thx github for the 3 next lines lol 
            if match:
                setup_e.colour = int(color.content.replace("#", "0x"), 0)
            else:
                await ctx.send("Not a valid hex color. Embed will have the default color. Restart if you want a custom color!")

        try:
            await setup_message.delete()
            await ctx.send("Do you want to send the following ticket tool message in {}? (The reaction will be add automatically) [y/n]".format(channel.mention), embed=setup_e)
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

        r = db.db_execute("UPDATE guilds SET `tickettool_id` = %s WHERE `guild_id` = %s", (f"{message.id} {message.channel.id}", ctx.guild.id))
        if r[0] is False: return await report_error(self.client, ctx, r)
        r = db.db_execute("UPDATE guilds SET `tickettool_logs` = %s WHERE `guild_id` = %s", (logs_channel.id, ctx.guild.id))
        if r[0] is False: return await report_error(self.client, ctx, r)

    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        r_tickettool_id = db.get_tickettool(payload.guild_id)
        if r_tickettool_id[0] is False: return await report_error_no_ctx(self.client, r_tickettool_id)
        tickettool_id = r_tickettool_id[1]
            
        channel = await self.client.fetch_channel(payload.channel_id)
        if payload.message_id == int(tickettool_id[0]) and str(payload.emoji) == "📩" and payload.member != self.client.user:
            for existing_channel in channel.category.text_channels:
                if existing_channel.name == f"{payload.member.name}-{payload.member.discriminator}" and existing_channel.topic == f"{payload.member.id}":
                    return await payload.member.send(f"Hi! You tried to contact the {existing_channel.guild.name} server staff but you already have an open ticket.\nHere is your ticket: {existing_channel.mention}")

            message = await channel.fetch_message(payload.message_id)
            await message.remove_reaction(payload.emoji, payload.member)

            guild = await self.client.fetch_guild(payload.guild_id)
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                payload.member: discord.PermissionOverwrite(read_messages=True)
            }

            if channel.category is None: # in case ticket tool channel has no category
                location = guild
            else:
                location = channel.category 

            channel = await location.create_text_channel(f"{payload.member.name}-{payload.member.discriminator}", overwrites=overwrites, topic=payload.member.id)
            
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
                if is_it_moderator_member(payload.member) is True:
                    await self.gen_html_close(channel, payload.member)
                    await channel.delete()


def setup(client):
    client.add_cog(Tickettool(client))