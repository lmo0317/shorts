import re, json, urllib.request, urllib.error

def fetch(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        return f"ERROR: {e}"

def get_ranking():
    html = fetch("https://pann.nate.com/talk/ranking?page=1")
    if html.startswith("ERROR"):
        return html
    pattern = re.compile(r'<a[^>]*href="(/talk/\d+)"[^>]*>(.*?)</a>', re.DOTALL)
    matches = pattern.findall(html)
    seen = set()
    results = []
    for href, title_html in matches:
        title = re.sub(r'<[^>]+>', '', title_html).strip()
        if title and href not in seen and len(title) > 5:
            seen.add(href)
            results.append({"href": href, "title": title})
        if len(results) >= 15:
            break
    return results

def get_article(href):
    url = f"https://pann.nate.com{href}"
    html = fetch(url)
    if html.startswith("ERROR"):
        return html

    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)

    title_match = re.search(r'<meta[^>]*property="og:title"[^>]*content="([^"]+)"', html)
    title = title_match.group(1) if title_match else ""

    cat_match = re.search(r'class="category"[^>]*>(.*?)</', html)
    category = cat_match.group(1) if cat_match else ""

    views_match = re.search(r'조회[^>]*>(\d[\d,]*)\s*</', html)
    views = views_match.group(1) if views_match else ""

    idx_start = html.find('조회')
    if idx_start > 0:
        for _ in range(3):
            idx_start = html.find('<', idx_start)
            if idx_start > 0:
                idx_start = html.find('>', idx_start) + 1

    idx_end = html.find('모바일에서 작성한 글')
    if idx_end == -1:
        idx_end = html.find('베스트 댓글')
    if idx_end == -1:
        idx_end = html.find('개의 댓글')
    if idx_end == -1:
        idx_end = html.find('네이트온 보내기')

    body = ""
    if idx_start > 0 and idx_end > idx_start:
        snippet = html[idx_start:idx_end]
        text = re.sub(r'<[^>]+>', '\n', snippet)
        lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 2]
        skip_words = ['신고', '네이트온', '페이스북', '트위터', '댓글운영', 'URL복사', '레이어']
        body_lines = []
        for l in lines:
            if not any(w in l for w in skip_words) and len(l) < 500:
                if not re.match(r'^[\d,]+$', l.replace(' ','')) and '실시간 랭킹' not in l:
                    body_lines.append(l)
        body = '\n'.join(body_lines)
        while body_lines and len(body_lines[0]) < 5:
            body_lines.pop(0)
        body = '\n'.join(body_lines)

    return {"title": title, "category": category, "views": views, "url": url, "body": body}

def get_top_by_views(limit=10, min_body=100):
    ranking = get_ranking()
    if isinstance(ranking, str):
        return ranking
    articles = []
    for item in ranking:
        a = get_article(item["href"])
        if isinstance(a, dict) and a.get("body") and len(a["body"]) >= min_body:
            try:
                a["_views_int"] = int(a["views"].replace(",", ""))
            except:
                a["_views_int"] = 0
            articles.append(a)
    articles.sort(key=lambda x: x["_views_int"], reverse=True)
    return articles[:limit]
