import json
import difflib
from pathlib import Path

import json
import difflib
from pathlib import Path

def generate_clean_kb():
    raw_file = Path("data/raw_services.json")
    clean_file = Path("data/services.json")

    if not raw_file.exists():
        print("⚠️ Esegui prima lo scraping!")
        return

    with open(raw_file, "r", encoding="utf-8") as f:
        raw = json.load(f)

    kb = {"servizi": []}
    for item in raw:
        faq = [
            {
                "domanda": f"Cos'è il servizio {item['nome']}?",
                "risposta": item.get("descrizione", "Servizio disponibile sul sito del Comune.")
            },
            {
                "domanda": f"Come posso richiedere il servizio {item['nome']}?",
                "risposta": f"Puoi presentare la richiesta seguendo le istruzioni sulla pagina ufficiale: {item.get('url', '')}"
            },
            {
                "domanda": f"Dove devo recarmi per usufruire del servizio {item['nome']}?",
                "risposta": "Generalmente presso l'ufficio comunale competente o tramite lo sportello online."
            },
            {
                "domanda": f"Quali documenti servono per il servizio {item['nome']}?",
                "risposta": "I documenti richiesti variano a seconda del servizio. Consulta la pagina ufficiale per l'elenco aggiornato."
            },
            {
                "domanda": f"Quanto tempo serve per completare il servizio {item['nome']}?",
                "risposta": "I tempi di lavorazione possono variare. In genere il Comune risponde entro pochi giorni lavorativi."
            },
            {
                "domanda": f"Quanto costa il servizio {item['nome']}?",
                "risposta": "Eventuali costi o diritti di segreteria sono indicati nella sezione 'Costi' della pagina del servizio."
            },
            {
                "domanda": f"Chi può richiedere il servizio {item['nome']}?",
                "risposta": "Il servizio è disponibile per i cittadini residenti o domiciliati nel Comune, salvo diversa indicazione."
            },
            {
                "domanda": f"Il servizio {item['nome']} può essere richiesto online?",
                "risposta": "Molti servizi comunali sono disponibili online tramite SPID o CIE. Verifica sulla pagina dedicata."
            },
            {
                "domanda": f"A chi posso chiedere informazioni sul servizio {item['nome']}?",
                "risposta": "Puoi contattare l’ufficio comunale competente, i cui recapiti sono indicati sulla scheda del servizio."
            },
            {
                "domanda": f"In quali orari è disponibile il servizio {item['nome']}?",
                "risposta": "Gli orari di apertura sono indicati nella sezione contatti o nella pagina del servizio sul sito del Comune."
            }
        ]

        kb["servizi"].append({"nome": item["nome"], "faq": faq})

    with open(clean_file, "w", encoding="utf-8") as f:
        json.dump(kb, f, indent=2, ensure_ascii=False)

    print(f"✅ Generato {clean_file}")


def get_answer_from_kb(question):
    with open("data/services.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    best = None
    score = 0
    for servizio in data["servizi"]:
        for faq in servizio["faq"]:
            ratio = difflib.SequenceMatcher(None, question.lower(), faq["domanda"].lower()).ratio()
            if ratio > score:
                best, score = faq["risposta"], ratio
    return best or "Mi dispiace, non ho trovato una risposta alla tua domanda."

if __name__ == "__main__":
    generate_clean_kb()
