import flask
import os
import flask_discord
from discord.ext import ipc
from main import TOKEN

app = flask.Flask(__name__)
ipc_client = ipc.Client(secret_key=TOKEN)  # secret_key must be the same as your server

app.secret_key = b"\x02\x13g\x11B\xa9\x82\xf0\xf9^A\x9d#}\x17-6\x9f\xe7eb\r\x8f\x8d"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"      # !! Only in development environment.

app.config["DISCORD_CLIENT_ID"] = 661171362856960011
app.config["DISCORD_CLIENT_SECRET"] = "vYgRUOe2sPvj4XNRzQ8uLyjS4WHztDZp"
app.config["DISCORD_REDIRECT_URI"] = "http://127.0.0.1:5000/callback"     
app.config["DISCORD_BOT_TOKEN"] = TOKEN      

discord_session = flask_discord.DiscordOAuth2Session(app)

@app.route("/")
async def index():
    member_count, guild = await ipc_client.request(
        "get_member_count", guild_id=840333999003533432
    )

    return f"""
    <html>
        <head>
            <title>Home</title>
        </head>
        <header>
            <ul>
                <a href="/hello/">Hello World !</a>
                <a href="/login/">login</a>
            </ul>
        </header>
        <body>
            <h1>Bienvenue !</h1>
            <p>Il y a {str(member_count)} membres sur {guild}</p>
        </body>
    </html>"""

@app.route("/hello/")
async def hello():
    return "Hello World !"

@app.route("/login/")
def login():
    return discord_session.create_session()
	

@app.route("/callback/")
def callback():
    discord_session.callback()
    return flask.redirect(flask.url_for(".me"))


@app.errorhandler(flask_discord.Unauthorized)
def redirect_unauthorized(e):
    return flask.redirect(flask.url_for("login"))

	
@app.route("/me/")
@flask_discord.requires_authorization
def me():
    user = discord_session.fetch_user()
    return f"""
    <html>
        <head>
            <title>{user.name}</title>
        </head>
        <body>
            <h1>{user.name}#{user.discriminator}</h1>
            <img src='{user.avatar_url}' />
        </body>
    </html>"""
