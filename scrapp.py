from bs4 import BeautifulSoup as bs
import requests as req
import re
import sys

url = "https://myanimelist.net"
listUrl = url+"/topanime.php"

def fetch_page(url):
    try:
        resp = req.get(url)
        resp.raise_for_status()
        return resp.text
    except req.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def getAnimeList (page=1):
    """  ดึงรายชื่ออนิเมะจาก MyAnimeList 
        * page: หน้าที่ต้องการ (1,2,3,...)
        * return: dict {"page": page, "data": [ {"link":..., "name":..., "img":..., "score":...}] }
    """
    json = {"page":page,
            "data":[]}
    link = listUrl + f"?limit={(page-1)*50}"
    html = fetch_page(link)
    pattern = r'<a[^>]*class="hoverinfo_trigger[^"]*"[^>]*href="([^"]+)"[^>]*>.*?<img[^>]*alt="Anime: ([^"]+)"[^>]*data-src="([^"]+)"[^>]*>.*?</a>.*?<span class="text on score-label score-[^"]+">([\d.]+)</span>'
    result = re.findall(pattern, html, re.DOTALL)
    for item in result:
        try:
            json["data"].append({
                "link": item[0],
                "name": item[1].replace('\n', ' ').strip(),
                "img": item[2].replace("r/50x70","").split("?")[0],
                "score": float(item[3])
            })
        except Exception as e:
            json["data"].append({
                "link": item[0],
                "name": item[1].replace('\n', ' ').strip(),
                "img": item[2].replace("r/50x70",""),
                "score": float(item[3]),
            })            
    return json



def getAminePage(animeID):
    """ ดึงข้อมูลอนิเมะจาก MyAnimeList ตาม ID
        * animeID: ID ของอนิเมะ (ตัวเลข)
        * return: json ของหน้ารายละเอียดอนิเมะ หรือ None ถ้าไม่พบ
    """
    if not str(animeID).isdigit():
        return None
    json = {"id":animeID}    
    link = url + f"/anime/{animeID}"
    html = fetch_page(link)
    namePattern = r'<h1[^>]*class="title-name h1_bold_none"[^>]*>.*?<strong>([^<]+)</strong>'
    name = re.findall(namePattern, html, re.DOTALL)[0]
    json["name"] = name.strip()
    imgPlattern = r'<div[^>]*class="leftside"[^>]*>.*?<img[^>]*src="([^"]+)"'
    img = re.findall(imgPlattern, html, re.DOTALL)[0]
    json["leftside"] = {"image":img}
    
    return json




print(getAminePage(5114))
    