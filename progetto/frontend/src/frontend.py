from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import httpx

app = FastAPI(title="Frontend Esonero 1")

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
    domains, gs_urls = await get_home_data()
    return templates.TemplateResponse(request=request, name="index.html", context={"domains": domains, "gs_urls": gs_urls})


################### ANALYZE ###################

@app.post("/analyze", response_class=HTMLResponse)
async def analyze_url(request: Request, url: str = Form(...)):
    domains, gs_urls = await get_home_data()
    
    parsed_data = None
    eval_data = None
    gold_text = None
    error = None

    # Handle parsing and evaluation requests
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            parse_resp = await client.get(f"{BACKEND_URL}/parse", params={"url": url})
            
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
            else:
                error = parse_resp.json().get("detail", f"Error in backend: {parse_resp.status_code}")
        
        except Exception as e:
            error = f"Error in communication with the server: {str(e)}"

    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={
            "domains": domains, 
            "gs_urls": gs_urls, 
            "parsed_data": parsed_data,
            "gold_text": gold_text,
            "eval_data": eval_data, 
            "error": error
        }
    )