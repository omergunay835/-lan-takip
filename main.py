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

# Filtreleme Kelimelerin
KEYWORDS = [
    "endüstri mühendis", "endüstri müh", "4689",
    "güvenlik", "koruma ve güvenlik", "silahlı", "5188"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scan_resmi_gazete():
    """1. Resmi Gazete Çeşitli İlanlar Taraması"""
    print("1/6 - Resmi Gazete taranıyor...")
    url = "https://www.resmigazete.gov.tr/cesitli-ilanlar"
    found = []
    try:
        res = requests.get(url, headers=HEADERS, verify=False, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        for link in soup.find_all("a"):
            text = link.get_text().strip()
            href = link.get("href", "")
            if any(kw in text.lower() for kw in KEYWORDS):
                if href and not href.startswith("http"):
                    href = "https://www.resmigazete.gov.tr/" + href.lstrip("/")
                found.append(f"<b>[Resmi Gazete]</b>\n{text}\n<a href='{href}'>İlan Linki</a>")
    except Exception as e:
        print(f"Resmi Gazete hatası: {e}")
    return found

def scan_ilan_gov():
    """2. İlan.gov.tr Personel Alımları Taraması"""
    print("2/6 - İlan.gov.tr taranıyor...")
    url = "https://www.ilan.gov.tr/ilan/kategori/9/personel-alimi-ve-eleman-arananlar"
    found = []
    try:
        res = requests.get(url, headers=HEADERS, verify=False, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        for card in soup.find_all("a"):
            text = card.get_text().strip()
            href = card.get("href", "")
            if any(kw in text.lower() for kw in KEYWORDS):
                if href and not href.startswith("http"):
                    href = "https://www.ilan.gov.tr" + href
                found.append(f"<b>[İlan.gov.tr]</b>\n{text[:150]}...\n<a href='{href}'>İlan Linki</a>")
    except Exception as e:
        print(f"İlan.gov.tr hatası: {e}")
    return list(set(found))

def scan_kamuilan_sbb():
    """3. Kamuilan SBB (Strateji ve Bütçe Başkanlığı) Taraması"""
    print("3/6 - Kamuilan SBB taranıyor...")
    url = "https://kamuilan.sbb.gov.tr/"
    found = []
    try:
        res = requests.get(url, headers=HEADERS, verify=False, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        for a in soup.find_all("a"):
            text = a.get_text().strip()
            href = a.get("href", "")
            if any(kw in text.lower() for kw in KEYWORDS):
                if href and not href.startswith("http"):
                    href = "https://kamuilan.sbb.gov.tr/" + href.lstrip("/")
                found.append(f"<b>[Kamuİlan SBB]</b>\n{text}\n<a href='{href}'>İlan Linki</a>")
    except Exception as e:
        print(f"Kamuilan SBB hatası: {e}")
    return list(set(found))

def scan_kariyer_kapisi():
    """4. Kariyer Kapısı Kamu Alımları Taraması"""
    print("4/6 - Kariyer Kapısı taranıyor...")
    url = "https://kariyerkapisi.cbiko.gov.tr/"
    found = []
    try:
        res = requests.get(url, headers=HEADERS, verify=False, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        for a in soup.find_all("a"):
            text = a.get_text().strip()
            href = a.get("href", "")
            if any(kw in text.lower() for kw in KEYWORDS):
                if href and not href.startswith("http"):
                    href = "https://kariyerkapisi.cbiko.gov.tr" + href
                found.append(f"<b>[Kariyer Kapısı]</b>\n{text}\n<a href='{href}'>İlan Linki</a>")
    except Exception as e:
        print(f"Kariyer Kapısı hatası: {e}")
    return list(set(found))

def scan_csb_personel():
    """5. Çevre, Şehircilik ve İklim Değişikliği Bakanlığı Personel Duyuruları"""
    print("5/6 - CSB Personel Dairesi taranıyor...")
    url = "https://personel.csb.gov.tr/duyurular"
    found = []
    try:
        res = requests.get(url, headers=HEADERS, verify=False, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        for a in soup.find_all("a"):
            text = a.get_text().strip()
            href = a.get("href", "")
            if any(kw in text.lower() for kw in KEYWORDS):
                if href and not href.startswith("http"):
                    href = "https://personel.csb.gov.tr/" + href.lstrip("/")
                found.append(f"<b>[CSB Personel]</b>\n{text}\n<a href='{href}'>İlan Linki</a>")
    except Exception as e:
        print(f"CSB Personel hatası: {e}")
    return list(set(found))

def scan_iskur():
    """6. İŞKUR Kamu İlanları Taraması"""
    print("6/6 - İŞKUR taranıyor...")
    url = "https://www.iskur.gov.tr/baglantilar/kamu-memur-alim-ilanlari/"
    found = []
    try:
        res = requests.get(url, headers=HEADERS, verify=False, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        for a in soup.find_all("a"):
            text = a.get_text().strip()
            href = a.get("href", "")
            if any(kw in text.lower() for kw in KEYWORDS):
                if href and not href.startswith("http"):
                    href = "https://www.iskur.gov.tr" + href
                found.append(f"<b>[İŞKUR Kamu Alımı]</b>\n{text}\n<a href='{href}'>İlan Linki</a>")
    except Exception as e:
        print(f"İŞKUR hatası: {e}")
    return list(set(found))

if __name__ == "__main__":
    results = []
    results.extend(scan_resmi_gazete())
    results.extend(scan_ilan_gov())
    results.extend(scan_kamuilan_sbb())
    results.extend(scan_kariyer_kapisi())
    results.extend(scan_csb_personel())
    results.extend(scan_iskur())
    
    # Tekrarlayan ilanları temizle
    unique_results = list(set(results))
    
    if unique_results:
        send_telegram(f"🚨 <b>YENİ İLAN UYUMU BULUNDU! ({len(unique_results)} Adet)</b>\n\n" + "\n\n-------------------\n\n".join(unique_results))
        print(f"{len(unique_results)} adet uygun ilan bulundu ve Telegram'a atıldı.")
    else:
        print("Bütün siteler taranmıştır. Niteliklerine uygun yeni ilan bulunamadı.")
send_telegram("✅ Test Mesajı: Telegram botun ve otomasyonun sorunsuz çalışıyor!")
