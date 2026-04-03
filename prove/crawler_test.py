#import per crawl4ai
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode,DefaultMarkdownGenerator

#import per pulizia md
import re  

#import per formato json
import json


async def main():


    

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
    remove_infobox_js = """
        const infoboxes = document.querySelectorAll('.infobox, .sidebar, .vertical-navbox, .navbox, .portal, .hatnote, .toc');
        infoboxes.forEach(box => box.remove());
    """


    #configuro il tipo di richiesta, bypassando la cache         
    crawler_config = CrawlerRunConfig(
                                      cache_mode=CacheMode.BYPASS,
                                      css_selector="#mw-content-text", # questa parte per avere un testo più pulito.
                                      markdown_generator=md_generator, # questo per generare markdown con personalizzazione
                                      js_code= remove_infobox_js
                                    )

    #struttura tipo open file
    async with AsyncWebCrawler(config=browser_config) as luridoverme:
        result = await luridoverme.arun(url="https://en.wikipedia.org/wiki/Donald_Trump", config=crawler_config)


    # in result ci sono un botto di campi:
    #result.succes
    #result.error_message

    #result.markdown
    #result.cleaned_html
    #result.html

    
    ##########################  PULIZIA DEL MARKDOWN  ##########################
    
    ris = re.sub(r"\[\d+\]|\[edit\]|(\*\*|_)(.*?)\1'", "", result.markdown)
    ris = re.sub(r'(\*\*|_)(.*?)\1', r'\2', ris)
    testo = re.split(r"##\s*(?:See also|References|Notes|Further reading|External links)", ris, flags=re.IGNORECASE)
    ris = testo[0].strip()

    
    #####################################################################################

    ##########################  SCRITTURA JSON     ###################################
    
    #estraggo il titolo
    titolo_match=re.search(r'<title>(.*?)</title>',result.html,re.IGNORECASE)
    if titolo_match:
        titolo_pag=titolo_match.group(1)
    else:
        titolo_pag="titolo non trovato"

    #creo il dizionario

    dati_estratti = {
        "url": "https://en.wikipedia.org/wiki/Donald_Trump",
        "domain": "en.wikipedia.org",
        "title": titolo_pag,
        "html_text": result.html,
        "parsed_text": ris 
    }

    #salvo in un file json

    with open("risultato.json", "w", encoding="utf-8") as file:
        json.dump(dati_estratti,file,indent=4, ensure_ascii=False)
    print("Scrittura completata! File salvato come 'risultato.json'.")

    #####################################################################################

asyncio.run(main())