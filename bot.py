import nextcord
import logging
import aiohttp
import asyncio
import configparser
from nextcord.ext import commands
import json

from tables import PendingRequest
import views

# config

intents = nextcord.Intents.default()
intents.members = True

config = configparser.ConfigParser()
config.read("config.ini")
# sonarr configs
api_key = config["sonarr"]["api_key"]
sonarr_url = config["sonarr"]["url"]
download_path = config["sonarr"]["download_path"]
# discord configs
discord_token = config["discord"]["token"]
admin_user_id = config["discord"]["admin_user_id"]

# logging
logger = logging.getLogger("nextcord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="ArrCord.log", encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)


# set prefix
bot = commands.Bot(command_prefix="-", intents=intents)


@bot.event
async def on_ready():
    on_ready.admin_user = await bot.fetch_user(admin_user_id)

    await PendingRequest.create_table(if_not_exists=True)


# define commands
@bot.command()
async def request(
    ctx,
    *series_name: str,
):
    if not series_name:
        await ctx.send("please specify a series name")
        return
    series_name.replace(" ", "%20")

    results = False
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{sonarr_url}/api/series/lookup?term={series_name}&apikey={api_key}"
        ) as raw_response:
            json_res = await raw_response.json()
            res = json_res[: min(5, len(json_res) - 1)]

    if len(res) > 0:
        results = True

    if results:
        view = views.SeriesSelectView(res, ctx, on_ready.admin_user)
        await ctx.send("Choose a series from the dropdown:", view=view)
    else:
        await ctx.send("No results found for your request")


@bot.command()
async def approve(ctx, *approve_select):
    Pending_Requests = await PendingRequest.select()

    if approve_select and len(Pending_Requests) > 0:
        series_raw = json.loads(
            Pending_Requests[int(approve_select[0]) - 1]["series_data"]
        )

        required_fields = [
            "tvdbId",
            "title",
            "titleSlug",
            "images",
            "seasons",
        ]
        series = {
            key: value for key, value in series_raw.items() if key in required_fields
        }
        # for quality profile may need to be configureable by admin
        series["profileId"] = 1
        series["rootFolderPath"] = download_path
        series["addOptions"] = {
            "ignoreEpisodesWithFiles": True,
            "ignoreEpisodesWithoutFiles": False,
            "searchForMissingEpisodes": True,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{sonarr_url}/api/series/?apikey={api_key}",
                json=series,
            ) as raw_response:
                json_res = await raw_response.json()
                print(json_res)

                await ctx.send(
                    f"adding :{Pending_Requests[int(approve_select[0]) - 1]['Title']}"
                )
                await PendingRequest.delete().where(
                    PendingRequest.id
                    == Pending_Requests[int(approve_select[0]) - 1]["id"]
                )
    elif len(Pending_Requests) > 0:
        Pending_embed = nextcord.Embed()
        for i in range(len(Pending_Requests)):
            Pending_embed.add_field(
                name=(f"{i+1}.{Pending_Requests[i]['Title']}"),
                inline=False,
                value=f"requested by: {Pending_Requests[i]['requester_name']}",
            )
        await ctx.send(embed=Pending_embed)
    else:
        await ctx.send("no pending requests")


@bot.command()
async def deny(ctx, *deny_select):
    Pending_Requests = await PendingRequest.select()

    if deny_select and len(Pending_Requests) > 0:

        print(deny_select)

        await PendingRequest.delete().where(
            PendingRequest.id == Pending_Requests[int(deny_select[0]) - 1]["id"]
        )

        await ctx.send(
            f"Denied request for :{Pending_Requests[int(deny_select[0]) - 1]['Title']} "
        )
    elif len(Pending_Requests) > 0:
        Pending_embed = nextcord.Embed()

        for i in range(len(Pending_Requests)):
            Pending_embed.add_field(
                name=(f"{i+1}.{Pending_Requests[i]['Title']}"),
                inline=False,
                value=f"requested by: {Pending_Requests[i]['requester_name']}",
            )
        await ctx.send(embed=Pending_embed)
    else:
        await ctx.send("no pending requests")


bot.run(discord_token)
