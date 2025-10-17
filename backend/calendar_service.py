from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_service():
    creds = Credentials.from_authorized_user_file("backend/token.json", SCOPES)
    return build("calendar", "v3", credentials=creds)

def check_availability(start, end):
    service = get_service()
    body = {
        "timeMin": start.isoformat() + "Z",
        "timeMax": end.isoformat() + "Z",
        "items": [{"id": "primary"}]
    }
    eventsResult = service.freebusy().query(body=body).execute()
    busy_times = eventsResult["calendars"]["primary"]["busy"]
    return len(busy_times) == 0

def create_event(user, service_name, start, end):
    service = get_service()
    event = {
        "summary": f"{service_name['title']} - {user['name']}",
        "description": f"Prenotazione per {service_name['title']}",
        "start": {"dateTime": start.isoformat(), "timeZone": "Europe/Rome"},
        "end": {"dateTime": end.isoformat(), "timeZone": "Europe/Rome"},
        "attendees": [{"email": user["email"]}],
    }
    created = service.events().insert(calendarId="primary", body=event).execute()
    return created.get("id")
