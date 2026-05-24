from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from urllib.parse import urlparse
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import json
import mariadb 
import httpx

from src.crawler_cbs import parser_cbs
from src.crawler_cnbc import parser_cnbc
from src.crawler_wiki import parser_wiki
from src.crawler_viaggi_usa import parser_viaggi_usa
from src.accuracy_tester import calculate_metrics
from src.init_db import setup_database, get_db_connection

OLLAMA_URL = "http://ollama:11434/api/generate"

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initialization of the database in progress...")
    setup_database()
    yield # 
    print("Shutdown of the server...")

app = FastAPI(title="Web Scraper API", lifespan=lifespan)

# Model for the output of /parse
class ParseResponse(BaseModel):
    url: str
    domain: str
    title: str
    html_text: str
    parsed_text: str

# Model for the input of POST /parse
class ParseRequest(BaseModel):
    url : str
    local : Optional[bool]

# Model for the output of /gs
class GoldStandardEntry(BaseModel):
    url: str
    domain: str
    title: str
    html_text: str
    gold_text: str

# Model for the output of /gold_standard_urls
class GoldStandardUrlsResponse(BaseModel):
    gold_standard_urls: List[str]


# Model for the output of /full_gs
class FullGoldStandardResponse(BaseModel):
    gold_standard: List[GoldStandardEntry]

# Model for the output of /domains
class DomainsResponse(BaseModel):
    domains: List[str]

# Model for the standard metrics
class TokenLevelEval(BaseModel):
    precision: float
    recall: float
    f1: float

# Model for the other metrics
class XEval(BaseModel):
    jaccard_similarity: float
    bigram_overlap: float
    cosine_similarity:float

# Model for the input of /evaluate
class EvaluateRequest(BaseModel):
    parsed_text: str
    gold_text: str

# Model for the output of /evaluate
class EvaluateResponse(BaseModel):
    token_level_eval: TokenLevelEval
    x_eval: XEval

# Model for the output of /evaluate_judge
class EvaluateJudgeResponse(BaseModel):
    model_name: str
    judge_score: int
    judge_feedback: str

# Model for the output of /full_gs_eval
class EvaluateResponse(BaseModel):
    token_level_eval: TokenLevelEval
    judge_score: float
    x_eval: XEval
   
# Model for the input of /add_web_resource
class AddWebResourceRequest(BaseModel):
    url: str
    html_text: str

# Model for the input of /add_gold_standard
class AddGoldStandardRequest(BaseModel):
    url: str
    gold_text: str

# Model for the input of DELETE requests
class DeleteRequest(BaseModel):
    url: str

# Model for the output of /db_stats
class DomainAvgEval(BaseModel):
    token_level_eval: TokenLevelEval 
    x_eval: XEval                    

class DomainAvgJudge(BaseModel):
    judge_score: float

class DbStatsResponse(BaseModel):
    web_resources: Dict[str, int]
    gold_standard: Dict[str, int]
    avg_eval: Dict[str, DomainAvgEval]
    avg_eval_judge: Dict[str, DomainAvgJudge]

################### ENDPOINTS ###################

################### PARSE ###################

@app.get("/parse", response_model=ParseResponse)
async def parse_article(url: str = Query(..., description="The URL of the article to analyze")):

    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    try:
        # Route request to the appropriate parser
        if domain == "en.wikipedia.org":
            return await parser_wiki(url,'')
        elif domain == "www.cbsnews.com":
            return await parser_cbs(url,'')
        elif domain == "www.cnbc.com":
            return await parser_cnbc(url,'')
        elif domain == "www.viaggi-usa.it":
            return await parser_viaggi_usa(url,'')
        else:
            raise HTTPException(status_code=400, detail=f"Domain not supported: {domain}")

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    
################## POST PARSE #################

@app.post("/parse", response_model = ParseResponse)
async def post_parse_article(data: ParseRequest):

    parsed_url = urlparse(data.url)
    domain = parsed_url.netloc

    supported_domains = ["en.wikipedia.org", "www.cbsnews.com", "www.cnbc.com", "www.viaggi-usa.it"]
    if domain not in supported_domains:
        raise HTTPException(status_code=400, detail=f"Domain not supported: {domain}")
    
    html_text = ""

    # if local==True it use the DB
    if data.local:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT html_text 
                FROM web_resources 
                WHERE url = ?
            """, (data.url,))
            
            row = cursor.fetchone()
          
            cursor.close()
            conn.close()
            
            if row:
                html_text = row[0]
            else:
                raise HTTPException(status_code=404, detail="URL not in local database")
        except mariadb.Error as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
    # if local==False do the download
    else: 
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(data.url, timeout=10.0) 
                response.raise_for_status() 
                html_text = response.text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"URL unreachable: {str(e)}")

    # request to the parser
    if domain == "en.wikipedia.org":
        return await parser_wiki(data.url,html_text)
    
    elif domain == "www.cbsnews.com":
        return await parser_cbs(data.url,html_text)
        
    elif domain == "www.cnbc.com":
        return await parser_cnbc(data.url,html_text)
    
    elif domain == "www.viaggi-usa.it":
        return await parser_viaggi_usa(data.url,html_text)
        
    else:
        raise HTTPException(status_code=400, detail=f"Domain not supported: {domain}")
    

################### DOMAINS ###################

@app.get("/domains", response_model=DomainsResponse)
async def get_supported_domains():
    file_path = f"../domains.json"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"domains.json not exists")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error decoding domains.json. The file contains invalid JSON.")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error while reading domains: {str(e)}")


################### GOLD STANDARD ###################

@app.get("/gold_standard", response_model=GoldStandardEntry)
async def get_single_gold_standard(url: str):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    
    supported_domains = ["en.wikipedia.org", "www.cbsnews.com", "www.cnbc.com", "www.viaggi-usa.it"]
    if domain not in supported_domains:
        raise HTTPException(status_code=400, detail=f"Domain not supported: {domain}")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
      
        cursor.execute("""
            SELECT w.url, w.domain, w.title, w.html_text, g.gold_text
            FROM web_resources w
            JOIN gold_standard g ON w.url = g.url
            WHERE w.url = ?
        """, (url,))
        
        row = cursor.fetchone()
        
        cursor.close()
        conn.close()

        if row:
            return {
                "url": row[0],
                "domain": row[1],
                "title": row[2],
                "html_text": row[3],
                "gold_text": row[4]
            }
        else:
            raise HTTPException(status_code=404, detail=f"URL {url} not found in the Gold Standard.")
    
    except mariadb.Error as e:
        raise HTTPException(status_code=500, detail=f"Error in Database: {e}")

################### GOLD STANDARD URLS ###################

@app.get("/gold_standard_urls", response_model=GoldStandardUrlsResponse)
async def get_gold_standard_urls(domain: str):
    conn = get_db_connection() 
    cursor = conn.cursor()
    
    try:
        query = """
            SELECT gs.url 
            FROM gold_standard gs 
            JOIN web_resources wr ON gs.url = wr.url 
            WHERE wr.domain = %s
        """
        cursor.execute(query, (domain,))
        
        results = cursor.fetchall()
        
        if not results:
            raise HTTPException(status_code=400, detail=f"Domain {domain} not supported.")
            
        urls = [row[0] for row in results]
        return {"gold_standard_urls": urls}
        
    except mariadb.Error as e:
        raise HTTPException(status_code=500, detail=f"Errore database: {str(e)}")
    finally:
        conn.close()

################### FULL GOLD STANDARD ###################

@app.get("/full_gold_standard", response_model=FullGoldStandardResponse)
async def get_full_gold_standard(domain: str):
    file_path = f"../gs_data/{domain}.json"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Gold standard for domain {domain} not found.")
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    return {"gold_standard": data}


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
            bigram_overlap=ris["bigram_overlap"],
            cosine_similarity=ris["cosine_similarity"]
        )
    }

################### EVALUATE JUDGE ###################

@app.post("/evaluate_judge", response_model=EvaluateJudgeResponse)
async def evaluate_judge(data: EvaluateRequest):
    
    # prompt for the LLM-as-a-Judge
    prompt = f"""Sei un giudice esperto nella valutazione di sistemi di Information Extraction.
    Devi confrontare il testo estratto (Parsed Text) con il testo di riferimento (Gold Standard).
    Valuta l'accuratezza semantica del testo estratto assegnando un punteggio da 1 a 5, dove:
    1 = Completamente errato o mancante
    5 = Perfettamente coerente e accurato

    Parsed Text:
    {data.parsed_text}

    Gold Standard:
    {data.gold_text}

    Rispondi solo ed esclusivamente con un JSON nel seguente formato, senza aggiungere testo prima o dopo:
    {{
        "judge_score": <inserisci il voto qui>,
        "judge_feedback": "<inserisci la motivazione qui>"
    }}
    """
    
    # Model to use
    target_model = "llama3.2" 
    
    # Payload for Ollama API
    payload = {
        "model": target_model,
        "prompt": prompt,
        "stream": False,
        "format": "json", 
        "options": {
            "temperature": 0.0 # for deterministic evaluations
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=900.0) as client:
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            
            result = response.json()
            raw_response = result.get("response", "")
            
            try:
                judge_output = json.loads(raw_response)
                
                return EvaluateJudgeResponse(
                    model_name=result.get("model", target_model),
                    judge_score=judge_output.get("judge_score", 0),
                    judge_feedback=judge_output.get("judge_feedback", "Nessun feedback generato")
                )
                
            except json.JSONDecodeError:
                # Fallback if the LLM doesn't respect the format
                # return score 0 and error
                return EvaluateJudgeResponse(
                    model_name=result.get("model", target_model),
                    judge_score=0, 
                    judge_feedback=f"FALLBACK: LLM didn't respect the JSON format. Raw response: {raw_response[:100]}..."
                )
            
    except httpx.ReadTimeout:
        raise HTTPException(status_code=504, detail="Timeout during the generation of LLM")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error of the LLM judge: {str(e)}")

################### FULL GS EVAL ###################

@app.get("/full_gs_eval", response_model=EvaluateResponse)
async def get_full_gs_eval(domain: str = Query(..., description="The domain for which to calculate the average metrics")):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT w.url, w.html_text, g.gold_text
            FROM web_resources w
            JOIN gold_standard g ON w.url = g.url
            WHERE w.domain = ?
        """, (domain,))
        
        rows = cursor.fetchall()
        
        if not rows:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail=f"No data found in the DB for the domain: {domain}")
            
    except mariadb.Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")
      
    tot_precision = 0.0
    tot_recall = 0.0
    tot_f1 = 0.0
    tot_jaccard = 0.0
    tot_bigram = 0.0
    tot_cosine = 0.0
    tot_judge= 0.0
    
    for row in rows:
        url, html_text, gold_text = row[0], row[1], row[2]

        data_parse = ParseRequest(url=url, html_text=html_text, local=True)
        
        try:
            parsed_response = await post_parse_article(data_parse)
            
            if isinstance(parsed_response, dict):
                parsed_text = parsed_response.get("parsed_text", "")
            elif hasattr(parsed_response, "parsed_text"):
                parsed_text = parsed_response.parsed_text
            else:               
                raise ValueError(f"Unrecognized response format for {url}")
                
            ris = calculate_metrics(parsed_text, gold_text)
            
            tot_precision += ris["precision"]
            tot_recall += ris["recall"]
            tot_f1 += ris["f1"]
            tot_jaccard += ris["jaccard_similarity"]
            tot_bigram += ris["bigram_overlap"]
            tot_cosine += ris["cosine_similarity"]

            # Call the endpoint evaluate_judge
            judge_payload = EvaluateRequest(parsed_text=parsed_text, gold_text=gold_text)
            judge_response = await evaluate_judge(judge_payload)
            tot_judge += judge_response.judge_score

            try:
                cursor.execute("""
                    INSERT INTO evaluation_results 
                        (url, precision_val, recall, f1, jaccard_similarity, bigram_overlap, cosine_similarity, judge_score, judge_feedback) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON DUPLICATE KEY UPDATE 
                        precision_val=VALUES(precision_val), 
                        recall=VALUES(recall), 
                        f1=VALUES(f1),
                        jaccard_similarity=VALUES(jaccard_similarity),
                        bigram_overlap=VALUES(bigram_overlap),
                        cosine_similarity=VALUES(cosine_similarity),
                        judge_score=VALUES(judge_score),
                        judge_feedback=VALUES(judge_feedback)
                """, (
                    url, 
                    ris["precision"], 
                    ris["recall"], 
                    ris["f1"], 
                    ris["jaccard_similarity"], 
                    ris["bigram_overlap"], 
                    ris["cosine_similarity"], 
                    judge_response.judge_score,
                    judge_response.judge_feedback
                ))
                conn.commit()  
            except mariadb.Error as db_err:
                print(f"Error saving results for {url}: {db_err}")
            

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error parsing {url}: {str(e)}")
            continue

    cursor.close()
    conn.close()

    n = len(rows)
    if n == 0:
        raise HTTPException(status_code=500, detail="Unable to calculate metrics: No documents processed")
    
    return {
        "token_level_eval": TokenLevelEval(
            precision=tot_precision / n,
            recall=tot_recall / n,
            f1=tot_f1 / n
        ),
        "judge_score":tot_judge / n,
        "x_eval": XEval(
            jaccard_similarity=tot_jaccard / n,
            bigram_overlap=tot_bigram / n,
            cosine_similarity=tot_cosine / n
        )
    }

################### ADD WEB RESOURCE ###################

@app.post("/add_web_resource")
async def add_web_resource(data: AddWebResourceRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO web_resources (url, html_text) VALUES (?, ?)", (data.url, data.html_text))
        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "ok"}
    except mariadb.Error as e:
        return {"status": "error", "message": str(e)}


################### ADD GOLD STANDARD ###################

@app.post("/add_gold_standard")
async def add_gold_standard(data: AddGoldStandardRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO gold_standard (url, gold_text) VALUES (?, ?)", (data.url, data.gold_text))
        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "ok"}
    except mariadb.Error as e:
        return {"status": "error", "message": str(e)}


################### DELETE WEB RESOURCE ###################

@app.delete("/web_resource")
async def delete_web_resource(data: DeleteRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM web_resources WHERE url = ?", (data.url,))
        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "ok"}
    except mariadb.Error as e:
        return {"status": "error", "message": str(e)}


################### DELETE GOLD STANDARD ###################

@app.delete("/gold_standard")
async def delete_gold_standard(data: DeleteRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM gold_standard WHERE url = ?", (data.url,))
        if cursor.rowcount == 0:
            return {"status": "error", "message": "URL not present in Gold Standard"}
        
        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "ok"}
    except mariadb.Error as e:
        return {"status": "error", "message": str(e)}
    

################### DB STATS ###################

@app.get("/db_stats", response_model=DbStatsResponse)
async def get_db_stats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT domain, COUNT(*) FROM web_resources GROUP BY domain")
        web_resources_dict = {str(row[0]): int(row[1]) for row in cursor.fetchall()}
        
        cursor.execute("""
            SELECT w.domain, COUNT(*) 
            FROM gold_standard g 
            JOIN web_resources w ON g.url = w.url 
            GROUP BY w.domain
        """)
        gold_standard_dict = {str(row[0]): int(row[1]) for row in cursor.fetchall()}
        
        # Averge metrics for domain
        cursor.execute("""
            SELECT 
                w.domain, 
                COALESCE(ROUND(AVG(e.precision_val), 2), 0.0), 
                COALESCE(ROUND(AVG(e.recall), 2), 0.0), 
                COALESCE(ROUND(AVG(e.f1), 2), 0.0), 
                COALESCE(ROUND(AVG(e.jaccard_similarity), 2), 0.0), 
                COALESCE(ROUND(AVG(e.bigram_overlap), 2), 0.0), 
                COALESCE(ROUND(AVG(e.cosine_similarity), 2), 0.0), 
                COALESCE(ROUND(AVG(e.judge_score), 2), 0.0)
            FROM evaluation_results e
            JOIN web_resources w ON e.url = w.url
            GROUP BY w.domain
        """)
        eval_rows = cursor.fetchall()
        
    except mariadb.Error as e:
        raise HTTPException(status_code=500, detail=f"Database aggregation error: {str(e)}")
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

    avg_eval_dict = {}
    avg_eval_judge_dict = {}
    
    for row in eval_rows:
        domain = str(row[0])
        
        avg_eval_dict[domain] = DomainAvgEval(
            token_level_eval=TokenLevelEval(
                precision=row[1],
                recall=row[2],
                f1=row[3]
            ),
            x_eval=XEval(
                jaccard_similarity=row[4],
                bigram_overlap=row[5],
                cosine_similarity=row[6]
            )
        )
        
        avg_eval_judge_dict[domain] = DomainAvgJudge(judge_score=row[7])
        
    return {
        "web_resources": web_resources_dict,
        "gold_standard": gold_standard_dict,
        "avg_eval": avg_eval_dict,
        "avg_eval_judge": avg_eval_judge_dict
    }

################### DB SCHEMA ###################

@app.get("/db_schema")
async def get_db_schema():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                c.TABLE_NAME, 
                c.COLUMN_NAME, 
                c.COLUMN_TYPE, 
                c.COLUMN_KEY, 
                k.REFERENCED_TABLE_NAME, 
                k.REFERENCED_COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS c
            LEFT JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE k
            ON c.TABLE_NAME = k.TABLE_NAME 
            AND c.COLUMN_NAME = k.COLUMN_NAME
            AND k.TABLE_SCHEMA = 'parser_db'
            WHERE c.TABLE_SCHEMA = 'parser_db'
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        schema = {}
        for (table, col, ctype, ckey, ref_table, ref_col) in rows:
            if table not in schema:
                schema[table] = {}
            
            desc = ctype
            if ckey == 'PRI': 
                desc += ", PK"
            if ref_table: 
                desc += f", FK({ref_table}.{ref_col})"
            
            schema[table][col] = desc
            
        cursor.close()
        conn.close()
        return schema
        
    except mariadb.Error as e:
        raise HTTPException(status_code=500, detail=f"Error in retrieving schema: {str(e)}")


################### STATUS ###################

@app.get("/status")
async def get_status():
    status = {"backend": "_", "database": "_", "ollama": "_"}
    
    try:
        conn = get_db_connection()
        conn.close()
        status["database"] = "ok"
    except Exception:
        status["database"] = "error"
            
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://ollama:11434", timeout=2.0)
            if resp.status_code == 200:
                status["ollama"] = "ok"
            else:
                status["ollama"] = "error"
    except Exception:
        status["ollama"] = "error"

    status["backend"] = "ok"       
    return status












if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003, reload=True)