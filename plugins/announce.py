import discord
import re
from discord.ext import commands
from main import MAINCOLOR

class Announce(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def announce(self, ctx):

        def yes_no_check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        def cancel_check(msg):
            if msg.content == "cancel":
                return True
            return False

        def check_channel(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        def check_title(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and len(msg.content) < 256

        def check_footer(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and len(msg.content) < 2048

        def check_description(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and len(msg.content) < 2048

        start_e = discord.Embed(
            title="Interactive announce started!",
            description="You can cancel it at any time by typing 'cancel'.\n\nWhere should the announce message go?\n**Please provid a valid channel**",
            color=MAINCOLOR
        )

        await ctx.send(embed=start_e)

        announce_e = discord.Embed()

        channel = await self.client.wait_for("message", check=check_channel)
        if cancel_check(channel):
            return await ctx.send("Cancelled!")
        if len(channel.channel_mentions) == 0:
            return await ctx.send("Cancelled as no valid channel was provided")
        channel = channel.channel_mentions[0]

        embed = discord.Embed(
            title="Should the embed have a title? [y/n]",
            description="*see the embed image for an example*"
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/858466787762896926/860865452158091264/embed_title.png")
        await ctx.send(embed=embed)
        response = await self.client.wait_for("message", check=yes_no_check)
        if cancel_check(response):
            return await ctx.send("Cancelled!")
        if response.content.lower() == "y":
            await ctx.send("What should be the title?")
            title = await self.client.wait_for("message", check=check_title)
            announce_e.title = title.content

        embed = discord.Embed(
            title="Should the embed have a description? [y/n]",
            description="*see the embed image for an example*"
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/858466787762896926/860866775821713448/embed_description.png")
        await ctx.send(embed=embed)
        response = await self.client.wait_for("message", check=yes_no_check)
        if cancel_check(response):
            return await ctx.send("Cancelled!")
        if response.content.lower() == "y":
            await ctx.send("What should be the description?")
            description = await self.client.wait_for("message", check=check_description)
            announce_e.description = description.content

        embed = discord.Embed(
            title="Should the embed have a footer? [y/n]",
            description="*see the embed image for an example*"
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/858466787762896926/860866713457000458/embed_footer.png")
        await ctx.send(embed=embed)
        response = await self.client.wait_for("message", check=yes_no_check)
        if cancel_check(response):
            return await ctx.send("Cancelled!")
        if response.content.lower() == "y":
            await ctx.send("What should be the footer?")
            footer = await self.client.wait_for("message", check=check_footer)
            announce_e.set_footer(text=footer.content)

        embed = discord.Embed(
            title="Should the embed have a thumbnail? [y/n]",
            description="*see the embed image for an example*"
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/858466787762896926/860866753139441674/embed_thumbnail.png")
        await ctx.send(embed=embed)
        response = await self.client.wait_for("message", check=yes_no_check)
        if cancel_check(response):
            return await ctx.send("Cancelled!")
        if response.content.lower() == "y":
            await ctx.send("What should be the thumbnail?\nPlease enter a valid url")
            thumbnail = await self.client.wait_for("message", check=yes_no_check)
            if len(thumbnail.attachments) >= 1:
                url = thumbnail.attachments[0].url
            else:
                url = thumbnail.content
            announce_e.set_thumbnail(url=url)

        embed = discord.Embed(
            title="Should the embed have an image? [y/n]",
            description="*see the embed image for an example*"
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/858466787762896926/860866732184698880/embed_image.png")
        await ctx.send(embed=embed)
        response = await self.client.wait_for("message", check=yes_no_check)
        if cancel_check(response):
            return await ctx.send("Cancelled!")
        if response.content.lower() == "y":
            await ctx.send("What should be the image?\nPlease enter a valid url")
            image = await self.client.wait_for("message", check=yes_no_check)
            if len(image.attachments) >= 1:
                url = image.attachments[0].url
            else:
                url = image.content
            announce_e.set_image(url=url)

        embed = discord.Embed(
            title="Should the embed have a custom color? (If no, the color will be the default) [y/n]",
            description="*see the embed image for an example*"
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/858466787762896926/860866691894738945/embed_color.png")
        await ctx.send(embed=embed)
        response = await self.client.wait_for("message", check=yes_no_check)
        if cancel_check(response):
            return await ctx.send("Cancelled!")
        if response.content.lower() == "y":
            await ctx.send("What should be the color?\nPlease enter a valid hex color (with `#` before)")
            color = await self.client.wait_for("message", check=yes_no_check)
            match = re.search(r"^#(?:[0-9a-fA-F]{3}){1,2}$", color.content) # thx github for the 3 next lines lol 
            if match:
                announce_e.colour = int(color.content.replace("#", "0x"), 0)
            else:
                await ctx.send("Not a valid hex color. Embed will have the default color. Restart if you want a custom color!")
                
        await ctx.send("Do you want to mention any role? [y/n]")
        response = await self.client.wait_for("message", check=yes_no_check)
        if cancel_check(response):
            return await ctx.send("Cancelled!")
        if response.content.lower() == "y":
            await ctx.send("Which role do you want to mention?\nCan be everyone or here")
            role = await self.client.wait_for("message", check=yes_no_check)
            if len(role.role_mentions) == 0:
                if role.content.lower() == "everyone" or role.content.lower() == "@everyone":
                    mention = "@everyone"
                elif role.content.lower() == "here" or role.content.lower() == "@here":
                    mention = "@here"
                else:
                    mention = "no"
            else:
                mention = role.role_mentions[0].mention
        else:
            mention = "no"

        try:
            await ctx.send("Do you want to send the following embed in {}? [y/n]".format(channel.mention), embed=announce_e)
        except discord.errors.HTTPException:
            return await ctx.send("Embed cannot be empty... Please retry")

        response = await self.client.wait_for("message", check=yes_no_check)
        if cancel_check(response):
            return await ctx.send("Cancelled!")
        if response.content.lower() == "y":
            if mention != "no":
                await channel.send(mention, embed=announce_e)
                return await ctx.send("Sent!")
            await channel.send(embed=announce_e)
            return await ctx.send("Sent!")  
        else:
            return await ctx.send("Cancelled!")   


def setup(client):
    client.add_cog(Announce(client))