from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import httpx

app = FastAPI(title="Frontend progetto")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
BACKEND_URL = "http://backend:8003"

async def get_home_data():
    domains = []
    gs_urls = []
    async with httpx.AsyncClient() as client:
        try:
            dom_resp = await client.get(f"{BACKEND_URL}/domains")
            if dom_resp.status_code == 200:
                domains = dom_resp.json().get("domains", [])
            
            for d in domains:
                gs_resp = await client.get(f"{BACKEND_URL}/full_gold_standard", params={"domain": d})
                if gs_resp.status_code == 200:
                    json_data = gs_resp.json()
                    gold_standard_list = json_data.get("gold_standard", [])
                    
                    for item in gold_standard_list:
                        gs_urls.append(item.get("url"))
        except:
            pass
    return domains, gs_urls


################### HOME ###################

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    domains, _ = await get_home_data()
    
    backend_status, db_status, ollama_status = "Offline", "Offline", "Offline"
    
    async with httpx.AsyncClient(timeout=3.0) as client:
        try:
            status_resp = await client.get(f"{BACKEND_URL}/status")
            if status_resp.status_code == 200:
                data = status_resp.json()
                backend_status = data.get("backend", "Online")
                db_status = data.get("db", "Online")
                ollama_status = data.get("ollama", "Online")
        except:
            pass 

    return templates.TemplateResponse(request=request, name="home.html", context={
        "domains": domains,
        "backend_status": backend_status,
        "db_status": db_status,
        "ollama_status": ollama_status
    })


################### ANALYZE ###################

@app.get("/analyze", response_class=HTMLResponse)
async def analyze_page(request: Request):
    _, gs_urls = await get_home_data()
    return templates.TemplateResponse(request=request, name="analyze.html", context={"gs_urls": gs_urls})

@app.post("/analyze", response_class=HTMLResponse)
async def analyze_url(request: Request, url: str = Form(...), mode: str = Form("live")):
    domains, gs_urls = await get_home_data()
    
    parsed_data = None
    eval_data = None
    gold_text = None
    judge_data = None
    error = None
    is_local = (mode == "local")

    # Handle parsing and evaluation requests
    async with httpx.AsyncClient(timeout=900.0) as client:
        try:
            parse_resp = await client.post(f"{BACKEND_URL}/parse", json={"url": url, "local": is_local})
            
            if parse_resp.status_code == 200:
                parsed_data = parse_resp.json()
                
                gs_resp = await client.get(f"{BACKEND_URL}/gold_standard", params={"url": url})
                
                if gs_resp.status_code == 200:
                    gold_text = gs_resp.json().get("gold_text")
                    eval_resp = await client.post(f"{BACKEND_URL}/evaluate", json={
                        "parsed_text": parsed_data["parsed_text"],
                        "gold_text": gold_text
                    })
                    if eval_resp.status_code == 200:
                        eval_data = eval_resp.json()
                    
                    judge_resp = await client.post(f"{BACKEND_URL}/evaluate_judge", json={
                        "parsed_text": parsed_data["parsed_text"],
                        "gold_text": gold_text
                    })
                    if judge_resp.status_code == 200:
                        judge_data = judge_resp.json()
            else:
                error = parse_resp.json().get("detail", f"Error in backend: {parse_resp.status_code}")
        
        except Exception as e:
            error = f"Error in communication with the server: {str(e)}"

    return templates.TemplateResponse(
        request=request, 
        name="analyze.html", 
        context={
            "domains": domains, 
            "gs_urls": gs_urls, 
            "parsed_data": parsed_data,
            "gold_text": gold_text,
            "eval_data": eval_data, 
            "judge_data": judge_data,
            "error": error,
            "selected_mode": mode
        }
    )

################### GOLD STANDARD MANAGE ###################

@app.get("/gs_manage", response_class=HTMLResponse)
async def gs_manage_get(request: Request, domain: str = None, success: str = None, error: str = None):
    domains, _ = await get_home_data()
    existing_urls = []
    
    if domain:
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(f"{BACKEND_URL}/full_gold_standard", params={"domain": domain})
                if resp.status_code == 200:
                    data = resp.json().get("gold_standard", [])
                    existing_urls = [item["url"] for item in data]
            except Exception:
                pass
                
    return templates.TemplateResponse(request=request, name="gs_manage.html", context={
        "domains": domains,
        "selected_domain": domain,
        "existing_urls": existing_urls,
        "success": success,
        "error": error
    })

@app.post("/gs_manage/action", response_class=HTMLResponse)
async def gs_manage_action(
    request: Request, 
    action: str = Form(...),
    domain: str = Form(None),
    url: str = Form(None),
    html_text: str = Form(None),
    gold_text: str = Form(None)
):
    domains, _ = await get_home_data()
    existing_urls = []
    fetched_html = html_text
    current_url = url
    success_msg = None
    error_msg = None

    async with httpx.AsyncClient(timeout=60.0) as client:
        if action == "fetch" and url:
            try:
                parse_resp = await client.post(f"{BACKEND_URL}/parse", json={"url": url, "local": False})
                if parse_resp.status_code == 200:
                    fetched_html = parse_resp.json().get("html_text", "")
                    success_msg = "HTML downloaded."
                else:
                    error_msg = "Error during the download."
            except Exception as e:
                error_msg = f"Connection error: {str(e)}"

        elif action == "save" and url and html_text and gold_text:
            try:
                res1 = await client.post(f"{BACKEND_URL}/add_web_resource", json={"url": url, "html_text": html_text})
                if res1.json().get("status") == "ok":
                    res2 = await client.post(f"{BACKEND_URL}/add_gold_standard", json={"url": url, "gold_text": gold_text})
                    if res2.json().get("status") == "ok":
                        success_msg = "Entry added to Gold Standard!"
                        fetched_html = None 
                        current_url = None
                    else:
                        error_msg = f"Saving GS error: {res2.json().get('message')}"
                else:
                    error_msg = f"Saving HTML error: {res1.json().get('message')}"
            except Exception as e:
                error_msg = str(e)
        
        elif action == "delete" and url:
            try:
                res = await client.request("DELETE", f"{BACKEND_URL}/web_resource", json={"url": url})
                if res.json().get("status") == "ok":
                    success_msg = "Resource deleted from database."
                    current_url = None
                else:
                    error_msg = f"Deletion error: {res.json().get('message')}"
            except Exception as e:
                error_msg = str(e)
                
        if domain:
            try:
                resp = await client.get(f"{BACKEND_URL}/full_gold_standard", params={"domain": domain})
                if resp.status_code == 200:
                    data = resp.json().get("gold_standard", [])
                    existing_urls = [item["url"] for item in data]
            except:
                pass

    return templates.TemplateResponse(request=request, name="gs_manage.html", context={
        "domains": domains,
        "selected_domain": domain,
        "existing_urls": existing_urls,
        "fetched_html": fetched_html,
        "current_url": current_url,
        "success": success_msg,
        "error": error_msg
    })

################### STATS ###################

@app.get("/stats", response_class=HTMLResponse)
async def stats_page(request: Request):
    domains, _ = await get_home_data()
    db_stats = None
    error_msg = None

    async with httpx.AsyncClient(timeout=1800.0) as client:
        try:
            resp = await client.get(f"{BACKEND_URL}/db_stats")
            if resp.status_code == 200:
                db_stats = resp.json()
            else:
                error_msg = f"Unable to retrieve statistics: error {resp.status_code}"
        except Exception as e:
            error_msg = f"Backend communication error: {str(e)}"

    return templates.TemplateResponse(
        request=request, 
        name="stats.html", 
        context={
            "db_stats": db_stats,
            "error": error_msg,
            "domains": domains
        }
    )

################### RUN EVALUATION ###################

@app.post("/run_eval")
async def run_eval_action(request: Request, domain: str = Form(...)):
    async with httpx.AsyncClient(timeout=1800.0) as client:
        try:
            resp = await client.get(f"{BACKEND_URL}/full_gs_eval", params={"domain": domain})
            if resp.status_code != 200:
                print(f"Errore dal backend: {resp.status_code}")
        except Exception as e:
            print(f"Errore di connessione durante la valutazione: {str(e)}")
            
    return RedirectResponse(url="/stats", status_code=303)