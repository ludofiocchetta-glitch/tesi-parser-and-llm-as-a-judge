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

# Model for the output of /parse
class ParseResponse(BaseModel):
    url: str
    domain: str
    title: str
    html_text: str
    parsed_text: str

# Model for the output of /gs
class GoldStandardEntry(BaseModel):
    url: str
    domain: str
    title: str
    html_text: str
    gold_text: str

# Model for the output of /domains
class DomainsResponse(BaseModel):
    domains: List[str]

# Model for the output of /evaluate
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


################### ENDPOINTS ###################

################### PARSE ###################

@app.get("/parse", response_model=ParseResponse)
async def parse_article(url: str = Query(..., description="The URL of the article to analyze")):

    parsed_uri = urlparse(url)
    domain = parsed_uri.netloc.replace("www.", "")

    # Route request to the appropriate parser
    if domain == "en.wikipedia.org":
        return await parser_wiki(url)
    
    elif domain == "cbsnews.com":
        return await parser_cbs(url)
        
    elif domain == "cnbc.com":
        return await parser_cnbc(url)
    
    elif domain == "viaggi-usa.it":
        return await parser_viaggi_usa(url)
        
    else:
        raise HTTPException(status_code=400, detail=f"Domain not supported: {domain}")
    

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
        raise HTTPException(status_code=404, detail=f"Domain {domain} not present in the Gold Standard.")
        
    with open(file_path, "r", encoding="utf-8") as f:
        gs_list = json.load(f)
        
    for item in gs_list:
        if item.get("url") == url:
            return item 
            
    raise HTTPException(status_code=404, detail=f"URL {url} not found in the Gold Standard.")

################### FULL GOLD STANDARD ###################

@app.get("/full_gold_standard", response_model=List[GoldStandardEntry])
async def get_full_gold_standard(domain: str):
    file_path = f"../gs_data/{domain}.json"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Gold standard for domain {domain} not found.")
    
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


################### FULL GS EVAL ###################

@app.get("/full_gs_eval", response_model=EvaluateResponse)
async def get_full_gs_eval(domain: str = Query(..., description="The domain for which to calculate the average metrics")):
    file_path = f"../gs_data/{domain}.json"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Domain {domain} not supported or GS not found.")
    
    with open(file_path, "r", encoding="utf-8") as f:
        gs_list = json.load(f)
        
    if not gs_list:
        raise HTTPException(status_code=400, detail=f"The Gold Standard for domain {domain} is empty.")
        
    tot_precision = 0.0
    tot_recall = 0.0
    tot_f1 = 0.0
    tot_jaccard = 0.0
    tot_overlap = 0.0
    tot_cosine = 0.0
    
    for item in gs_list:
        url = item.get("url")
        gold_text = item.get("gold_text")
        
        try:
            parsed_response = await parse_article(url)
            
            if isinstance(parsed_response, dict):
                parsed_text = parsed_response["parsed_text"]
            else:
                parsed_text = parsed_response.parsed_text
                
            ris = calculate_metrics(parsed_text, gold_text)
            
            tot_precision += ris["precision"]
            tot_recall += ris["recall"]
            tot_f1 += ris["f1"]
            tot_jaccard += ris["jaccard_similarity"]
            tot_overlap += ris["overlap_coefficient"]
            tot_cosine += ris["cosine_similarity"]
            

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error parsing {url}: {str(e)}")
            
    n = len(gs_list)
    
    return {
        "token_level_eval": TokenLevelEval(
            precision=tot_precision / n,
            recall=tot_recall / n,
            f1=tot_f1 / n
        ),
        "x_eval": XEval(
            jaccard_similarity=tot_jaccard / n,
            overlap_coefficient=tot_overlap / n,
            cosine_similarity=tot_cosine / n
        )
    }



    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)