import requests
from bs4 import BeautifulSoup
import time
import random

# === Configuration du Bot Telegram ===
telegram_token = '7738170805:AAEl-eE9FOw9KnWl9AMF1SjprSVCRB8-L7E'
chat_id = '6395554104'

# === Liste des mots-clés maximisée ===
KEYWORDS = [
    "data",
    "data analyst",
    "data scientist",
    "big data",
    "data engineer",
    "machine learning",
    "deep learning",
    "intelligence artificielle",
    "artificial intelligence",
    "python",
    "sql",
    "bi",
    "business intelligence",
    "power bi",
    "tableau",
    "finance",
    "financial analyst",
    "contrôle de gestion",
    "contrôleur de gestion",
    "risk",
    "audit",
    "auditeur",
    "business analyst",
    "analyste",
    "conseil",
    "consultant",
    "consulting",
    "stratégie",
    "strategy",
    "investment",
    "banque",
    "private equity",
    "venture capital",
    "management",
    "gestion de projet",
    "project management",
    "operations",
    "product manager",
    "product owner",
    "project owner",
    "transformation digitale",
    "innovation",
    "rpa",
    "robotic process automation",
    "supply chain",
    "logistique",
    "analyse de données",
    "business development",
    "business dev",
    "marketing analyst",
    "e-commerce",
    "achats",
    "pmo"
]

# === Fonction pour envoyer un message Telegram ===
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    response = requests.post(url, data=payload)
    print("=== Résultat de l'envoi ===")
    print(f"Status Code : {response.status_code}")
    print(f"Réponse brute : {response.text}")

    if response.status_code == 200:
        print("✅ Message envoyé avec succès !")
    else:
        print("❌ Erreur d'envoi Telegram.")

# === Fonction pour vérifier si un titre contient un mot-clé intéressant ===
def is_relevant(title):
    title_lower = title.lower()
    for keyword in KEYWORDS:
        if keyword in title_lower:
            return True
    return False

# === Fonction pour scraper les stages LinkedIn ===
def scrape_linkedin_jobs():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    }

    url = "https://www.linkedin.com/jobs/search/?keywords=stage&location=Paris%2C%20Île-de-France%2C%20France&f_TPR=r604800"

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Erreur HTTP {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    jobs = []

    job_cards = soup.select('ul.jobs-search__results-list li')

    for card in job_cards:
        try:
            title_element = card.select_one('h3')
            company_element = card.select_one('h4')
            location_element = card.select_one('span.job-search-card__location')
            link_element = card.select_one('a')

            title = title_element.get_text(strip=True) if title_element else "N/A"
            company = company_element.get_text(strip=True) if company_element else "N/A"
            location = location_element.get_text(strip=True) if location_element else "N/A"
            link = link_element.get('href') if link_element else "N/A"

            title_lower = title.lower()

            # === Filtres : sans alternance + mots-clés + Paris ===
            if ("alternance" in title_lower) or ("apprenti" in title_lower):
                continue

            if "paris" in location.lower() and is_relevant(title):
                jobs.append({
                    'title': title,
                    'company': company,
                    'location': location,
                    'link': link
                })

        except Exception as e:
            print(f"⚠️ Erreur analyse carte : {e}")

    return jobs

# === Fonction principale avec boucle infinie ===
def main():
    print("🚀 Bot LinkedIn lancé pour chercher des stages DATA - FINANCE - STRATEGIE - CONSEIL - BUSINESS ANALYST...")

    known_jobs = set()

    while True:
        jobs = scrape_linkedin_jobs()

        if not jobs:
            print("❌ Aucun stage pertinent trouvé pour ce cycle.")
        else:
            print(f"✅ {len(jobs)} stages pertinents trouvés. Envoi vers Telegram...")

        for job in jobs:
            unique_id = f"{job['title']}-{job['company']}-{job['location']}"

            if unique_id not in known_jobs:
                known_jobs.add(unique_id)
                message = f"🚀 *Stage détecté !*\n\n👔 Poste : {job['title']}\n🏢 Entreprise : {job['company']}\n📍 Lieu : {job['location']}\n🔗 [Voir l'offre ici]({job['link']})"
                send_telegram_message(message)
                time.sleep(random.uniform(1.5, 3.5))  # Pause entre messages

        print("⏳ Attente de 5 minutes avant la prochaine recherche...")
        time.sleep(300)

# === Lancer le bot ===
if __name__ == "__main__":
    main()
