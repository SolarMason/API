# API.NEPA-PRO.COM

> The open-source free-API directory — **805 APIs across 51 categories**, served as an installable iOS PWA. Built by **NEPA-PRO** (Northeast PA · Veteran Owned).

🌐 Live: <https://api.nepa-pro.com>
📦 Data source: <https://github.com/SolarMason/FREE-APIS>

---

## What this is

A single-page Progressive Web App that catalogs every free public API listed in the SolarMason/FREE-APIS repo. All 805 API entries are **server-rendered into the HTML** so search engines and AI agents can index them without running JavaScript, while a lightweight client script provides instant search and filtering.

### Features

| | |
|---|---|
| **805 APIs · 51 categories** | All inline in `index.html` for SEO + AI crawlers |
| **iOS-native UI** | SF Pro stack, safe-area insets, sticky blurred header, bottom tab bar |
| **Real-time search** | `/` keyboard shortcut, debounced, name + description |
| **Filter chips** | Auth type (none/key/OAuth), HTTPS-only, CORS-only |
| **Mega menu** | Desktop ≥1024px — full 51-category grid in a glass card |
| **Quick-jump chips** | Mobile horizontal scroller for all 51 categories |
| **Dark / light** | Manual toggle + respects `prefers-color-scheme` |
| **Installable PWA** | `manifest.webmanifest` with maskable icons + iOS apple-touch-icon |
| **Offline-capable** | Service worker, cache-first shell, network-first nav |
| **100/100 SEO** | Comprehensive meta, OG, Twitter card, full JSON-LD graph |
| **AI / voice ready** | `SpeakableSpecification`, FAQ schema, `WebAPI` ItemList of all 805 |
| **OG share card** | 1200×630 "business card" with NEPA-PRO branding |

---

## File map

```
.
├── index.html                     # 916 KB — main PWA shell, all 805 APIs inline
├── manifest.webmanifest           # PWA manifest with icons + shortcuts
├── sw.js                          # service worker (cache-first shell)
├── robots.txt                     # allows all crawlers + AI bots
├── sitemap.xml                    # root + 51 category fragments
├── apis.json                      # normalized API dataset (226 KB)
├── assets/
│   ├── icon-{192,256,384,512}.png # PWA icons (any purpose)
│   ├── icon-maskable-512.png      # PWA maskable icon
│   ├── apple-touch-icon.png       # 180×180 iOS home screen
│   ├── favicon-{16,32,64}.png     # browser favicons
│   ├── og-card.png                # 1200×630 OpenGraph share card
│   └── twitter-card.png           # same image, named for Twitter
├── build_data.py                  # rebuilds apis.json from source
├── build_assets.py                # rebuilds all icons + OG card
├── build_html.py                  # rebuilds index.html from apis.json
├── build_sitemap.py               # rebuilds sitemap.xml
└── .github/workflows/deploy.yml   # GitHub Pages auto-deploy
```

---

## Deploy

### Recommended: GitHub Pages (same pattern as Solar-Mason-Dev)

1. **Create a new repo** under your `SolarMason` (or `NEPA-PRO`) GitHub org, e.g. `api.nepa-pro`.
2. Push this entire directory (including `.github/workflows/deploy.yml`).
3. In **Settings → Pages**, set **Source = GitHub Actions**.
4. In **Settings → Pages → Custom domain**, enter `api.nepa-pro.com` (the workflow also writes a `CNAME` file on every deploy).
5. At your DNS provider for `nepa-pro.com`, add a **CNAME record**: `api → <your-org>.github.io.`
6. Wait for the cert to provision (a few minutes), then check **Enforce HTTPS**.

### Manual / other hosts

Drop the whole folder into Cloudflare Pages, Netlify, Vercel, S3 + CloudFront, or any static host. Two requirements:

- `manifest.webmanifest` and `sw.js` must be served from the **root** (`/`), not a subpath.
- `/sw.js` should be served with `Service-Worker-Allowed: /` and a short `Cache-Control` (e.g. `max-age=0` or `no-cache`) so updates roll out.

---

## Rebuilding

```bash
# 1. refresh dataset (currently hardcoded; edit build_data.py to add new APIs)
python3 build_data.py

# 2. regenerate icons + OG card
python3 build_assets.py

# 3. regenerate HTML (always run after build_data.py)
python3 build_html.py

# 4. regenerate sitemap
python3 build_sitemap.py
```

---

## SEO notes

- **JSON-LD `@graph`** in `<head>` includes `Organization` (NEPA-PRO), `WebSite` with `SearchAction`, `BreadcrumbList`, full 805-item `ItemList` of `WebAPI` entities, `FAQPage`, and `SpeakableSpecification` for voice agents.
- **`robots.txt`** explicitly allows `GPTBot`, `ClaudeBot`, `anthropic-ai`, `PerplexityBot`, `Google-Extended`, `Applebot-Extended`, `Bingbot`, `CCBot`, `DuckDuckBot`.
- **Sitemap** lists each category as a URL fragment so search engines can deep-link to topical sections.
- **Schema markup on each card**: every `<article>` is `itemtype="https://schema.org/WebAPI"` with `name`, `description`, `url` props.

---

© NEPA-PRO · Northeast Pennsylvania · Veteran Owned and Operated
