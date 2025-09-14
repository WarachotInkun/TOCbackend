from bs4 import BeautifulSoup as bs
import requests as req
import re
import sys


url = "https://myanimelist.net/topanime.php"

def fetch_page(url):
    try:
        resp = req.get(url)
        resp.raise_for_status()
        return resp.text
    except req.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def getAnimeList ():
    """  ดึงรายชื่ออนิเมะจาก MyAnimeList 
        * return: list ของ tuple (ลิงก์, ชื่ออนิเมะ)
    """
    html = fetch_page(url)
    pattern = r'<a href="([^"]+)"[^>]*class="hoverinfo_trigger"[^>]*>([^<]+)</a>'
    result = re.findall(pattern, html)
    return result




print(getAnimeList())
    