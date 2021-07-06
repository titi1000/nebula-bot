from discord.ext import commands, ipc

class IpcRoutes(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ipc_ready(self):
        print("IPC server is ready.")

    @commands.Cog.listener()
    async def on_ipc_error(self, endpoint, error):
            print(endpoint, "raised", error)

    @ipc.server.route()
    async def get_member_count(self, data):
        guild = await self.client.fetch_guild(data.guild_id)

        return len(await guild.fetch_members(limit=1000).flatten()), guild.name
    
    @ipc.server.route()
    async def get_channels(self, data):
        guild = await self.client.fetch_guild(data.guild_id)

        return await guild.fetch_channels(), guild.name

    @ipc.server.route()
    async def get_roles(self, data):
        guild = await self.client.fetch_guild(data.guild_id)

        return await guild.fetch_roles(), guild.name


def setup(client):
    client.add_cog(IpcRoutes(client))