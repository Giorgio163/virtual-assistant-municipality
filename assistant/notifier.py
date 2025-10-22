from datetime import datetime
from pathlib import Path

LOG_FILE = Path("logs/notifications.log")

def log(message):
    LOG_FILE.parent.mkdir(exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {message}\n")

def send_confirmation(service, date):
    msg = f"Conferma: appuntamento per {service} il {date}"
    print(msg)
    log(msg)

def send_reminder(service, date):
    msg = f"Promemoria: appuntamento per {service} domani ({date})"
    print(msg)
    log(msg)
