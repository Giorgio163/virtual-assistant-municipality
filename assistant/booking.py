import json
from datetime import datetime
from pathlib import Path

APPOINTMENTS_FILE = Path("data/appointments.json")

def load_appointments():
    if not APPOINTMENTS_FILE.exists():
        return []
    return json.load(open(APPOINTMENTS_FILE, "r", encoding="utf-8"))

def save_appointments(apps):
    json.dump(apps, open(APPOINTMENTS_FILE, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

def book_appointment(service, date, time="09:00"):
    datetime_str = f"{date} {time}"
    apps = load_appointments()

    if any(a["service"] == service and a.get("datetime") == datetime_str for a in apps):
        return f"Mi dispiace, {service} non è disponibile il {date} alle {time}."

    app = {
        "service": service,
        "datetime": datetime_str,
        "created_at": datetime.now().isoformat()
    }
    apps.append(app)
    save_appointments(apps)
    return f"Appuntamento confermato per {service} il {date} alle {time}!"

