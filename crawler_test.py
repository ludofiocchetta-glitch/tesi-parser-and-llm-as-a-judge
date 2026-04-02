#import per crawl4ai
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode,DefaultMarkdownGenerator

#import per pulizia md
import re  


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


    #configuro il tipo di richiesta, bypassando la cache         
    crawler_config = CrawlerRunConfig(
                                      cache_mode=CacheMode.BYPASS,
                                      css_selector="#mw-content-text", # questa parte per avere un testo più pulito.
                                      markdown_generator=md_generator) # questo per generare markdown con personalizzazione

    #struttura tipo open file
    async with AsyncWebCrawler(config=browser_config) as luridoverme:
        result = await luridoverme.arun(url="https://en.wikipedia.org/wiki/TonyPitony", config=crawler_config)


    # in result ci sono un botto di campi:
    #result.succes
    #result.error_message

    #result.markdown
    #result.cleaned_html
    #result.html

    
    ##########################  PULIZIA DEL MARKDOWN  ##########################
    
    ris = re.sub("\[\d+\]|\[edit\]", "", result.markdown)
    testo = re.split(r"##\s*References", ris, flags=re.IGNORECASE)
    ris = testo[0].strip()
    
    
    #####################################################################################



    ##########################  SCRITTURA IN FILE  ##########################
    
    #print(result.markdown)
    with open("risultato.md", "w", encoding="utf-8") as file:
        file.write(ris)
    print("Scrittura completata! File salvato come 'risultato.markdown'.")

    #####################################################################################

asyncio.run(main())