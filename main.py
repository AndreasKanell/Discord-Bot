import asyncio
from html import unescape
import aiohttp
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os 
import random

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

user_histories = {}
MAX_HISTORY = 10  # Keep the last 10 messages (to prevent the model from running out of memory)

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

# ---------------------------- Commands --------------------------------------------

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

# --------------- AI Interaction --------------------------------
# Helper function to split huge messages
async def send_long_message(channel, text, reference_message=None):
    chunk_size = 1900 # Slightly below 2000 for absolute safety
    # Split the text into chunks
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    
    for idx, chunk in enumerate(chunks):
        if idx == 0 and reference_message:
            # Reply to the user with the first chunk
            await reference_message.reply(chunk)
        else:
            # Send the remaining chunks sequentially
            await channel.send(chunk)

@bot.event
async def on_message(message):
    # Ignore messages sent by the bot itself to prevent loops
    if message.author.bot:
        return

    # Check if the bot was mentioned in the message
    if bot.user in message.mentions:
        # Show that the bot is "typing"
        async with message.channel.typing():
            # Remove the mention (e.g., @ProjectBot) from the user's text
            user_input = message.content.replace(f'<@{bot.user.id}>', '').strip()
            user_id = message.author.id

            # If the user hasn't spoken before, create an empty history
            if user_id not in user_histories:
                # You can place a System Prompt here for specific behavior
                user_histories[user_id] = [
                    {"role": "system", "content": "You are a helpful, conversational AI assistant on a Discord server. Give clear and practical answers."}
                ]

            # Add the current question to memory
            user_histories[user_id].append({"role": "user", "content": user_input})

            # Keep only the defined message limit (leaving the system prompt intact at index 0)
            if len(user_histories[user_id]) > MAX_HISTORY + 1:
                user_histories[user_id] = [user_histories[user_id][0]] + user_histories[user_id][-MAX_HISTORY:]

            # Prepare Ollama API call (Using /api/chat endpoint instead of /api/generate)
            url = "http://localhost:11434/api/chat"
            payload = {
                "model": "llama3.1", # Make sure this is the model you have downloaded
                "messages": user_histories[user_id],
                "stream": False
            }

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload) as response:
                        if response.status == 200:
                            data = await response.json()
                            ai_response = data['message']['content']

                            # Add the AI's response to memory so it remembers for next time
                            user_histories[user_id].append({"role": "assistant", "content": ai_response})

                            # Send the response using the new helper function for long texts
                            await send_long_message(message.channel, ai_response, reference_message=message)
                        else:
                            await message.reply(f"⚠️ Error communicating with local AI. Status: {response.status}")
            except Exception as e:
                await message.reply(f"❌ Connection error: {e}")

    # CRITICAL: Without this line, no other commands (like !weather or !trivia) will work!
    await bot.process_commands(message)

# weather 
@bot.command()
async def weather(ctx, *,  city: str):
    API_KEY="b997d99e6b49cb7ec166cebecd5f2367"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=el"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    city_name = data["name"]
                    country = data["sys"]["country"]
                    temp = data["main"]["temp"]
                    feels_like = data["main"]["feels_like"]
                    humidity = data["main"]["humidity"]
                    description = data["weather"][0]["description"].capitalize()
                    icon_code = data["weather"][0]["icon"] 

                    embed = discord.Embed(
                        title=f"🌤️ Καιρός σε {city_name}, {country}",
                        color=discord.Color.blue()
                    )
                    
                    embed.add_field(name="Θερμοκρασία", value=f"{temp}°C", inline=True)
                    embed.add_field(name="Αίσθηση", value=f"{feels_like}°C", inline=True)
                    embed.add_field(name="Υγρασία", value=f"{humidity}%", inline=True)
                    embed.add_field(name="Συνθήκες", value=description, inline=False)
                    
                    embed.set_thumbnail(url=f"http://openweathermap.org/img/wn/{icon_code}@2x.png")

                    await ctx.send(embed=embed)
                
                elif response.status == 404:
                    await ctx.send(f"❌ Η περιοχή '{city}' δεν βρέθηκε. Δοκίμασε με λατινικούς χαρακτήρες (π.χ. Athens).")
                else:
                    await ctx.send(f"⚠️ Πρόβλημα με το API. Κωδικός σφάλματος: {response.status}")
                    
        except Exception as e:
            await ctx.send(f"❌ Σφάλμα σύνδεσης: {e}")


class TriviaView(discord.ui.View):
    def __init__(self, correct_label, correct_answer, author):
        #  15 seconds timout
        super().__init__(timeout=15.0) 
        self.correct_label = correct_label
        self.correct_answer = correct_answer
        self.author = author
        self.message = None 

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("❌ This is not your trivia question!", ephemeral=True)
            return False
        return True

    
    async def process_answer(self, interaction: discord.Interaction, choice: str):
        # disable all the buttons
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)

        # sends the answer
        if choice == self.correct_label:
            await interaction.response.send_message(f"✅ Correct! The answer is **{self.correct_answer}**.")
        else:
            await interaction.response.send_message(f"❌ Wrong! The correct answer was **{self.correct_label}** ({self.correct_answer}).")
        
        self.stop()

    @discord.ui.button(label="A", style=discord.ButtonStyle.primary)
    async def btn_a(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_answer(interaction, "A")

    @discord.ui.button(label="B", style=discord.ButtonStyle.primary)
    async def btn_b(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_answer(interaction, "B")

    @discord.ui.button(label="C", style=discord.ButtonStyle.primary)
    async def btn_c(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_answer(interaction, "C")

    @discord.ui.button(label="D", style=discord.ButtonStyle.primary)
    async def btn_d(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_answer(interaction, "D")

    # if 15 have passed
    async def on_timeout(self):
        if self.message:
            for child in self.children:
                child.disabled = True
            await self.message.edit(view=self)
            await self.message.reply(f"⏳ Time is up! The correct answer was **{self.correct_label}** ({self.correct_answer}).")

# tech quiz command
@bot.command()
async def quiz(ctx):
    url = "https://opentdb.com/api.php?amount=1&category=18&type=multiple"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data["response_code"] != 0:
                        await ctx.send("⚠️ Could not fetch a trivia question at the moment.")
                        return

                    question_data = data["results"][0]
                    question = unescape(question_data["question"])
                    correct_answer = unescape(question_data["correct_answer"])
                    incorrect_answers = [unescape(ans) for ans in question_data["incorrect_answers"]]

                    all_options = incorrect_answers + [correct_answer]
                    random.shuffle(all_options)

                    labels = ["A", "B", "C", "D"]
                    options_dict = {labels[i]: all_options[i] for i in range(4)}
                    correct_label = [k for k, v in options_dict.items() if v == correct_answer][0]

                    options_text = "\n".join([f"**{k}.** {v}" for k, v in options_dict.items()])

                    embed = discord.Embed(
                        title="🧠 Tech Trivia Time!",
                        description=f"**{question}**\n\n{options_text}",
                        color=discord.Color.purple()
                    )

                    embed.set_footer(text="Click a button below. You have 15 seconds!")

                    
                    view = TriviaView(correct_label, correct_answer, ctx.author)
                    
                    message = await ctx.send(embed=embed, view=view)
                    
                    view.message = message

                else:
                    await ctx.send(f"⚠️ API Error. Status code: {response.status}")
                    
        except Exception as e:
            await ctx.send(f"❌ Connection error: {e}")

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
        name="🤖 AI Interaction",
        value=f"`@{bot.user.name} [question]` - Mention the bot to chat with the local AI model (Llama 3.1) with conversational memory.",
        inline=False
    )

    embed.set_footer(
        text=f"Requested from {ctx.author.display_name}",
        icon_url=ctx.author.display_avatar.url
    )

    # Weather Command
    embed.add_field(
        name="🌤️ Weather", 
        value="`!weather [city]` - Displays the current weather conditions and temperature for the specified city.", 
        inline=False
    )

    # Quiz Command
    embed.add_field(
        name="🧠 Quiz", 
        value="`!quiz` - Starts a 15-second interactive multiple-choice tech quiz using buttons.", 
        inline=False
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
