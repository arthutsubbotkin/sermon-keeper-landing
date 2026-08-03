import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';
import { SITE } from '../utils/site';

// Hand-rolled sitemap so every blog URL carries a real <lastmod> from its
// updatedDate — @astrojs/sitemap could not emit per-post dates. Lives at
// /sitemap.xml to match the URL robots.txt has always advertised.
export const GET: APIRoute = async () => {
	const posts = await getCollection('blog');
	const iso = (d: Date) => d.toISOString().slice(0, 10);

	type Entry = { loc: string; lastmod?: string; changefreq: string; priority: string };
	const entries: Entry[] = [
		{ loc: `${SITE.url}/`, changefreq: 'weekly', priority: '1.0' },
		{ loc: `${SITE.url}/blog`, changefreq: 'weekly', priority: '0.9' },
		{ loc: `${SITE.url}/about`, changefreq: 'monthly', priority: '0.5' },
		{ loc: `${SITE.url}/privacy`, changefreq: 'yearly', priority: '0.3' },
		{ loc: `${SITE.url}/terms`, changefreq: 'yearly', priority: '0.3' },
	];

	for (const p of posts) {
		entries.push({
			loc: `${SITE.url}/blog/${p.id}`,
			lastmod: iso(p.data.updatedDate ?? p.data.pubDate),
			changefreq: 'monthly',
			// The pillar is the site's most important page; rank it above the rest.
			priority: p.id === 'best-sermon-notes-apps' ? '0.9' : '0.8',
		});
	}

	const body = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${entries
	.map(
		(e) =>
			`  <url><loc>${e.loc}</loc>${e.lastmod ? `<lastmod>${e.lastmod}</lastmod>` : ''}<changefreq>${e.changefreq}</changefreq><priority>${e.priority}</priority></url>`
	)
	.join('\n')}
</urlset>
`;

	return new Response(body, {
		headers: { 'Content-Type': 'application/xml; charset=utf-8' },
	});
};
