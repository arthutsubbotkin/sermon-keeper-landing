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

## Writing style

House rules for every article, existing and new. Follow them when drafting and
when editing.

**Density is the main one. One idea = one paragraph, developed.**

A paragraph should carry a thought from start to finish: typically 45–90 words,
three to five sentences. State the point, then support it, then land it. Do not
chop a single thought into a run of one-sentence paragraphs — that is what makes
a page feel like debris rather than an argument, and it is the most common fault
in these articles.

Reference measurement (2026-07-05): our median paragraph was 30 words with 59% of
paragraphs under 35 words. The publications we are matching run 45–90. Never
"improve readability" by splitting a paragraph that holds one idea; a long
paragraph is only a problem when it holds two.

**Lists are for genuinely parallel, enumerable things** — steps in order,
options being compared, specs. If the items are full thoughts that build on each
other, they are prose and belong in a paragraph. A bulleted list of five
sentences reads worse than one good paragraph.

**One-sentence paragraphs are a tool for emphasis.** Use one deliberately, after
a developed paragraph, to land a point. A page with many of them has none.

Also:

- No parentheses in titles or headings. Say the qualifier plainly instead:
  "How to Record a Sermon on iPhone in 2026", not "(2026 Guide)"; "Method 1:
  Voice Memos, free and already on your phone", not "(free, already on your
  phone)".
- No em dashes. Use a colon when a label introduces what follows, a comma for an
  appositive, or a full stop when the second half stands on its own.
- Bold run-in labels ("Clear a little storage first.") are set in Inter against
  the Charter body; this is handled by CSS, just write them as `<strong>`.
- Every article opens with a lead paragraph in `<p class="article-intro">` that
  answers the query in its first sentence.
- Free tier wording is "Free 3-day trial" with no recording-count qualifier.

## Conventions

- Blog hero images: 1200px wide JPG, stored in `scss/image/blog/photos/`
- Image naming matches article slug: `<slug>.jpg`
- All new articles must be added to `sitemap.xml` and `blog/index.html`
- After changes: resubmit sitemap in Google Search Console
