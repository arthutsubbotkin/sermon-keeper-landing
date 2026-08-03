import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';

// Static output. `format: 'directory'` emits /blog/<slug>/index.html, which Vercel
// serves at /blog/<slug> — identical to the URLs the old hand-written site exposed
// via cleanUrls. Do not change this without adding redirects.
export default defineConfig({
	site: 'https://sermonkeeper.app',
	trailingSlash: 'never',
	// The migration must not alter post wording, so keep straight quotes/dashes
	// exactly as the hand-written HTML had them.
	markdown: {
		smartypants: false,
	},
	build: {
		format: 'directory',
		inlineStylesheets: 'auto',
	},
	// Sitemap is emitted by the custom endpoint at src/pages/sitemap.xml.ts
	// (so every blog URL carries a real <lastmod>). robots.txt points at it.
	integrations: [mdx()],
});
