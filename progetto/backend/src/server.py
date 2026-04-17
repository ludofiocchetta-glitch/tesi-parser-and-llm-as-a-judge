from fastapi import FastAPI, HTTPException, Query
from urllib.parse import urlparse
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import json

from src.crawler_test_cbs import parser_cbs
from src.crawler_test_cnbc import parser_cnbc
from src.crawler_test_wiki import parser_wiki
from src.crawler_test_viaggi_usa import parser_viaggi_usa
from src.accuracy_tester import calculate_metrics

app = FastAPI(title="Web Scraper API")

# Modello per l'output di /parse
class ParseResponse(BaseModel):
    url: str
    domain: str
    title: str
    html_text: str
    parsed_text: str

# Modello per l'output di /gs
class GoldStandardEntry(BaseModel):
    url: str
    domain: str
    title: str
    html_text: str
    gold_text: str

# Modello per l'output di /domains
class DomainsResponse(BaseModel):
    domains: List[str]

# Modelli per la valutazione
class TokenLevelEval(BaseModel):
    precision: float
    recall: float
    f1: float

class XEval(BaseModel):
    jaccard_similarity: float
    overlap_coefficient:float
    cosine_similarity:float

class EvaluateRequest(BaseModel):
    parsed_text: str
    gold_text: str

class EvaluateResponse(BaseModel):
    token_level_eval: TokenLevelEval
    x_eval: XEval


################### PARSE ###################

@app.get("/parse", response_model=ParseResponse)
async def parse_article(url: str = Query(..., description="L'URL dell'articolo da analizzare")):

    parsed_uri = urlparse(url)
    domain = parsed_uri.netloc.replace("www.", "")

    # Smista la richiesta al file corretto
        
    if domain == "en.wikipedia.org":
        risultato = await parser_wiki(url)
        return risultato
    
    elif domain == "cbsnews.com":
        risultato = await parser_cbs(url)
        return risultato
        
    elif domain == "cnbc.com":
        risultato = await parser_cnbc(url)
        return risultato
    
    elif domain == "viaggi-usa.it":
        risultato = await parser_viaggi_usa(url)
        return risultato
        
    else:
        raise HTTPException(status_code=400, detail=f"Dominio non supportato: {domain}")
    

################### DOMAINS ###################

@app.get("/domains", response_model=DomainsResponse)
async def get_supported_domains():
    file_path = f"../domains.json"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"domains.json not exists")
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    return data


################### GOLD STANDARD ###################

@app.get("/gold_standard", response_model=GoldStandardEntry)
async def get_single_gold_standard(url: str):
    parsed_uri = urlparse(url)
    domain = parsed_uri.netloc.replace("www.", "")
    
    file_path = f"../gs_data/{domain}.json"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dominio non presente nel Gold Standard.")
        
    with open(file_path, "r", encoding="utf-8") as f:
        gs_list = json.load(f)
        
    for item in gs_list:
        if item.get("url") == url:
            return item 
            
    raise HTTPException(status_code=404, detail="URL non trovato nel Gold Standard.")


################### FULL GOLD STANDARD ###################

@app.get("/full_gold_standard", response_model=List[GoldStandardEntry])
async def get_full_gold_standard(domain: str):
    file_path = f"../gs_data/{domain}.json"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Gold standard per il dominio {domain} non trovato.")
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    return data


################### EVALUATE ###################

@app.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_text(data: EvaluateRequest):
    ris=calculate_metrics(data.parsed_text,data.gold_text)
    return {"token_level_eval": TokenLevelEval (
            precision=ris["precision"],
            recall=ris["recall"],
            f1=ris["f1"]
        ),
        "x_eval": XEval(
            jaccard_similarity=ris["jaccard_similarity"],
            overlap_coefficient=ris["overlap_coefficient"],
            cosine_similarity=ris["cosine_similarity"]
        )}











    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)