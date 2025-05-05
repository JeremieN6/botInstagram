# script.py
import os
import time
import random
from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired
from dotenv import load_dotenv
from datetime import datetime
import requests

# Load .env
if os.path.exists(".env.local"):
    load_dotenv(".env.local")

# Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage"
    params = {
        "chat_id": os.getenv('TELEGRAM_CHAT_ID'),
        "text": message,
    }
    requests.get(url, params=params)

# Test
send_telegram_message("✅ Test message - Bot is running.")

# Instagram
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

def run_bot(origin="manuel"):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    send_telegram_message(f"🚀 Script lancé en mode *{origin}* à {now}")

    cl = Client()
    try:
        if os.path.exists("settings.json"):
            cl.load_settings("settings.json")
            cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        else:
            raise Exception("Pas de settings.json")
    except ChallengeRequired:
        send_telegram_message("⚠️ Challenge Instagram requis.")
        return
    except Exception:
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        cl.dump_settings("settings.json")

    accounts = ["mathildtantot", "popstantot", "sophieraiin", "cecerose", "cece_rosee_", "yumi.etoo", "wettmelons", "devon.shae", "verofozzy"]
    random.shuffle(accounts)

    for account in accounts:
        try:
            send_telegram_message(f"🔍 Traitement de {account}...")
            user_id = cl.user_id_from_username(account)
            medias = cl.user_medias(user_id, 5)

            for media in medias:
                cl.media_like(media.id)
                send_telegram_message(f"❤️ Post liké de {account}")
                comments = cl.media_comments(media.id)
                for comment in comments[:5]:
                    cl.comment_like(comment.pk)
                    send_telegram_message(f"💬 Commentaire liké sur {account}")
                time.sleep(random.uniform(2, 4))
        except ChallengeRequired:
            send_telegram_message(f"🚫 Challenge required pour {account}")
        except Exception as e:
            send_telegram_message(f"❌ Erreur {account} : {e}")
        time.sleep(random.uniform(5, 10))

    send_telegram_message(f"✅ Script terminé à {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 👇 LANCE LE BOT
if __name__ == "__main__":
    run_bot()