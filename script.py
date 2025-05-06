import os
import time
import random
from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, LoginRequired
from dotenv import load_dotenv
from datetime import datetime
import requests

# Load .env
if os.path.exists(".env.local"):
    load_dotenv(".env.local")

INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SETTINGS_PATH = "settings.json"

MAX_LIKES_PER_ACCOUNT = 3
MAX_COMMENT_LIKES_PER_POST = 10

ACCOUNTS_TO_TARGET = [
    "mathildtantot", "popstantot", "sophieraiin", "cecerose", 
    "cece_rosee_", "yumi.etoo", "wettmelons", "devon.shae"
]

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        params = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        requests.get(url, params=params)
    except Exception as e:
        print(f"[Telegram Error] {e}")

# Test de démarrage
send_telegram_message("✅ Test message - Bot is running.")

def init_instagram_client():
    cl = Client()
    try:
        if os.path.exists(SETTINGS_PATH):
            cl.load_settings(SETTINGS_PATH)
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        cl.dump_settings(SETTINGS_PATH)
    except ChallengeRequired:
        send_telegram_message("⚠️ *Challenge Instagram requis.* Interruption du bot.")
        raise
    except Exception as e:
        send_telegram_message(f"🔁 *Nouvelle tentative de login...* Erreur : `{e}`")
        cl = Client()
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        cl.dump_settings(SETTINGS_PATH)
    return cl

def wait_random_delay(min_sec, max_sec):
    delay = random.uniform(min_sec, max_sec)
    send_telegram_message(f"⏳ Attente de `{delay:.1f}` secondes avant la prochaine action.")
    time.sleep(delay)

def run_bot(origin="manuel"):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    send_telegram_message(f"🚀 *Script lancé* en mode `{origin}` à `{now}`")

    cl = init_instagram_client()
    random.shuffle(ACCOUNTS_TO_TARGET)

    for account in ACCOUNTS_TO_TARGET:
        try:
            send_telegram_message(f"🔍 Traitement de `{account}`...")
            user_id = cl.user_id_from_username(account)
            medias = cl.user_medias(user_id, amount=5)
            random.shuffle(medias)

            posts_liked = 0

            for media in medias[:MAX_LIKES_PER_ACCOUNT]:
                media_info = cl.media_info(media.id)
                if media_info.has_liked:
                    send_telegram_message(f"🔁 Post déjà liké pour `{account}` – passage au suivant.")
                    continue

                cl.media_like(media.id)
                posts_liked += 1
                send_telegram_message(f"❤️ Post liké pour `{account}`")
                wait_random_delay(4, 7)

                comments = cl.media_comments(media.id)
                comments_liked = 0
                comments_checked = 0

                for comment in comments[:MAX_COMMENT_LIKES_PER_POST]:
                    comments_checked += 1
                    if comment.has_liked:
                        continue
                    cl.comment_like(comment.pk)
                    comments_liked += 1
                    wait_random_delay(2, 4)

                if comments_checked > 0 and comments_liked == 0:
                    send_telegram_message("💬 Aucun nouveau commentaire à liker – tous déjà traités.")
                elif comments_liked > 0:
                    send_telegram_message(f"💬 `{comments_liked}` commentaires likés sur le post de `{account}`")

                wait_random_delay(5, 10)

            if posts_liked == 0:
                send_telegram_message(f"✅ Tous les derniers posts de `{account}` ont déjà été likés – rien à faire.")

        except ChallengeRequired:
            send_telegram_message(f"🚫 *Challenge requis* pour `{account}` – passage au suivant.")
            continue
        except LoginRequired:
            send_telegram_message("🔁 *Session expirée* – reconnexion...")
            cl = init_instagram_client()
        except Exception as e:
            send_telegram_message(f"❌ *Erreur avec `{account}`* : `{e}`")

        wait_random_delay(15, 30)

    end = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    send_telegram_message(f"✅ *Script terminé* à `{end}`")

if __name__ == "__main__":
    run_bot()
