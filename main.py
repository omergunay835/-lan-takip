import os
import io
import requests
from bs4 import BeautifulSoup
import urllib3
from pypdf import PdfReader

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

# Genişletilmiş Anahtar Kelime Listesi
KEYWORDS = [
    # Güvenlik & Mühendislik
    "endüstri mühendis", "endüstri müh", "4689",
    "güvenlik", "koruma ve güvenlik", "silahlı", "5188",
    # Herhangi Bir Lisans / Genel Kamu Kadroları
    "zabıta", "itfaiye eri", "mübaşir", "infaz koruma", "ikm",
    "büro personeli", "memur alımı", "düz memur", "4001",
    "jandarma", "subay", "astsubay", "uzman erbaş", "sahil güvenlik",
    "herhangi bir lisans"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scan_pdf_content(pdf_url):
    """PDF linkini indirip içindeki metinde anahtar kelimeleri arar."""
    try:
        res = requests.get(pdf_url, headers=HEADERS, verify=False, timeout=10)
        if res.status_code == 200:
            pdf_file = io.BytesIO(res.content)
            reader = PdfReader(pdf_file)
            full_text = ""
            for page in reader.pages:
                full_text += page.extract_text() or ""
            
            text_lower = full_text.lower()
            for kw in KEYWORDS:
                if kw in text_lower:
                    return True, kw
    except Exception as e:
        print(f"PDF okunurken hata ({pdf_url}): {e}")
    return False, None

def check_text_or_pdf(text, href):
    """Metinde veya PDF iceriginde arama yapar."""
    text_lower = text.lower()
    # 1. Doğrudan HTML metninde arama
    for kw in KEYWORDS:
        if kw in text_lower:
            return True, f"Başlık Eşleşmesi: {kw}"
    
    # 2. Eğer link bir PDF ise, indirip içini okuma
    if href.lower().endswith(".pdf"):
        matched, kw = scan_pdf_content(href)
        if matched:
            return True, f"PDF Detay Eşleşmesi: {kw}"
            
    return False, None

def scan_resmi_gazete():
    """1. Resmi Gazete Taraması + PDF Okuma"""
    print("1/6 - Resmi Gazete (Metin + PDF) taranıyor...")
    url = "https://www.resmigazete.gov.tr/cesitli-ilanlar"
    found = []
    try:
        res = requests.get(url, headers=HEADERS, verify=False, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        for link in soup.find_all("a"):
            text = link.get_text().strip()
            href = link.get("href", "")
            if href and not href.startswith("http"):
                href = "https://www.resmigazete.gov.tr/" + href.lstrip("/")
            
            matched, reason = check_text_or_pdf(text, href)
            if matched:
                found.append(f"<b>[Resmi Gazete]</b> ({reason})\n{text}\n<a href='{href}'>İlan/PDF Linki</a>")
    except Exception as e:
        print(f"Resmi Gazete hatası: {e}")
    return found

def scan_ilan_gov():
    """2. İlan.gov.tr Taraması"""
    print("2/6 - İlan.gov.tr taranıyor...")
    url = "https://www.ilan.gov.tr/ilan/kategori/9/personel-alimi-ve-eleman-arananlar"
    found = []
    try:
        res = requests.get(url, headers=HEADERS, verify=False, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        for card in soup.find_all("a"):
            text = card.get_text().strip()
            href = card.get("href", "")
            if href and not href.startswith("http"):
                href = "https://www.ilan.gov.tr" + href
            
            matched, reason = check_text_or_pdf(text, href)
            if matched:
                found.append(f"<b>[İlan.gov.tr]</b> ({reason})\n{text[:150]}...\n<a href='{href}'>İlan Linki</a>")
    except Exception as e:
        print(f"İlan.gov.tr hatası: {e}")
    return list(set(found))

def scan_kamuilan_sbb():
    """3. Kamuilan SBB Taraması"""
    print("3/6 - Kamuilan SBB taranıyor...")
    url = "https://kamuilan.sbb.gov.tr/"
    found = []
    try:
        res = requests.get(url, headers=HEADERS, verify=False, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        for a in soup.find_all("a"):
            text = a.get_text().strip()
            href = a.get("href", "")
            if href and not href.startswith("http"):
                href = "https://kamuilan.sbb.gov.tr/" + href.lstrip("/")
            
            matched, reason = check_text_or_pdf(text, href)
            if matched:
                found.append(f"<b>[Kamuİlan SBB]</b> ({reason})\n{text}\n<a href='{href}'>İlan Linki</a>")
    except Exception as e:
        print(f"Kamuilan SBB hatası: {e}")
    return list(set(found))

def scan_kariyer_kapisi():
    """4. Kariyer Kapısı Taraması"""
    print("4/6 - Kariyer Kapısı taranıyor...")
    url = "https://kariyerkapisi.cbiko.gov.tr/"
    found = []
    try:
        res = requests.get(url, headers=HEADERS, verify=False, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        for a in soup.find_all("a"):
            text = a.get_text().strip()
            href = a.get("href", "")
            if href and not href.startswith("http"):
                href = "https://kariyerkapisi.cbiko.gov.tr" + href
            
            matched, reason = check_text_or_pdf(text, href)
            if matched:
                found.append(f"<b>[Kariyer Kapısı]</b> ({reason})\n{text}\n<a href='{href}'>İlan Linki</a>")
    except Exception as e:
        print(f"Kariyer Kapısı hatası: {e}")
    return list(set(found))

def scan_csb_personel():
    """5. CSB Personel Dairesi Taraması"""
    print("5/6 - CSB Personel Dairesi taranıyor...")
    url = "https://personel.csb.gov.tr/duyurular"
    found = []
    try:
        res = requests.get(url, headers=HEADERS, verify=False, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        for a in soup.find_all("a"):
            text = a.get_text().strip()
            href = a.get("href", "")
            if href and not href.startswith("http"):
                href = "https://personel.csb.gov.tr/" + href.lstrip("/")
            
            matched, reason = check_text_or_pdf(text, href)
            if matched:
                found.append(f"<b>[CSB Personel]</b> ({reason})\n{text}\n<a href='{href}'>İlan Linki</a>")
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
            if href and not href.startswith("http"):
                href = "https://www.iskur.gov.tr" + href
            
            matched, reason = check_text_or_pdf(text, href)
            if matched:
                found.append(f"<b>[İŞKUR Kamu Alımı]</b> ({reason})\n{text}\n<a href='{href}'>İlan Linki</a>")
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
    
    unique_results = list(set(results))
    
    if unique_results:
        send_telegram(f"🚨 <b>YENİ İLAN UYUMU BULUNDU! ({len(unique_results)} Adet)</b>\n\n" + "\n\n-------------------\n\n".join(unique_results))
        print(f"{len(unique_results)} adet uygun ilan bulundu ve Telegram'a atıldı.")
    else:
        print("Bütün siteler ve PDF kılavuzları taranmıştır. Uygun ilan bulunamadı.")
