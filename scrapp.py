from bs4 import BeautifulSoup as bs
import requests as req
import re


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
    genres_match = re.search(r'Genres:</span>(.*?)(<br>|</div>)', leftside_html, re.DOTALL)
    genres = []
    if genres_match:
        genres = re.findall(r'<a [^>]*>([^<]+)</a>', genres_match.group(1))
    duration_match = re.search(r'Duration:</span>\s*([^<]+)</div>', leftside_html)
    rating_match = re.search(r'Rating:</span>\s*([^<]+)</div>', leftside_html)


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
        "Genres": genres,
        "Duration": duration_match.group(1).strip() if duration_match else None,
        "Rating": rating_match.group(1).strip() if rating_match else None
        
    }
    json["leftside"]["info"] = info


    score_match = re.search(r'Score:</span>\s*<span[^>]*>([^<]+)</span>', leftside_html)
    uservotes_match = re.search(r'([\d,]+) users', leftside_html)
    ranked_match = re.search(r'Ranked:</span>\s*([^<]+)<sup>', leftside_html)
    popularity_match = re.search(r'Popularity:</span>\s*([^<]+)</div>', leftside_html)
    members_match = re.search(r'Members:</span>\s*([^<]+)</div>', leftside_html)
    favorites_match = re.search(r'Favorites:</span>\s*([^<]+)</div>', leftside_html)

    

    stat ={
        "Score": score_match.group(1).strip() if score_match else None,
        "UserVotes": uservotes_match.group(1).strip() if uservotes_match else None,
        "Ranked": ranked_match.group(1).strip() if ranked_match else None,
        "Popularity": popularity_match.group(1).strip() if popularity_match else None,
        "Members": members_match.group(1).strip() if members_match else None,
        "Favorites": favorites_match.group(1).strip() if favorites_match else None
    }
    json["stat"] = stat

    synopsis_match = re.search(r'<p itemprop="description">(.*?)</p>', html, re.DOTALL)
    synopsis = synopsis_match.group(1).strip() if synopsis_match else None

    json["synopsis"] = synopsis
    related_match = re.search(r'<div[^>]*class="related-entries"[^>]*>(.*?)</td>', html, re.DOTALL)
    related_html = related_match.group(1) if related_match else ''

    related = re.findall(r'<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>', related_html)


    entries = []
    for m in re.finditer(r'<div class="entry\b.*?>.*?</div>\s*</div>', related_html, flags=re.S):
        block = m.group(0)
        m_img2x = re.search(r'data-srcset="[^"]*?(\S+)\s*2x"', block)
        if m_img2x:
            img_url = m_img2x.group(1)
        else:
            img_url = re.search(r'<img[^>]+src="([^"]+)"', block).group(1)
        relation = re.search(r'<div class="relation">\s*([\s\S]*?)\s*</div>', block).group(1)
        relation = " ".join(relation.split())
        m_title = re.search(r'<div class="title">\s*<a href="([^"]+)">\s*([^<]+)\s*</a>', block)
        link, title = m_title.group(1), m_title.group(2).strip()
        entries.append({
            "image": img_url.replace("r/50x70","").replace("r/100x140","").replace("1x,","").split("?")[0],
            "relation": relation,
            "title": title,
            "ID": link.split("/")[4],
            "Type": link.split("/")[3],
        })
    json["related"] = entries

    voiceActors_match = re.search(r'<h2 id="characters">Characters & Voice Actors</h2>(.*?)<a name="staff"', html, re.DOTALL)

    voiceActors = []
    voiceActors_html = voiceActors_match.group(1)
    for m in re.finditer(r'<table[^>]*(.*?)</table>', voiceActors_html, re.DOTALL):
        row = m.group(1).split('</td>')
        char_img_match = re.search(r'<img\b[^>]*(?:data-src|src)="([^"]+)"', row[0])
        char_name_match = re.search(r'<h3[^>]*>\s*<a[^>]*>([^<]+)</a>', row[1])

        role_match = re.search(r'<small>([^<]+)</small>', row[1])
        role = role_match.group(1).strip() if role_match else None

        va_img_match = re.search(r'<img\b[^>]*(?:data-src|src)="([^"]+)"', row[3])
        va_name_match = re.search(r'<td class="[^"]*?">\s*<a href="[^"]+">([^<]+)</a>', row[2])
        char_img = char_img_match.group(1).replace("r/50x70/","").replace("r/42x62/","").split("?")[0] if char_img_match else None
        char_name = char_name_match.group(1).strip() if char_name_match else None
        va_img = va_img_match.group(1).replace("r/50x70/","").replace("r/42x62/","").split("?")[0] if va_img_match else None
        va_name = va_name_match.group(1).strip() if va_name_match else None
        voiceActors.append({
            "character": {
                "name": char_name,
                "role": role,
                "image": char_img
            },
            "voice_actor": {
                "name": va_name,
                "image": va_img
            }
        })

        json["voice_actors"] = voiceActors


    return json



    