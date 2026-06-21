import discord
from discord.ext import commands
from datetime import timedelta, timezone, datetime
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

active_spams = {}
already_replied = set()
active_loopmutes = {}

@bot.event
async def on_ready():
    print(f'✅ Bot connecté en tant que {bot.user}')

@bot.command(name='spam')
async def spam(ctx, count: int, *, message: str):
    channel_id = ctx.channel.id

    if count > 5:
        await ctx.send("5 max negro c plus rapide")
        return

    if channel_id in active_spams:
        await ctx.send("att")
        return

    await ctx.message.delete()
    active_spams[channel_id] = True

    coros = [ctx.send(message) for _ in range(count)]
    await asyncio.gather(*coros)

    active_spams.pop(channel_id, None)

@bot.command(name='clear')
@commands.has_permissions(administrator=True)
async def clear(ctx, count: int):
    if count > 100:
        await ctx.send("100 max !")
        return
    await ctx.channel.purge(limit=count + 1)

@bot.command(name='ping')
async def ping(ctx):
    latence = round(bot.latency * 1000)
    await ctx.send(f'🏓 Pong ! {latence}ms')

@bot.command(name='loopmute')
@commands.has_permissions(administrator=True)
async def loopmute(ctx, member: discord.Member):
    if member.id in active_loopmutes:
        await ctx.send("❌ Déjà en cours pour ce membre !")
        return

    active_loopmutes[member.id] = True
    await ctx.message.delete()

    while active_loopmutes.get(member.id):
        await member.edit(mute=True)
        await asyncio.sleep(2)
        await member.edit(mute=False)
        await asyncio.sleep(2)

@bot.command(name='stoploopmute')
@commands.has_permissions(administrator=True)
async def stoploopmute(ctx, member: discord.Member):
    if member.id in active_loopmutes:
        active_loopmutes.pop(member.id)
        await member.edit(mute=False)
        await ctx.send(f"✅ Loop mute arrêté pour {member.mention}")
    else:
        await ctx.send("❌ Aucun loop mute en cours pour ce membre.")

@bot.command(name='spammute')
async def spammutevocal(ctx, member: discord.Member, count: int = 10):
    if not member.voice:
        await ctx.send("❌ Ce membre n'est pas en vocal !")
        return
    await ctx.message.delete()
    for _ in range(count):
        await member.edit(mute=True)
        await asyncio.sleep(0.3)
        await member.edit(mute=False)
        await asyncio.sleep(0.3)

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return
    if '🇮🇱' not in str(reaction.emoji):
        return
    key = reaction.message.id
    if key in already_replied:
        return
    already_replied.add(key)
    await asyncio.sleep(0.1)
    await reaction.message.reply(f"{reaction.message.author.mention} goy")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage : `/spam <nombre> <message>`")

import os
bot.run(os.environ['DISCORD_TOKEN'])
