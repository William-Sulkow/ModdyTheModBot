import json
import time
import discord.utils
from discord.ext import commands

client = commands.Bot(command_prefix='.')
client.data = {}

bot_id = 995417323416604753


def pwd():
    with open("key.txt") as f:
        return f.read()


def dump_data():
    with open("data.json", "r+") as data_file:
        data_file.truncate(0)
        data_file.write(json.dumps(client.data))


def strike(u, g_id):
    client.data[g_id]["struck"].append(u)


async def report(msg):
    await msg.author.ban()

    embed = discord.Embed(title="BLACKLIST ALERT", description=f"Message: {msg.content}", colour=discord.Colour.red())
    embed.set_footer(text=time.strftime("%a, %d-%b-%Y %T EST", time.gmtime()))
    embed.set_author(name=f"{msg.author.display_name}")
    embed.set_thumbnail(url=msg.author.avatar_url)

    await client.get_channel(client.data[str(msg.guild.id)]["admin_channel"]).send(embed=embed)

    strike(msg.author.id, str(msg.guild.id))
    await msg.author.send(f"```🔴🔴🔴YOU HAVE BEEN PERMANENTLY BANNED FROM **{msg.guild.name}**🔴🔴🔴```")

    dump_data()


@client.event
async def on_ready():
    with open("data.json") as f:
        d = json.loads(f.read())
    client.data = d
    print('Bot Initiated!')


@client.event
async def on_message(msg):
    g_id = str(msg.guild.id)
    author = msg.author

    if g_id in client.data and author.id != bot_id and client.data[g_id]["admin_channel"] != msg.channel.id:
        data = client.data[str(msg.guild.id)]
        if [] not in (data["blacklist"], data["whitelist"]) and [r.name for r in author.roles if
                                                                 r.name in data["whitelist"]] == []:
            for word in data["blacklist"]:
                if word in msg.content:
                    await msg.delete()
                    await report(msg)

    await client.process_commands(msg)


@client.command()
@commands.has_role("ModdyController")
async def clear(ctx):
    await ctx.channel.purge()


@client.command()
@commands.has_role("ModdyController")
async def admin_channel(ctx):
    g_id = str(ctx.guild.id)

    if g_id in client.data:
        client.data[g_id]["admin_channel"] = ctx.channel.id
    else:
        client.data[g_id] = {"admin_channel": ctx.channel.id, "blacklist": [], "whitelist": [], "struck": []}

    dump_data()

    await ctx.send(f"Admin channel has been set to {ctx.channel.name}", delete_after=3)
    await ctx.message.delete()


@client.command()
@commands.has_role("ModdyController")
async def blacklist(ctx, *s):
    g_id = str(ctx.guild.id)
    if g_id in client.data:
        data = client.data[g_id]

        if ctx.channel.id == data["admin_channel"]:
            word = ' '.join(s)
            if word not in data["blacklist"]:
                data["blacklist"].append(word)
                await ctx.send("Added!", delete_after=3)
            else:
                data["blacklist"].remove(word)
                await ctx.send("Removed!", delete_after=3)
        else:
            await ctx.send("```ERROR: cmd can only be sent in admin channel```", delete_after=3)
    else:
        await ctx.send("```ERROR: no admin channel set```", delete_after=3)

    await ctx.message.delete()

    dump_data()


@client.command()
@commands.has_role("ModdyController")
async def bl_send(ctx):
    g_id = str(ctx.guild.id)
    if g_id in client.data:
        if ctx.channel.id == client.data[g_id]["admin_channel"]:
            await ctx.author.send("\n".join(client.data[g_id]["blacklist"]))
        else:
            await ctx.send("```ERROR: cmd can only be sent in admin channel```", delete_after=3)
    else:
        await ctx.send("```ERROR: no admin channel set```", delete_after=3)

    await ctx.message.delete()


@client.command()
@commands.has_role("ModdyController")
async def wl_send(ctx):
    g_id = str(ctx.guild.id)
    if g_id in client.data:
        if ctx.channel.id == client.data[g_id]["admin_channel"]:
            await ctx.author.send("\n".join(client.data[g_id]["whitelist"]))
        else:
            await ctx.send("```ERROR: cmd can only be sent in admin channel```", delete_after=3)
    else:
        await ctx.send("```ERROR: no admin channel set```", delete_after=3)

    await ctx.message.delete()


@client.command()
@commands.has_role("ModdyController")
async def whitelist(ctx, r):
    guild = ctx.guild
    g_id = str(guild.id)

    if g_id in client.data:
        wl = client.data[g_id]["whitelist"]
        role = discord.utils.get(guild.roles, name=r)
        if role is not None:
            if role in wl:
                wl.remove(role.name)
                await ctx.send("Removed!", delete_after=3)
            else:
                wl.append(role.name)
                await ctx.send("Added!", delete_after=3)
        else:
            await ctx.send("```ERROR: role does not exist```", delete_after=3)
    else:
        await ctx.send("```ERROR: no admin channel set```", delete_after=3)

    await ctx.message.delete()

    dump_data()


@client.command()
@commands.has_role("ModdyController")
async def ub(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discrim = member.split("#")

    for ban_entry in banned_users:
        user = ban_entry.user
        if (user.name, user.discriminator) == (member_name, member_discrim):
            await ctx.guild.unban(user)
            await ctx.send("User has been unbanned!", delete_after=3)
            return


client.run(pwd())
