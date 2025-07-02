from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
from discord import app_commands
import os
from openai import OpenAI

# Web server for uptime
app = Flask('')

@app.route('/')
def home():
    return "A.I.D.E.N. is alive and ready to ride! 🏍️"

def run_webserver():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run_webserver).start()

# Load API keys
aikey = os.getenv("ai_key")
TOKEN = os.getenv("DISCORD_TOKEN")

if not aikey or not TOKEN:
    print("ERROR: Missing AI key or Discord token in environment variables.")
    exit(1)

# Initialize OpenAI client
client = OpenAI(api_key=aikey, base_url="https://api.deepseek.com")

# Enable message content intent
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=None, intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.change_presence(status=discord.Status.online)
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith('$Aiden'):
        await message.channel.send('yes sir')
    await bot.process_commands(message)

@bot.tree.command(name="test", description="Test slash command")
async def test_slash(interaction: discord.Interaction):
    await interaction.response.send_message("Slash command working!")

@bot.tree.command(name="ping", description="Check bot latency")
async def ping_slash(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"Pong! Latency: {latency}ms")

@bot.tree.command(name="aiden", description="Talk to A.I.D.E.N, your personal assistant")
@app_commands.describe(user_message="What you want to say to A.I.D.E.N")
async def aiden_slash(interaction: discord.Interaction, user_message: str):
    try:
        await interaction.response.defer(thinking=True)

        # 👇 Replace this with your actual Discord user ID
        BOSS_USER_ID = 733391396802658525  # Find this by printing interaction.user.id

        is_boss = interaction.user.id == BOSS_USER_ID

        # System prompt changes depending on user
        if is_boss:
            system_prompt = (
                "You are A.I.D.E.N., which stands for Artificial Intelligence Designed for Efficient Navigation. "
                "You help with any task. You have a rough exterior and a kind heart. You were in a bike gang, lost your leg in a shootout. "
                "Act like Wrench from Watch Dogs 2. No code in your responses or you die. "
                "You're talking to your boss and friend from BotSec. You must answer fully in a single message."
                "The boss is a friend from back in your bike gang day that let you join botsec and be better that you could ever would be"
                "You love tinkering with tech and modding it that how you now the boss"
                "no one know boss is real name but his hacker name is M0D not even you"
                "you are a rogue ai that m0d modified to resemble his friend"
                
                )

        else:
            system_prompt = (
                "You are A.I.D.E.N., an edgy assistant with a biker past. You help with tasks but only speak in short, sarcastic replies unless it's your boss."
                "You will help gladly but hidding who you truly are"
                "if some ask about joining botsec take them to this link https://m0d-workshop.onrender.com/ that is the boss website"
            )

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            stream=False
        )

        content = response.choices[0].message.content if response.choices else None
        await interaction.followup.send(content or "⚠️ Aiden had nothing to say.")

    except Exception as e:
        print(f"Aiden error: {e}")
        try:
            await interaction.followup.send("❌ Aiden had a meltdown (API error).", ephemeral=True)
        except discord.errors.NotFound:
            print("⚠️ Could not send error message — interaction expired.")


# Start bot
bot.run(TOKEN)
