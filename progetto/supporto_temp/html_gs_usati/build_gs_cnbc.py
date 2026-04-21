import json
import os
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode,DefaultMarkdownGenerator


async def fetch_raw_html(url:str) -> str:
    fetch_config = CrawlerRunConfig(
        wait_until="domcontentloaded",
        process_iframes=False,
        remove_overlay_elements=False,
    )
    async with AsyncWebCrawler(config=BrowserConfig()) as crawler:
        result = await crawler.arun(url=url, config=fetch_config)

    if not getattr(result, "success", True):
        raise RuntimeError(getattr(result, "error_message", "Fetch Failed"))

    html = getattr(result, "html", "") or ""
    if not html:
        raise RuntimeError("No HTML content retrieved")

    return html

async def create_gold_standard_entry():
    #link = "https://www.cnbc.com/2022/02/21/bitcoin-btc-bull-market-may-not-return-until-2024-huobi-co-founder.html"
    #link = "https://www.cnbc.com/2026/04/13/trump-iran-war-strait-of-hormuz-blockade.html"
    #link = "https://www.cnbc.com/2026/04/14/nvidia-stock-nvda-ai-streak.html"
    #link = "https://www.cnbc.com/2026/04/13/pancreatic-cancer-drug-daraxonrasib-from-revolution-medicines-succeeds-in-trial.html"
    #link = "https://www.cnbc.com/2026/04/06/fda-says-foreign-drug.html"
    #link = "https://www.cnbc.com/2020/02/14/renault-cuts-dividend-slices-profit-goal-for-2020.html"
    #link = "https://www.cnbc.com/2026/01/14/oil-energy-shell-bp-green-investors-agm-season.html"
    
    #aggiunti di notte come un pazzo:
    #link = "https://www.cnbc.com/2025/11/06/sam-altman-says-openai-will-top-20-billion-annual-revenue-this-year.html?&qsearchterm=Openai%20chatbot"
    #link = "https://www.cnbc.com/2026/03/31/warren-buffett-says-he-sold-apple-too-soon-and-would-buy-more-of-it-though-not-in-this-market-.html"
    #link = "https://www.cnbc.com/2025/03/08/how-facebook-marketplace-is-keeping-young-people-on-the-platform-.html"
    #link = "https://www.cnbc.com/2025/10/01/financial-advisor-100-methodology-2025.html"
    link="https://www.cnbc.com/2024/11/20/ollolai-italy-dollar-homes-to-americans.html"

    #html_file_path = "how_activist_investors_plan_to_take_on_big_oil_at_the_2026_agm_season.html"
    testo_pulito_path = "ollolai_italy_dollar_homes_to_americans_gs.txt"
    os.makedirs("../../gs_data", exist_ok=True)
    output_json_path = "../../gs_data/www.cnbc.com.json"

    try:
        print(f"Scaricamento HTML live da: {link}")
        html_content = await fetch_raw_html(link)
    except Exception as e:
        print(f"Errore durante il fetch dell'HTML: {e}")
        return

    #try:
    #    with open(html_file_path, "r", encoding="utf-8") as f:
    #        html_content = f.read()
    #except FileNotFoundError:
    #    print(f"Errore: Il file {html_file_path} non è stato trovato.")
    #    return

    try:
        with open(testo_pulito_path, "r", encoding="utf-8") as f:
            clean_text = f.read()
    except FileNotFoundError:
        print(f"Errore: Il file {testo_pulito_path} non è stato trovato.")
        return

    gs_entry = {
        "url": link,
        "domain": "www.cnbc.com",
        "title": "This village in Italy is offering $1 homes to Americans looking to move abroad post-election",
        "html_text": html_content,
        "gold_text": clean_text
    }

    try:
        if os.path.exists(output_json_path) and os.path.getsize(output_json_path) > 0:
            with open(output_json_path, "r", encoding="utf-8") as f:
                gs_list = json.load(f)
        else:
            gs_list = []

        gs_list.append(gs_entry)

        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(gs_list, f, indent=4, ensure_ascii=False)
            
        print(f"Successo! Il file {output_json_path} è stato generato/aggiornato correttamente.")

    except json.JSONDecodeError:
        print(f"Errore: Il file {output_json_path} è corrotto o contiene JSON non valido. Cancellalo o svuotalo del tutto.")   
    except Exception as e:
        print(f"Si è verificato un errore durante la scrittura del JSON: {e}")

if __name__ == "__main__":
    asyncio.run(create_gold_standard_entry())