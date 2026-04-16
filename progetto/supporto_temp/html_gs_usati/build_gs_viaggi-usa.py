import json
import os

def create_gold_standard_entry():

    #link ="https://www.viaggi-usa.it/passaporto-per-usa/"
    #link="https://www.viaggi-usa.it/eventi-san-diego/"



    link ="https://www.viaggi-usa.it/parchi-usa/grand-canyon/"

    html_file_path = "grand_canyon_guida_al_meraviglioso_parco_dellarizona.html"
    testo_pulito_path = "grand_canyon_guida_al_meraviglioso_parco_dellarizona_gs.txt"
    
    os.makedirs("../../gs_data", exist_ok=True)
    output_json_path = "../../gs_data/viaggi-usa.it.json"

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
        "domain": "viaggi-usa.it",
        "title": "Passaporto per USA: documenti, pratiche e tempi rilascio",
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