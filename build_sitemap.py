#!/usr/bin/env python3
"""Generate sitemap.xml — root URL + each category as a deep link."""
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
DATA = json.loads((ROOT / "apis.json").read_text())
TODAY = date.today().isoformat()
BASE = "https://api.nepa-pro.com"

urls = [
    {"loc": f"{BASE}/", "priority": "1.0", "changefreq": "weekly"},
]
for cat in DATA["categories"]:
    urls.append(
        {
            "loc": f"{BASE}/#cat-{cat['slug']}",
            "priority": "0.8",
            "changefreq": "weekly",
        }
    )

lines = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap-0.9">']
for u in urls:
    lines.append("  <url>")
    lines.append(f"    <loc>{u['loc']}</loc>")
    lines.append(f"    <lastmod>{TODAY}</lastmod>")
    lines.append(f"    <changefreq>{u['changefreq']}</changefreq>")
    lines.append(f"    <priority>{u['priority']}</priority>")
    lines.append("  </url>")
lines.append("</urlset>")

(ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote sitemap with {len(urls)} URLs")
