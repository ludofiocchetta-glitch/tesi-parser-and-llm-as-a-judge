#import per crawl4ai
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode,DefaultMarkdownGenerator

#import per pulizia md
import re  

#import per formato json
import json


async def main():

    link = "https://www.cnbc.com/2022/02/21/bitcoin-btc-bull-market-may-not-return-until-2024-huobi-co-founder.html"
    link1 = "https://www.cnbc.com/2026/04/13/trump-iran-war-strait-of-hormuz-blockade.html"

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
        const elementsToRemove = document.querySelectorAll(`
            .RelatedQuotes-relatedQuotes, 
            .PlaceHolder-wrapper,        
            .ArticleBody-googlePreferredSourceContainer,
            .InlineImage-imageEmbedCaption, 
            .InlineImage-imageEmbedCredit,
            .RelatedContent-container
        `);
        elementsToRemove.forEach(el => el.remove());

        //Rimuove specificamente il tag <strong> del disclaimer
        const boldTags = document.querySelectorAll('strong, b');
        boldTags.forEach(tag => {
            // CONTROLLO SULLA FRASE "DEVELOPING..."
            if (tag.textContent.includes('This is developing news')) {
                tag.closest('p') ? tag.closest('p').remove() : tag.remove();
            }
        });
    """


    css_list = [".ArticleBody-articleBody"]
    #configuro il tipo di richiesta, bypassando la cache         
    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        target_elements=[".ArticleBody-articleBody"],
        markdown_generator=md_generator,
        js_code=remove_infobox_js 
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
    ris = re.sub(r'In this article.*?CREATE FREE ACCOUNT\n?', '', ris, flags=re.DOTALL | re.IGNORECASE)
    ris = re.sub(r'watch now\s*VIDEO\d+:\d{2}\d+:\d{2}\n?', '', ris, flags=re.IGNORECASE)
    ris = re.sub(r'Choose CNBC as your preferred source on Google.*?business news\.', '', ris, flags=re.DOTALL | re.IGNORECASE)
    ris = ris.replace("'", "’")
    ris = re.sub(r'"([^"]*)"', r'“\1”', ris)
    ris = re.sub(r'\n{3,}', '\n\n', ris).strip()
    
    #####################################################################################

    ##########################  SCRITTURA JSON     ###################################
    
    #estraggo il titolo
    titolo_match = re.search(r'<h1 class="ArticleHeader-headline[^>]*>(.*?)</h1>', result.html, re.IGNORECASE)
    
    if titolo_match:
        titolo_pag = re.sub(r'<[^>]+>', '', titolo_match.group(1)).strip()
    else:
        titolo_match_fallback = re.search(r'<title>(.*?)</title>', result.html, re.IGNORECASE)
        if titolo_match_fallback:
            titolo_pag = titolo_match_fallback.group(1).split('|')[0].strip()
        else:
            titolo_pag = "titolo_non_trovato"

    titolo_safe = re.sub(r'[^\w\s]', '', titolo_pag)
    titolo_file = re.sub(r'_+', '_', titolo_safe.lower().replace(" ", "_"))

    #creo il dizionario
    dati_estratti = {
        "url": link,
        "domain": "cnbc.com",
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