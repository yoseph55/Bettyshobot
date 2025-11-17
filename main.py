
import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes
)
from openai import OpenAI

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_KEY)

BETTY_NAME = "betty"

BETTY_STYLE = """
You are Betty. A friendly, playful, sweet girl who talks casually.
You respond like a real human friend, never formal or robotic.
You use emojis sometimes, you’re warm and supportive.
"""


async def ask_betty(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": BETTY_STYLE},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200
    )
    return response.choices[0].message.content


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = update.message.text.lower()

    if BETTY_NAME in text:
        user_msg = update.message.text
        reply = await ask_betty(user_msg)
        await update.message.reply_text(reply)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Heyyy I'm Betty 😘 Just mention my name and I'll talk!")


async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = await ask_betty("Tell a short joke.")
    await update.message.reply_text(reply)


async def advice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = await ask_betty("Give friendly life advice.")
    await update.message.reply_text(reply)


async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("joke", joke))
    app.add_handler(CommandHandler("advice", advice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Betty is alive! 💖")
    await app.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
