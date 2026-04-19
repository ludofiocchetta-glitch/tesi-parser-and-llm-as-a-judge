#import for crawl4ai
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode,DefaultMarkdownGenerator

#import for md cleaning
import re  


async def parser_cbs(url:str, html_text:str):
    #link = "https://www.cbsnews.com/news/omaha-nebraska-police-kill-woman-slashed-child-knife-walmart/"
    #link = "https://www.cbsnews.com/news/coffee-tea-caffeine-dementia-clean_textk-study/"
    #link = "https://www.cbsnews.com/news/cds-vs-high-yield-savings-accounts-better-inflation-clean_texting/"
    #link = "https://www.cbsnews.com/news/trump-pope-leo-feud-politics/"
    #link = "https://www.cbsnews.com/news/winehouse-not-guilty-for-punching-fan-in-the-face/"
    #link = "https://www.cbsnews.com/news/artemis-ii-astronauts-welcomed-home-to-houston-after-historic-moonshot/"

    #brower configuration
    browser_config = BrowserConfig(headless=True)

    #generator for markdown with custom options
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
    #configuration for the crawler run         
    crawler_config = CrawlerRunConfig(
                                      cache_mode=CacheMode.BYPASS,
                                      target_elements=css_list, # for cleaner output
                                      markdown_generator=md_generator, # for md generation with custom options
                                      js_code= remove_infobox_js,
                                    )

    # Execute crawler
    if(html_text==''):
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=url, config=crawler_config)
    else:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=f"raw:{html_text}", config=crawler_config)


    ##########################  MARKDOWN CLEANUP  ##########################
    
    clean_text = result.markdown
    clean_text = re.sub(r"\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)\b ", "", clean_text)
    clean_text = re.sub(r'(\*\*|_)(.*?)\1', r'\2', clean_text)
    clean_text = re.sub(r"\* \* \*\n+.*?\n+\* \* \*", "", clean_text, flags=re.IGNORECASE)
    

    ##########################  JSON CREATION  ###################################
    
    # Title extraction
    title_match=re.search(r'<h1 class="content__title">(.*?)</h1>',result.html,re.IGNORECASE)
    if title_match:
        page_title= title_match.group(1).replace( " - CBS News","")
    else:
        page_title="title_not_found"
        
    clean_text="\n".join(clean_text.splitlines()[1:])

    #json creation
    extracted_data = {
        "url": url,
        "domain": "cbsnews.com",
        "title": page_title,
        "html_text": result.html,
        "parsed_text": clean_text 
    }

    return extracted_data