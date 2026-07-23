import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

// The hand-written site had per-page <title>, og:title and twitter:title that were
// deliberately different from the on-page H1 (shorter for the SERP, longer for social).
// The schema keeps them separate so the migration can preserve each one exactly
// instead of collapsing them into a single string.
const blog = defineCollection({
	// Content Layer glob loader: entry.id is the filename without extension,
	// which is exactly the URL slug (/blog/<id>).
	loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/blog' }),
	schema: z.object({
		// On-page H1.
		title: z.string(),
		// Curated short label used in "Keep reading" cards, where the full H1 is too long.
		shortTitle: z.string().optional(),
		// <title> — Google truncates past ~60 rendered characters.
		metaTitle: z.string().max(60),
		// <meta name="description"> — keep under the SERP snippet limit.
		description: z.string().max(158),
		keywords: z.string().optional(),

		// Social. Fall back to metaTitle/description when omitted.
		ogTitle: z.string().optional(),
		ogDescription: z.string().optional(),
		twitterTitle: z.string().optional(),
		twitterDescription: z.string().optional(),

		pubDate: z.coerce.date(),
		updatedDate: z.coerce.date().optional(),
		// Visible date line, e.g. "Updated July 4, 2026" vs plain "April 9, 2026".
		displayDate: z.string(),
		readingTime: z.number().int().positive(),

		// One of the three staff writers. Roles live in src/utils/authors.ts.
		author: z.enum(['Maya Ellison', 'Daniel Osei', 'Grace Whitfield']),

		heroImage: z.string(),
		heroImageAlt: z.string(),
		heroWidth: z.number().int().optional(),
		heroHeight: z.number().int().optional(),
		// Older posts render the hero in .article-hero-image, newer ones in .article-lead.
		heroStyle: z.enum(['lead', 'hero-image']).default('lead'),
		// Social preview image. Defaults to the post's own hero, which is what we want
		// almost always; set it only to pin a different image deliberately.
		ogImage: z.string().optional(),

		// Per-post campaign token: ct=landing_blog_<utmToken>_<placement>.
		// Must stay unique per post — attribution in App Store Connect depends on it.
		utmToken: z.string(),

		category: z.enum(['reviews', 'guides', 'comparisons']).default('guides'),
		// Blog-listing card copy. The hand-written index used bespoke headlines,
		// excerpts and tag labels rather than reusing the meta fields, so they are
		// stored per post instead of being derived.
		cardTitle: z.string().optional(),
		cardText: z.string().optional(),
		cardTag: z.string().optional(),
		// Overrides the listing card's date line. Only needed where the card was
		// hand-updated to show a refresh date instead of the publish date.
		cardDate: z.string().optional(),
		// Tiebreaker for posts sharing a pubDate; lower sorts first. Preserves the
		// curated order of the three posts published on the same day.
		sortWeight: z.number().default(0),
		tags: z.array(z.string()).default([]),
		isPillar: z.boolean().default(false),
		featured: z.boolean().default(false),

		// Posts shipped with either title-case or sentence-case FAQ headings; keep each
		// one as it was rather than normalising and changing a visible heading.
		faqHeading: z.string().default('Frequently asked questions'),

		// Drives both the visible accordion and the FAQPage JSON-LD, so the two can
		// never drift apart (Google requires the visible answer to match the schema).
		faq: z
			.array(z.object({ question: z.string(), answer: z.string() }))
			.default([]),

		// Optional HowTo JSON-LD (used by the record-on-iPhone and SOAP-method guides).
		howTo: z
			.object({
				name: z.string(),
				description: z.string(),
				totalTime: z.string().optional(),
				steps: z.array(z.object({ name: z.string(), text: z.string() })),
			})
			.optional(),

		// Closing conversion card. Omitted on posts that end with a plain CTA instead.
		finalCta: z
			.object({
				heading: z.string(),
				text: z.string(),
				pills: z.array(z.string()).optional(),
				imageAlt: z.string().optional(),
			})
			.optional(),

		// Placement segment for the closing CTA's ct= token. Older posts shipped as
		// "cta1"/"cta2"; keeping their original value preserves attribution history.
		finalCtaPlacement: z.string().default('final'),

		// JSON string holding any additional JSON-LD blocks a page carried (e.g. the
		// pillar's ItemList) so nothing is silently dropped in migration.
		extraSchemasJson: z.string().optional(),

		// Exactly three sibling slugs for the "Keep reading" block.
		sidebarNote: z
		.object({ heading: z.string(), text: z.string() })
		.optional(),
	related: z.array(z.string()).length(3),
	}),
});

export const collections = { blog };
