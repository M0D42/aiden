import os
import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask, request
from openai import OpenAI
import threading

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    print("[Flask] Health check endpoint hit")
    return "Aiden is alive!", 200

def aiden():
    print("[Bot] Starting bot setup...")

    aikey = os.environ.get('ai_key')
    token = os.environ.get('DISCORD_TOKEN')

    print(f"[Env] AI Key present? {'Yes' if aikey else 'No'}")
    print(f"[Env] Discord Token present? {'Yes' if token else 'No'}")
    if token:
        print(f"[Env] Discord Token starts with: {token[:4]}...")

    if not aikey:
        print("[Error] AI_KEY environment variable not set")
        return
    if not token:
        print("[Error] DISCORD_TOKEN environment variable not set")
        return

    try:
        client = OpenAI(api_key=aikey, base_url="https://api.deepseek.com")
        print("[OpenAI] Client initialized")
    except Exception as e:
        print(f"[Error] Failed to initialize OpenAI client: {e}")
        return

    intents = discord.Intents.default()
    intents.message_content = True
    print(f"[Discord] Intents set: message_content={intents.message_content}")

    # Use command_prefix="!" or None depending on your needs
    bot = commands.Bot(command_prefix=None, intents=intents)

    @bot.event
    async def on_ready():
        print(f"[Discord] Bot logged in as: {bot.user} (ID: {bot.user.id})")
        await bot.change_presence(status=discord.Status.online)
        try:
            synced = await bot.tree.sync()
            print(f"[Discord] Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"[Discord Error] Failed to sync commands: {e}")

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return
        print(f"[Discord] Message received from {message.author}: {message.content}")
        if message.content.startswith('$Aiden'):
            await message.channel.send('yes sir')
        await bot.process_commands(message)

    @bot.tree.command(name="test", description="Test slash command")
    async def test_slash(interaction: discord.Interaction):
        print("[Command] /test invoked")
        await interaction.response.send_message("Slash command working!")

    @bot.tree.command(name="ping", description="Check bot latency")
    async def ping_slash(interaction: discord.Interaction):
        latency = round(bot.latency * 1000)
        print(f"[Command] /ping invoked, latency={latency}ms")
        await interaction.response.send_message(f"Pong! Latency: {latency}ms")

    @bot.tree.command(name="aiden", description="Talk to A.I.D.E.N, your personal assistant")
    @app_commands.describe(user_message="What you want to say to A.I.D.E.N")
    async def aiden_slash(interaction: discord.Interaction, user_message: str):
        print(f"[Command] /aiden invoked with message: {user_message}")
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
            content = response.choices[0].message.content if response.choices else None
            print(f"[OpenAI] Response received: {content}")
            if content:
                await interaction.followup.send(content)
            else:
                await interaction.followup.send("⚠️ Aiden had nothing to say.")
        except Exception as e:
            print(f"[OpenAI Error] {e}")
            await interaction.followup.send("❌ Aiden had a meltdown (API error). Try again later.", ephemeral=True)

    try:
        print("[Bot] Running bot...")
        bot.run(token)
    except Exception as e:
        print(f"[Bot Error] Exception during bot.run(): {e}")

if __name__ == "__main__":
    print("[Main] Starting bot thread and Flask app")
    bot_thread = threading.Thread(target=aiden, daemon=True)
    bot_thread.start()
    app.run(host="0.0.0.0", port=10000)
