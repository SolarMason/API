#!/usr/bin/env python3
"""Generate index.html for API.NEPA-PRO.COM PWA.

- Server-renders all 805 APIs as semantic HTML for crawlability + AI agents.
- Comprehensive SEO: meta, OG, Twitter, JSON-LD (WebSite, Organization,
  ItemList, FAQPage, BreadcrumbList, SpeakableSpecification, SearchAction).
- iOS-native UI with safe-area insets, mega menu on desktop, mobile tab bar,
  light/dark toggle, real-time search, filter chips.
"""
import json
import html
import re
from pathlib import Path

ROOT = Path(__file__).parent
DATA = json.loads((ROOT / "apis.json").read_text())

SITE_URL = "https://api.nepa-pro.com"
SITE_NAME = "API.NEPA-PRO.COM"
SITE_TAGLINE = "The Open-Source API Directory"
SITE_DESC = (
    f"Browse {DATA['total']} free public APIs across {len(DATA['categories'])} categories. "
    "Curated, searchable, installable as an iOS app. Free tier, no gatekeepers, "
    "built for builders by NEPA-PRO."
)


def esc(s: str) -> str:
    """HTML-escape, gracefully handling None."""
    if s is None:
        return ""
    return html.escape(str(s), quote=True)


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


# ---- Build JSON-LD structured data --------------------------------------- #
def build_jsonld() -> str:
    """Comprehensive structured data for Google + voice agents."""
    organization = {
        "@type": "Organization",
        "@id": f"{SITE_URL}/#organization",
        "name": "NEPA-PRO",
        "alternateName": "NEPA Pro",
        "url": "https://nepa-pro.com",
        "logo": f"{SITE_URL}/assets/icon-512.png",
        "description": (
            "Northeast Pennsylvania property maintenance, construction, "
            "and solar operations. Veteran owned."
        ),
        "areaServed": {"@type": "Place", "name": "Northeast Pennsylvania"},
        "sameAs": ["https://solarmason.com", "https://nepa-pro.com"],
    }

    website = {
        "@type": "WebSite",
        "@id": f"{SITE_URL}/#website",
        "url": SITE_URL,
        "name": SITE_NAME,
        "description": SITE_DESC,
        "publisher": {"@id": f"{SITE_URL}/#organization"},
        "inLanguage": "en-US",
        "potentialAction": {
            "@type": "SearchAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": f"{SITE_URL}/?q={{search_term_string}}",
            },
            "query-input": "required name=search_term_string",
        },
    }

    breadcrumbs = {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Home",
                "item": SITE_URL,
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": "Free API Directory",
                "item": f"{SITE_URL}/#directory",
            },
        ],
    }

    # ItemList of every API for crawler indexing
    item_list_elements = []
    pos = 1
    for cat in DATA["categories"]:
        for api in cat["apis"]:
            item_list_elements.append(
                {
                    "@type": "ListItem",
                    "position": pos,
                    "item": {
                        "@type": "WebAPI",
                        "name": api["name"],
                        "url": api["url"],
                        "description": api["description"],
                        "category": cat["name"],
                        "isAccessibleForFree": True,
                    },
                }
            )
            pos += 1

    item_list = {
        "@type": "ItemList",
        "@id": f"{SITE_URL}/#api-directory",
        "name": "Free Public APIs",
        "numberOfItems": DATA["total"],
        "itemListElement": item_list_elements,
    }

    faq = {
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": "How many free APIs are listed?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": (
                        f"API.NEPA-PRO.COM indexes {DATA['total']} free public APIs "
                        f"across {len(DATA['categories'])} categories."
                    ),
                },
            },
            {
                "@type": "Question",
                "name": "Are all of these APIs really free?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": (
                        "Yes. Every API in this directory offers a free tier. "
                        "Some require an API key registration but the access is free."
                    ),
                },
            },
            {
                "@type": "Question",
                "name": "Can I install API.NEPA-PRO.COM as an iOS app?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": (
                        "Yes. Tap the share icon in Safari and choose Add to Home Screen. "
                        "The site is a Progressive Web App with offline support."
                    ),
                },
            },
            {
                "@type": "Question",
                "name": "Who maintains this directory?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": (
                        "NEPA-PRO, a veteran-owned operations and construction company "
                        "based in Northeast Pennsylvania. The source repository is "
                        "github.com/SolarMason/FREE-APIS."
                    ),
                },
            },
            {
                "@type": "Question",
                "name": "What categories of APIs are available?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": (
                        "Categories include "
                        + ", ".join(c["name"] for c in DATA["categories"][:10])
                        + ", and "
                        + str(len(DATA["categories"]) - 10)
                        + " more."
                    ),
                },
            },
        ],
    }

    speakable = {
        "@type": "WebPage",
        "@id": f"{SITE_URL}/#speakable",
        "speakable": {
            "@type": "SpeakableSpecification",
            "cssSelector": ["h1", ".hero-tagline", ".stat-value"],
        },
        "url": SITE_URL,
    }

    graph = {
        "@context": "https://schema.org",
        "@graph": [organization, website, breadcrumbs, item_list, faq, speakable],
    }
    return json.dumps(graph, separators=(",", ":"))


# ---- Build category mega-menu and cards ---------------------------------- #
def auth_label(a: str) -> str:
    if not a or a.lower() in ("no", "none", ""):
        return "no auth"
    return a


def api_card_html(api: dict, cat_slug: str) -> str:
    name = esc(api["name"])
    url = esc(api["url"])
    desc = esc(api["description"])
    auth = auth_label(api.get("auth", ""))
    auth_class = (
        "noauth"
        if auth == "no auth"
        else ("oauth" if auth.lower() == "oauth" else "key")
    )
    https = api.get("https", "")
    cors = api.get("cors", "")

    badges = [f'<span class="badge badge-{auth_class}">{esc(auth)}</span>']
    if https == "Yes":
        badges.append('<span class="badge badge-https">HTTPS</span>')
    if cors == "Yes":
        badges.append('<span class="badge badge-cors">CORS</span>')
    elif cors == "No":
        badges.append('<span class="badge badge-cors-no">no CORS</span>')

    data_auth = esc(auth)
    return (
        f'<article class="api-card" data-name="{esc(api["name"].lower())}" '
        f'data-desc="{esc(api["description"].lower())}" '
        f'data-auth="{data_auth.lower()}" data-https="{esc(https)}" data-cors="{esc(cors)}" '
        f'itemscope itemtype="https://schema.org/WebAPI">'
        f'<a class="api-link" href="{url}" target="_blank" rel="noopener noreferrer" '
        f'itemprop="url" aria-label="Open {name}">'
        f'<div class="api-head">'
        f'<h3 class="api-name" itemprop="name">{name}</h3>'
        f'<svg class="api-icon" viewBox="0 0 24 24" aria-hidden="true">'
        f'<path d="M7 17L17 7M17 7H8M17 7V16" stroke="currentColor" '
        f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>'
        f"</svg>"
        f"</div>"
        f'<p class="api-desc" itemprop="description">{desc}</p>'
        f'<div class="api-badges">{"".join(badges)}</div>'
        f"</a></article>"
    )


def category_section_html(cat: dict) -> str:
    cat_slug = cat["slug"]
    cat_name = esc(cat["name"])
    count = cat["count"]
    cards = "\n".join(api_card_html(a, cat_slug) for a in cat["apis"])
    return (
        f'<section class="cat-section" id="cat-{cat_slug}" data-cat="{cat_slug}" '
        f'aria-labelledby="catname-{cat_slug}">'
        f'<header class="cat-header">'
        f'<h2 id="catname-{cat_slug}" class="cat-title">{cat_name}</h2>'
        f'<span class="cat-count">{count}</span>'
        f"</header>"
        f'<div class="cat-grid">{cards}</div>'
        f"</section>"
    )


def mega_menu_html() -> str:
    """Group 51 categories into 4 columns for desktop mega menu."""
    cats = DATA["categories"]
    n = len(cats)
    cols = 4
    per = (n + cols - 1) // cols
    col_html = []
    for i in range(cols):
        chunk = cats[i * per : (i + 1) * per]
        if not chunk:
            continue
        items = "".join(
            f'<li><a href="#cat-{c["slug"]}" data-cat-jump="{c["slug"]}">'
            f'<span>{esc(c["name"])}</span><em>{c["count"]}</em></a></li>'
            for c in chunk
        )
        col_html.append(f'<ul class="mega-col">{items}</ul>')
    return (
        '<div class="mega" id="mega" hidden>'
        '<div class="mega-inner">'
        '<div class="mega-cols">' + "".join(col_html) + "</div>"
        '<div class="mega-foot">'
        f'<span>{DATA["total"]} APIs · {n} categories · 100% free tier</span>'
        '<a class="mega-cta" href="https://github.com/SolarMason/FREE-APIS" '
        'target="_blank" rel="noopener">Source on GitHub →</a>'
        "</div></div></div>"
    )


# ---- Build the document -------------------------------------------------- #
def build_html() -> str:
    jsonld = build_jsonld()
    sections = "\n".join(category_section_html(c) for c in DATA["categories"])
    mega = mega_menu_html()

    # Quick-jump nav chips (mobile-friendly, scrolling horizontal)
    cat_chips = "".join(
        f'<a class="chip-jump" href="#cat-{c["slug"]}" data-cat-jump="{c["slug"]}">'
        f'{esc(c["name"])} <em>{c["count"]}</em></a>'
        for c in DATA["categories"]
    )

    return f"""<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, user-scalable=yes">
<title>{SITE_NAME} · {DATA['total']} Free Public APIs · {len(DATA['categories'])} Categories</title>
<meta name="description" content="{esc(SITE_DESC)}">
<meta name="author" content="NEPA-PRO">
<meta name="keywords" content="free apis, public apis, api directory, open source apis, rest api list, free api, developer apis, api catalog, json api, public-apis, no auth apis, free tier apis, api index, build with apis">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
<meta name="googlebot" content="index, follow">
<meta name="theme-color" content="#0A0A0F" media="(prefers-color-scheme: dark)">
<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">
<meta name="color-scheme" content="dark light">
<meta name="format-detection" content="telephone=no">
<link rel="canonical" href="{SITE_URL}/">

<!-- iOS PWA -->
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="API NEPA">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">

<!-- Favicons -->
<link rel="icon" type="image/png" sizes="16x16" href="/assets/favicon-16.png">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="icon" type="image/png" sizes="64x64" href="/assets/favicon-64.png">
<link rel="shortcut icon" href="/assets/favicon-32.png">

<!-- Open Graph -->
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{SITE_NAME} · {DATA['total']} Free Public APIs">
<meta property="og:description" content="{esc(SITE_DESC)}">
<meta property="og:url" content="{SITE_URL}/">
<meta property="og:image" content="{SITE_URL}/assets/og-card.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="API.NEPA-PRO.COM — 805 free APIs, 51 categories, built for builders">
<meta property="og:locale" content="en_US">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{SITE_NAME} · {DATA['total']} Free Public APIs">
<meta name="twitter:description" content="{esc(SITE_DESC)}">
<meta name="twitter:image" content="{SITE_URL}/assets/twitter-card.png">
<meta name="twitter:image:alt" content="API.NEPA-PRO.COM — 805 free APIs, 51 categories">

<!-- Geo / publisher -->
<meta name="geo.region" content="US-PA">
<meta name="geo.placename" content="Northeast Pennsylvania">
<link rel="publisher" href="https://nepa-pro.com">

<!-- Preconnect / preload -->
<link rel="preload" as="image" href="/assets/icon-192.png">

<!-- Structured data -->
<script type="application/ld+json">{jsonld}</script>

<style>
/* ───────── design tokens ───────── */
:root {{
  --bg: #0A0A0F;
  --bg-2: #12141C;
  --bg-3: #181B26;
  --surface: rgba(24,27,38,0.72);
  --surface-solid: #181B26;
  --border: rgba(255,255,255,0.08);
  --border-strong: rgba(255,255,255,0.14);
  --text: #F5F6FA;
  --text-2: #C2C6D2;
  --muted: #8C91A0;
  --amber: #FFB400;
  --amber-2: #FFD246;
  --blue: #007AFF;
  --green: #34C759;
  --red: #FF453A;

  --radius-card: 18px;
  --radius-btn: 14px;
  --radius-pill: 999px;

  --header-h: 56px;
  --tabbar-h: 64px;

  --shadow-card: 0 1px 0 rgba(255,255,255,0.04) inset, 0 8px 24px rgba(0,0,0,0.4);
  --shadow-pop: 0 12px 32px rgba(0,0,0,0.55);

  --safe-top: env(safe-area-inset-top, 0px);
  --safe-bottom: env(safe-area-inset-bottom, 0px);
  --safe-left: env(safe-area-inset-left, 0px);
  --safe-right: env(safe-area-inset-right, 0px);

  --font-system: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text",
    "Helvetica Neue", "Segoe UI", system-ui, sans-serif;
  --font-mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
}}

html[data-theme="light"] {{
  --bg: #F7F7FB;
  --bg-2: #FFFFFF;
  --bg-3: #F0F1F6;
  --surface: rgba(255,255,255,0.78);
  --surface-solid: #FFFFFF;
  --border: rgba(0,0,0,0.08);
  --border-strong: rgba(0,0,0,0.14);
  --text: #0B0D14;
  --text-2: #3A3F4C;
  --muted: #6B7280;
  --amber: #C77900;
  --amber-2: #E6A100;
  --shadow-card: 0 1px 0 rgba(0,0,0,0.02) inset, 0 4px 14px rgba(0,0,0,0.06);
}}

/* ───────── base ───────── */
*, *::before, *::after {{ box-sizing: border-box; }}
html {{ -webkit-text-size-adjust: 100%; scroll-behavior: smooth; }}
body {{
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-system);
  font-size: 16px;
  line-height: 1.5;
  letter-spacing: -0.01em;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  overscroll-behavior-y: contain;
  padding-bottom: calc(var(--tabbar-h) + var(--safe-bottom) + 16px);
  min-height: 100vh;
  background-image:
    radial-gradient(ellipse at top, rgba(255,180,0,0.06) 0%, transparent 50%),
    radial-gradient(ellipse at bottom right, rgba(0,122,255,0.05) 0%, transparent 60%);
  background-attachment: fixed;
}}
html[data-theme="light"] body {{
  background-image:
    radial-gradient(ellipse at top, rgba(255,180,0,0.10) 0%, transparent 60%),
    radial-gradient(ellipse at bottom right, rgba(0,122,255,0.06) 0%, transparent 60%);
}}

a {{ color: inherit; text-decoration: none; }}
button {{ font-family: inherit; cursor: pointer; }}
.sr-only {{
  position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
  overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0;
}}
.skip-link {{
  position: absolute; left: -9999px; top: 0; z-index: 1000;
  background: var(--amber); color: #000; padding: 10px 16px;
  border-radius: 0 0 12px 0; font-weight: 600;
}}
.skip-link:focus {{ left: 0; }}

/* ───────── header (sticky, blurred, safe-area) ───────── */
.header {{
  position: sticky; top: 0; z-index: 50;
  padding-top: var(--safe-top);
  background: color-mix(in oklab, var(--bg) 75%, transparent);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 0.5px solid var(--border);
}}
.header-inner {{
  height: var(--header-h);
  display: flex; align-items: center; gap: 10px;
  padding: 0 calc(16px + var(--safe-left)) 0 calc(16px + var(--safe-right));
  max-width: 1280px; margin: 0 auto;
}}
.brand {{
  display: flex; align-items: center; gap: 10px;
  font-weight: 700; letter-spacing: -0.02em; font-size: 17px;
  white-space: nowrap;
}}
.brand-mark {{
  width: 30px; height: 30px; border-radius: 8px;
  background: linear-gradient(160deg, #1A1D28 0%, #0B0C12 100%);
  display: grid; place-items: center; flex-shrink: 0;
  box-shadow: 0 0 0 0.5px var(--border-strong), inset 0 1px 0 rgba(255,255,255,0.05);
}}
.brand-mark svg {{ width: 18px; height: 18px; display: block; }}
.brand-mark .b {{ stroke: var(--amber); stroke-width: 2; fill: none; stroke-linecap: round; stroke-linejoin: round; }}
.brand-mark .d {{ fill: var(--blue); }}
.brand-text strong {{ display: block; line-height: 1; color: var(--text); }}
.brand-text small {{ display: block; font-size: 10px; color: var(--amber); font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; margin-top: 2px; }}

/* desktop nav */
.nav-desktop {{
  display: none;
  margin-left: 8px;
  position: relative;
}}
.nav-trigger {{
  display: inline-flex; align-items: center; gap: 6px;
  height: 36px; padding: 0 14px;
  background: transparent; color: var(--text-2);
  border: 1px solid var(--border); border-radius: var(--radius-btn);
  font-size: 14px; font-weight: 500;
  transition: all 0.15s ease;
}}
.nav-trigger:hover {{ background: var(--bg-3); color: var(--text); }}
.nav-trigger[aria-expanded="true"] {{ background: var(--bg-3); color: var(--text); }}
.nav-trigger svg {{ width: 12px; height: 12px; transition: transform 0.2s; }}
.nav-trigger[aria-expanded="true"] svg {{ transform: rotate(180deg); }}

.header-search {{
  flex: 1; min-width: 0;
  position: relative;
  max-width: 480px; margin-left: auto;
}}
.header-search input {{
  width: 100%; height: 36px;
  background: var(--bg-3);
  border: 1px solid var(--border);
  border-radius: var(--radius-pill);
  color: var(--text);
  padding: 0 16px 0 38px;
  font-size: 15px; font-family: inherit;
  transition: border-color 0.15s, background 0.15s;
}}
.header-search input::placeholder {{ color: var(--muted); }}
.header-search input:focus {{
  outline: none;
  border-color: var(--amber);
  background: var(--bg-2);
}}
.search-icon {{
  position: absolute; left: 12px; top: 50%; transform: translateY(-50%);
  width: 16px; height: 16px; color: var(--muted); pointer-events: none;
}}
.search-clear {{
  position: absolute; right: 8px; top: 50%; transform: translateY(-50%);
  width: 22px; height: 22px; border: none; border-radius: 50%;
  background: var(--muted); color: var(--bg);
  display: none; align-items: center; justify-content: center;
  font-size: 14px; line-height: 1;
}}
.search-clear.show {{ display: inline-flex; }}

.theme-toggle {{
  width: 36px; height: 36px;
  background: var(--bg-3); border: 1px solid var(--border);
  border-radius: var(--radius-btn);
  display: inline-grid; place-items: center;
  color: var(--text-2);
  flex-shrink: 0;
}}
.theme-toggle:hover {{ color: var(--text); }}
.theme-toggle svg {{ width: 16px; height: 16px; }}
.theme-toggle .sun {{ display: none; }}
html[data-theme="light"] .theme-toggle .moon {{ display: none; }}
html[data-theme="light"] .theme-toggle .sun {{ display: block; }}

/* ───────── mega menu (desktop only) ───────── */
.mega {{
  position: absolute; top: calc(100% + 8px); left: 16px; right: 16px;
  max-width: 1100px; margin: 0 auto;
  background: var(--surface-solid);
  border: 1px solid var(--border-strong);
  border-radius: 18px;
  box-shadow: var(--shadow-pop);
  padding: 22px;
  z-index: 60;
}}
.mega[hidden] {{ display: none; }}
.mega-cols {{
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 16px 28px;
}}
.mega-col {{ list-style: none; padding: 0; margin: 0; }}
.mega-col li {{ margin: 0; }}
.mega-col a {{
  display: flex; align-items: baseline; justify-content: space-between;
  padding: 6px 8px; border-radius: 8px;
  font-size: 14px; color: var(--text-2);
  transition: background 0.12s, color 0.12s;
}}
.mega-col a:hover {{ background: var(--bg-3); color: var(--text); }}
.mega-col a em {{
  font-style: normal; font-size: 11px; color: var(--muted);
  font-weight: 600; font-family: var(--font-mono);
}}
.mega-foot {{
  margin-top: 18px; padding-top: 16px; border-top: 1px solid var(--border);
  display: flex; justify-content: space-between; align-items: center;
  font-size: 13px; color: var(--muted);
}}
.mega-cta {{ color: var(--amber) !important; font-weight: 600; }}

/* ───────── hero ───────── */
.hero {{
  padding: 28px 16px 8px;
  max-width: 1280px; margin: 0 auto;
}}
.hero-eyebrow {{
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;
  color: var(--amber);
  padding: 5px 10px; border: 1px solid var(--amber); border-radius: var(--radius-pill);
  background: rgba(255,180,0,0.08);
  margin-bottom: 14px;
}}
.hero h1 {{
  font-size: clamp(32px, 7vw, 56px); line-height: 1.04; letter-spacing: -0.035em;
  font-weight: 800; margin: 0 0 12px;
}}
.hero h1 .accent {{ color: var(--amber); }}
.hero-tagline {{
  font-size: clamp(15px, 2.4vw, 18px); color: var(--text-2);
  margin: 0 0 22px; max-width: 640px;
}}
.hero-stats {{
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 8px; margin-bottom: 8px; max-width: 640px;
}}
.stat {{
  padding: 10px 12px;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 14px;
  backdrop-filter: blur(10px);
}}
.stat-value {{
  font-size: 22px; font-weight: 800; line-height: 1; color: var(--amber);
  font-variant-numeric: tabular-nums; letter-spacing: -0.02em;
}}
.stat-label {{
  font-size: 11px; color: var(--muted); margin-top: 4px;
  font-weight: 500;
}}

/* ───────── filter chips ───────── */
.controls {{
  position: sticky; top: calc(var(--header-h) + var(--safe-top));
  z-index: 40;
  padding: 12px 16px 12px;
  background: color-mix(in oklab, var(--bg) 88%, transparent);
  backdrop-filter: saturate(180%) blur(18px);
  -webkit-backdrop-filter: saturate(180%) blur(18px);
  border-bottom: 0.5px solid var(--border);
  max-width: 1280px; margin: 0 auto;
}}
.filter-row {{
  display: flex; gap: 8px; align-items: center;
  overflow-x: auto; -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  padding-bottom: 2px;
}}
.filter-row::-webkit-scrollbar {{ display: none; }}
.chip {{
  flex-shrink: 0;
  display: inline-flex; align-items: center; gap: 6px;
  height: 32px; padding: 0 14px;
  background: var(--bg-3); border: 1px solid var(--border);
  border-radius: var(--radius-pill);
  color: var(--text-2); font-size: 13px; font-weight: 500;
  white-space: nowrap;
  transition: all 0.15s ease;
}}
.chip:hover {{ color: var(--text); }}
.chip.active {{
  background: var(--amber); color: #000; border-color: var(--amber);
  font-weight: 600;
}}
.chip em {{ font-style: normal; opacity: 0.7; font-family: var(--font-mono); font-size: 11px; }}
.chip-divider {{
  flex-shrink: 0; width: 1px; height: 20px; background: var(--border); margin: 0 2px;
}}

/* horizontal category quick-jump (mobile) */
.cat-jump-row {{
  margin-top: 10px;
  display: none;
  gap: 6px;
  overflow-x: auto; -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}}
.cat-jump-row::-webkit-scrollbar {{ display: none; }}
.chip-jump {{
  flex-shrink: 0;
  display: inline-flex; align-items: center; gap: 6px;
  height: 30px; padding: 0 12px;
  background: transparent; border: 1px solid var(--border);
  border-radius: var(--radius-pill);
  color: var(--text-2); font-size: 12px;
  white-space: nowrap;
}}
.chip-jump em {{ font-style: normal; opacity: 0.6; font-family: var(--font-mono); font-size: 10px; }}

/* ───────── content ───────── */
.directory {{
  padding: 16px;
  max-width: 1280px; margin: 0 auto;
}}
.results-banner {{
  display: none;
  padding: 10px 14px; margin-bottom: 16px;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 12px;
  font-size: 13px; color: var(--text-2);
}}
.results-banner.show {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; }}
.results-banner b {{ color: var(--amber); font-variant-numeric: tabular-nums; }}
.results-banner button {{
  background: transparent; border: 1px solid var(--border); color: var(--text-2);
  border-radius: 8px; padding: 4px 10px; font-size: 12px;
}}

.cat-section {{ margin-bottom: 32px; scroll-margin-top: 130px; }}
.cat-section.hidden {{ display: none; }}
.cat-header {{
  display: flex; align-items: baseline; gap: 10px;
  margin: 0 0 12px; padding: 0 2px;
}}
.cat-title {{
  font-size: 22px; font-weight: 700; letter-spacing: -0.02em;
  margin: 0;
}}
.cat-count {{
  font-size: 12px; color: var(--muted); font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
}}
.cat-grid {{
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
}}

/* api card */
.api-card {{
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-card);
  overflow: hidden;
  backdrop-filter: blur(8px);
  transition: transform 0.15s ease, border-color 0.15s ease, background 0.15s ease;
  box-shadow: var(--shadow-card);
}}
.api-card.hidden {{ display: none; }}
.api-card:hover {{ border-color: var(--border-strong); transform: translateY(-1px); }}
.api-link {{
  display: block; padding: 14px 16px;
  color: inherit;
}}
.api-head {{
  display: flex; align-items: center; justify-content: space-between;
  gap: 10px; margin-bottom: 4px;
}}
.api-name {{
  font-size: 15px; font-weight: 600; letter-spacing: -0.01em;
  margin: 0;
  color: var(--text);
}}
.api-icon {{
  width: 14px; height: 14px;
  color: var(--muted);
  flex-shrink: 0;
  transition: color 0.15s, transform 0.15s;
}}
.api-card:hover .api-icon {{ color: var(--amber); transform: translate(1px, -1px); }}
.api-desc {{
  font-size: 13px; color: var(--text-2); margin: 0 0 10px;
  line-height: 1.45;
  display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;
  overflow: hidden;
}}
.api-badges {{ display: flex; gap: 5px; flex-wrap: wrap; }}
.badge {{
  display: inline-flex; align-items: center;
  height: 20px; padding: 0 8px;
  border-radius: var(--radius-pill);
  font-size: 10.5px; font-weight: 600; letter-spacing: 0.01em;
  font-family: var(--font-mono);
  background: var(--bg-3); color: var(--text-2);
  border: 1px solid var(--border);
}}
.badge-noauth {{ background: rgba(52,199,89,0.12); color: var(--green); border-color: rgba(52,199,89,0.3); }}
.badge-oauth {{ background: rgba(0,122,255,0.14); color: var(--blue); border-color: rgba(0,122,255,0.3); }}
.badge-key {{ background: rgba(255,180,0,0.14); color: var(--amber); border-color: rgba(255,180,0,0.3); }}
.badge-https {{ background: transparent; color: var(--text-2); }}
.badge-cors {{ background: transparent; color: var(--text-2); }}
.badge-cors-no {{ background: transparent; color: var(--muted); opacity: 0.65; }}

.no-results {{
  display: none;
  text-align: center; padding: 60px 20px;
  color: var(--muted);
}}
.no-results.show {{ display: block; }}
.no-results svg {{ width: 48px; height: 48px; margin: 0 auto 16px; color: var(--muted); opacity: 0.5; }}
.no-results h3 {{ color: var(--text); margin: 0 0 6px; font-weight: 600; }}

/* ───────── footer ───────── */
.footer {{
  max-width: 1280px; margin: 32px auto 0; padding: 24px 16px;
  border-top: 1px solid var(--border);
  font-size: 13px; color: var(--muted);
  display: flex; flex-wrap: wrap; gap: 16px; justify-content: space-between; align-items: center;
}}
.footer a {{ color: var(--text-2); }}
.footer a:hover {{ color: var(--amber); }}

/* ───────── mobile tab bar ───────── */
.tabbar {{
  position: fixed; left: 0; right: 0; bottom: 0;
  z-index: 60;
  padding-bottom: var(--safe-bottom);
  background: color-mix(in oklab, var(--bg) 78%, transparent);
  backdrop-filter: saturate(180%) blur(24px);
  -webkit-backdrop-filter: saturate(180%) blur(24px);
  border-top: 0.5px solid var(--border);
}}
.tabbar-inner {{
  height: var(--tabbar-h);
  display: grid; grid-template-columns: repeat(4, 1fr);
  max-width: 480px; margin: 0 auto;
  padding: 0 calc(8px + var(--safe-left)) 0 calc(8px + var(--safe-right));
}}
.tab {{
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 3px;
  background: transparent; border: 0;
  color: var(--muted); font-size: 10px; font-weight: 500;
  -webkit-tap-highlight-color: transparent;
}}
.tab svg {{ width: 22px; height: 22px; }}
.tab.active {{ color: var(--amber); }}

/* ───────── breakpoints ───────── */
@media (min-width: 600px) {{
  .cat-grid {{ grid-template-columns: repeat(2, 1fr); }}
}}
@media (min-width: 900px) {{
  .cat-grid {{ grid-template-columns: repeat(3, 1fr); }}
}}
@media (min-width: 1024px) {{
  .nav-desktop {{ display: flex; }}
  .tabbar {{ display: none; }}
  body {{ padding-bottom: 40px; }}
  .header-search {{ max-width: 360px; }}
  .hero {{ padding: 48px 16px 8px; }}
  .hero-stats {{ max-width: none; grid-template-columns: repeat(4, 220px); }}
}}
@media (min-width: 1280px) {{
  .cat-grid {{ grid-template-columns: repeat(4, 1fr); }}
}}
@media (max-width: 1023px) {{
  .cat-jump-row {{ display: flex; }}
}}

@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{ animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }}
  html {{ scroll-behavior: auto; }}
}}

::selection {{ background: var(--amber); color: #000; }}
</style>
</head>
<body>

<a class="skip-link" href="#main">Skip to content</a>

<header class="header" role="banner">
  <div class="header-inner">
    <a class="brand" href="/" aria-label="API NEPA-PRO home">
      <span class="brand-mark" aria-hidden="true">
        <svg viewBox="0 0 24 24">
          <path class="b" d="M9 4c-2 0-3 1-3 3v3c0 1-1 2-2 2 1 0 2 1 2 2v3c0 2 1 3 3 3"/>
          <path class="b" d="M15 4c2 0 3 1 3 3v3c0 1 1 2 2 2-1 0-2 1-2 2v3c0 2-1 3-3 3"/>
          <circle class="d" cx="12" cy="12" r="1.6"/>
        </svg>
      </span>
      <span class="brand-text">
        <strong>API NEPA</strong>
        <small>by NEPA-PRO</small>
      </span>
    </a>

    <nav class="nav-desktop" aria-label="Categories">
      <button class="nav-trigger" id="megaTrigger" aria-expanded="false" aria-controls="mega">
        Categories
        <svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2 4l4 4 4-4" stroke="currentColor" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </button>
      {mega}
    </nav>

    <div class="header-search" role="search">
      <svg class="search-icon" viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2" fill="none"/>
        <path d="M21 21l-4.3-4.3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
      <label class="sr-only" for="q">Search APIs</label>
      <input id="q" type="search" inputmode="search" autocomplete="off" autocorrect="off" spellcheck="false" placeholder="Search {DATA['total']} APIs…">
      <button class="search-clear" id="qClear" type="button" aria-label="Clear search">×</button>
    </div>

    <button class="theme-toggle" id="themeToggle" type="button" aria-label="Toggle color theme">
      <svg class="moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 12.8A9 9 0 1111.2 3a7 7 0 009.8 9.8z" fill="currentColor"/></svg>
      <svg class="sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4.5" fill="currentColor"/><g stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M5.6 18.4L7 17M17 7l1.4-1.4"/></g></svg>
    </button>
  </div>
</header>

<main id="main">

<section class="hero" aria-labelledby="hero-h">
  <span class="hero-eyebrow">● Live · Updated continuously</span>
  <h1 id="hero-h">{DATA['total']} free APIs.<br><span class="accent">Built for builders.</span></h1>
  <p class="hero-tagline">An open-source directory of free public APIs across {len(DATA['categories'])} categories. Curated, searchable, installable as an iOS app. No paywalls, no gatekeepers.</p>
  <div class="hero-stats" role="list">
    <div class="stat" role="listitem"><div class="stat-value">{DATA['total']}</div><div class="stat-label">APIs Indexed</div></div>
    <div class="stat" role="listitem"><div class="stat-value">{len(DATA['categories'])}</div><div class="stat-label">Categories</div></div>
    <div class="stat" role="listitem"><div class="stat-value">100%</div><div class="stat-label">Free Tier</div></div>
    <div class="stat" role="listitem"><div class="stat-value">PWA</div><div class="stat-label">iOS Install</div></div>
  </div>
</section>

<div class="controls" id="controls">
  <div class="filter-row" role="group" aria-label="Filter APIs">
    <button class="chip active" data-filter="auth" data-value="all" type="button">All <em>{DATA['total']}</em></button>
    <button class="chip" data-filter="auth" data-value="no" type="button">No Auth</button>
    <button class="chip" data-filter="auth" data-value="apikey" type="button">API Key</button>
    <button class="chip" data-filter="auth" data-value="oauth" type="button">OAuth</button>
    <span class="chip-divider" aria-hidden="true"></span>
    <button class="chip" data-filter="https" data-value="yes" type="button">HTTPS only</button>
    <button class="chip" data-filter="cors" data-value="yes" type="button">CORS</button>
  </div>
  <div class="cat-jump-row" id="catJump" aria-label="Jump to category">
    {cat_chips}
  </div>
</div>

<section class="directory" id="directory" aria-label="API directory">
  <div class="results-banner" id="resultsBanner" role="status" aria-live="polite">
    <span>Showing <b id="resultsCount">{DATA['total']}</b> of {DATA['total']} APIs</span>
    <button id="resetFilters" type="button">Reset</button>
  </div>

  <div id="catList">
{sections}
  </div>

  <div class="no-results" id="noResults" role="status">
    <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="1.5" fill="none"/><path d="M21 21l-4.3-4.3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
    <h3>No APIs match</h3>
    <p>Try different keywords or reset your filters.</p>
  </div>
</section>

</main>

<footer class="footer" role="contentinfo">
  <div>
    © <span id="year">2026</span> NEPA-PRO · Northeast PA · Veteran Owned
  </div>
  <div>
    <a href="https://github.com/SolarMason/FREE-APIS" target="_blank" rel="noopener">Source</a>
    &nbsp;·&nbsp;
    <a href="https://nepa-pro.com" target="_blank" rel="noopener">nepa-pro.com</a>
    &nbsp;·&nbsp;
    <a href="https://solarmason.com" target="_blank" rel="noopener">solarmason.com</a>
  </div>
</footer>

<nav class="tabbar" role="navigation" aria-label="Primary mobile">
  <div class="tabbar-inner">
    <button class="tab active" data-tab="home" type="button">
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M3 11l9-7 9 7v9a1 1 0 01-1 1h-5v-6h-6v6H4a1 1 0 01-1-1z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>
      <span>Home</span>
    </button>
    <button class="tab" data-tab="search" type="button">
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="1.8"/><path d="M21 21l-4.3-4.3" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
      <span>Search</span>
    </button>
    <button class="tab" data-tab="categories" type="button">
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="3" y="3" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="1.8"/><rect x="14" y="3" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="1.8"/><rect x="3" y="14" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="1.8"/><rect x="14" y="14" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="1.8"/></svg>
      <span>Browse</span>
    </button>
    <button class="tab" data-tab="info" type="button">
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.8"/><path d="M12 10v6M12 7.5v.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
      <span>About</span>
    </button>
  </div>
</nav>

<script>
(function() {{
  'use strict';

  // ── theme ──────────────────────────────────────────────────────────────
  var ls = (function() {{ try {{ return window.localStorage; }} catch(e) {{ return null; }} }})();
  var storedTheme = ls && ls.getItem('apinepa-theme');
  if (storedTheme === 'light' || storedTheme === 'dark') {{
    document.documentElement.setAttribute('data-theme', storedTheme);
  }}
  var tt = document.getElementById('themeToggle');
  tt.addEventListener('click', function() {{
    var cur = document.documentElement.getAttribute('data-theme');
    var next = cur === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', next);
    if (ls) ls.setItem('apinepa-theme', next);
  }});

  // ── year ───────────────────────────────────────────────────────────────
  document.getElementById('year').textContent = new Date().getFullYear();

  // ── search & filter ────────────────────────────────────────────────────
  var q = document.getElementById('q');
  var qClear = document.getElementById('qClear');
  var banner = document.getElementById('resultsBanner');
  var resultsCount = document.getElementById('resultsCount');
  var noResults = document.getElementById('noResults');
  var catList = document.getElementById('catList');
  var reset = document.getElementById('resetFilters');

  var allCards = Array.prototype.slice.call(document.querySelectorAll('.api-card'));
  var allSections = Array.prototype.slice.call(document.querySelectorAll('.cat-section'));
  var TOTAL = {DATA['total']};

  var filters = {{ q: '', auth: 'all', https: false, cors: false }};

  function applyFilters() {{
    var qs = filters.q.trim().toLowerCase();
    var matchAuth = filters.auth;
    var visible = 0;

    for (var i = 0; i < allCards.length; i++) {{
      var c = allCards[i];
      var hide = false;

      if (qs) {{
        var n = c.getAttribute('data-name') || '';
        var d = c.getAttribute('data-desc') || '';
        if (n.indexOf(qs) === -1 && d.indexOf(qs) === -1) hide = true;
      }}

      if (!hide && matchAuth !== 'all') {{
        var a = c.getAttribute('data-auth') || '';
        if (matchAuth === 'no' && a !== 'no auth') hide = true;
        else if (matchAuth === 'apikey' && a !== 'apikey') hide = true;
        else if (matchAuth === 'oauth' && a !== 'oauth') hide = true;
      }}

      if (!hide && filters.https && c.getAttribute('data-https') !== 'Yes') hide = true;
      if (!hide && filters.cors && c.getAttribute('data-cors') !== 'Yes') hide = true;

      if (hide) {{
        c.classList.add('hidden');
      }} else {{
        c.classList.remove('hidden');
        visible++;
      }}
    }}

    // hide empty sections
    for (var j = 0; j < allSections.length; j++) {{
      var sec = allSections[j];
      var anyVisible = sec.querySelector('.api-card:not(.hidden)');
      if (anyVisible) sec.classList.remove('hidden');
      else sec.classList.add('hidden');
    }}

    // banner + no-results
    var hasFilter = qs || matchAuth !== 'all' || filters.https || filters.cors;
    if (hasFilter) {{
      banner.classList.add('show');
      resultsCount.textContent = visible;
    }} else {{
      banner.classList.remove('show');
    }}
    if (visible === 0) noResults.classList.add('show');
    else noResults.classList.remove('show');

    if (qs.length > 0) qClear.classList.add('show');
    else qClear.classList.remove('show');
  }}

  // search input (debounced)
  var debounceT;
  q.addEventListener('input', function() {{
    clearTimeout(debounceT);
    debounceT = setTimeout(function() {{
      filters.q = q.value;
      applyFilters();
    }}, 80);
  }});
  qClear.addEventListener('click', function() {{
    q.value = ''; filters.q = ''; applyFilters(); q.focus();
  }});

  // filter chips
  document.querySelectorAll('.chip[data-filter]').forEach(function(chip) {{
    chip.addEventListener('click', function() {{
      var f = chip.getAttribute('data-filter');
      var v = chip.getAttribute('data-value');
      if (f === 'auth') {{
        document.querySelectorAll('.chip[data-filter="auth"]').forEach(function(c) {{ c.classList.remove('active'); }});
        chip.classList.add('active');
        filters.auth = v;
      }} else if (f === 'https') {{
        filters.https = !filters.https;
        chip.classList.toggle('active', filters.https);
      }} else if (f === 'cors') {{
        filters.cors = !filters.cors;
        chip.classList.toggle('active', filters.cors);
      }}
      applyFilters();
    }});
  }});

  reset.addEventListener('click', function() {{
    q.value = '';
    filters = {{ q: '', auth: 'all', https: false, cors: false }};
    document.querySelectorAll('.chip[data-filter="auth"]').forEach(function(c) {{
      c.classList.toggle('active', c.getAttribute('data-value') === 'all');
    }});
    document.querySelectorAll('.chip[data-filter="https"],.chip[data-filter="cors"]').forEach(function(c) {{
      c.classList.remove('active');
    }});
    applyFilters();
  }});

  // ── mega menu ─────────────────────────────────────────────────────────
  var megaT = document.getElementById('megaTrigger');
  var mega = document.getElementById('mega');
  function openMega() {{ mega.hidden = false; megaT.setAttribute('aria-expanded', 'true'); }}
  function closeMega() {{ mega.hidden = true; megaT.setAttribute('aria-expanded', 'false'); }}
  megaT.addEventListener('click', function(e) {{
    e.stopPropagation();
    if (mega.hidden) openMega(); else closeMega();
  }});
  document.addEventListener('click', function(e) {{
    if (!mega.hidden && !mega.contains(e.target) && e.target !== megaT) closeMega();
  }});
  document.addEventListener('keydown', function(e) {{
    if (e.key === 'Escape' && !mega.hidden) closeMega();
  }});

  // close mega menu when picking a category
  document.querySelectorAll('[data-cat-jump]').forEach(function(a) {{
    a.addEventListener('click', function() {{ closeMega(); }});
  }});

  // ── tab bar (mobile) ──────────────────────────────────────────────────
  var tabs = document.querySelectorAll('.tab');
  tabs.forEach(function(t) {{
    t.addEventListener('click', function() {{
      var which = t.getAttribute('data-tab');
      tabs.forEach(function(x) {{ x.classList.toggle('active', x === t); }});
      if (which === 'home') {{
        window.scrollTo({{ top: 0, behavior: 'smooth' }});
      }} else if (which === 'search') {{
        q.focus();
        window.scrollTo({{ top: 80, behavior: 'smooth' }});
      }} else if (which === 'categories') {{
        var cj = document.getElementById('catJump');
        if (cj) cj.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
      }} else if (which === 'info') {{
        document.querySelector('.footer').scrollIntoView({{ behavior: 'smooth', block: 'start' }});
      }}
    }});
  }});

  // ── keyboard shortcut: '/' focuses search ────────────────────────────
  document.addEventListener('keydown', function(e) {{
    if (e.key === '/' && document.activeElement !== q) {{
      e.preventDefault();
      q.focus();
    }}
  }});

  // ── deep-link from URL ?q= ─────────────────────────────────────────────
  try {{
    var url = new URL(window.location.href);
    var initialQ = url.searchParams.get('q');
    if (initialQ) {{
      q.value = initialQ;
      filters.q = initialQ;
      applyFilters();
    }}
  }} catch(e) {{}}

  // ── service worker registration ───────────────────────────────────────
  if ('serviceWorker' in navigator) {{
    window.addEventListener('load', function() {{
      navigator.serviceWorker.register('/sw.js').catch(function() {{}});
    }});
  }}
}})();
</script>
</body>
</html>
"""


def main() -> None:
    out = ROOT / "index.html"
    html_str = build_html()
    out.write_text(html_str, encoding="utf-8")
    size_kb = out.stat().st_size / 1024
    print(f"Wrote {out} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
