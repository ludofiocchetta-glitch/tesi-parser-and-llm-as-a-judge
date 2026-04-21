import json
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def fix_json():
    file_path = "../../gs_data/www.cnbc.com.json" 
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    browser_config = BrowserConfig(headless=True)
    run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, delay_before_return_html=3.0, magic=True)
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        for item in data:
            url = item['url']
            print(f"Scaricando HTML perfetto per: {url}")
            result = await crawler.arun(url=url, config=run_config)
            
            if "ArticleBody-articleBody" in result.html:
                item['html_text'] = result.html
                print("HTML estratto e aggiornato!")
            else:
                print("CNBC ha bloccato la richiesta.")
                
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    print("FILE CNBC AGGIORNATO!")

if __name__ == "__main__":
    asyncio.run(fix_json())