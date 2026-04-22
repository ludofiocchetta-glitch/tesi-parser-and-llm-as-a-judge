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
    link1="https://www.cbsnews.com/news/winehouse-not-guilty-for-punching-fan-in-the-face/"
    link2="https://www.cbsnews.com/news/artemis-ii-astronauts-welcomed-home-to-houston-after-historic-moonshot/"
    link3="https://www.cbsnews.com/news/trump-pope-leo-feud-politics/"
    link4="https://www.cbsnews.com/news/coffee-tea-caffeine-dementia-risk-study/"
    link5="https://www.cbsnews.com/news/cds-vs-high-yield-savings-accounts-better-inflation-rising/"
    link6="https://www.cbsnews.com/news/omaha-nebraska-police-kill-woman-slashed-child-knife-walmart/"
    link7="https://www.cbsnews.com/news/russia-ukraine-war-deadliest-aerial-assault-of-year/"
    link8="https://www.cbsnews.com/news/gut-health-best-foods-chocolate-fiber/"
    link9="https://www.cbsnews.com/news/moms-decline-mental-health-study/"
    link="https://www.cbsnews.com/news/netherlands-tesla-self-driving-features-europe/"

    #html_file_path = "woman_killed_by_police_at_omaha_walmart_after_allegedly_kidnapping_slashing_child.html"
    testo_pulito_path = "netherlands_tesla_self_driving_features_europe_gs.txt"
    
    os.makedirs("../../gs_data", exist_ok=True)
    output_json_path = "../../gs_data/www.cbsnews.com.json"

    #try:
       # with open(html_file_path, "r", encoding="utf-8") as f:
           # html_content = f.read()
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
        "domain": "www.cbsnews.com",
        "title": "Tesla owners approved to use self-driving features in Netherlands, a first for Europe",
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