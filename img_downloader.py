import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import time
from carcard import CarCard
import re
from collections import Counter

df = pd.read_csv("db_cleaned.csv")
cards = []
for _, row in df.iterrows():
    card = CarCard(
        name=row["name"],
        manufacturer=row["man"],
        year=row["year"],
        model=row["model"],
        car_type=row["type"],
        rarity=row["rarity"],
        country=row["country"],
        car_class=row["class"],
        pi=row["PI"],
        speed=row["speed"],
        handling=row["handling"],
        acceleration=row["acceleration"],
        launch=row["launch"],
        braking=row["braking"],
        offroad=row["offroad"],
        avg_stat=row["avg"]
    )
    cards.append(card)


BASE_URL = "https://forza.fandom.com/wiki/"
SAVE_FOLDER = "images/cars"
headers = {
    "User-Agent": "Mozilla/5.0"
}
total_images = len(cards)
modelli = [c.model for c in cards]
counter = Counter(modelli)
not_found = []
for i, c in enumerate(cards):
    print(f"Immagine {i + 1}/{total_images}")
    manufacturer = c.manufacturer
    model = c.model
    if "Welcome Pack" in model:
        model = model.replace("Welcome Pack", "")
    elif "Forza Edition" in model:
        model = model.replace("Forza Edition", "")
    name = c.name
    name_save = re.sub(r'[<>:"/\\|?*]', '', f"{name}.png")
    man_us = manufacturer.replace("_", "-").replace(" ", "_").replace("\"", "%27").replace("'", "%27").replace("#", "")
    model_us = model.replace("_", "-").replace(" ", "_").replace("\"", "%27").replace("'", "%27").replace("#", "")
    man_piu = manufacturer.replace("_", "-").replace(" ", "+").replace("\"", "%27").replace("'", "%27").replace("#", "")
    model_piu = model.replace("_", "-").replace(" ", "+").replace("\"", "%27").replace("'", "%27").replace("#", "")

    urls_to_try = []

    # Primo tentativo: manufacturer + model con us e +
    if manufacturer == "Extreme E":
        page_name_full = "Extreme_E_Odyssey_21_e-SUV"
        file_name_full = f"Extreme+E+Odyssey+21+e-SUV+{model_piu}+Large"
    elif "(" in model:
        page_name_full = f"{man_us}_{model_us}"
        file_name_full = f"FH5+{man_piu}+{model_piu.replace('(', '').replace(')', '')}.png"
    else:
        page_name_full = f"{man_us}_{model_us}"
        file_name_full = f"FH5+{man_piu}+{model_piu}.png"

    save_path_full = os.path.join(SAVE_FOLDER, name_save)
    url_full = f"{BASE_URL}{page_name_full}?file={file_name_full}"
    urls_to_try.append((url_full, file_name_full, save_path_full))

    # Secondo tentativo: manufacturer + model con us e us
    page_name_full = f"{man_us}_{model_us}"
    file_name_full = f"FH5_{man_us}_{model_us}.png"
    save_path_full = os.path.join(SAVE_FOLDER, name_save)
    url_full = f"{BASE_URL}{page_name_full}?file={file_name_full}"
    urls_to_try.append((url_full, file_name_full, save_path_full))

    # Terzo tentativo: solo model con us e +
    page_name_model = model_us
    file_name_model = f"FH5+{model_piu}.png"
    save_path_model = os.path.join(SAVE_FOLDER, name_save)
    url_model = f"{BASE_URL}{page_name_model}?file={file_name_model}"
    urls_to_try.append((url_model, file_name_model, save_path_model))

    # Quarto tentativo: solo model con us e us
    page_name_model = model_us
    file_name_model = f"FH5_{model_us}.png"
    save_path_model = os.path.join(SAVE_FOLDER, name_save)
    url_model = f"{BASE_URL}{page_name_model}?file={file_name_model}"
    urls_to_try.append((url_model, file_name_model, save_path_model))

    # Quinto tentativo: man + model con HOR_XB1
    page_name_full = f"{man_us}_{model_us}"
    file_name_full = f"FH5+{man_piu}+{model_piu}.png"
    save_path_full = os.path.join(SAVE_FOLDER, name_save)
    url_full = f"{BASE_URL}{page_name_full}?file=HOR+XB1+{file_name_full}"
    urls_to_try.append((url_full, file_name_full, save_path_full))

    # Sesto tentativo: man + model con Large alla fine
    page_name_full = f"{man_us}_{model_us}"
    file_name_full = f"FH5_{man_us}_{model_us}_Large.png"
    save_path_full = os.path.join(SAVE_FOLDER, name_save)
    url_full = f"{BASE_URL}{page_name_full}?file={file_name_full}"
    urls_to_try.append((url_full, file_name_full, save_path_full))

    # Settimo tentativo: man + model con anno
    page_name_full = f"{man_us}_{model_us}"
    file_name_full = f"FH5_{man_piu}+{model_piu.replace('(','').replace(')','')}.png"
    save_path_full = os.path.join(SAVE_FOLDER, name_save)
    url_full = f"{BASE_URL}{page_name_full}?file={file_name_full}"
    urls_to_try.append((url_full, file_name_full, save_path_full))

    found = False
    for url, file_name, save_path in urls_to_try:
        if os.path.exists(save_path):
            print(f"⏭️ File già presente, skip: {file_name}")
            found = True
            break
    for url, file_name, save_path in urls_to_try:
        if not found:
            url_input = input(f"url per {name_save}")
            print(f"Tentativo download da: {url_input}")
            try:
                resp = requests.get(url_input, headers=headers, stream=True, timeout=3)
                print(f"Connesso alla pagina")
                resp.raise_for_status()
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.content, "html.parser")
                    img_tag = soup.find("a", class_="image-thumbnail")
                    if img_tag and "href" in img_tag.attrs:
                        img_url = img_tag['href']
                        if img_url.startswith("//"):
                            img_url = "https:" + img_url
                        img_resp = requests.get(img_url, headers=headers, stream=True, timeout=5)
                        img_resp.raise_for_status()
                        with open(save_path, "wb") as f:
                            for chunk in img_resp.iter_content(chunk_size=8192):
                                f.write(chunk)
                        print(f"✅ Salvata {name_save}")
                        found = True
                        break
            except Exception as e:
                print(f"{e}")
            time.sleep(1)

    if not found:
        print(f"⚠️ Nessuna immagine trovata per: {name_save}")
        not_found.append(model)

print("🏁 Download completato.")
with open("missing_photos", "w", encoding="utf-8") as f:
    for model in not_found:
        f.write(f"{model}\n")
