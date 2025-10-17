from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import json, os
from calendar_service import check_availability, create_event

app = Flask(__name__)

scheduler = BackgroundScheduler()
scheduler.start()

with open("kb/services.json", encoding="utf8") as f:
    KB = json.load(f)

@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    query = data.get("query", "").lower()

    for service in KB:
        for faq in service["faqs"]:
            if faq["q"].lower() in query:
                return jsonify({"answer": faq["a"]})

    return jsonify({"answer": "Mi dispiace, non ho trovato informazioni su questo argomento."})

@app.route("/book", methods=["POST"])
def book():
    data = request.get_json()
    user = data.get("user")
    service = data.get("service")
    date_str = data.get("date")

    try:
        start_time = datetime.fromisoformat(date_str)
        end_time = start_time + timedelta(minutes=30)
    except Exception:
        return jsonify({"error": "Formato data non valido"}), 400

    if not check_availability(start_time, end_time):
        return jsonify({"error": "Slot non disponibile"}), 409

    event_id = create_event(user, service, start_time, end_time)

    os.makedirs("logs", exist_ok=True)
    log = {
        "user": user,
        "service": service,
        "date": date_str,
        "event_id": event_id,
        "created_at": datetime.now().isoformat()
    }
    with open("logs/appointments.log", "a", encoding="utf8") as f:
        f.write(json.dumps(log) + "\n")

    reminder_time = start_time - timedelta(hours=24)
    scheduler.add_job(send_reminder, 'date', run_date=reminder_time, args=[log])

    return jsonify({"message": "Appuntamento confermato!", "event_id": event_id})

def send_reminder(log):
    with open("logs/reminders.log", "a", encoding="utf8") as f:
        f.write(json.dumps({
            "event_id": log["event_id"],
            "user": log["user"],
            "sent_at": datetime.now().isoformat()
        }) + "\n")
    print(f"Promemoria inviato a {log['user']['name']}")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
