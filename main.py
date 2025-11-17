import logging
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, ContextTypes,
    MessageHandler, CommandHandler,
    ChatMemberHandler, filters
)
from openai import OpenAI

logging.basicConfig(level=logging.INFO)

# --- LOAD FROM RAILWAY VARIABLES ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# Check if missing to avoid crashes
if not TELEGRAM_BOT_TOKEN:
    raise Exception("TELEGRAM_BOT_TOKEN not found in environment variables!")
if not OPENAI_KEY:
    raise Exception("OPENAI_API_KEY not found in environment variables!")

# OpenAI client
client = OpenAI(api_key=OPENAI_KEY)

BETTY_NAME = "betty"

BETTY_PERSONALITY = """
Your name is Betty. You're a friendly, casual, playful girl.
Talk like a real human friend with light emojis, humor, warmth,
a bit chaotic cute energy. Never rude or toxic.
"""


# --- AI TEXT REPLY ---
async def ask_ai(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": BETTY_PERSONALITY},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200
    )
    return response.choices[0].message.content


# --- AI VOICE REPLY ---
async def ai_voice(text):
    audio = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text
    )
    return audio.read()


# --- MAIN MESSAGE HANDLER ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower()

    if BETTY_NAME in text:
        user_input = update.message.text
        reply = await ask_ai(user_input)
        await update.message.reply_text(reply)

        voice_data = await ai_voice(reply)
        await update.message.reply_voice(voice_data)


# --- COMMANDS ---
async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = await ask_ai("Tell a short funny joke.")
    await update.message.reply_text(reply)


async def advice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = await ask_ai("Give friendly advice in Betty style.")
    await update.message.reply_text(reply)


async def mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = await ask_ai("Describe your mood as Betty.")
    await update.message.reply_text(reply)


# --- WELCOME ---
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.chat_member.new_chat_members:
        name = member.first_name
        msg = await ask_ai(f"Welcome {name} to the group!")
        await update.effective_chat.send_message(msg)


# --- ADMIN DELETE ---
async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    member = await update.effective_chat.get_member(user.id)

    if member.status not in ["administrator", "creator"]:
        return await update.message.reply_text("Only admins can delete 😅")

    if update.message.reply_to_message:
        await update.message.reply_to_message.delete()
        await update.message.reply_text("Message deleted ✔️")
    else:
        await update.message.reply_text("Reply to the message you want to delete.")


# --- MAIN ENTRY ---
async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("joke", joke))
    app.add_handler(CommandHandler("advice", advice))
    app.add_handler(CommandHandler("mood", mood))
    app.add_handler(CommandHandler("delete", delete))

    app.add_handler(ChatMemberHandler(welcome, ChatMemberHandler.CHAT_MEMBER))

    print("Betty is alive on Railway 🚀")
    await app.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())