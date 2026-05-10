import re, json, urllib.request, urllib.parse, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "script"))

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        return f"ERROR: {e}"

def strip_html(html):
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    return re.sub(r'<[^>]+>', '', html).strip()

def search_natepann(keyword, limit=10):
    results = []

    from crawler import get_top_by_views, get_article, get_ranking

    ranking = get_ranking()
    if isinstance(ranking, list):
        for item in ranking[:20]:
            a = get_article(item["href"])
            if isinstance(a, dict):
                title = a.get("title", "")
                views = a.get("views", "")
                body = a.get("body", "")
                views_int = 0
                try:
                    views_int = int(views.replace(",", ""))
                except:
                    pass
                url = a.get("url", f"https://pann.nate.com{item['href']}")
                results.append({
                    "title": title,
                    "url": url,
                    "source": "natepann",
                    "views": views,
                    "views_int": views_int,
                    "body_length": len(body) if body else 0,
                    "body_snippet": re.sub(r'\s+', ' ', body[:150]).strip() if body else ""
                })

    results.sort(key=lambda x: x.get("views_int", 0), reverse=True)

    if keyword:
        filtered = [r for r in results if keyword in r["title"] or keyword in r.get("body_snippet", "")]
        if len(filtered) >= 3:
            results = filtered

    return results[:limit]

def search_natepann_ranking(limit=10):
    from crawler import get_ranking, get_article

    ranking = get_ranking()
    if isinstance(ranking, str):
        return []

    results = []
    for item in ranking[:20]:
        a = get_article(item["href"])
        if isinstance(a, dict):
            results.append({
                "title": a.get("title", item.get("title", "")),
                "url": a.get("url", f"https://pann.nate.com{item['href']}"),
                "source": "natepann",
                "views": a.get("views", ""),
                "body_snippet": a.get("body", "")[:200] if a.get("body") else ""
            })
        if len(results) >= limit:
            break
    return results

def search_youtube(keyword, limit=10):
    query = urllib.parse.quote(keyword + " 쇼츠")
    url = f"https://www.youtube.com/results?search_query={query}"
    html = fetch(url)
    if html.startswith("ERROR"):
        return []

    results = []
    video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
    titles_raw = re.findall(r'"title":{"runs":\[{"text":"(.*?)"}\]', html)
    view_counts = re.findall(r'"viewCountText":\{"simpleText":"(.*?)"\}', html)

    seen = set()
    for i, vid in enumerate(video_ids):
        if vid in seen:
            continue
        seen.add(vid)
        title = titles_raw[i] if i < len(titles_raw) else ""
        title = title.replace("&amp;", "&").replace("&quot;", '"').replace("&#39;", "'")
        views = view_counts[i] if i < len(view_counts) else ""
        results.append({
            "title": title,
            "url": f"https://www.youtube.com/watch?v={vid}",
            "source": "youtube",
            "views": views
        })
        if len(results) >= limit:
            break

    return results

def format_results(nate_results, youtube_results):
    lines = []
    lines.append("=" * 70)
    lines.append("📺 YouTube Shorts")
    lines.append("=" * 70)
    lines.append("")
    lines.append("| # | 제목 | 간략 내용 | 조회수 |")
    lines.append("|---|------|----------|--------|")
    for i, r in enumerate(youtube_results, 1):
        title = r["title"][:40]
        views = r.get("views", "N/A")
        snippet = r.get("body_snippet", "")[:50] if r.get("body_snippet") else "-"
        lines.append(f"| {i} | {title} | {snippet} | {views} |")

    lines.append("")
    lines.append("=" * 70)
    lines.append("📝 네이트판")
    lines.append("=" * 70)
    lines.append("")
    lines.append("| # | 제목 | 간략 내용 | 조회수 | 본문길이 |")
    lines.append("|---|------|----------|--------|----------|")
    for i, r in enumerate(nate_results, 1):
        title = r["title"][:40]
        views = r.get("views", "N/A")
        snippet = r.get("body_snippet", "")[:60] if r.get("body_snippet") else "-"
        body_len = r.get("body_length", 0)
        lines.append(f"| {i} | {title} | {snippet} | {views} | {body_len}자 |")

    return "\n".join(lines)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Shorts content research tool")
    parser.add_argument("keyword", nargs="*", default=["연애", "갈등"], help="Search keywords")
    parser.add_argument("--nate", type=int, default=10, help="Number of NatePann results")
    parser.add_argument("--youtube", type=int, default=10, help="Number of YouTube results")
    parser.add_argument("--ranking", action="store_true", help="Use NatePann ranking instead of keyword search")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    keyword = " ".join(args.keyword) if args.keyword else "연애 갈등"

    print(f"🔍 Searching for: {keyword}", file=sys.stderr)

    yt_results = search_youtube(keyword, limit=args.youtube)
    print(f"📺 YouTube: {len(yt_results)} results", file=sys.stderr)

    if args.ranking:
        nate_results = search_natepann_ranking(limit=args.nate)
    else:
        nate_results = search_natepann(keyword, limit=args.nate)
    print(f"📝 NatePann: {len(nate_results)} results", file=sys.stderr)

    if args.json:
        print(json.dumps({"youtube": yt_results, "natepann": nate_results}, ensure_ascii=False, indent=2))
    else:
        print(format_results(nate_results, yt_results))

if __name__ == "__main__":
    main()