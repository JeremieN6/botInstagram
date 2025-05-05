# bot_launcher.py
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from script import run_bot
import os
from dotenv import load_dotenv

if os.path.exists(".env.local"):
    load_dotenv(".env.local")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot lancé à la main, traitement en cours...")
    run_bot(origin="manuel")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
