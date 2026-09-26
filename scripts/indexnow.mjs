// Tells Bing — and every other IndexNow engine (Yandex, Seznam, Naver…) — that
// the site changed, so new and updated pages are recrawled in hours instead of
// weeks. ChatGPT search reads Bing's index, so this is also how a fresh page
// reaches AI answers. Run after a production deploy: `npm run deploy` does both.
//
// The key is public by design: IndexNow proves ownership by fetching
// https://sermonkeeper.app/<KEY>.txt, which lives in public/.

const HOST = 'sermonkeeper.app';
const KEY = '140e3d9e82a915aa10163fd9f0770be1';

const sitemap = await fetch(`https://${HOST}/sitemap.xml`).then((r) => r.text());
const urlList = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]);
if (urlList.length === 0) {
	console.error('IndexNow: no URLs found in the live sitemap — nothing sent.');
	process.exit(1);
}

const res = await fetch('https://api.indexnow.org/indexnow', {
	method: 'POST',
	headers: { 'Content-Type': 'application/json; charset=utf-8' },
	body: JSON.stringify({
		host: HOST,
		key: KEY,
		keyLocation: `https://${HOST}/${KEY}.txt`,
		urlList,
	}),
});

// 200 = accepted; 202 = accepted, key still being verified (normal the first time).
console.log(`IndexNow: ${res.status} ${res.statusText} — ${urlList.length} URLs submitted`);
if (res.status !== 200 && res.status !== 202) {
	console.error(await res.text());
	process.exit(1);
}
