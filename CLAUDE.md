# Sermon Keeper Landing

Marketing website for the Sermon Keeper iOS app.

## Stack

- Static HTML/CSS site hosted on **Vercel**
- Domain: **sermonkeeper.app**
- No build step — plain HTML files served directly

## Structure

```
/                    → index.html (landing page)
/blog/               → blog/index.html (blog listing)
/blog/<slug>         → blog/<slug>.html (articles)
/privacy             → privacy.html
/terms               → terms.html
/scss/style.css      → all styles
/scss/image/         → all images
/scss/image/blog/photos/ → blog hero images (JPG, 1200px wide)
/sitemap.xml         → sitemap for Google
/vercel.json         → Vercel config (headers, cleanUrls)
```

## Blog

8 articles total. Each article has:
- Hero section (`.article-hero`) with gray background `#F8FAFC`
- Hero image (`.article-hero-image`) — full-width gray bg, image max 720px centered
- Article body (`.article-body`) — max 720px centered
- Quick Comparison table (`.article-table`) — `border-radius: 16px`
- FAQ section or article-faq section
- CTA buttons linking to App Store

Blog card images on index use photos from `scss/image/blog/photos/<slug>.jpg`.

## Key CSS classes

- `.article-hero` — full-width, `background: #F8FAFC`
- `.article-hero-image` — full-width gray bg, contains centered img
- `.article-table` — comparison tables, `border-radius: 16px`, `border-collapse: separate`
- `.faq-list` — FAQ block, `border-radius: 16px`
- `.article-cta` — CTA blocks, `border-radius: 20px`

## SEO

- Google Search Console verified (tag on all pages)
- Google Analytics: `G-M8FJDVHNCY`
- Sitemap: `/sitemap.xml` — update `lastmod` when changing pages
- Blog images from Unsplash (free commercial use)
- Structured data (JSON-LD) on all pages

## Conventions

- Blog hero images: 1200px wide JPG, stored in `scss/image/blog/photos/`
- Image naming matches article slug: `<slug>.jpg`
- All new articles must be added to `sitemap.xml` and `blog/index.html`
- After changes: resubmit sitemap in Google Search Console
