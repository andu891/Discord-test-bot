import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os


load_dotenv()

token = os.getenv("DISCORD_TOKEN")

magu_role = "paks"
target = "totallynotandresesaltaccount"

handler = logging.FileHandler(filename="discord.log",encoding="utf-8",mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!",intents=intents)



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
    voice_state = member.guild.voice_client
    owner = list(filter(lambda user: user.name == "andu891" ,member.guild.members))[0]
    
  
    if magu_role not in map(lambda x: x.name,member.roles): # only runs for members with the role
        return 
        
    if member == bot.user: # Doesn't run for bot itself
        return
    if after.channel: # If the after has a channel try to join
        print(f"Trying to join {member.name}")
        if before.channel and before.channel != after.channel: # if the member switches channels leave the previous vc before joining
            await voice_state.disconnect()
        await after.channel.connect(timeout=30.0,reconnect=True,self_deaf=True,self_mute=False) # connect to the members vc
        await owner.send(f"{member.name} joined {after.channel}")
    else:
        await voice_state.disconnect()
        







@bot.command()
async def hello(_c):
    await _c.send(f"Hello {_c.author.mention}!")


@bot.command()
async def dm(_c,*,msg):
    await _c.author.send(msg)

@bot.command()
async def reply(_c):
    await _c.reply("Replied!")



@bot.command()
async def poll(_c,*,question):
    embed = discord.Embed(title="New Poll",description=question)
    poll_message= await _c.send(embed=embed)
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎")


@bot.command()
async def assign(_c):
    role = discord.utils.get(_c.guild.roles,name=magu_role)
    if role:
        await _c.author.add_roles(role)
        await _c.send(f"{_c.author.mention} is now assigned {magu_role} role!")
    else:
        await _c.send("Role does not exist")


@bot.command()
async def remove(_c):
    role = discord.utils.get(_c.guild.roles,name=magu_role)
    if role:
        await _c.author.remove_roles(role)
        await _c.send(f"{_c.author.mention} has had {magu_role} role removed!")
    else:
        await _c.send("Role does not exist")

    
@bot.command()
@commands.has_role(magu_role)
async def munch(_c):
    await _c.send("MMMM Munch Munch")

@munch.error
async def munch_error(_c,error):
    await _c.send(f"{_c.author.mention},You aren't invited.")


bot.run(token, log_handler=handler, log_level=logging.DEBUG)