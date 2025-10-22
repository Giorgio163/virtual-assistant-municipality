from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json, time

options = Options()
options.add_argument("--headless=new")
driver = webdriver.Chrome(options=options)

URL = "https://www.comune.codroipo.ud.it/it/servizi-224003"
driver.get(URL)
time.sleep(3)

links = []
elems = driver.find_elements("tag name", "a")
for e in elems:
    href = e.get_attribute("href")
    text = e.text.strip()
    if href and text and "/it/" in href and len(text) > 5:
        links.append({"nome": text, "url": href})

driver.quit()

with open("data/raw_services.json", "w", encoding="utf-8") as f:
    json.dump(links, f, indent=2, ensure_ascii=False)

print(f"✅ Trovati {len(links)} servizi dinamici.")
