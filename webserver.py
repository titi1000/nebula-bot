import flask
from discord.ext import ipc
from main import TOKEN

app = flask.Flask(__name__)
ipc_client = ipc.Client(secret_key=TOKEN)  # secret_key must be the same as your server


@app.route("/")
async def index():
    member_count, guild = await ipc_client.request(
        "get_member_count", guild_id=840333999003533432
    )

    return f"Il y a {str(member_count)} membres sur {guild}"
