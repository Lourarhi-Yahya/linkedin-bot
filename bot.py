import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os

# === Paramètres Telegram (via variables d'environnement)
telegram_token = os.getenv("TELEGRAM_TOKEN")
chat_id = os.getenv("CHAT_ID")

# === Fonction pour envoyer un message Telegram
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    requests.post(url, data=payload)

# === Fonction pour scraper LinkedIn sans Selenium
def scrape_linkedin():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    }

    url = "https://www.linkedin.com/jobs/search?keywords=stage&location=France"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Erreur HTTP {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    jobs = []
    job_cards = soup.select('ul.jobs-search__results-list li')  # Adapté pour la page LinkedIn Jobs

    for card in job_cards:
        try:
            title = card.select_one('h3').get_text(strip=True)
            company = card.select_one('h4').get_text(strip=True)
            location = card.select_one('span.job-search-card__location').get_text(strip=True)
            link = card.select_one('a').get('href')

            jobs.append({
                'title': title,
                'company': company,
                'location': location,
                'link': link
            })
        except Exception as e:
            print(f"Erreur lors de l'analyse d'une carte: {e}")
            continue

    return jobs

# === Fonction principale
def main_loop():
    print("🚀 Bot LinkedIn Stage démarré...")
    known_jobs = set()

    while True:
        jobs = scrape_linkedin()

        for job in jobs:
            unique_id = f"{job['title']}-{job['company']}-{job['location']}"

            if unique_id not in known_jobs:
                known_jobs.add(unique_id)
                message = f"🚀 *Nouveau Stage trouvé !*\n\n👔 Poste : {job['title']}\n🏢 Entreprise : {job['company']}\n📍 Lieu : {job['location']}\n🔗 Lien : {job['link']}"
                send_telegram_message(message)
                print(f"✅ Nouveau stage envoyé : {job['title']} chez {job['company']}")

        print("⏳ En attente avant prochaine recherche...")
        time.sleep(random.randint(500, 700))  # Attendre environ 10 minutes

# === Démarrer le bot
if __name__ == "__main__":
    main_loop()
