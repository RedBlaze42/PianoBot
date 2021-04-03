import discord,json,pyttsx3,asyncio

def load_config():
    with open("config.json","r") as file:
        bot.config=json.load(file)

def save_config():
    with open("config.json","w") as file:
        json.dump(bot.config,file)

bot=discord.Client()

load_config()

@bot.event
async def on_ready():
    print("Bot ready")
    bot.tts = pyttsx3.init()
    bot.tts.setProperty('rate', 140) 
    bot.tts.setProperty('voice', bot.tts.getProperty('voices')[0].id)

@bot.event
async def on_message(message):
    if message.guild.id==bot.config["server"] and message.content.startswith("!piano"):
        args=message.content.split(" ")[1:]
        try:
            if len(args)>0 and args[0]=="event" and message.author.guild_permissions.manage_messages:
                max_participants=int(args[1])
            elif len(args)>0 and args[0]=="say" and message.author.guild_permissions.manage_messages and message.author.voice is not None:
                
                bot.tts.save_to_file(" ".join(args[1:]), 'temp.mp3')
                bot.tts.runAndWait()
                if len(bot.voice_clients)>0:
                    voice=bot.voice_clients[0]
                    if voice.channel.id!=message.author.voice.channel.id:
                        await voice.disconnect()
                        voice = await message.author.voice.channel.connect()
                else:
                    voice = await message.author.voice.channel.connect()
                source=discord.FFmpegPCMAudio("temp.mp3")
                voice.play(source, after=None)

        except (IndexError, ValueError):
            message.channel.send("Mauvais paramètres")


bot.run(bot.config["token"])