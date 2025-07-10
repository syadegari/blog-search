from fastapi import FastAPI
from hybrid_search import search
import requests
import bs4
import re


app = FastAPI()


def preview(url, n=30):
    text = bs4.BeautifulSoup(requests.get(url, timeout=10).text, "lxml").get_text()
    return " ".join(re.findall(r"\w+", text)[:n])+"..."


@app.get("/search")
def search_api(q: str):
    hits = search(q)
    for hit in hits:
        hit["snippet"] = preview(hit["url"])
    return {"query": q, "results": hits}
