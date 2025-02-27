import sys
import requests
import json
from bs4 import BeautifulSoup
from dateutil.parser import isoparse
import datetime

def get_published_date_ldjson(soup):
    published_date = None
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        try:
            data = json.loads(script.get_text())
        except (json.JSONDecodeError, TypeError):
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if "datePublished" in item and item["datePublished"]:
                return item["datePublished"]
            elif "dateCreated" in item and item["dateCreated"]:
                published_date = item["dateCreated"]
            elif "dateModified" in item and item["dateModified"]:
                published_date = item["dateModified"]
    return published_date

def get_published_date_from_time(soup):
    time_elem = soup.find("time", itemprop="datepublished")
    if time_elem:
        if time_elem.has_attr("datetime"):
            return time_elem["datetime"]
        else:
            text = time_elem.get_text().strip()
            return text.replace("公開日:", "").strip()
    return None

def get_published_date_from_meta(soup):
    published_date = None
    meta_pub = soup.find("meta", property="article:published_time")
    if meta_pub and meta_pub.get("content"):
        published_date = meta_pub.get("content")
    else:
        meta_pub = soup.find("meta", attrs={"name": "datePublished"})
        if meta_pub and meta_pub.get("content"):
            published_date = meta_pub.get("content")
        else:
            meta_created = soup.find("meta", attrs={"name": "dateCreated"})
            if meta_created and meta_created.get("content"):
                published_date = meta_created.get("content")
            else:
                meta_mod = soup.find("meta", attrs={"name": "dateModified"})
                if meta_mod and meta_mod.get("content"):
                    published_date = meta_mod.get("content")
    return published_date

def check_article_publication(url: str):
    """
    指定したURLの記事の公開日時を抽出し、
    その記事が現在（今日）から過去3日以内であれば(True, "YYYY-MM-DDTHH:MM")、
    それより古い場合は(False, "YYYY-MM-DDTHH:MM")を返します。
    公開日時の抽出に失敗した場合は(False, "情報なし")を返します。
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        )
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print("URL取得エラー:", e)
        return False, "情報なし"
    
    soup = BeautifulSoup(response.content, "html.parser")
    
    # 公開日時の抽出（優先順：ld+json > <time> > meta）
    published_date = get_published_date_ldjson(soup)
    if not published_date:
        published_date = get_published_date_from_time(soup)
    if not published_date:
        published_date = get_published_date_from_meta(soup)
    
    if not published_date:
        return False, "情報なし"
    
    try:
        dt = isoparse(published_date)
        # タイムゾーン情報を削除して、offset-naiveにする
        dt = dt.replace(tzinfo=None)
        formatted_date = dt.strftime("%Y-%m-%dT%H:%M")
    except Exception as e:
        print("日付のパースに失敗しました:", e)
        return False, "情報なし"
    
    now = datetime.datetime.now()
    # 未来の日付はFalseで返す
    if dt > now:
        return False, formatted_date
    
    # 現在から3日以内かどうかを判定
    if dt >= now - datetime.timedelta(days=3):
        return True, formatted_date
    else:
        return False, formatted_date

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python <ファイル名.py> <URL>")
        sys.exit(1)
    input_url = sys.argv[1]
    result, pub_date = check_article_publication(input_url)
    if result:
        print("記事は今日から3日以内に公開されています。公開日時:", pub_date)
    else:
        print("記事は今日から3日より前の公開、もしくは公開日時が取得できませんでした。公開日時:", pub_date)
