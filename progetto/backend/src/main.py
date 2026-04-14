from fastapi import FastAPI, HTTPException, Query
from urllib.parse import urlparse

#from crawler_test_cbs import parser_cbs
#from crawler_test_cnbc import parser_cnbc
from crawler_test_wiki import parser_wiki

app = FastAPI(title="Web Scraper API")

@app.get("/parse")
async def parse_article(url: str = Query(..., description="L'URL dell'articolo da analizzare")):

    parsed_uri = urlparse(url)
    domain = parsed_uri.netloc.replace("www.", "")

    # Smista la richiesta al file corretto
        
    if domain == "en.wikipedia.org":
        risultato = await parser_wiki(url)
        return risultato
    
    #elif domain == "cbsnews.com":
        #risultato = await parser_cbs(url)
        #return risultato
        
    #elif domain == "cnbc.com":
        #risultato = await parser_cnbc(url)
        #return risultato
        
    else:
        raise HTTPException(status_code=400, detail=f"Dominio non supportato: {domain}")
    
if __name__ == "__main__":
    import uvicorn
    # Avvia il server direttamente da qui!
    uvicorn.run(app, host="127.0.0.1", port=8000)