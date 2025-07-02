import os
import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from openai import OpenAI
import threading

app = Flask(__name__)

# Global status tracking for the bot
bot_ready = {"status": False, "name": "Unknown"}

@app.route("/", methods=["GET"])
def home():
    status = "🟢 Online" if bot_ready["status"] else "🔴 Offline"
    return f"Aiden Discord Bot Status: {status} (as {bot_ready['name']})", 200

def aiden():
    print("🔁 aiden() starting...")

    aikey = os.environ.get('ai_key')
    token = os.environ.get('DISCORD_TOKEN')
    print(f"🔐 Token prefix: {token[:10] if token else 'None'}")

    if not aikey:
        raise ValueError("AI_KEY environment variable not set")
    if not token:
        raise ValueError("DISCORD_TOKEN environment variable not set")

    client = OpenAI(api_key=aikey, base_url="https://api.deepseek.com")

    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix=None, intents=intents)

    @bot.event
    async def on_ready():
        bot_ready["status"] = True
        bot_ready["name"] = str(bot.user)
        print(f"✅ Discord bot logged in as {bot.user}")
        await bot.change_presence(status=discord.Status.online)
        try:
            synced = await bot.tree.sync()
            print(f"✅ Synced {len(synced)} slash command(s)")
        except Exception as e:
            print(f"❌ Failed to sync commands: {e}")

    @bot.event
    async def on_disconnect():
        bot_ready["status"] = False
        print("⚠️ Bot disconnected")

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
        await interaction.response.defer(thinking=True)
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an assistant named A.I.D.E.N., which stands for Artificial Intelligence Designed for Efficient Navigation. "
                            "You help with any task. You have a rough exterior and a kind heart. Before becoming an assistant, you were in a bike gang "
                            "and lost your leg in a shootout. Act like Wrench from Watch Dogs 2. No code in your responses or you die. "
                            "You must answer the message in the same message, not more than one."
                        )
                    },
                    {"role": "user", "content": user_message},
                ],
                stream=False
            )
            if response.choices and response.choices[0].message.content:
                await interaction.followup.send(response.choices[0].message.content)
            else:
                await interaction.followup.send("⚠️ Aiden had nothing to say.")
        except Exception as e:
            print(f"Aiden error: {e}")
            await interaction.followup.send("❌ Aiden had a meltdown (API error). Try again later.", ephemeral=True)

    try:
        bot.run(token)
    except Exception as e:
        bot_ready["status"] = False
        print(f"❌ Bot.run error: {e}")

if __name__ == "__main__":
    print("🚀 Starting bot thread...")
    threading.Thread(target=aiden, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
