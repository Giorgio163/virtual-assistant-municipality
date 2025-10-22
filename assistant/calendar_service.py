from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
import os

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TOKEN_PATH = "backend/token.json"
CREDENTIALS_PATH = "backend/credentials.json"

def get_calendar_service():
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError("⚠️ Manca il file backend/credentials.json (crealo dalla console Google Cloud)")
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES
            )
            creds = flow.run_local_server(port=8080, prompt="consent", access_type="offline")
            if not creds.refresh_token:
                print("⚠️ Nessun refresh_token nel token. Riavvia l'autenticazione con 'prompt=consent'.")

        os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
        with open(TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())
        print(f"✅ Token salvato in {TOKEN_PATH}")

    return build("calendar", "v3", credentials=creds)


def get_authenticated_email(service):
    about = service.calendarList().list().execute()
    if "items" in about and len(about["items"]) > 0:
        primary = next((c for c in about["items"] if c.get("primary")), about["items"][0])
        return primary.get("id")
    return None


def check_availability(start: datetime, end: datetime) -> bool:
    service = get_calendar_service()
    body = {
        "timeMin": start.isoformat() + "Z",
        "timeMax": end.isoformat() + "Z",
        "items": [{"id": "primary"}]
    }

    events_result = service.freebusy().query(body=body).execute()
    busy_times = events_result["calendars"]["primary"]["busy"]
    return len(busy_times) == 0


def create_event(summary, date, time, user_name="Utente", user_email=None):
    service = get_calendar_service()
    start = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    end = start + timedelta(hours=1)

    if not check_availability(start, end):
        print(f"⚠️ Fascia oraria già occupata: {date} {time}")
        return None

    if not user_email:
        user_email = get_authenticated_email(service)

    event = {
        "summary": f"{summary} - {user_name}",
        "description": f"Prenotazione per {summary}",
        "start": {"dateTime": start.isoformat(), "timeZone": "Europe/Rome"},
        "end": {"dateTime": end.isoformat(), "timeZone": "Europe/Rome"},
        "attendees": [{"email": user_email}],
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "email", "minutes": 30},
                {"method": "popup", "minutes": 10}
            ],
        },
    }

    created = service.events().insert(
        calendarId="primary",
        body=event,
        sendUpdates="all"
    ).execute()

    print(f"✅ Evento aggiunto su Google Calendar e email inviata a {user_email}")
    return created.get("id")
