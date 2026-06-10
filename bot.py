import discord
from discord.ext import commands
import asyncio
import os
from aiohttp import web

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

active_spams = {}
already_replied = set()
active_loopmutes = {}

# ── KEEP ALIVE (Railway) ────────────────────────────────────────────────────────

async def health_check(request):
    return web.Response(text="OK")

async def start_web():
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 8080)))
    await site.start()

# ── EVENTS ──────────────────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    print(f'✅ Bot connecté en tant que {bot.user}')
    await start_web()

# ── VOCAL 24/7 ──────────────────────────────────────────────────────────────────

@bot.command(name='connect')
async def connect(ctx):
    print(f"[DEBUG] connect appelé par {ctx.author} | voice: {ctx.author.voice}")
    if not ctx.author.voice:
        await ctx.send("❌ T'es même pas en vocal frère.")
        return

    channel = ctx.author.voice.channel
    print(f"[DEBUG] channel: {channel}")

    if ctx.guild.voice_client:
        await ctx.guild.voice_client.move_to(channel)
        await ctx.send(f"✅ Déplacé dans **{channel.name}**")
        return

    try:
        await channel.connect()
        await ctx.send(f"✅ Connecté dans **{channel.name}** 🔒")
    except Exception as e:
        print(f"[DEBUG] ERREUR connect: {e}")
        await ctx.send(f"❌ Erreur : {e}")
        
    async def keep_alive():
        while True:
            await asyncio.sleep(30)
            if not ctx.guild.voice_client:
                break
            if not ctx.guild.voice_client.is_connected():
                try:
                    await channel.connect()
                except Exception:
                    pass

    bot.loop.create_task(keep_alive())

@bot.command(name='disconnect')
async def disconnect(ctx):
    if ctx.guild.voice_client:
        await ctx.guild.voice_client.disconnect()
        await ctx.send("👋 Déconnecté du vocal.")
    else:
        await ctx.send("❌ Je suis pas en vocal.")

# ── COMMANDES ───────────────────────────────────────────────────────────────────

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
async def stoploopmute(ctx, member: discord.Member):
    if member.id in active_loopmutes:
        active_loopmutes.pop(member.id)
        await member.edit(mute=False)
        await ctx.send(f"✅ Loop mute arrêté pour {member.mention}")
    else:
        await ctx.send("❌ Aucun loop mute en cours pour ce membre.")

@bot.command(name='spammute')
async def spammute(ctx, member: discord.Member, count: int = 10):
    if count > 5:
        await ctx.send("❌ 5 max !")
        return
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
    await reaction.message.reply(
        f"{reaction.message.author.mention} goy https://tenor.com/view/big-yahu-tel-aviv-impressed-netanyahu-israel-gif-13606388048953703900"
    )

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage : `/spam <nombre> <message>`")

bot.run(os.environ['DISCORD_TOKEN'])
