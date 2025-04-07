import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests

# === Configuration du BOT Telegram ===
telegram_token = '7738170805:AAEl-eE9FOw9KnWl9AMF1SjprSVCRB8-L7E'
chat_id = '6395554104'

# === Configuration Selenium ===
options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-blink-features")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Anti-détection
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined})
    """
})

# === Fonction pour envoyer message sur Telegram ===
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    requests.post(url, data=payload)

# === Fonction pour scroller humainement ===
def human_scroll():
    for _ in range(3):
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(random.uniform(1, 2))

# === Fonction principale de scraping et d'envoi ===
def scrape_and_notify():
    known_offers = set()  # Pour éviter les doublons
    
    base_url = "https://www.linkedin.com/jobs/search/?keywords=stage"
    
    while True:
        try:
            print("🔎 Ouverture de LinkedIn...")
            driver.get(base_url)
            time.sleep(random.uniform(3, 5))
            human_scroll()

            offers = driver.find_elements(By.CSS_SELECTOR, "ul.jobs-search__results-list li")

            print(f"✅ Nombre d'offres trouvées : {len(offers)}")
            new_stages = 0

            for offer in offers:
                try:
                    title_element = offer.find_element(By.CSS_SELECTOR, "h3")
                    company_element = offer.find_element(By.CSS_SELECTOR, "h4")
                    location_element = offer.find_element(By.CSS_SELECTOR, "div>div>div>div>span")
                    link_element = offer.find_element(By.TAG_NAME, "a")

                    title = title_element.text.strip()
                    company = company_element.text.strip()
                    location = location_element.text.strip()
                    link = link_element.get_attribute('href')

                    unique_key = title + company + location  # Identifiant unique pour une offre

                    if unique_key not in known_offers:
                        known_offers.add(unique_key)
                        new_stages += 1
                        message = f"🚀 *Nouveau Stage Trouvé !*\n\n👔 Poste : {title}\n🏢 Entreprise : {company}\n📍 Lieu : {location}\n🔗 Lien : {link}"
                        send_telegram_message(message)
                        print(f"🔔 Stage envoyé sur Telegram : {title}")

                except Exception as e:
                    print(f"⚠️ Erreur dans l'extraction d'une offre : {e}")

            print(f"🎯 {new_stages} nouvelles offres envoyées cette session.")

        except Exception as e:
            print(f"❌ Erreur principale : {e}")

        print("🕒 Pause de 10 minutes avant prochaine recherche...")
        time.sleep(600)  # 10 minutes
        

# === Lancement du script ===
scrape_and_notify()
