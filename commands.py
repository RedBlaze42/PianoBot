from asyncio import sleep
from gtts import gTTS
import discord

async def say(message,args,bot,channel):
    content=" ".join(args[1:])
    if content!="":
        if message.author.id!=70046836743745536:
            tts=gTTS(content,lang="fr",tld="fr")
        else:
            tts=gTTS(content,lang="fr",tld="ca")
        tts.save("temp.mp3")
        if len(bot.voice_clients)>0:
            voice=bot.voice_clients[0]
            if voice.channel.id!=channel.id:
                await voice.disconnect()
                voice = await channel.connect()
                await sleep(2)
        else:
            voice = await channel.connect()
            await sleep(2)
        
        source=discord.FFmpegPCMAudio("temp.mp3")
        voice.play(source, after=None)

async def disconnect(bot):
    if len(bot.voice_clients)>0:
        voice=bot.voice_clients[0]
        await voice.disconnect()