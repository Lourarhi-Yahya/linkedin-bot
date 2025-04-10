import requests
from bs4 import BeautifulSoup
import time
import random
import re

# === Configuration du Bot Telegram ===
telegram_token = '7738170805:AAEl-eE9FOw9KnWl9AMF1SjprSVCRB8-L7E'
chat_id = '6395554104'

# === Liste des mots-clés métiers ===
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

# === Mois pour détection intelligente ===
MONTHS_PATTERN = (
    "janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre|"
    "january|february|march|april|may|june|july|august|september|october|november|december"
)

# === Fonction d'envoi Telegram ===
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    response = requests.post(url, data=payload)
    print(f"📤 Message envoyé. Status : {response.status_code}")

# === Fonction pour vérifier la pertinence du titre ===
def is_relevant(title):
    title_lower = title.lower()
    return any(keyword in title_lower for keyword in KEYWORDS)

# === Fonction pour extraire date de début et lien entreprise ===
def get_start_date_and_company_link(linkedin_link):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    }
    try:
        response = requests.get(linkedin_link, headers=headers)
        if response.status_code != 200:
            return "Non spécifiée", linkedin_link
        
        soup = BeautifulSoup(response.text, 'html.parser')
        description = soup.get_text(separator=' ').lower()

        # Recherche de la date
        match = re.search(r"(début|start|entrée en fonction|démarrage).{0,15}(" + MONTHS_PATTERN + r")\s*(\d{4})?", description)
        if match:
            mois = match.group(2).capitalize()
            annee = match.group(3) if match.group(3) else ""
            start_date = f"{mois} {annee}".strip()
        else:
            match_alt = re.search(r"(" + MONTHS_PATTERN + r")\s*(\d{4})", description)
            if match_alt:
                mois = match_alt.group(1).capitalize()
                annee = match_alt.group(2)
                start_date = f"{mois} {annee}"
            else:
                # Chercher ASAP ou "dès que possible"
                if any(term in description for term in ["asap", "dès que possible", "immédiatement", "soon"]):
                    start_date = "ASAP"
                else:
                    start_date = "Non spécifiée"

        # Lien vers l'entreprise
        apply_link = None
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if 'apply' in href or 'careers' in href:
                if not href.startswith('/'):
                    apply_link = href
                    break

        if not apply_link:
            apply_link = linkedin_link

        return start_date, apply_link

    except Exception as e:
        print(f"⚠️ Erreur accès page offre : {e}")
        return "Non spécifiée", linkedin_link

# === Fonction pour scraper LinkedIn (offres publiées récemment) ===
def scrape_linkedin_jobs():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    }
    url = "https://www.linkedin.com/jobs/search/?keywords=stage&location=Paris%2C%20Île-de-France%2C%20France&f_TPR=r2592000"  # 30 derniers jours

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
                start_date, company_link = get_start_date_and_company_link(full_link)

                jobs.append({
                    'title': title,
                    'company': company,
                    'location': location,
                    'linkedin_link': full_link,
                    'start_date': start_date,
                    'company_link': company_link
                })
                time.sleep(random.uniform(1, 2))

        except Exception as e:
            print(f"⚠️ Erreur analyse offre : {e}")

    return jobs

# === Fonction principale ===
def main():
    print("🚀 Bot LinkedIn TEMPS RÉEL lancé...")

    known_jobs = set()

    while True:
        jobs = scrape_linkedin_jobs()

        if not jobs:
            print("❌ Aucun nouveau stage trouvé.")
        else:
            print(f"✅ {len(jobs)} stages trouvés dans les 30 derniers jours.")

        for job in jobs:
            unique_id = f"{job['title']}-{job['company']}-{job['location']}"

            if unique_id not in known_jobs:
                start_date_lower = job['start_date'].lower()

                # --- FILTRE : Avril OU ASAP ---
                if (
                    "avril" in start_date_lower
                    or "april" in start_date_lower
                    or "asap" in start_date_lower
                    or "dès que possible" in start_date_lower
                    or "immédiatement" in start_date_lower
                    or "soon" in start_date_lower
                ):
                    known_jobs.add(unique_id)

                    message = (
                        f"🚀 *Stage détecté (Avril ou ASAP) !*\n\n"
                        f"👔 Poste : {job['title']}\n"
                        f"🏢 Entreprise : {job['company']}\n"
                        f"📍 Lieu : {job['location']}\n"
                        f"🗓️ Début estimé : {job['start_date']}\n"
                        f"🔗 [Lien LinkedIn]({job['linkedin_link']})\n"
                        f"🌐 [Lien Entreprise]({job['company_link']})"
                    )
                    send_telegram_message(message)
                    time.sleep(random.uniform(1.5, 3.5))
                else:
                    print(f"❌ Stage ignoré (pas Avril/ASAP) : {job['title']} chez {job['company']}")

        print("⏳ Attente 1 minute avant la prochaine vérification...")
        time.sleep(60)

# === Lancer ===
if __name__ == "__main__":
    main()
