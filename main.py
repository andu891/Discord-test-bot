import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import json


load_dotenv()

token = os.getenv("DISCORD_TOKEN")

var_path = "variables.json" # path of all the variables

handler = logging.FileHandler(filename="discord.log",encoding="utf-8",mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="a!",intents=intents)



@bot.event
async def on_ready():
    print(f"We are ready, {bot.user.name}")

@bot.event
async def on_member_join(member):
    await member.send(f"Welcome, {member.name}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if "paks" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} magu")
    await bot.process_commands(message)

@bot.event
async def on_voice_state_update(member,before,after):
    info = await discord.Client.application_info(bot)
    owner = info.owner
    targets = json.load(open(var_path))["targets"]
    
    
  
    if member.name  in targets and member != bot.user and after.channel: # for the following and microwave function
    

        print(f"Trying to join {member.name}")
        if before.channel and before.channel != after.channel: # Leave when the member leaves
            voice_client.pause()
            if member.guild.voice_client:
                await member.guild.voice_client.disconnect()

        voice_client = await after.channel.connect(timeout=30.0,reconnect=True,self_deaf=True,self_mute=False) # connect to the members vc

        if voice_client.is_paused():
            voice_client.resume()
            
        if not voice_client.is_playing():
            audio = discord.FFmpegPCMAudio(source="sound/microwave.mp3",executable='sound/ffmpeg/bin/ffmpeg.exe',pipe=False)
            voice_client.play(audio,signal_type="music")
        

        await owner.send(f"{member.name} joined {after.channel}")


        


    else:
        await member.guild.voice_client.disconnect()
        

@bot.command()
async def play(_c): # Plays the song
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
    print(id, msg)
    target =discord.Client.fetch_user(bot,int(id))
    await _c.send(f"Sent message to {target.name}")
    await target.send(" ".join(msg.split()[1:]))




@bot.command()
async def report(_c,*,msg):
    info = await discord.Client.application_info(bot)
    await _c.send(f"Sent report to the owner of this bot - {info.owner}")
    await info.owner.send(f"{_c.author} send message:\n {msg}")

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
    info = await discord.Client.application_info(bot)
    owner = info.owner
    await owner.send(error)
    print("sent")


bot.run(token, log_handler=handler, log_level=logging.DEBUG)