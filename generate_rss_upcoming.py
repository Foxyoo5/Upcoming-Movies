import os
import requests
from datetime import datetime, timezone
from xml.sax.saxutils import escape

TMDB_API_KEY = os.environ["TMDB_API_KEY"]
TMDB_URL = "https://api.themoviedb.org/3/movie/upcoming"
IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
OUTPUT_FILE = "docs/upcoming.xml"


def fetch_movies():
    params = {"api_key": TMDB_API_KEY, "language": "en-US", "page": 1, "region": "US"}
    resp = requests.get(TMDB_URL, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()["results"]


def build_rss(movies):
    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    items = []

    for m in movies:
        title = escape(m.get("title", "Untitled"))
        poster_path = m.get("poster_path")
        overview = escape(m.get("overview", ""))
        link = f"https://www.themoviedb.org/movie/{m['id']}"

        if poster_path:
            poster_url = f"{IMAGE_BASE}{poster_path}"
            image_tag = f'<img src="{poster_url}" alt="{title}" /><br/>'
            enclosure = f'<enclosure url="{poster_url}" type="image/jpeg" />'
        else:
            poster_url = ""
            image_tag = ""
            enclosure = ""

        description = f"{image_tag}{overview}"

        items.append(f"""
    <item>
      <title>{title}</title>
      <link>{link}</link>
      <guid isPermaLink="false">{m['id']}</guid>
      <pubDate>{now}</pubDate>
      <description><![CDATA[{description}]]></description>
      {enclosure}
    </item>""")

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Upcoming Movies</title>
    <link>https://www.themoviedb.org/movie/upcoming</link>
    <description>Upcoming movies, from TMDB</description>
    <lastBuildDate>{now}</lastBuildDate>
    <ttl>720</ttl>
    {''.join(items)}
  </channel>
</rss>"""


def main():
    movies = fetch_movies()
    rss = build_rss(movies)
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(rss)
    print(f"Wrote {len(movies)} movies to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
