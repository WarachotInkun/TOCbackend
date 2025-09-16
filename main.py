import requests

from fastapi import FastAPI
import scrapp
from fastapi import Query
import requests




app = FastAPI()

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
    url = f"https://myanimelist.net/search/prefix.json?type=anime&keyword={keyword}&v=1"
    resp = requests.get(url)
    json = resp.json()

    for i in json['categories'][0]['items']:
        i["image_url"] = i["image_url"].replace("r/116x180/","").split("?")[0]
        i.pop("thumbnail_url", None)
        i.pop("url", None)
    return json     