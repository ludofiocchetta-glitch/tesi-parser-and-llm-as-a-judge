#import for crawl4ai
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode,DefaultMarkdownGenerator

#import for md cleaning
import re  


async def parser_viaggi_usa(url: str, html_text:str) -> dict:
   
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

# Javascript snippet
    remove_infobox_js = """
    const h1 = document.querySelector('h1.gb-headline');
    const article = document.querySelector('article');

    if (h1 && article) {
        article.prepend(h1);
    }

    const allHeadlines = document.querySelectorAll('.gb-headline');
    allHeadlines.forEach(el => {
        if (el !== h1) {
            el.remove();
        }
    });

    const patterns = [
        'div[class*="gb-container-"]', 
        'div[class*="gb-accordion"]',
        '.widget-title', 
        '.PlaceHolder-wrapper',        
        '.InlineImage-imageEmbedCaption', 
        '.InlineImage-imageEmbedCredit',
        '.RelatedContent-container',
        '.inside-navigation',
        '.breadcrumbs',
        '.no_bullets',
        '.su-image-carousel',
        '.su-button',
        '.su-button-center',
        '.su-tabs',
        '.su-note',
        '.su-quote',
        '#toc_container', // <-- Questo è l'indice!
        '.postevidenza',
        '.has-text-align-center',
        '.featured-links',
        'p:has(> .featured-links)',
        'p.has-text-align-center:has(a.featured-links)',
        '.wp-element-caption',
        '.gm-style',
        '.viaggi-usa-highlight'
    ];
    
    patterns.forEach(selector => {
        document.querySelectorAll(selector).forEach(el => {
            // Evitiamo di cancellare il contenitore principale o il nostro titolo, ma distruggiamo il resto
            if (el.tagName.toLowerCase() !== 'article' && el !== h1) {
                el.remove();
            }
        });
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
    clean_text = re.sub(r'#',"",clean_text)
    clean_text = re.sub(r'([a-zA-Z0-9])\(', r'\1 (', clean_text)
    clean_text = re.sub(r'\s+([,.;!?])', r'\1', clean_text)
    clean_text = re.sub(r'Ecco quindi tutti i nostri articoli dedicati a.*?(?:[:\.])',"",clean_text,flags=re.IGNORECASE | re.DOTALL)
    clean_text = re.sub(r'_(.*?)_', r'\1', clean_text) 
    clean_text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', clean_text)
    clean_text = re.sub(r'\* ','',clean_text)
    clean_text = re.sub(r'<span[^>]*data-mce-type="bookmark"[^>]*>.*?</span>', '', clean_text)

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
        "domain": "www.viaggi-usa.it",
        "title": page_title,
        "html_text": result.html,
        "parsed_text": clean_text 
    }

    return extracted_data

