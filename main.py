import requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import scrapp
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all domains
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods
    allow_headers=["*"],  # allow all headers
)

@app.get("/v1/health")
def health():
    return "ok"


@app.get("/v1/animes")
def fetch_page(page: int = Query(1, description="Page number")):
    return scrapp.getAnimeList(page=page)


@app.get("/v1/anime/{id}")
def fetch_page(id: int):
    return scrapp.getAminePage(id)


@app.get("/v1/search")
def search_anime(keyword: str):
    return scrapp.search_anime(keyword)



@app.get("/v1/csv")
def export_csv():
    import pandas as pd
    data = scrapp.get_all_anime_data()
    df = pd.DataFrame({
        "Name": data[0],
        "Score": data[1],
        "Type": data[2],
        "Episodes": data[3],
        "Aired": data[4],
        "Studios": data[5],
        "Premiered": data[6]
})
    filename = 'anime_data.csv'
    df.to_csv(filename, index=False)
    return FileResponse(
        path=filename,
        filename=filename,
        media_type='text/csv',
        headers={"Content-Disposition": "attachment; filename=anime_data.csv"}
    )
    


