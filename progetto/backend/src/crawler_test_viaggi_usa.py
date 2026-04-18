#import for crawl4ai
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode,DefaultMarkdownGenerator

#import for md cleaning
import re  


async def parser_viaggi_usa(url: str):
    #link = "https://www.viaggi-usa.it/parchi-usa/grand-canyon/"
    #link = "https://www.viaggi-usa.it/eventi-san-diego/"
    #link = "https://www.viaggi-usa.it/passaporto-per-usa/"
    #link = "https://www.viaggi-usa.it/route-66-storia/"
    #link = "https://www.viaggi-usa.it/four-mile-old-west-town-museum/"
    #link = "https://www.viaggi-usa.it/oahu-cosa-vedere/"

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
        //'.wp-block-list',
        'p:has(> .featured-links)',
        'p.has-text-align-center:has(a.featured-links)',
        '.wp-element-caption',
        '.has-text-align-center'
    ];
    
    patterns.forEach(selector => {
        document.querySelectorAll(selector).forEach(el => el.remove());
    });
    """


    css_list = ["article"]
    #configuration for the crawler run         
    crawler_config = CrawlerRunConfig(
                                      cache_mode=CacheMode.BYPASS,
                                      target_elements=css_list, 
                                      
                                      markdown_generator=md_generator,
                                      js_code= remove_infobox_js
                                    )

    # Execute crawler
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=crawler_config)


    ##########################  MARKDOWN CLEANUP  ##########################
    
    clean_text = result.markdown
    clean_text = re.sub(r"\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)\b ", "", clean_text)
    clean_text = re.sub(r'(\*\*|_)(.*?)\1', r'\2', clean_text)
    clean_text = re.sub(r"\* \* \*\n+.*?\n+\* \* \*", "", clean_text, flags=re.IGNORECASE)
    clean_text = re.sub(r'#',"",clean_text)
    clean_text = re.sub(r'([a-zA-Z0-9])\(', r'\1 (', clean_text)
    clean_text = re.sub(r'\s+([,.;!?])', r'\1', clean_text)
    clean_text = re.sub(r'Ecco quindi tutti i nostri articoli dedicati a.*?(?:[:\.])',"",clean_text,flags=re.IGNORECASE | re.DOTALL)
    clean_text = re.sub(r'_(.*?)_', r'\1', clean_text) 
    clean_text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', clean_text)
    clean_text = re.sub(r'\* ','',clean_text)
    

    ##########################  JSON CREATION  ###################################
    
    # Title extraction
    title_match = re.search(r'<title>(.*?)</title>', result.html, re.IGNORECASE | re.DOTALL)
    if title_match:
        page_title = re.sub(r'<.*?>', '', title_match.group(1)).strip()
    else:
        page_title="title_not_found"    

    #json creation
    extracted_data = {
        "url": url,
        "domain": "viaggi-usa.it",
        "title": page_title,
        "html_text": result.html,
        "parsed_text": clean_text 
    }

    return extracted_data

