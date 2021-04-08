
from gtts import gTTS
import discord

async def say(message,args,bot):
    content=" ".join(args[1:])
    if content!="":
        tts=gTTS(content,lang="fr")
        tts.save("temp.mp3")
        if len(bot.voice_clients)>0:
            voice=bot.voice_clients[0]
            if voice.channel.id!=message.author.voice.channel.id:
                await voice.disconnect()
                voice = await message.author.voice.channel.connect()
        else:
            voice = await message.author.voice.channel.connect()
        source=discord.FFmpegPCMAudio("temp.mp3")
        voice.play(source, after=None)