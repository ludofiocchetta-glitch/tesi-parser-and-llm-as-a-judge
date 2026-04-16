import json
import os

def create_gold_standard_entry():
    link1="https://www.cbsnews.com/news/winehouse-not-guilty-for-punching-fan-in-the-face/"
    link2="https://www.cbsnews.com/news/artemis-ii-astronauts-welcomed-home-to-houston-after-historic-moonshot/"
    link3="https://www.cbsnews.com/news/trump-pope-leo-feud-politics/"
    link4="https://www.cbsnews.com/news/coffee-tea-caffeine-dementia-risk-study/"
    link="https://www.cbsnews.com/news/cds-vs-high-yield-savings-accounts-better-inflation-rising/"
    
    html_file_path = "woman_killed_by_police_at_omaha_walmart_after_allegedly_kidnapping_slashing_child.html"
    testo_pulito_path = "woman_killed_by_police_at_omaha_walmart_after_allegedly_kidnapping_slashing_child_gs.txt"
    
    os.makedirs("../../gs_data", exist_ok=True)
    output_json_path = "../../gs_data/cbsnews.com.json"

    try:
        with open(html_file_path, "r", encoding="utf-8") as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"Errore: Il file {html_file_path} non è stato trovato.")
        return

    try:
        with open(testo_pulito_path, "r", encoding="utf-8") as f:
            clean_text = f.read()
    except FileNotFoundError:
        print(f"Errore: Il file {testo_pulito_path} non è stato trovato.")
        return

    gs_entry = {
        "url": link,
        "domain": "cbsnews.com",
        "title": "Woman killed by police at Omaha Walmart after allegedly kidnapping, slashing child",
        "html_text": html_content,
        "gold_text": clean_text
    }

    try:
        if os.path.exists(output_json_path):
            with open(output_json_path, "r", encoding="utf-8") as f:
                gs_list = json.load(f)
        else:
            gs_list = []

        gs_list.append(gs_entry)

        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(gs_list, f, indent=4, ensure_ascii=False)
            
        print(f"Successo! Il file {output_json_path} è stato generato/aggiornato correttamente.")
        
    except Exception as e:
        print(f"Si è verificato un errore durante la scrittura del JSON: {e}")

if __name__ == "__main__":
    create_gold_standard_entry()