from assistant.knowledge_base import get_answer_from_kb
from assistant.booking import book_appointment
from assistant.notifier import send_confirmation
from assistant.calendar_service import create_event
import json
import re
from datetime import datetime
import unicodedata
from difflib import get_close_matches

pending_booking = {}

SINONIMI_SERVIZI = {
    "carta d'identità elettronica": [
        "carta identita", "identità elettronica", "rinnovo carta", "rifacimento documento",
        "documento identità", "identita elettronica", "nuova carta identita","carta d'identita"
    ],
    "certificato di residenza": [
        "residenza", "cambio residenza", "certificato residenza"
    ],
    "stato civile": [
        "matrimonio", "nascita", "divorzio", "stato civile"
    ],
    "tari": [
        "tassa rifiuti", "rifiuti", "tarsu", "immondizia"
    ],
    "ufficio tecnico": [
        "edilizia", "permesso di costruire", "urbanistica", "costruzione"
    ]
}

NUMERI_PAROLE = {
    "uno": 1, "due": 2, "tre": 3, "quattro": 4, "cinque": 5, "sei": 6,
    "sette": 7, "otto": 8, "nove": 9, "dieci": 10, "undici": 11, "dodici": 12,
    "tredici": 13, "quattordici": 14, "quindici": 15, "sedici": 16,
    "diciassette": 17, "diciotto": 18, "diciannove": 19, "venti": 20,
    "ventuno": 21, "ventidue": 22, "ventitré": 23, "ventiquattro": 24,
    "venticinque": 25, "ventisei": 26, "ventisette": 27, "ventotto": 28,
    "ventinove": 29, "trenta": 30, "trentuno": 31
}


def load_services():
    try:
        with open("data/services.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return [s["nome"].lower() for s in data if "nome" in s]
    except Exception as e:
        print(f"⚠️ Errore caricamento servizi: {e}")
        return []

SERVIZI_COMUNALI = load_services()


def extract_date(text: str) -> str:
    text = text.lower()
    months = {
        "gennaio":1, "febbraio":2, "marzo":3, "aprile":4, "maggio":5, "giugno":6,
        "luglio":7, "agosto":8, "settembre":9, "ottobre":10, "novembre":11, "dicembre":12
    }

    match_iso = re.search(r"\d{4}-\d{2}-\d{2}", text)
    if match_iso:
        return match_iso.group(0)

    match = re.search(r"(\d{1,2}|\w+)\s*(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)", text)
    if match:
        day_text, month_name = match.groups()
        day = NUMERI_PAROLE.get(day_text, day_text)
        try:
            date = datetime(datetime.now().year, months[month_name], int(day))
            return date.strftime("%Y-%m-%d")
        except ValueError:
            return None

    match = re.search(r"(\d{1,2})\s*(\d{1,2})", text)
    if match:
        day, month = match.groups()
        try:
            date = datetime(datetime.now().year, int(month), int(day))
            return date.strftime("%Y-%m-%d")
        except ValueError:
            return None

    return None


def extract_time(text: str) -> str:
    import re
    text = text.lower()

    match = re.search(r"(\d{1,2}):(\d{2})", text)
    if match:
        hour, minute = match.groups()
        return f"{int(hour):02d}:{int(minute):02d}"

    match = re.search(r"(?:alle\s+)?(\d{1,2})(?:\s*(del|di)\s*(mattino|pomeriggio|sera))?", text)
    if match:
        hour_str, _, period = match.groups()
        hour = int(hour_str)
        minute = 0
        if period:
            if period in ["pomeriggio", "sera"] and hour < 12:
                hour += 12
        return f"{hour:02d}:{minute:02d}"

    return "09:00"


def normalize_text(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")
    text = text.replace("'", "").replace("’", "").replace("`", "")
    text = text.replace("  ", " ")
    return text.strip()

def find_service_in_input(user_input: str):
    normalized_input = normalize_text(user_input)

    for servizio, sinonimi in SINONIMI_SERVIZI.items():
        for sinonimo in sinonimi:
            if normalize_text(sinonimo) in normalized_input:
                return servizio

    for nome_servizio in SERVIZI_COMUNALI:
        if normalize_text(nome_servizio) in normalized_input:
            return nome_servizio

    normalized_services = [normalize_text(s) for s in SERVIZI_COMUNALI]
    matches = get_close_matches(normalized_input, normalized_services, n=1, cutoff=0.5)
    if matches:
        index = normalized_services.index(matches[0])
        return SERVIZI_COMUNALI[index]

    return None


def handle_user_input(user_input: str) -> str:
    global pending_booking
    user_input = user_input.lower()

    if "waiting_for_email" in pending_booking:
        user_email = user_input.strip()
        if not re.match(r"[^@]+@[^@]+\.[^@]+", user_email):
            return "L'indirizzo email non sembra valido. Puoi riprovare?"

        service = pending_booking["service"]
        date = pending_booking["date"]
        time = pending_booking.get("time", "09:00")

        msg = book_appointment(service, date, time)
        send_confirmation(service, date)

        try:
            create_event(service, date, time=time, user_name="Cittadino", user_email=user_email)
        except Exception as e:
            print(f"⚠️ Errore durante la creazione evento su Google Calendar: {e}")

        pending_booking = {}
        return f"✅ Prenotazione confermata per '{service}' il {date} alle {time}. Ti ho inviato una conferma via email a {user_email}."

    if "prenota" in user_input or "appuntamento" in user_input:
        service = find_service_in_input(user_input)
        if not service:
            return "Non ho riconosciuto il servizio. Puoi specificare il nome esatto (es. 'Carta d'identità' o 'Stato civile')?"

        date = extract_date(user_input)
        time = extract_time(user_input)
        if not date:
            return "Non ho capito la data, puoi ripetere per favore indicando giorno e mese?"

        pending_booking = {
            "waiting_for_email": True,
            "service": service.title(),
            "date": date,
            "time": time
        }
        return f"Perfetto! Per completare la prenotazione per '{service.title()}' il {date} alle {time}, mi scrivi la tua email?"


    return get_answer_from_kb(user_input)
