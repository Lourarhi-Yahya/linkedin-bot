import requests
from bs4 import BeautifulSoup
import time
import random
import re

# === Configuration du Bot Telegram ===
telegram_token = '7738170805:AAEl-eE9FOw9KnWl9AMF1SjprSVCRB8-L7E'
chat_id = '6395554104'

# === Liste des mots-clés maximisée ===
KEYWORDS = [
    "data", "data analyst", "data scientist", "big data", "data engineer",
    "machine learning", "deep learning", "intelligence artificielle",
    "artificial intelligence", "python", "sql", "bi", "business intelligence",
    "power bi", "tableau", "finance", "financial analyst", "contrôle de gestion",
    "contrôleur de gestion", "risk", "audit", "auditeur", "business analyst",
    "analyste", "conseil", "consultant", "consulting", "stratégie", "strategy",
    "investment", "banque", "private equity", "venture capital", "management",
    "gestion de projet", "project management", "operations", "product manager",
    "product owner", "project owner", "transformation digitale", "innovation",
    "rpa", "robotic process automation", "supply chain", "logistique",
    "analyse de données", "business development", "business dev",
    "marketing analyst", "e-commerce", "achats", "pmo"
]

# === Mois en français et anglais pour reconnaissance dans le texte
MONTHS_PATTERN = (
    "janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre|"
    "january|february|march|april|may|june|july|august|september|october|november|december"
)

# === Fonction pour envoyer un message Telegram ===
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    response = requests.post(url, data=payload)
    print(f"Status : {response.status_code} | Réponse : {response.text}")

# === Fonction pour vérifier si un titre est pertinent
def is_relevant(title):
    title_lower = title.lower()
    return any(keyword in title_lower for keyword in KEYWORDS)

# === Fonction pour aller chercher la description du stage et détecter la date
def get_start_date_from_description(link):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    }
    try:
        response = requests.get(link, headers=headers)
        if response.status_code != 200:
            return "Non spécifiée"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        description = soup.get_text(separator=' ')
        description = description.lower()

        # Regex pour capter "début janvier 2025", "start: September 2025", etc.
        match = re.search(r"(début|start|entrée en fonction|démarrage).{0,15}(" + MONTHS_PATTERN + r")\s*(\d{4})?", description)
        
        if match:
            mois = match.group(2).capitalize()
            annee = match.group(3) if match.group(3) else ""
            return f"{mois} {annee}".strip()
        
        # Sinon, chercher directement un mois et une année dans tout le texte
        match_alt = re.search(r"(" + MONTHS_PATTERN + r")\s*(\d{4})", description)
        if match_alt:
            mois = match_alt.group(1).capitalize()
            annee = match_alt.group(2)
            return f"{mois} {annee}"

    except Exception as e:
        print(f"Erreur lors de l'accès à la description : {e}")

    return "Non spécifiée"

# === Fonction pour scraper les offres LinkedIn ===
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

            if ("alternance" in title_lower) or ("apprenti" in title_lower):
                continue

            if "paris" in location.lower() and is_relevant(title):
                full_link = f"https://www.linkedin.com{link}" if link.startswith("/") else link
                start_date = get_start_date_from_description(full_link)
                jobs.append({
                    'title': title,
                    'company': company,
                    'location': location,
                    'link': full_link,
                    'start_date': start_date
                })
                time.sleep(random.uniform(1, 2))  # Pause entre les requêtes (anti-ban)

        except Exception as e:
            print(f"⚠️ Erreur carte offre : {e}")

    return jobs

# === Fonction principale avec boucle infinie
def main():
    print("🚀 Bot LinkedIn INTELLIGENT lancé...")

    known_jobs = set()

    while True:
        jobs = scrape_linkedin_jobs()

        if not jobs:
            print("❌ Aucun stage pertinent trouvé.")
        else:
            print(f"✅ {len(jobs)} stages pertinents trouvés. Envoi en cours...")

        for job in jobs:
            unique_id = f"{job['title']}-{job['company']}-{job['location']}"

            if unique_id not in known_jobs:
                known_jobs.add(unique_id)
                message = (
                    f"🚀 *Stage détecté !*\n\n"
                    f"👔 Poste : {job['title']}\n"
                    f"🏢 Entreprise : {job['company']}\n"
                    f"📍 Lieu : {job['location']}\n"
                    f"🗓️ Début estimé : {job['start_date']}\n"
                    f"🔗 [Voir l'offre ici]({job['link']})"
                )
                send_telegram_message(message)
                time.sleep(random.uniform(1.5, 3.5))

        print("⏳ Pause de 5 minutes avant prochaine recherche...")
        time.sleep(300)

# === Lancer le bot
if __name__ == "__main__":
    main()
