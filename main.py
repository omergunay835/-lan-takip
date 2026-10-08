import os
import requests
from bs4 import BeautifulSoup
import urllib3

# SSL uyarılarını kapat
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Telegram Bilgilerini GitHub Secrets'tan Al
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(message):
    """Telegram üzerinden bildirim gönderir."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bilgileri eksik!")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram mesajı gönderilemedi: {e}")

# Aranacak Anahtar Kelimeler
KEYWORDS = [
    "endüstri mühendis", "endüstri müh", "4689",
    "güvenlik", "koruma ve güvenlik", "silahlı", "5188"
]

def scan_resmi_gazete():
    """Resmi Gazete Çeşitli İlanlar Sayfasını Tarar"""
    print("Resmi Gazete taranıyor...")
    url = "https://www.resmigazete.gov.tr/cesitli-ilanlar"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        res = requests.get(url, headers=headers, verify=False, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        links = soup.find_all("a")
        
        found_matches = []
        for link in links:
            text = link.get_text().strip()
            href = link.get("href", "")
            
            # Kelime kontrolü
            text_lower = text.lower()
            if any(kw in text_lower for kw in KEYWORDS):
                if href and not href.startswith("http"):
                    href = "https://www.resmigazete.gov.tr/" + href.lstrip("/")
                found_matches.append(f"<b>Resmi Gazete İlanı:</b>\n{text}\n<a href='{href}'>İlan Linki</a>")
        
        return found_matches
    except Exception as e:
        print(f"Resmi Gazete taranırken hata: {e}")
        return []

def scan_ilan_gov():
    """İlan.gov.tr Personel Alım Sayfasını Tarar"""
    print("İlan.gov.tr taranıyor...")
    url = "https://www.ilan.gov.tr/ilan/kategori/9/personel-alimi-ve-eleman-arananlar"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        res = requests.get(url, headers=headers, verify=False, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        cards = soup.find_all("a")
        
        found_matches = []
        for card in cards:
            text = card.get_text().strip()
            href = card.get("href", "")
            text_lower = text.lower()
            
            if any(kw in text_lower for kw in KEYWORDS):
                if href and not href.startswith("http"):
                    href = "https://www.ilan.gov.tr" + href
                found_matches.append(f"<b>İlan.gov.tr İlanı:</b>\n{text[:150]}...\n<a href='{href}'>İlan Linki</a>")
        
        # Tekrarlayanları temizle
        return list(set(found_matches))
    except Exception as e:
        print(f"İlan.gov.tr taranırken hata: {e}")
        return []

if __name__ == "__main__":
    results = []
    results.extend(scan_resmi_gazete())
    results.extend(scan_ilan_gov())
    
    if results:
        send_telegram(f"🚨 <b>YENİ İLAN UYUMU BULUNDU! ({len(results)} Adet)</b>\n\n" + "\n\n-------------------\n\n".join(results))
        print(f"{len(results)} adet uygun ilan bulundu ve Telegram'a atıldı.")
    else:
        print("Uygun ilan bulunamadı.")
