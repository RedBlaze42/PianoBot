import discord,json,asyncio,arrow
import commands,discord_event

def load_config():
    with open("config.json","r") as file:
        bot.config=json.load(file)

def save_config():
    bot.config["events"]=[event.to_json() for event in bot.events]
    with open("config.json","w") as file:
        json.dump(bot.config,file)

bot=discord.Client()

load_config()
bot.already_started=False

@bot.event
async def on_ready():
    if not bot.already_started:
        bot.events=[await discord_event.DiscordEvent.from_json(data,bot) for data in bot.config["events"]]
        print("Bot ready")
        bot.already_started=True

async def refresh_events():
    for event in bot.events:
        if (arrow.now()-event.event_date).total_seconds()>5*3600:
            await event.close()
            bot.events.remove(event)
    save_config()

@bot.event
async def on_message(message):
    if message.guild.id==bot.config["server"] and message.content.startswith("!piano"):
        args=message.content.split(" ")[1:]
        try:
            if len(args)>0 and args[0]=="event" and message.author.guild_permissions.manage_messages:
                event=await discord_event.DiscordEvent.from_command(args[1:],message,bot)
                if event is not None: bot.events.append(event)
                save_config()
            elif len(args)>0 and args[0]=="say" and message.author.voice is not None:
                commands.say(message,args,bot)
        except (IndexError, ValueError):
            await message.channel.send("Mauvais paramètres")

@bot.event
async def on_raw_reaction_add(payload):
    if payload.message_id in [event.message.id for event in bot.events]: await refresh_events()
    for event in bot.events:
        if payload.message_id==event.message.id and payload.emoji.is_unicode_emoji():
            if payload.emoji.name=="✅":
                await event.add_participant(payload.user_id)
                save_config()
            elif payload.emoji.name=="❌":
                await event.remove_participant(payload.user_id)
                save_config()

bot.run(bot.config["token"])