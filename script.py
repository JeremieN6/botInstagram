# script.py
import os
import time
import random
import logging
from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired
from dotenv import load_dotenv
from telegram import Bot
from datetime import datetime

# Load .env
if os.path.exists(".env.local"):
    load_dotenv(".env.local")

# Telegram init
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")
bot = Bot(token=bot_token)

def send_telegram_log(message):
    bot.send_message(chat_id=chat_id, text=message)

# Instagram init
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

def run_bot(origin="manuel"):
    send_telegram_log(f"🚀 Script lancé ({origin}) - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    cl = Client()
    try:
        if os.path.exists("settings.json"):
            cl.load_settings("settings.json")
            cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        else:
            raise Exception("Pas de settings.json")
    except ChallengeRequired:
        send_telegram_log("⚠️ Challenge Instagram requis.")
        return
    except Exception:
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        cl.dump_settings("settings.json")

    accounts = ["mathildtantot", "popstantot", "sophieraiin", "cecerose", "cece_rosee_", "yumi.etoo", "wettmelons", "devon.shae", "verofozzy"]
    random.shuffle(accounts)

    for account in accounts:
        try:
            send_telegram_log(f"🔍 Traitement de {account}...")
            user_id = cl.user_id_from_username(account)
            medias = cl.user_medias(user_id, 5)

            for media in medias:
                cl.media_like(media.id)
                send_telegram_log(f"❤️ Post liké de {account}")
                comments = cl.media_comments(media.id)
                for comment in comments[:5]:
                    cl.comment_like(comment.pk)
                    send_telegram_log(f"💬 Commentaire liké sur {account}")
                time.sleep(random.uniform(2, 4))
        except ChallengeRequired:
            send_telegram_log(f"🚫 Challenge required pour {account}")
        except Exception as e:
            send_telegram_log(f"❌ Erreur {account} : {e}")
        time.sleep(random.uniform(5, 10))

    send_telegram_log("✅ Script terminé.")
