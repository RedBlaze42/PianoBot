import arrow,discord
from discord import message

def find_event_in_channel(events,channel_id):
    event_ids=[event.message.id for event in events if event.message.channel.id==channel_id]
    if len(event_ids)==0: return None
    event=[event for event in events if event.message.id==max(event_ids)][0]
    return event

def event_from_id(events,message_id):
    event=[event for event in events if event.message.id==message_id]
    if len(event)==0: return None
    return event[0]

class DiscordEvent():

    def __init__(self,bot,event_date,max_participants,message,participants,name):
        self.bot=bot
        self.event_date=event_date
        self.max_participants=max_participants
        self.message=message
        self.participants=participants
        self.active=True
        self.name=name

    @classmethod
    async def from_command(cls,args,cmd_message,bot):#Commande: 10 14:14 08/04/2021
        try:
            max_participants=int(args[0])
            event_date=arrow.get(args[1]+" "+args[2],"HH:mm DD/MM/YYYY",tzinfo="Europe/Paris")
        except arrow.parser.ParserError:
            await cmd_message.channel.send("Le format de date n'est pas réspecté, piano fait un effort, exemple: {}".format(arrow.utcnow().to("Europe/Paris").format("HH:mm DD/MM/YYYY")))
            return None
        name=" ".join(args[3:])
        if name=="": name="Evènement"

        await cmd_message.delete()
        embed = discord.Embed(title="{} du {}:".format(name,event_date.format("DD/MM à HH:mm")), colour=discord.Colour(0xff0000), timestamp=event_date.datetime, description="Aucun participant, max {}".format(max_participants))
        message=await cmd_message.channel.send(embed=embed)
        await message.add_reaction("✅")
        await message.add_reaction("❌")
        return cls(bot,event_date,max_participants,message,list(),name)

    @classmethod
    async def from_json(cls,data,bot):
        channel=await bot.fetch_channel(data["channel_id"])
        message=await channel.fetch_message(data["message_id"])
        event_date=arrow.get(data["event_date_timestamp"]).to("Europe/Paris")
        return cls(bot,event_date,data["max_participants"],message,data["participants"],data["name"])

    def to_json(self):
        return {"channel_id":self.message.channel.id,
                "message_id":self.message.id,
                "event_date_timestamp":self.event_date.timestamp(),
                "max_participants":self.max_participants,
                "participants":self.participants,
                "name":self.name}

    async def add_participant(self,id,top=False):
        if not id in self.participants:
            if top:
                self.participants.insert(0,id)
            else:
                self.participants.append(id)
        await self.update_message()

    async def remove_participant(self,id):
        if id in self.participants:
            self.participants.remove(id)
        await self.update_message()

    async def update_message_state(self):
        self.message = await (await self.bot.fetch_channel(self.message.channel.id)).fetch_message(self.message.id)
        return self.message
    
    async def remove_reactions(self):
        reactions=(await self.update_message_state()).reactions
        for reaction in reactions:
            if isinstance(reaction.emoji,str) and reaction.emoji in ["✅","❌"]:
                users = await reaction.users().flatten()
                for user in users:
                    if not user.id==self.bot.user.id:
                        await reaction.remove(user)

    async def close(self):
        #embed = discord.Embed(title="{} du {}:".format(self.name,self.event_date.format("DD/MM à HH:mm")), colour=discord.Colour(0x000000), description="Evènement terminé")
        #await self.message.edit(embed=embed)
        await self.message.delete()
        self.active=False

    async def update_message(self):
        embed = discord.Embed(title="{} du {}:".format(self.name,self.event_date.format("DD/MM à HH:mm")), colour=discord.Colour(0xff0000), timestamp=self.event_date.datetime)
        embed.description="Max {} participants".format(self.max_participants)
        if len(self.participants)>0:
            participant_list="\n".join(["<@{}>".format(user_id) for user_id in self.participants[:self.max_participants]])
            embed.add_field(name="Participants:",value=participant_list)
        else:
            embed.description="Aucun participant, max {}".format(self.max_participants)
        if len(self.participants)>self.max_participants:
            participant_list="\n".join(["<@{}>".format(user_id) for user_id in self.participants[self.max_participants:]])
            embed.add_field(name="Remplaçants:",value=participant_list)

        await self.message.edit(embed=embed)
        await self.remove_reactions()