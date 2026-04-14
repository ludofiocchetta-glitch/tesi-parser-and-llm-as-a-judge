#import per crawl4ai
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode,DefaultMarkdownGenerator

#import per pulizia md
import re  

#import per formato json
import json

#import per gestione file
import os


async def main():

    
    link1= "https://en.wikipedia.org/wiki/Donald_Trump"
    link2="https://en.wikipedia.org/wiki/Artificial_intelligence"
    link3 = "https://en.wikipedia.org/wiki/Charles_Darwin"
    link4="https://en.wikipedia.org/wiki/Lanzarote"
    link = "https://en.wikipedia.org/wiki/Alfa_Romeo_159"
    link6 = "https://en.wikipedia.org/wiki/Scooby-Doo"

    #configuro il browser
    browser_config = BrowserConfig(headless=True)



    #generatore per migliorare il Markdown creato
    md_generator = DefaultMarkdownGenerator(
        options={
            "ignore_links": True,
            "escape_html": False,
            "ignore_images": True
        }
    )

    #javascript snippet per togliere l'infobox,sidebar,hatnote...
    #e le descrizioni sotto le immagini
    remove_infobox_js = """
        const infoboxes = document.querySelectorAll('.infobox, .sidebar, .vertical-navbox, .navbox, .portal, .toc, .metadata, .ambox, .hatnote, .shortdescription, .figcaption, .thumbcaption');
        infoboxes.forEach(box => box.remove());
        const figures = document.querySelectorAll('figure'); 
        figures.forEach(f => f.remove());
    """


    css_list = ["h1#firstHeading","#mw-content-text"]
    #configuro il tipo di richiesta, bypassando la cache         
    crawler_config = CrawlerRunConfig(
                                      cache_mode=CacheMode.BYPASS,
                                      target_elements=css_list, # questa parte per avere un testo più pulito.
                                      markdown_generator=md_generator, # questo per generare markdown con personalizzazione
                                      js_code= remove_infobox_js
                                    )

    #struttura tipo open file
    async with AsyncWebCrawler(config=browser_config) as pippo:
        result = await pippo.arun(url=link, config=crawler_config)


    # in result ci sono un botto di campi:
    #result.succes
    #result.error_message

    #result.markdown
    #result.cleaned_html
    #result.html

    
    ##########################  PULIZIA DEL MARKDOWN  ##########################
    
    ris = re.sub(r"\[[a-z]\]|\[\d+\]|\[edit\]|\[show\]|\[update\]|\[\s*\]|ⓘ", "", result.markdown)
    ris = re.sub(r'(\*\*|_)(.*?)\1', r'\2', ris)
    ris=re.sub(r"\[citation needed\]|\[clarification needed\]|\[supporting\]|\[[A-Z]+\]","",ris)
    # rimuove separatori delle wikitable
    ris = re.sub(r"^\|[-:\s|]+\|\n?", "", ris, flags=re.MULTILINE)
    ris = re.sub(r"\s*\|\s*", " ", ris)
    ris=re.sub(r"\*\*","",ris)
    testo = re.split(r"##\s*(?:See also|References|Notes|Further reading|External links)", ris, flags=re.IGNORECASE)
    ris = testo[0].strip()

    
    #####################################################################################

    ##########################  CREAZIONE JSON     ###################################
    
    #estraggo il titolo
    titolo_match=re.search(r'<title>(.*?)</title>',result.html,re.IGNORECASE)
    if titolo_match:
        titolo_pag= titolo_match.group(1).replace( " - Wikipedia","")
        titolo_file= titolo_pag.lower().replace(" ", "_")
    else:
        titolo_pag="titolo non trovato"
        titolo_file= "titolo_non_trovato"

    ris="\n".join(ris.splitlines()[1:])
    #creo il dizionario

    dati_estratti = {
        "url": link,
        "domain": "en.wikipedia.org",
        "title": titolo_pag,
        "html_text": result.html,
        "parsed_text": ris 
    }

    ##########################  PATH  ##################################################
    dest_json = "./json_garbage/wikipedia" 
    dest_md = "./md_garbage/wikipedia"
    
    os.makedirs(dest_json, exist_ok=True)
    os.makedirs(dest_md, exist_ok=True)

    path_json = os.path.join(dest_json, f"{titolo_file}.json")
    path_md = os.path.join(dest_md, f"{titolo_file}.md")

    ##########################  SCRITTURA IN JSON  #####################################

    with open(path_json, "w", encoding="utf-8") as file:
        json.dump(dati_estratti, file, indent=4, ensure_ascii=False)
    print(f"Scrittura completata! File salvato come '{titolo_file}.json'.")

    ##########################  SCRITTURA IN MD  #######################################
    
    with open(path_md, "w", encoding="utf-8") as file:
        file.write(ris)
    print(f"Scrittura completata! File salvato come '{titolo_file}.md'.")

    ####################################################################################

asyncio.run(main())