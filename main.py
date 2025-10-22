import json
from assistant.chatbot import handle_user_input

def main():
    config = json.load(open("config.json", "r", encoding="utf-8"))
    print(config["prompt"])
    print("Digita 'esci' per uscire.\n")

    while True:
        user_input = input("👤 Tu: ")
        if user_input.lower() == "esci":
            break

        response = handle_user_input(user_input)
        print(f"🤖 Assistente: {response}\n")

if __name__ == "__main__":
    main()
