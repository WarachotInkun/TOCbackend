from bs4 import BeautifulSoup as bs
import requests as req
import re
url = "https://myanimelist.net"
listUrl = url+"/topanime.php"


def fetch_page(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ( like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        resp = req.get(url, headers=headers, timeout=10)
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
        try:
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
        except:
            continue
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

        try:
            va_img_match = re.search(r'<img\b[^>]*(?:data-src|src)="([^"]+)"', row[3])
        except IndexError:
            va_img_match = None
        try:
            va_name_match = re.search(r'<td class="[^"]*?">\s*<a href="[^"]+">([^<]+)</a>', row[2])
        except IndexError:
            va_name_match = None
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



def search_anime(keyword):
    """ ค้นหาอนิเมะจาก MyAnimeList ตามคำค้น
        * keyword: คำค้น (string)
        * return: json ของผลการค้นหา หรือ None ถ้าไม่พบ
    """
    json = {"categories": [{"type": "anime", "items": []}]}
    link = f"https://myanimelist.net/anime.php?cat=anime&q={keyword}&type=0&score=0&status=0&p=0&r=0&sm=0&sd=0&sy=0&em=0&ed=0&ey=0&c%5B%5D=a&c%5B%5D=b&c%5B%5D=c&c%5B%5D=f"
    
    html = fetch_page(link)
    if html is None:
        return json
    
    anime_links = re.findall(r'href="https://myanimelist\.net/anime/(\d+)/[^"]*"', html)
    image_urls = re.findall(r'(?:data-src|src)="([^"]*myanimelist\.net[^"]*images/anime[^"]*)"', html)
    titles = re.findall(r'<strong>([^<]+)</strong>', html)
    media_types = re.findall(r'<td[^>]*width="45"[^>]*>\s*([^<]+)\s*</td>', html)
    scores = re.findall(r'<td[^>]*width="50"[^>]*>\s*([\d\.]+)\s*</td>', html) 
    ep = re.findall(r'<td[^>]*width="40"[^>]*>\s*([\d\.]+)\s*</td>', html) 
    for i in range(min(5, len(anime_links), len(titles), len(image_urls))):
        try:
            episode = int(ep[i])
        except (ValueError, IndexError):
            episode = 0
        anime_item = {
            "id": int(anime_links[i]),
            "type": "anime",
            "name": titles[i].strip(),
            "image_url": image_urls[i].replace("r/50x70/", "").replace("r/100x140/", "").split("?")[0],
            "payload": {
                "media_type": media_types[i].strip() if i < len(media_types) else "Unknown",
                "score": scores[i] if i < len(scores) else "N/A",
                "status": f"{episode} episodes" if episode >1 else (f"{episode} episode" if episode==1 else "Unknown")
            }
        }
        json["categories"][0]["items"].append(anime_item)
    
    return json


def getAnimeData(page):
    link = listUrl + f"?limit={(page-1)*50}"
    resp_text = fetch_page(link)
    if not resp_text:
        return None
    pattern = r'<a[^>]*class="hoverinfo_trigger[^"]*"[^>]*href="([^"]+)"[^>]*>.*?<img[^>]*alt="Anime: ([^"]+)"[^>]*"[^>]*>.*?</a>.*?<span class="text on score-label score-[^"]+">([\d.]+)</span>'
    matches = re.findall(pattern, resp_text, re.DOTALL)
    if not matches:
        return None
    anime_names = []
    anime_scores = []
    anime_types = []
    anime_episodes = []
    anime_aired = []
    anime_studios = []
    anime_premiered = []
    for match in matches:
        url = match[0]
        info = GetAnimeInfo(url)
        if not info:
            continue
        anime_names.append(match[1].replace('&amp;#039;', "'"))
        anime_scores.append(match[2])
        anime_types.append(info.get("type", "N/A"))
        anime_episodes.append(info.get("episodes", "N/A"))
        anime_aired.append(info.get("aired", "N/A"))
        anime_studios.append(info.get("studios", "N/A"))
        anime_premiered.append(info.get("premiered", "N/A"))
    return (anime_names, anime_scores, anime_types, anime_episodes, anime_aired, anime_studios, anime_premiered)

def GetAnimeInfo(anime_url):
    resp_text = fetch_page(anime_url)
    if not resp_text:
        return None
    try:
        leftside_div = re.findall(r'<div[^>]*class="leftside"[^>]*>(.*?)Resources', resp_text, re.DOTALL)[0]
        leftside_html = leftside_div if leftside_div else ''
        aired_match = re.search(r'Aired:</span>\s*([^<]+)</div>', leftside_html)
        studios_match = re.search(r'Studios:</span>\s*<a[^>]*>([^<]+)</a>', leftside_html)
        premiered_match = re.search(r'Premiered:</span>\s*<a[^>]*>([^<]+)</a>', leftside_html)
        type_match = re.search(r'Type:</span>\s*<a[^>]*>([^<]+)</a>', leftside_html)
        episodes_match = re.search(r'Episodes:</span>\s*([\d]+)', leftside_html)
    except IndexError:
        print(f"Error parsing leftside div for URL: {anime_url}")
        return None
    return {
        "type": type_match.group(1).strip() if type_match else "N/A",
        "episodes": episodes_match.group(1).strip() if episodes_match else "N/A",
        "aired": aired_match.group(1).strip() if aired_match else "N/A",
        "studios": studios_match.group(1).strip() if studios_match else "N/A",
        "premiered": premiered_match.group(1).strip() if premiered_match else "N/A"
    }

def get_all_anime_data():
    """ดึงชื่ออนิเมะจาก 10 หน้าแรกของ MyAnimeList top anime
    * return: list ของชื่ออนิเมะ
    """
    lists = ([],[],[],[],[],[],[])
    
    for i in range(1, 11):
        print(f"Fetching page {i}...")
        data = getAnimeData(i)
        if data:
            for j in range(len(lists)):
                lists[j].extend(data[j])
        else:
            print(f"No data found for page {i}")

    return lists

