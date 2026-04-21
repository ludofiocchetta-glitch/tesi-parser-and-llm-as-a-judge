import json
import os

def create_gold_standard_entry():
    link = "https://www.cnbc.com/2022/02/21/bitcoin-btc-bull-market-may-not-return-until-2024-huobi-co-founder.html"
    #link = "https://www.cnbc.com/2026/04/13/trump-iran-war-strait-of-hormuz-blockade.html"
    #link = "https://www.cnbc.com/2026/04/14/nvidia-stock-nvda-ai-streak.html"
    #link = "https://www.cnbc.com/2026/04/13/pancreatic-cancer-drug-daraxonrasib-from-revolution-medicines-succeeds-in-trial.html"
    #link = "https://www.cnbc.com/2026/04/06/fda-says-foreign-drug.html"
    #link = "https://www.cnbc.com/2020/02/14/renault-cuts-dividend-slices-profit-goal-for-2020.html"

    html_file_path = "next_bitcoin_bull_run_wont_happen_until_end_2024_says_top_crypto_exchange_cofounder.html"
    testo_pulito_path = "next_bitcoin_bull_run_wont_happen_until_end_2024_says_top_crypto_exchange_cofounder_gs.txt"
    
    os.makedirs("../../gs_data", exist_ok=True)
    output_json_path = "../../gs_data/www.cnbc.com.json"

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
        "domain": "www.cnbc.com",
        "title": "Next bitcoin bull run won’t happen until end 2024, says top crypto exchange co-founder",
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