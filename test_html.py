from fastapi import FastAPI
from fastapi.responses import HTMLResponse
app = FastAPI()
@app.get("/preview")
def preview(title: str = "Test", risk: int = 0):
    html = f"<html><body><h1>{title}</h1><p>Risk: {risk}</p></body></html>"
    return HTMLResponse(content=html)
