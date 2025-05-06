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
        
    MAX_ACCOUNTS = 5  # à ajuster, par exemple 3 à 5 comptes max par session
    MAX_LIKES_PER_ACCOUNT = 3  # on ne like que 3 posts max
    MAX_COMMENT_LIKES_PER_POST = 2  # on ne like que 2 commentaires max par post

    accounts = ["mathildtantot", "popstantot", "sophieraiin", "cecerose", "cece_rosee_", "yumi.etoo", "wettmelons", "devon.shae"]
    random.shuffle(accounts)

    accounts = ["mathildtantot", "popstantot", "sophieraiin", "cecerose", "cece_rosee_", "yumi.etoo", "wettmelons", "devon.shae", "verofozzy"]
    random.shuffle(accounts)

    for i, account in enumerate(accounts[:MAX_ACCOUNTS]):  # ⬅️ Limite le nombre d'accounts traités
        try:
            send_telegram_message(f"🔍 Traitement de {account}...")

            user_id = cl.user_id_from_username(account)
            medias = cl.user_medias(user_id, 5)
            random.shuffle(medias)

            for media in medias[:MAX_LIKES_PER_ACCOUNT]:  # ⬅️ Limite les likes par compte
                cl.media_like(media.id)
                send_telegram_message(f"❤️ Post liké de {account}")

                comments = cl.media_comments(media.id)
                for comment in comments[:MAX_COMMENT_LIKES_PER_POST]:  # ⬅️ Limite les likes de commentaires
                    cl.comment_like(comment.pk)
                    send_telegram_message(f"💬 Commentaire liké sur {account}")

                time.sleep(random.uniform(4, 7))  # pause entre posts

        except ChallengeRequired:
            send_telegram_message(f"🚫 Challenge required pour {account}")
        except Exception as e:
            send_telegram_message(f"❌ Erreur {account} : {e}")

        time.sleep(random.uniform(15, 25))  # pause entre comptes

    send_telegram_message(f"✅ Script terminé à {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 👇 LANCE LE BOT
if __name__ == "__main__":
    run_bot()