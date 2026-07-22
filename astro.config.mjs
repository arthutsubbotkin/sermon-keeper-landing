import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import mdx from '@astrojs/mdx';

// Static output. `format: 'directory'` emits /blog/<slug>/index.html, which Vercel
// serves at /blog/<slug> — identical to the URLs the old hand-written site exposed
// via cleanUrls. Do not change this without adding redirects.
export default defineConfig({
	site: 'https://sermonkeeper.app',
	trailingSlash: 'never',
	build: {
		format: 'directory',
		inlineStylesheets: 'auto',
	},
	integrations: [
		mdx(),
		sitemap({
			// Legacy sitemap listed only real pages; keep 404 and asset routes out.
			filter: (page) => !page.includes('/404'),
			serialize(item) {
				// Mirror the priorities/changefreq the hand-written sitemap.xml used.
				if (item.url === 'https://sermonkeeper.app/') {
					return { ...item, changefreq: 'weekly', priority: 1.0 };
				}
				if (item.url.includes('/blog/')) {
					const isIndex = item.url.endsWith('/blog');
					return {
						...item,
						changefreq: isIndex ? 'weekly' : 'monthly',
						priority: isIndex ? 0.8 : 0.8,
					};
				}
				if (item.url.includes('/privacy') || item.url.includes('/terms')) {
					return { ...item, changefreq: 'yearly', priority: 0.3 };
				}
				return { ...item, changefreq: 'monthly', priority: 0.6 };
			},
		}),
	],
});
