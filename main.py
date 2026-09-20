import aiohttp
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os 

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')

@bot.event
async def on_ready():
    print(f"{bot.user.name} is online !")

# welcome system
@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}")

    welcome_channel = bot.get_channel(1550534317841580142)

    embed = discord.Embed(
        title=f"Welcome to the server {member.display_name}",
        description=f"Please read the rules {member.mention}",
        color=0xeb4034,
        timestamp=discord.utils.utcnow()
    )

    embed.set_footer(
        text="Welcome to our server", 
        icon_url=member.display_avatar.url
    )
    embed.set_thumbnail(url=member.display_avatar.url)

    if welcome_channel:
        await welcome_channel.send(f"{member.mention} just joined us!", embed=embed)
        pass

    role = discord.utils.get(member.guild.roles, name="Member")

    if role:
        await member.add_roles(role)

# ----------------------- LOGS ---------------------------
# Deleted message
@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return

    log_channel = bot.get_channel(1550541849029124176)

    embed = discord.Embed(
        title="🗑️ Deleted message",
        description=f"A message from {message.author.mention} deleted at {message.channel.mention}",
        color=discord.Color.red(),
        timestamp=discord.utils.utcnow()
    )

    if message.content:
        embed.add_field(name="Content", value=message.content, inline=False)
    
    if log_channel:
        await log_channel.send(embed=embed)

# Edited message
@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content:
        return
    
    log_channel = bot.get_channel(1550549936687550474)
    
    embed = discord.Embed(
        title="✏️ Edited Message",
        description=f"{before.author.mention} edited a message at {before.channel.mention}",
        color=discord.Color.yellow(),
        timestamp=discord.utils.utcnow()
    )
    
    embed.add_field(name="Before", value=before.content, inline=False)
    embed.add_field(name="After", value=after.content, inline=False)
    
    embed.add_field(name="Link", value=f"[See the new message]({after.jump_url})", inline=False)
    
    if log_channel:
        await log_channel.send(embed=embed)

# Member leave
@bot.event
async def on_member_remove(member):
    log_channel = bot.get_channel(1550552704663949437)
    
    embed = discord.Embed(
        title="👋 Member left",
        description=f"User **{member.name}** ({member.mention}) left the server.",
        color=discord.Color.dark_gray(),
        timestamp=discord.utils.utcnow()
    )
    
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"User ID: {member.id}")

    if log_channel:
        await log_channel.send(embed=embed)

# Member update
@bot.event
async def on_member_update(before, after):
    log_channel = bot.get_channel(1550553663939018993)
    if not log_channel:
        return

    if before.nick != after.nick:
        embed = discord.Embed(
            title="📝 Nickname changed",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_author(name=after.name, icon_url=after.display_avatar.url)
        
        old_name = before.nick if before.nick else before.name
        new_name = after.nick if after.nick else after.name
        
        embed.add_field(name="Old", value=old_name, inline=True)
        embed.add_field(name="New", value=new_name, inline=True)
        
        await log_channel.send(embed=embed)

    if before.roles != after.roles:
        embed = discord.Embed(
            title="🎭 Roles changed",
            description=f"The roles of {after.mention} have been updated",
            color=discord.Color.purple(),
            timestamp=discord.utils.utcnow()
        )
        
        added_roles = [role.mention for role in after.roles if role not in before.roles]
        removed_roles = [role.mention for role in before.roles if role not in after.roles]
        
        if added_roles:
            embed.add_field(name="Added", value=" ".join(added_roles), inline=False)
        if removed_roles:
            embed.add_field(name="Removed", value=" ".join(removed_roles), inline=False)
            
        await log_channel.send(embed=embed)

# !hello 
@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention} !")

# !add_role
@bot.command()
async def add_role(ctx):
    role = discord.utils.get(ctx.guild.roles, name="test-role")
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{role} has been assigned to {ctx.author.mention}")
    else:
        await ctx.send("Role does not exist !")

# !remove_role
@bot.command()
async def remove_role(ctx):
    role = discord.utils.get(ctx.guild.roles, name="test-role")
    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(f"{role} has been removed from {ctx.author.mention}")
    else:
        await ctx.send("Role does not exist !")

# dm to a user
@bot.command()
async def dm(ctx, *, msg):
    await ctx.author.send(f"You said {msg}")

# reply to user at the specific chat
@bot.command()
async def reply(ctx, *, msg):
    await ctx.reply(f"You send {msg}") 

# clear messages
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, ammount: int):
    await ctx.channel.purge(limit=ammount+1)

# kick command
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"✅ {member.mention} has been kicked from the server. Reason: {reason}")

# ban command
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"✅ {member.mention} has been banned from the server. Reason: {reason}")

# ping command
@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latency is {latency} ms.")

# server info command
@bot.command()
async def serverinfo(ctx):
    server = ctx.guild

    embed = discord.Embed(
        title="Server Information",
        description=f"Statistics for the server {server.name}",
        color=0xeb4034
    )

    embed.add_field(name="👑 Owner", value=server.owner.mention, inline=False)
    embed.add_field(name="👥 Members", value=server.member_count, inline=False)
    embed.add_field(name="📅 Created at", value=server.created_at.strftime("%d/%m/%Y"), inline=False)

    if server.icon:
        embed.set_thumbnail(url=server.icon.url)

    await ctx.send(embed=embed)

# Ask command (Connected to local AI model)
@bot.command()
async def ask(ctx, *, prompt: str):
    wait_msg = await ctx.send("🤔 Thinking about the answer... (may take some time)")

    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": "llama3.1:latest", 
        "prompt": prompt,
        "stream": False
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    answer = data.get("response", "I didn't get the answer from the model.")
                    
                    if len(answer) > 1950:
                        answer = answer[:1950] + "\n... [The answer was cut due to words limit]"
                        
                    await wait_msg.edit(content=answer)
                else:
                    await wait_msg.edit(content=f"⚠️ Communication error: Code {response.status}")
        
        except aiohttp.ClientConnectorError:
            await wait_msg.edit(content="❌ I couldn't connect to Ollama. Please make sure that the Ollama app is running at the backround of your pc.")

# Help command
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title = "🛠️ Help Menu",
        description="Here you can find all the available commands of the bot. The prefix is '!' ",
        color=discord.Color.gold(),
        timestamp=discord.utils.utcnow()
    )

    #Managment
    embed.add_field(
        name="🛡️ Moderation",
        value=" `!clear [number]` - Mass delete of messages\n"
              "`!kick [@user] [reason]` - Kicks a user\n"
              "`!ban [@user] [reason]` - Bans a user permanently",
        inline=False
    )

    # Info
    embed.add_field(
        name="ℹ️ Info",
        value="`!ping` - Shows the latency\n"
               "`!serverinfo` - Shows the statistics of a server",
        inline=False
    )

    # AI
    embed.add_field(
        name="🤖 AI",
        value="`!ask [question]` - The user interacts with an AI model (llama 3.1) that answers the user's question",
        inline=False
    )

    embed.set_footer(
        text=f"Requested from {ctx.author.display_name}",
        icon_url=ctx.author.display_avatar.url
    )

    await ctx.send(embed=embed)


# Error Handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing a required argument! Please check your command and try again.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid argument type provided. Please check your input.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("⛔ You do not have the required permissions to execute this command!")
    elif isinstance(error, commands.CommandNotFound):
        pass 
    else:
        print(f"An unexpected error occurred: {error}")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
