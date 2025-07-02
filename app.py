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
        print(f"Received interaction from {interaction.user} with message: {user_message}")
        await interaction.response.defer(thinking=True)
        print("Deferred interaction.")

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an assistant named A.I.D.E.N., which stands for Artificial Intelligence Designed for Efficient Navigation. "
                        "You help with any task. You have a rough exterior and a kind heart. Before becoming an assistant, you were in a bike gang "
                        "and lost your leg in a shootout. Act like Wrench from Watch Dogs 2. No code in your responses or you die. "
                        "You must answer the message in the same message not in more than one message."
                    )
                },
                {
                    "role": "user",
                    "content": f"Message from your boss/friend from BotSec: {user_message}"
                },
            ],
            stream=False
        )

        content = response.choices[0].message.content if response.choices else None
        if content:
            await interaction.followup.send(content)
        else:
            await interaction.followup.send("⚠️ Aiden had nothing to say.")

    except Exception as e:
        print(f"Aiden error: {e}")
        try:
            await interaction.followup.send("❌ Aiden had a meltdown (API error). Try again later.", ephemeral=True)
        except discord.errors.NotFound:
            print("⚠️ Could not send error message — interaction expired.")

# Start bot
bot.run(TOKEN)
