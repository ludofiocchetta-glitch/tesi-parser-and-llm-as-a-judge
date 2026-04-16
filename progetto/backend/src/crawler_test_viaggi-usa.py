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
    #link = "https://www.viaggi-usa.it/parchi-usa/grand-canyon/"
    #link="https://www.viaggi-usa.it/eventi-san-diego/"
    #link="https://www.viaggi-usa.it/passaporto-per-usa/"
    link="https://www.viaggi-usa.it/route-66-storia/"

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
    const patterns = [
        'div[class*="gb-container-"]', 
        'div[class*="gb-accordion"]',
        //
        '.widget-title', 
        // Colpisce le headline di GenerateBlocks ignorando l'ID dinamico
        'h1[class*="gb-headline"]', 
        'h2[class*="gb-headline"]',
        'h3[class*="gb-headline"]',
        //
        '.PlaceHolder-wrapper',        
        '.InlineImage-imageEmbedCaption', 
        '.InlineImage-imageEmbedCredit',
        '.RelatedContent-container',
        '.inside-navigation',
        '.breadcrumbs',
        '.no_bullets',
        '.su-spoiler-title',
        '.su-spoiler', 
        '.su-spoiler-content',
        '.su-u-clearfix',
        '.su-u-trim',
        '.has-text-align-center',
        '.featured-links',
        '.wp-block-list',
        'p:has(> .featured-links)',
        'p.has-text-align-center:has(a.featured-links)'
    ];
    
    patterns.forEach(selector => {
        document.querySelectorAll(selector).forEach(el => el.remove());
    });
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
    ris = re.sub(r"\* \* \*\n+.*?\n+\* \* \*", "", ris, flags=re.IGNORECASE)
    ris = re.sub(r'#',"",ris)
    ris = re.sub(r'([a-zA-Z0-9])\(', r'\1 (', ris)
    ris = re.sub(r'\s+([,.;!?])', r'\1', ris)
    ris = re.sub(r'Ecco quindi tutti i nostri articoli dedicati a.*?(?:[:\.])',"",ris,flags=re.IGNORECASE | re.DOTALL)
    
    #####################################################################################

    ##########################  CREAZIONE JSON     ###################################
    
    #estraggo il titolo
    titolo_match = re.search(r'<title>(.*?)</title>', result.html, re.IGNORECASE | re.DOTALL)
    if titolo_match:
        titolo_pag = re.sub(r'<.*?>', '', titolo_match.group(1)).strip()
    else:
        titolo_pag="titolo non trovato"
    
    titolo_safe = re.sub(r'[^\w\s]', '', titolo_pag)
    titolo_file = re.sub(r'_+', '_', titolo_safe.lower().replace(" ", "_"))
    

    #creo il dizionario

    dati_estratti = {
        "url": link,
        "domain": "viaggi-usa.it",
        "title": titolo_pag,
        "html_text": result.html,
        "parsed_text": ris 
    }

    ##########################  PATH  ##################################################
    dest_json = "./json_garbage/viaggi-usa" 
    dest_md = "./md_garbage/viaggi-usa"
    
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