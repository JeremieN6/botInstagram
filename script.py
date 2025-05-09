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

# Déterminer si on est dans GitHub Actions
IS_GITHUB_ACTION = os.getenv("GITHUB_WORKFLOW") == "true"

MAX_LIKES_PER_ACCOUNT = 3
MAX_COMMENT_LIKES_PER_POST = 10

ACCOUNTS_TO_TARGET = [
    "mathildtantot", "popstantot", "sophieraiin", "cecerose", 
    "cece_rosee_", "yumi.etoo", "wettmelons", "devon.shae"
]

class BotStats:
    def __init__(self):
        self.posts_liked = 0
        self.comments_liked = 0
        self.challenges_encountered = 0
        self.wait_count = 0
        self.total_wait_time = 0
        self.errors_count = 0

    def format_wait_time(self):
        minutes = int(self.total_wait_time // 60)
        seconds = int(self.total_wait_time % 60)
        if minutes > 0:
            return f"{minutes}min{seconds}s"
        return f"{seconds}s"

    def get_summary(self):
        return (
            f"🎯 Le Bot a terminé :\n"
            f"- 💖 {self.posts_liked} posts likés\n"
            f"- 💬 {self.comments_liked} commentaires likés\n"
            f"- 🚫 {self.challenges_encountered} challenges\n"
            f"- ⚠️ {self.errors_count} erreurs\n"
            f"- ⌛ {self.wait_count} attentes pour {self.format_wait_time()} d'attente totale"
        )

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

def wait_random_delay(min_sec, max_sec, stats):
    delay = random.uniform(min_sec, max_sec)
    stats.wait_count += 1
    stats.total_wait_time += delay
    send_telegram_message(f"⏳ Attente de `{delay:.1f}` secondes avant la prochaine action.")
    time.sleep(delay)

def run_bot(origin="manuel"):
    # Initialiser les stats
    stats = BotStats()
    
    # Déterminer le mode de lancement pour le message
    launch_mode = "🤖 automatique (GitHub Actions)" if IS_GITHUB_ACTION and origin == "auto" else \
                 "📱 Telegram" if origin == "telegram" else \
                 "👤 manuel"
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    send_telegram_message(f"🚀 *Script lancé en mode {launch_mode}* à `{now}`")

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
                stats.posts_liked += 1
                send_telegram_message(f"❤️ Post liké pour `{account}`")
                wait_random_delay(4, 7, stats)

                comments = cl.media_comments(media.id)
                comments_liked = 0
                comments_checked = 0

                for comment in comments[:MAX_COMMENT_LIKES_PER_POST]:
                    comments_checked += 1
                    if comment.has_liked:
                        continue
                    cl.comment_like(comment.pk)
                    comments_liked += 1
                    stats.comments_liked += 1
                    wait_random_delay(2, 4, stats)

                if comments_checked > 0 and comments_liked == 0:
                    send_telegram_message("💬 Aucun nouveau commentaire à liker – tous déjà traités.")
                elif comments_liked > 0:
                    send_telegram_message(f"💬 `{comments_liked}` commentaires likés sur le post de `{account}`")

                wait_random_delay(5, 10, stats)

            if posts_liked == 0:
                send_telegram_message(f"✅ Tous les derniers posts de `{account}` ont déjà été likés – rien à faire.")

        except ChallengeRequired:
            stats.challenges_encountered += 1
            send_telegram_message(f"🚫 *Challenge requis* pour `{account}` – passage au suivant.")
            continue
        except LoginRequired:
            stats.errors_count += 1
            send_telegram_message("🔁 *Session expirée* – reconnexion...")
            cl = init_instagram_client()
        except Exception as e:
            stats.errors_count += 1
            send_telegram_message(f"❌ *Erreur avec `{account}`* : `{e}`")

        wait_random_delay(15, 30, stats)

    end = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    send_telegram_message(f"✅ *Script terminé* à `{end}`")
    send_telegram_message(stats.get_summary())

def check_telegram_commands():
    last_update_id = None
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
            if last_update_id:
                url += f"?offset={last_update_id + 1}"
            response = requests.get(url)
            updates = response.json()["result"]

            for update in updates:
                last_update_id = update["update_id"]
                message = update.get("message", {})
                text = message.get("text", "")
                chat_id = message.get("chat", {}).get("id")

                if text == "/start" and str(chat_id) == TELEGRAM_CHAT_ID:
                    send_telegram_message("🟢 Commande `/start` reçue. Lancement du bot...")
                    run_bot("telegram")

        except Exception as e:
            print(f"[Command Check Error] {e}")
        
        time.sleep(10)  # Vérifie toutes les 10 secondes


if __name__ == "__main__":
    from threading import Thread

    # Lancer en mode planifié ET écouter les commandes Telegram en parallèle
    Thread(target=check_telegram_commands).start()
    
    # Si on est dans GitHub Actions, lancer automatiquement
    if IS_GITHUB_ACTION:
        run_bot("auto")
    # Sinon, on peut choisir de lancer manuellement en décommentant la ligne ci-dessous
    # run_bot("manuel")