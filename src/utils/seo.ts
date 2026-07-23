import { SITE, AUTHORS, type AuthorName } from './site';

const publisher = {
	'@type': 'Organization',
	name: SITE.name,
	url: SITE.url,
	logo: { '@type': 'ImageObject', url: SITE.logo },
};

function isoDate(d: Date): string {
	return d.toISOString().slice(0, 10);
}

export interface BlogPostingInput {
	headline: string;
	description: string;
	image: string;
	pubDate: Date;
	updatedDate?: Date;
	author: AuthorName;
	url: string;
}

export function blogPostingSchema(i: BlogPostingInput) {
	return {
		'@context': 'https://schema.org',
		'@type': 'BlogPosting',
		headline: i.headline,
		description: i.description,
		image: i.image,
		datePublished: isoDate(i.pubDate),
		dateModified: isoDate(i.updatedDate ?? i.pubDate),
		author: {
			'@type': 'Person',
			name: i.author,
			jobTitle: AUTHORS[i.author].role,
			worksFor: { '@type': 'Organization', name: SITE.name },
		},
		publisher,
		mainEntityOfPage: { '@type': 'WebPage', '@id': i.url },
	};
}

/**
 * Built from the same `faq` frontmatter that renders the visible accordion, so the
 * schema answer and the on-page answer are guaranteed identical — Google drops (or
 * penalises) FAQ rich results when they drift.
 */
export function faqSchema(faq: { question: string; answer: string }[]) {
	return {
		'@context': 'https://schema.org',
		'@type': 'FAQPage',
		mainEntity: faq.map((f) => ({
			'@type': 'Question',
			name: f.question,
			acceptedAnswer: { '@type': 'Answer', text: f.answer },
		})),
	};
}

export function howToSchema(h: {
	name: string;
	description: string;
	totalTime: string;
	steps: { name: string; text: string }[];
}) {
	return {
		'@context': 'https://schema.org',
		'@type': 'HowTo',
		name: h.name,
		description: h.description,
		totalTime: h.totalTime,
		step: h.steps.map((s, n) => ({
			'@type': 'HowToStep',
			position: n + 1,
			name: s.name,
			text: s.text,
		})),
	};
}

export function breadcrumbSchema(trail: { name: string; item?: string }[]) {
	return {
		'@context': 'https://schema.org',
		'@type': 'BreadcrumbList',
		itemListElement: trail.map((t, n) => ({
			'@type': 'ListItem',
			position: n + 1,
			name: t.name,
			...(t.item ? { item: t.item } : {}),
		})),
	};
}
