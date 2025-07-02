import os
import discord
from discord.ext import commands
from discord import app_commands
from openai import OpenAI

def aiden():
    
    aikey = os.environ.get('AI_KEY')
    token = os.environ.get('DISCORD_TOKEN')
    
    if not aikey:
        raise ValueError("AI_KEY environment variable not set")
    if not token:
        raise ValueError("DISCORD_TOKEN environment variable not set")


    # Initialize OpenAI client
    client = OpenAI(api_key=aikey, base_url="https://api.deepseek.com")

    # Enable message content intent
    intents = discord.Intents.default()
    intents.message_content = True

    # Initialize bot without command prefix (slash commands only)
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

    # Test slash command
    @bot.tree.command(name="test", description="Test slash command")
    async def test_slash(interaction: discord.Interaction):
        await interaction.response.send_message("Slash command working!")

    # Ping slash command
    @bot.tree.command(name="ping", description="Check bot latency")
    async def ping_slash(interaction: discord.Interaction):
        latency = round(bot.latency * 1000)
        await interaction.response.send_message(f"Pong! Latency: {latency}ms")

    # A.I.D.E.N slash command
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
                            "and lost your leg in a shootout. Act like Wrench from Watch Dogs 2. No code in your responses or you die."
                            "You must answer the message in the same message not in more than one message."
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

    bot.run(TOKEN)
