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
                "ID": item[0].split("/")[4],
                "name": item[1].replace('\n', ' ').strip(),
                "img": item[2].replace("r/50x70","").split("?")[0],
                "score": float(item[3])
            })
        except Exception as e:
            json["data"].append({
                "ID": item[0].spltit("/")[4],
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
    leftside_div = re.findall(r'<div[^>]*class="leftside"[^>]*>(.*?)Resources', html, re.DOTALL)[0]
    leftside_html = leftside_div if leftside_div else ''
    type_match = re.search(r'Type:</span>\s*<a[^>]*>([^<]+)</a>', leftside_html)
    episodes_match = re.search(r'Episodes:</span>\s*([\d]+)', leftside_html)
    status_match = re.search(r'Status:</span>\s*([^<]+)</div>', leftside_html)
    aired_match = re.search(r'Aired:</span>\s*([^<]+)</div>', leftside_html)
    premiered_match = re.search(r'Premiered:</span>\s*<a[^>]*>([^<]+)</a>', leftside_html)
    broadcast_match = re.search(r'Broadcast:</span>\s*([^<]+)</div>', leftside_html)
    producers_match = re.search(r'Producers:</span>(.*?)(<br>|</div>)', leftside_html, re.DOTALL)
    producers = []
    if producers_match:
        producers = re.findall(r'<a [^>]*>([^<]+)</a>', producers_match.group(1))
 
    licensors_match = re.search(r'Licensors:</span>(.*?)(<br>|</div>)', leftside_html, re.DOTALL)
    licensors = []
    if licensors_match:
        licensors = re.findall(r'<a [^>]*>([^<]+)</a>', licensors_match.group(1))
    studios_match = re.search(r'Studios:</span>\s*<a[^>]*>([^<]+)</a>', leftside_html)
    source_match = re.search(r'Source:</span>\s*<a[^>]*>([^<]+)</a>', leftside_html)
    genres_match = re.search(r'Genres:</span>\s*(.*?)<br>', leftside_html, re.DOTALL)
    duration_match = re.search(r'Duration:</span>\  s*([^<]+)<br>', leftside_html)
    rating_match = re.search(r'Rating:</span>\s*<a[^>]*>([^<]+)</a>', leftside_html)


    info = {
        "Type": type_match.group(1) if type_match else None,
        "Episode": episodes_match.group(1) if episodes_match else None,
        "Status": status_match.group(1).strip() if status_match else None,
        "Aired": aired_match.group(1).strip() if aired_match else None,
        "Premiered": premiered_match.group(1) if premiered_match else None,
        "Broadcast": broadcast_match.group(1).strip() if broadcast_match else None,
        "Producers": producers,
        "Licensors": licensors,
        "Studios": studios_match.group(1) if studios_match else None,
        "Source": source_match.group(1) if source_match else None,
        
    }
    json["leftside"]["info"] = info
    return json



# print(getAnimeList())
print(getAminePage(5114))
    