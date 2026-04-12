#import per crawl4ai
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode,DefaultMarkdownGenerator

#import per pulizia md
import re  

#import per formato json
import json


async def main():

    link="https://www.cbsnews.com/news/artemis-ii-astronauts-welcomed-home-to-houston-after-historic-moonshot/"

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
        const infoboxes = document.querySelectorAll('.ad, .newsletter, .content__grid, .content__google, .embed__caption-container, .component__item-recirc-block, .component__title, .content__tags, .content__footer');
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
        result = await pippo.arun(url=link, config=crawler_config)


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
    
    #####################################################################################

    ##########################  SCRITTURA JSON     ###################################
    
    #estraggo il titolo
    titolo_match=re.search(r'<h1 class="content__title">(.*?)</h1>',result.html,re.IGNORECASE)
    if titolo_match:
        titolo_pag= titolo_match.group(1).replace( " - CBS News","")
        titolo_file= titolo_pag.lower().replace(" ", "_")
    else:
        titolo_pag="titolo non trovato"
        titolo_file= "titolo_non_trovato"

    #creo il dizionario

    dati_estratti = {
        "url": link,
        "domain": "cbsnews.com",
        "title": titolo_pag,
        "html_text": result.html,
        "parsed_text": ris 
    }

    #salvo in un file json

    with open(f"{titolo_file}.json", "w", encoding="utf-8") as file:
        json.dump(dati_estratti, file, indent=4, ensure_ascii=False)
    print(f"Scrittura completata! File salvato come '{titolo_file}.json'.")

    #####################################################################################


    ##########################  SCRITTURA IN FILE  ##########################
    
    with open(f"{titolo_file}.md", "w", encoding="utf-8") as file:
        file.write(ris)
    print(f"Scrittura completata! File salvato come '{titolo_file}.md'.")

    #with open(f"{titolo_file}_raw.md", "w", encoding="utf-8") as file:
    #   file.write(result.markdown)
    #print(f"Scrittura completata! File salvato come '{titolo_file}_raw.md'.")

    #####################################################################################

asyncio.run(main())