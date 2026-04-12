import json
import os

def create_gold_standard_entry():
    link="https://www.cbsnews.com/news/winehouse-not-guilty-for-punching-fan-in-the-face/"
    link1="https://www.cbsnews.com/news/artemis-ii-astronauts-welcomed-home-to-houston-after-historic-moonshot/"

    html_file_path = "winehouse_not_guilty_for_punching_fan_in_the_face.html"
    testo_pulito_path = "winehouse_not_guilty_for_punching_fan_in_the_face_gs.txt"
    
    os.makedirs("../gs_data", exist_ok=True)
    output_json_path = "../gs_data/cbsnews.com_gs.json"

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
        "title": "Winehouse Not Guilty for Punching Fan in the Face",
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