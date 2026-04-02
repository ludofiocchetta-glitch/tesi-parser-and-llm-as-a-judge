import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def main():
    #configuro il browser
    browser_config = BrowserConfig(headless=True)

    #configuro il tipo di richiesta, bypassando la cache         #questa parte per avere un testo più pulito.
    crawler_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS,css_selector="#mw-content-text")

    #struttura tipo open file
    async with AsyncWebCrawler(config=browser_config) as luridoverme:
        result = await luridoverme.arun(url="https://en.wikipedia.org/wiki/TonyPitony", config=crawler_config)


    # in result ci sono un botto di campi:
    #result.succes
    #result.error_message

    #result.markdown
    #result.cleaned_html
    #result.html

    #print(result.markdown)
    with open("risultato.md", "w", encoding="utf-8") as file:
        file.write(result.markdown)
    print("Scrittura completata! File salvato come 'risultato.markdown'.")

asyncio.run(main())