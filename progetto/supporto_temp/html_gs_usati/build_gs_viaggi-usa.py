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
    
    #link ="https://www.viaggi-usa.it/passaporto-per-usa/"
    #link = "https://www.viaggi-usa.it/eventi-san-diego/"
    #link ="https://www.viaggi-usa.it/parchi-usa/grand-canyon/"
    #link = "https://www.viaggi-usa.it/route-66-storia/"
    #link = "https://www.viaggi-usa.it/four-mile-old-west-town-museum/"
    #link = "https://www.viaggi-usa.it/oahu-cosa-vedere/"
    #link = "https://www.viaggi-usa.it/itinerari/mid-west/ohio/"
    #link = "https://www.viaggi-usa.it/great-falls-virginia/"
    #link = "https://www.viaggi-usa.it/itinerari/mid-west/minnesota/"
    link = "https://www.viaggi-usa.it/itinerari/north-west/oregon/"

    #html_file_path = "charles_darwin.html"
    testo_pulito_path = "Oregon_USA_tutti_gli_itinerari_on_the_road_per_esplorare_lo_stato_gs.txt"
    
    os.makedirs("../../gs_data", exist_ok=True)
    output_json_path = "../../gs_data/www.viaggi-usa.it.json"

    #try:
        #with open(html_file_path, "r", encoding="utf-8") as f:
            #html_content = f.read()
    #except FileNotFoundError:
        #print(f"Errore: Il file {html_file_path} non è stato trovato.")
        #return

    try:
        print(f"Scaricamento HTML live da: {link}")
        html_content = await fetch_raw_html(link)
    except Exception as e:
        print(f"Errore durante il fetch dell'HTML: {e}")
        return

    try:
        with open(testo_pulito_path, "r", encoding="utf-8") as f:
            clean_text = f.read()
    except FileNotFoundError:
        print(f"Errore: Il file {testo_pulito_path} non è stato trovato.")
        return

    gs_entry = {
        "url": link,
        "domain": "www.viaggi-usa.it",
        "title": "Oregon USA: tutti gli itinerari on the road per esplorare lo stato",
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
    asyncio.run(create_gold_standard_entry())