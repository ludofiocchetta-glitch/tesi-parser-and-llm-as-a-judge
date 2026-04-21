#import for crawl4ai
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode,DefaultMarkdownGenerator

#import for md cleaning
import re  


async def parser_cnbc(url:str, html_text:str):

    #link = "https://www.cnbc.com/2026/04/14/eric-swalwell-accuser-rape-california.html"
    #link = "https://www.cnbc.com/2026/04/06/fda-says-foreign-drug.html"
    #link = "https://www.cnbc.com/2026/04/13/pancreatic-cancer-drug-daraxonrasib-from-revolution-medicines-succeeds-in-trial.html"
    #link = "https://www.cnbc.com/2026/04/14/nvidia-stock-nvda-ai-streak.html"
    #link = "https://www.cnbc.com/2022/02/21/bitcoin-btc-bull-market-may-not-return-until-2024-huobi-co-founder.html"
    #link = "https://www.cnbc.com/2026/04/13/trump-iran-war-strait-of-hormuz-blockade.html"

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
        const elementsToRemove = document.querySelectorAll(`
            .RelatedQuotes-relatedQuotes, 
            .PlaceHolder-wrapper,        
            .ArticleBody-googlePreferredSourceContainer,
            .InlineImage-imageEmbedCaption, 
            .InlineImage-imageEmbedCredit,
            .RelatedContent-container,
            .ReadMore-container-cnbc,
            .RenderKeyPoints-wrapper
        `);
        elementsToRemove.forEach(el => el.remove());

        //Remove tag <strong> of the disclaimer
        const boldTags = document.querySelectorAll('strong, b');
        boldTags.forEach(tag => {
            // CONTROLLO SULLA FRASE "DEVELOPING..."
            if (tag.textContent.includes('This is developing news')) {
                tag.closest('p') ? tag.closest('p').remove() : tag.remove();
            }
        });
    """

    #configuration for the crawler run        
    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        target_elements=[".group"],
        markdown_generator=md_generator,
        js_code=remove_infobox_js 
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
    clean_text = re.sub(r'In this article.*?CREATE FREE ACCOUNT\n?', '', clean_text, flags=re.DOTALL | re.IGNORECASE)
    clean_text = re.sub(r'watch now\s*VIDEO\d+:\d{2}\d+:\d{2}\n?', '', clean_text, flags=re.IGNORECASE)
    clean_text = re.sub(r'Choose CNBC as your preferred source on Google.*?business news\.', '', clean_text, flags=re.DOTALL | re.IGNORECASE)
    clean_text = clean_text.replace("'", "’")
    clean_text = re.sub(r'"([^"]*)"', r'“\1”', clean_text)
    clean_text = re.sub(r"^Watch:\s*.*$", "", clean_text, flags=re.MULTILINE | re.IGNORECASE)
    clean_text = re.sub(r'\n{3,}', '\n\n', clean_text).strip()
    

    ##########################  CREAZIONE JSON     ###################################
    
    # Title extraction
    title_match = re.search(r'<h1 class="ArticleHeader-headline[^>]*>(.*?)</h1>', result.html, re.IGNORECASE)
    
    if title_match:
        page_title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
    else:
        title_match_fallback = re.search(r'<title>(.*?)</title>', result.html, re.IGNORECASE)
        if title_match_fallback:
            page_title = title_match_fallback.group(1).split('|')[0].strip()
        else:
            page_title = "title_not_found"

    #json creation
    extracted_data = {
        "url": url,
        "domain": "www.cnbc.com",
        "title": page_title,
        "html_text": result.html,
        "parsed_text": clean_text 
    }
    
    return extracted_data