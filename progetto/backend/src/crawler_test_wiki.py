#import for crawl4ai
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode,DefaultMarkdownGenerator

#import for md cleaning
import re  


async def parser_wiki(url:str, html_text:str):
    #link = "https://en.wikipedia.org/wiki/Donald_Trump"
    #link = "https://en.wikipedia.org/wiki/Artificial_intelligence"
    #link = "https://en.wikipedia.org/wiki/Charles_Darwin"
    #link = "https://en.wikipedia.org/wiki/Lanzarote"
    #link = "https://en.wikipedia.org/wiki/Alfa_Romeo_159"
    #link = "https://en.wikipedia.org/wiki/Scooby-Doo"

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
        const infoboxes = document.querySelectorAll('.infobox, .sidebar, .vertical-navbox, .navbox, .portal, .toc, .metadata, .ambox, .hatnote, .shortdescription, .figcaption, .thumbcaption');
        infoboxes.forEach(box => box.remove());
        const figures = document.querySelectorAll('figure'); 
        figures.forEach(f => f.remove());
    """

    css_list = ["h1#firstHeading","#mw-content-text"]
    #configuration for the crawler run
    crawler_config = CrawlerRunConfig(
                                      cache_mode=CacheMode.BYPASS,
                                      target_elements=css_list, # for cleaner output
                                      markdown_generator=md_generator, # for md generation with custom options
                                      js_code= remove_infobox_js
                                    )
    # Execute crawler
    if(html_text==''):
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=url, config=crawler_config)
    else:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=f"raw:{html_text}", config=crawler_config)

 
    ##########################  MARKDOWN CLEANUP  ##########################
    
    clean_text = re.sub(r"\[[a-z]\]|\[\d+\]|\[edit\]|\[show\]|\[update\]|\[\s*\]|ⓘ", "", result.markdown)
    clean_text = re.sub(r'(\*\*|_)(.*?)\1', r'\2', clean_text)
    clean_text = re.sub(r"\[citation needed\]|\[clarification needed\]|\[supporting\]|\[[A-Z]+\]","",clean_text)
    clean_text = re.sub(r"^\|[-:\s|]+\|\n?", "", clean_text, flags=re.MULTILINE)
    clean_text = re.sub(r"\s*\|\s*", " ", clean_text)
    clean_text = re.sub(r"\*\*","",clean_text)
    text = re.split(r"##\s*(?:See also|References|Notes|Further reading|External links)", clean_text, flags=re.IGNORECASE)
    clean_text = text[0].strip()


    ##########################  JSON  CREATION   ##########################
    
    # Title extraction
    title_match=re.search(r'<title>(.*?)</title>', result.html, re.IGNORECASE)
    if title_match:
        page_title= title_match.group(1).replace( " - Wikipedia","")
    else:
        page_title="title_not_found"
    

    #json creation
    extracted_data = {
        "url": url,
        "domain": "en.wikipedia.org",
        "title": page_title,
        "html_text": result.html,
        "parsed_text": clean_text 
    }

    return extracted_data