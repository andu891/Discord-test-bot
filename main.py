from discord.ext import commands
from dotenv import load_dotenv
from discord import EventStatus
from random import randint
from random import shuffle as shuffle_list
from audio_downloader import download_audio
from discord.ext import tasks, commands
from yt_api import search, playlist as get_playlist, get_title

import json
import os
import logging
import discord
import asyncio



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


### helpers
def get_vars() -> dict:
    with open("vars.json", "r") as file:
        data = json.load(file)
        file.close
    return data
    
def set_vars(new_data) -> None:
    data = get_vars()
    with open("vars.json","w") as file:
        
        json.dump(data|new_data,file)
        file.close()


async def report_error( error) -> None:
    owner = await get_owner()
    await owner.send(error)

    
async def get_owner() -> discord.user:
    id = get_vars()["owner_id"]
    return await discord.Client.fetch_user(bot,id)




### Events 
@bot.event
async def on_ready():
    print(f"We are ready, {bot.user.name}")
    info = await discord.Client.application_info(bot)
    set_vars({"owner_id":info.owner.id,"loop":False})
    global music
    music = music_player()
    
    
    
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
        
        await owner.send(f"{message.author}: {text}")
    await bot.process_commands(message)

    
@bot.event
async def on_scheduled_event_update(before,after): # Features: Event start message 

    if not before.status == EventStatus.active and after.status == EventStatus.active: # when the event has just started find general and send the message
        general_channel_name = get_vars()["general"]
        general_channel = list(filter(lambda channel: channel.name == general_channel_name,after.guild.channels))[0]
        await general_channel.send(f"{after.guild.default_role} {after.name} on alustanud!!!")

##### Cogs

class music_player(commands.Cog):
    def __init__(self):
        self.queue: list = []
        self.loop: bool = False
        self.play: bool = False
        self.voice_client: discord.VoiceClient = None
        self.current_song: str = ""
        self.player.start()
    
    def cog_unload(self):
        self.player.cancel()



    @tasks.loop(seconds=1.0)
    async def player(self):
        def __after__(id):
            if self.loop:
                self.queue.append(id)


        if bot.voice_clients:
            self.voice_client = bot.voice_clients[0]

        if not bot.voice_clients or not self.voice_client.is_playing():# if not doing anything clear presence
            await bot.change_presence()
        
        if self.voice_client and not self.voice_client.is_playing() and not self.voice_client.is_paused() and self.play and self.queue: # if not playing song and theres a queue play!
            
                    



            self.current_song = self.queue.pop(0)
            if self.current_song not in os.listdir(f"./sound/songs"):
                    await download_audio(self.current_song)
            path = f"sound/songs/{self.current_song}/" + os.listdir(f"./sound/songs/{self.current_song}")[0] # the path of the song file

            
            
            ##play song
            audio = discord.FFmpegPCMAudio(source=path, executable="sound/ffmpeg/bin/ffmpeg.exe")
            self.voice_client.play(audio,signal_type="music", after=lambda x: __after__(self.current_song))

            ##download next 2 songs
            for song in self.queue[0:2]:
                if song not in os.listdir(f"./sound/songs"):
                    asyncio.create_task(download_audio(song))
                    


            ##Change presence
            activity = discord.Activity(type=discord.ActivityType.listening, name=f"Playing {os.listdir(f'./sound/songs/{self.current_song}')[0][:-18]}")
            await bot.change_presence(activity=activity)


    @player.before_loop
    async def before_player(self):
        await bot.wait_until_ready()
        
        


###### Commands
@bot.command()
async def reset_vars(_c): # resets JSON file to default
    info = await discord.Client.application_info(bot)
    owner_id = info.owner.id
    set_vars({"targets":[],"owner":owner_id,"general":"general"})

@bot.command() 
async def target(_c,*,msg:str):# sets the target for microwave

    set_vars({"target":msg})
    await _c.send(f"Added {msg} to targets")


@bot.command()
async def play(_c,*,msg:str): # Plays a song from youtube URL
    voice_client = _c.guild.voice_client # the voice client of the bot
    id = msg[-11:]
    

    if "https" not in msg:
        id = search(msg) # get the id from the name
        if id == None:
            await _c.send("Error: Song not found")
            return
        
    
    if "&list=" in msg:
        id = get_playlist(msg.split("&")[1].replace("list=",""))
        
    


    if not voice_client:# if bots not in a channel connect
        voice_client = await _c.author.voice.channel.connect(timeout=30.0,reconnect=False,self_deaf=True,self_mute=False)

    music.play = True
    if type(id) == str :
        music.queue.append(id)
    elif type(id) == list:
        music.queue = music.queue + id
    
    await _c.send(f"Added to queue")


@play.error
async def play_error(_c,error):
    await report_error(error)
        

@bot.command()
async def loop(_c):
    

    if not _c.guild.voice_client or not _c.guild.voice_client.is_playing():
        await _c.send("Im not playing a song!")
        return

    music.loop = not music.loop
    if music.loop:
        await _c.send("Now Looping!")

    else:
        await _c.send("Stopped Looping!")

      

@bot.command()
async def shuffle(_c):
    if music.queue:
        shuffle_list(music.queue)
    await _c.send("Shuffled!")
    


@bot.command()
async def coinflip(_c):
    if randint(0,1) == 1:
        await _c.send("Heads")
    else:
        await _c.send("Tails")

        
@bot.command()
async def queue(_c,*,msg=1):
    out = ""
    i=10*(msg-1) + 1
    if msg == 1:
        out = f"Current: {os.listdir(f'./sound/songs/{music.current_song}')[0][0:-17]}\n" 


    titles = get_title(music.queue[10*(msg-1):10*msg])

    for name in titles:
        out += f"{i}. {name}\n"

    out += f"\npage {msg}\t\tlength  {len(music.queue)}"

    await _c.send(out)






@bot.command()
async def stop(_c): # Stops the song
    music.play = False
    music.queue = []
    _c.guild.voice_client.stop()

@bot.command()
async def skip(_c):
    _c.guild.voice_client.stop()

@bot.command()
async def pause(_c): # Pauses the song
    _c.guild.voice_client.pause()


@bot.command()
async def resume(_c): # Resumes the song
    _c.guild.voice_client.resume()

@bot.command()
async def send(_c, *, msg:str):
    id = msg.split()[0]
    target = await discord.Client.fetch_user(bot,int(id))
    await _c.send(f"Sent message to {target.name}")
    await target.send(" ".join(msg.split()[1:]))


@bot.command()
async def report(_c,*,msg:str):
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
async def create_guild(_c):
    guild = await discord.Client.create_guild(self=bot,name="test_server")
    guild: discord.Guild
    invite = await guild.channels[0].create_invite()
    await get_owner().send(invite)
    



@bot.command() # creates a poll with reactions
async def poll(_c,*,question:str):
    embed = discord.Embed(title="New Poll",description=question)
    poll_message= await _c.send(embed=embed)
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎")





bot.run(token, log_handler=handler, log_level=logging.DEBUG)