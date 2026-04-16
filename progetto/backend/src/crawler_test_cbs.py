#import per crawl4ai
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode,DefaultMarkdownGenerator

#import per pulizia md
import re  

#import per formato json
import json

#import per gestione file
import os


async def parser_cbs(url:str):

    #link = "https://www.cbsnews.com/news/omaha-nebraska-police-kill-woman-slashed-child-knife-walmart/"
    #link = "https://www.cbsnews.com/news/coffee-tea-caffeine-dementia-risk-study/"
    #link = "https://www.cbsnews.com/news/cds-vs-high-yield-savings-accounts-better-inflation-rising/"
    #link = "https://www.cbsnews.com/news/trump-pope-leo-feud-politics/"
    #link = "https://www.cbsnews.com/news/winehouse-not-guilty-for-punching-fan-in-the-face/"
    #link = "https://www.cbsnews.com/news/artemis-ii-astronauts-welcomed-home-to-houston-after-historic-moonshot/"

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

    #javascript snippet
    remove_infobox_js = """
        const infoboxes = document.querySelectorAll('.content__grid, .content__google, .embed__caption-container, .component__item-recirc-block, .component__title, .content__tags, .content__footer, .item--asset-wrapper, .bodysmall, .postAux, .component__item-recirc, .content__body--footer, .content__meta--brand-font');
        infoboxes.forEach(box => box.remove());
    """


    css_list = ["article"]
    #configuro il tipo di richiesta, bypassando la cache         
    crawler_config = CrawlerRunConfig(
                                      cache_mode=CacheMode.BYPASS,
                                      target_elements=css_list, # questa parte per avere un testo più pulito.
                                      markdown_generator=md_generator, # questo per generare markdown con personalizzazione
                                      js_code= remove_infobox_js
                                    )

    #struttura tipo open file
    async with AsyncWebCrawler(config=browser_config) as pippo:
        result = await pippo.arun(url=url, config=crawler_config)


    # in result ci sono un botto di campi:
    #result.succes
    #result.error_message

    #result.markdown
    #result.cleaned_html
    #result.html

    
    ##########################  PULIZIA DEL MARKDOWN  ##########################
    
    ris = result.markdown
    ris = re.sub(r"\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)\b ", "", ris)
    ris = re.sub(r'(\*\*|_)(.*?)\1', r'\2', ris)
    ris = re.sub(r"\* \* \*\n+.*?\n+\* \* \*", "", ris, flags=re.IGNORECASE)
    
    #####################################################################################

    ##########################  CREAZIONE JSON     ###################################
    
    #estraggo il titolo
    titolo_match=re.search(r'<h1 class="content__title">(.*?)</h1>',result.html,re.IGNORECASE)
    if titolo_match:
        titolo_pag= titolo_match.group(1).replace( " - CBS News","")
    else:
        titolo_pag="titolo non trovato"
    
    titolo_safe = re.sub(r'[^\w\s]', '', titolo_pag)
    titolo_file = re.sub(r'_+', '_', titolo_safe.lower().replace(" ", "_"))
    
    ris="\n".join(ris.splitlines()[1:])

    #creo il dizionario

    dati_estratti = {
        "url": url,
        "domain": "cbsnews.com",
        "title": titolo_pag,
        "html_text": result.html,
        "parsed_text": ris 
    }

    ##########################  PATH  ##################################################
    #dest_json = "./json_garbage/cbs" 
    #dest_md = "./md_garbage/cbs"
    
    #os.makedirs(dest_json, exist_ok=True)
    #os.makedirs(dest_md, exist_ok=True)

    #path_json = os.path.join(dest_json, f"{titolo_file}.json")
    #path_md = os.path.join(dest_md, f"{titolo_file}.md")

    ##########################  SCRITTURA IN JSON  #####################################

    #with open(path_json, "w", encoding="utf-8") as file:
        #json.dump(dati_estratti, file, indent=4, ensure_ascii=False)
    #print(f"Scrittura completata! File salvato come '{titolo_file}.json'.")

    ##########################  SCRITTURA IN MD  #######################################
    
    #with open(path_md, "w", encoding="utf-8") as file:
        #file.write(ris)
    #print(f"Scrittura completata! File salvato come '{titolo_file}.md'.")

    ####################################################################################
    
    return dati_estratti

#asyncio.run(main())