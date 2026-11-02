# STATUS — sermon-keeper-landing

Обновлено: 2026-11-02

## Сейчас
Лендинг + блог Sermon Keeper на sermonkeeper.app. Astro SSG, деплой на Vercel. 12 статей в блоге, SEO настроен.

## Последнее сделано
- 02.11 в проде: новая главная (герой, how it works, Obadiah, FAQ 14 вопросов, синий финальный баннер FinalBanner), шапка-островок на всех страницах (на страницах без героя всегда закреплена), баннер в блоге по сетке статей, новая нижняя стикер-панель, копирование почты в подвале, события ui_click и faq_toggle в GA4.
- 28.10 в проде (коммит 27fda6a): GA4 на G-G5X7TV8P56 (старый G-M8FJDVHNCY убран), события scroll_depth и article; обновлены 5 статей (sermon notes + PDF-шаблон, SOAP, best AI transcription, Bible references, Bible versions); на главной ссылка на статью о заметках. Редизайн главной не выложен: патч в Marketing/site-drafts/.
- Миграция с чистого HTML на Astro
- 12 статей в блоге (sermon recording, church notes, AI transcription, SOAP method и др.)
- SEO: Google Search Console, Analytics (G-G5X7TV8P56 с 28.10), sitemap, JSON-LD
- CTA-система: inline + final card + sticky bar, чёткие лимиты

## Решения
- Astro SSG + Vercel
- Домен sermonkeeper.app
- build.format: 'directory', trailingSlash: 'never' — сохранение URL старого сайта
- Два формата CTA: ArticleCTA (inline) и ArticleCTACard (final)

## Ждёт Артура
- Search Console: запросить индексирование 5 обновлённых статей.
- GA4: проверить события в реальном времени; зарегистрировать параметры ct, article, page_path, depth.
- Решить судьбу редизайна главной (патч от 09.10).
- Уточнить: статус индексации блога в GSC
- Уточнить: планируются ли новые статьи?

## Дальше
- Неизвестно, уточнить у Артура
