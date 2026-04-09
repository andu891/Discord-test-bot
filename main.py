import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
from discord import EventStatus
from random import randint
import json



load_dotenv()

token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename="discord.log",encoding="utf-8",mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.members = True
intents.voice_states = True
intents.guild_scheduled_events = True

bot = commands.Bot(command_prefix="a!",intents=intents)

def get_vars():
    with open("vars.json", "r") as file:
        data = json.load(file)
        file.close
    return data
    
def set_vars(new_data) -> None:
    data = get_vars()
    with open("vars.json","w") as file:
        
        json.dump(data|new_data,file)
        file.close()





@bot.event
async def on_ready():
    print(f"We are ready, {bot.user.name}")
    info = await discord.Client.application_info(bot)
    set_vars({"owner_id":info.owner.id})
    
    
@bot.event
async def on_message(message): # 🗿
    text = message.clean_content
    owner = await get_owner()

    if message.author == bot.user:
        return
    if randint(1,100) == 1:
        await message.add_reaction("🗿")

    if "andu" in text and "lühike" in text:
        for reaction in ["👎","🫃","🐒"]:
            await message.add_reaction(reaction)

    if not message.guild and message.author  != owner:
        
        print("sent")
        await owner.send(f"{message.author}: {text}")
    await bot.process_commands(message)

@bot.event
async def on_voice_state_update(member,before,after): # microwave
    targets = get_vars()["targets"]
    voice_client = member.guild.voice_client
    
    if member.name  in targets and member != bot.user: # following and microwave function

        if not voice_client:# if the bot isn't connected to a channel connect it
            print(f"Trying to join {member.name}")
            voice_client = await after.channel.connect(timeout=30.0,reconnect=False,self_deaf=True,self_mute=False) 
        
        else:# updates the bots voice channel to the members
            await member.guild.change_voice_state(channel=after.channel,self_deaf=True,self_mute=False)# automatically leaves when channel is null

        

        if not voice_client.is_playing():# if the audio isn't playing play it 
            audio = discord.FFmpegPCMAudio(source="sound/microwave.mp3",executable='sound/ffmpeg/bin/ffmpeg.exe',pipe=False)
            voice_client.play(audio,signal_type="music")
    
@bot.event
async def on_scheduled_event_update(before,after): # Features: Event start message 
    print(after.status)
    print(before.status)
    if not before.status == EventStatus.active and after.status == EventStatus.active: # when the event has just started find general and send the message
        general_channel_name = G["general"]
        general_channel = list(filter(lambda channel: channel.name == general_channel_name,after.guild.channels))[0]
        print("started")
        await general_channel.send(f"{after.guild.default_role} {after.name} on alustanud!!!")

    
        
@bot.command()
async def reset_vars(_c):
    info = await discord.Client.application_info(bot)
    owner_id = info.owner.id
    set_vars({"targets":[],"owner":owner_id,"general":"general"})

@bot.command()
async def target(_c,*,msg):
    old = get_vars()["targets"]
    if old:
        set_vars({"targets":old.append(msg)})
    else:
        set_vars({"targets":[msg]})

    await _c.send(f"Added {msg} to targets")


@bot.command()
async def play(_c): # Plays the song
    #TODO: Make this actually use youtube links
    audio = discord.FFmpegPCMAudio(source="sound/song.mp3",executable="sound/ffmpeg/bin/ffmpeg.exe",pipe=False)
    _c.guild.voice_client.play(audio,signal_type="music")
    await _c.send(f"Playing song ")
    
@play.error
async def play_error(_c,error):
    await report_error(error)

@bot.command()
async def stop(_c): # Stops the song
    _c.guild.voice_client.stop()


@bot.command()
async def pause(_c): # Pauses the song
    _c.guild.voice_client.pause()


@bot.command()
async def resume(_c): # Resumes the song
    _c.guild.voice_client.resume()

@bot.command()
async def send(_c, *, msg):
    id = msg.split()[0]
    target = await discord.Client.fetch_user(bot,int(id))
    await _c.send(f"Sent message to {target.name}")
    await target.send(" ".join(msg.split()[1:]))




@bot.command()
async def report(_c,*,msg):
    owner = await get_owner()
    await owner.send(msg)
    

@bot.command()
async def join(_c): # Joins the authors vc
    await _c.channel.send(f"Joining {_c.author.voice.channel.name}")
    await _c.author.voice.channel.connect(timeout=30.0,reconnect=True,self_deaf=True,self_mute=False)
@join.error
async def join_error(_c, error):
    await report_error(error)

@bot.command()
async def leave(_c):# leaves vc
    await _c.guild.voice_client.disconnect()


@bot.command()
async def hello(_c): # greets author
    await _c.send(f"Hello {_c.author.mention}!")


@bot.command()
async def dm(_c,*,msg): # dm's author
    await _c.author.send(msg)

@bot.command()
async def reply(_c): # replies author
    await _c.reply("Replied!")



@bot.command() # creates a poll with reactions
async def poll(_c,*,question):
    embed = discord.Embed(title="New Poll",description=question)
    poll_message= await _c.send(embed=embed)
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎")


async def report_error( error):
    owner = await get_owner()
    await owner.send(error)

    
async def get_owner():
    id = get_vars()["owner_id"]
    return await discord.Client.fetch_user(bot,id)



bot.run(token, log_handler=handler, log_level=logging.DEBUG)