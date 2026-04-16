from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import httpx
import os

app = FastAPI(title="Frontend Esonero 1")

templates = Jinja2Templates(directory="templates")

BACKEND_URL = "http://backend:8003"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BACKEND_URL}/domains")
            response.raise_for_status()
            domains = response.json().get("domains", [])
        except httpx.RequestError:
            domains = [] 

    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"domains": domains}
    )

@app.post("/analyze", response_class=HTMLResponse)
async def analyze_url(request: Request, url: str = Form(...)):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/parse", params={"url": url})
        try:
            if response.status_code == 200:
                parsed_data = response.json()
                error = None
            else:
                try:
                    error = response.json().get("detail", "Errore del server backend")
                except:
                    error = f"Il backend ha risposto con errore {response.status_code}"
                parsed_data = None
        except Exception as e:
            error = f"Errore di comunicazione: {str(e)}"
            parsed_data = None

    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={
            "parsed_data": parsed_data,
            "error": error
        }
    )