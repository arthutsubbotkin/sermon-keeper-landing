export const SITE = {
	url: 'https://sermonkeeper.app',
	name: 'Sermon Keeper',
	email: 'hello@sermonkeeper.app',
	logo: 'https://sermonkeeper.app/apple-touch-icon.png',
	ogImage: 'https://sermonkeeper.app/scss/image/og-image.png',
	gaId: 'G-M8FJDVHNCY',
	gscVerification: 'GzWm1GYrAg1L0JO-iXAhefw8FZXLoDcHjCJSepGntPg',
	appId: '6758739935',
	appStoreListing: 'https://apps.apple.com/app/apple-store/id6758739935',
	// Apple Search Ads / App Analytics campaign provider token.
	ptToken: '128512327',
} as const;

/**
 * App Store link with campaign attribution.
 * `token` is the per-post identifier (e.g. "soap_method"), `placement` is where on
 * the page the link sits (header, nav, inline, final, sticky_bar, ...). Every link
 * must carry one so App Store Connect can attribute installs to a specific post.
 */
export function appStoreUrl(token: string, placement: string): string {
	const ct = `landing_blog_${token}_${placement}`;
	return `${SITE.appStoreListing}?pt=${SITE.ptToken}&ct=${ct}&mt=8`;
}

/** Non-blog pages (home, about, privacy) use a flatter campaign namespace. */
export function pageAppStoreUrl(ct: string): string {
	return `${SITE.appStoreListing}?pt=${SITE.ptToken}&ct=${ct}&mt=8`;
}

export const AUTHORS = {
	'Maya Ellison': {
		slug: 'maya-ellison',
		role: 'Product Writer',
		avatar: '/scss/image/blog/authors/maya-ellison.jpg',
	},
	'Daniel Osei': {
		slug: 'daniel-osei',
		role: 'Bible Study Writer',
		avatar: '/scss/image/blog/authors/daniel-osei.jpg',
	},
	'Grace Whitfield': {
		slug: 'grace-whitfield',
		role: 'Sermon Notes Writer',
		avatar: '/scss/image/blog/authors/grace-whitfield.jpg',
	},
} as const;

export type AuthorName = keyof typeof AUTHORS;
