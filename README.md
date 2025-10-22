
# Virtual Assistant for Municipality — Quick Start Guide

This README explains step‑by‑step how to run and test the **Virtual Assistant for Municipality** prototype on your local machine.  
It covers environment setup, scraping the municipality website, generating the knowledge base, running the text chatbot, connecting Google Calendar.

---

## Prerequisites

- Python 3.9 or newer
- Git (optional)
- A web browser (Chrome, Safari, or Firefox)
- For Google Calendar integration: a Google account and a Google Cloud project with Calendar API enabled
- Internet connection

---

## 1 — Clone the project

Clone the project using:

```bash
git clone https://github.com/Giorgio163/virtual-assistant-municipality.git
cd virtual-assistant-municipality
```

---

## 2 — Create and activate a virtual environment

On macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows (PowerShell):

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

---

## 3 — Install Python dependencies

Make sure your virtual environment is active, then install required packages:

```bash
pip install -r backend/requirements.txt
```

---

## 4 — Scraping municipality services (produce raw data)

**Selenium dynamic scraper (Please give it some time to finish)**

```bash
python scraper/scrape_codroipo_selenium.py
```

Expected output (example):

```
✅ Trovati 71 servizi dinamici.
```
---

## 5 — Generate the Knowledge Base

Run:

```bash
python -m assistant.knowledge_base
```

This reads `data/raw_services.json` and creates `data/services.json` (the processed knowledge base). The script automatically generates at least 10 Q&A entries per service.

---

## 6 — Configure Google Calendar integration

To create events in Google Calendar, follow these steps:

1. Go to Google Cloud Console: https://console.cloud.google.com/apis/dashboard  
2. Create a new project (e.g., "Virtual Assistant Municipality")  
3. Enable **Google Calendar API** for the project  
4. Create OAuth credentials → **OAuth client ID** → Application type **Desktop app**  
5. Download the `credentials.json` file and place it in the project:

```
backend/credentials.json
```

> The application will create `backend/token.json` automatically after you authorize it.

---

## 7 — Run the assistant (text CLI)

Start the assistant:

```bash
python main.py
```

You will see the system prompt and a `Tu:` prompt to type:

Examples:

- `Cos'è la carta d'identità elettronica?`  
- `Prenota la carta d'identità per il 5 novembre`

The assistant will:
- answer from the knowledge base, or
- create a local appointment and create a Google Calendar event.
- To receive the confirmation e-mail please use a different e-mail than the one used for the `credentials.json`

---

## 8 — Google OAuth first-run

On first run, if Google Calendar integration is enabled and `backend/token.json` does not exist, the program will open a browser window for OAuth consent. If the browser does not open automatically, copy the printed URL into your browser.

---


