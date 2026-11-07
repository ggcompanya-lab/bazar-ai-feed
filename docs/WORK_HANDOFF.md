# Work handoff — довърши Bazar.bg интеграцията еднократно

## За какво е проектът
Система за публикуване на всякакви продукти в **Bazar.bg**. Потребителят изпраща снимките в ChatGPT, преглежда цена и описание, казва „Качвай“. Одобрението важи само за тази обява. AI качва файловете, попълва каталога и синхронизира feed. Bazar.bg чете един и същи XML URL.

## Вече работещи технически части
- GitHub repo: https://github.com/ggcompanya-lab/bazar-ai-feed
- GitHub Pages / XML: https://ggcompanya-lab.github.io/bazar-ai-feed/feed.xml
- GitHub Actions: https://github.com/ggcompanya-lab/bazar-ai-feed/actions/workflows/build-feed.yml
- WordPress.com медийна библиотека за снимки: blog ID `258510069`, сайт `https://bazaraiphotos.wordpress.com`. Оригинална снимка бе качена директно от ChatGPT и публичният URL беше проверен в GitHub Actions.
- WordPress MCP action `wpcom_media_create` приема `file` за снимка от чата и връща `source_url`. Използвай този URL в нов продукт; не пази API ключове.
- За нова обява се променя `products.json`, GitHub Actions валидира `preflight.py`, `test_feed.py`, `build_feed.py`, `verify_feed.py`, после директно публикува Pages чрез artifact. Няма необходимост от повторно създаване на feed.
- Първи продукт: `SAS-JACKET-001`, Saint + Sinner, размер L, ново с етикет, цена 39.90 €, категория 311, 4 реални снимки в `images/SAS-JACKET-001`. `status=approved_pending_import`: НЕ е потвърдено, че е публикувано в Bazar.bg.

## Единствени оставащи задачи в браузъра
1. **GitHub Settings → Pages → Build and deployment → Source: GitHub Actions.** Това прекратява конкуриращото се старо публикуване от main branch. Новият GitHub Actions workflow вече е дал успешен deployment, но GitHub продължава да показва и `pages build and deployment` за branch pushes. Потвърди от Pages, че именно GitHub Actions е текущият Source.
2. Влез в потребителския профил на Bazar.bg (потребителят влиза лично, не събирай парола в чат).
3. `https://bazar.bg/user/import` → Автоматичен feed → Нов feed. Постави `https://ggcompanya-lab.github.io/bazar-ai-feed/feed.xml`. Анализирай и съпостави категория 311; разреши еднократно импорт след проверка на всички полета. Провери изискванията за `images` (четири URL, разделени с `|`), `type=215`, `sizes=L`, `condition=1`, `price_type`, `allow_offers`, адрес/телефон по профил. Ако някое поле се отхвърли, коригирай XML генератора в GitHub, без да сменяш постоянния URL.
4. Установи активен Premium/Premium Plus; **не купувай без изрично съгласие**.
5. Стартирай импорт. Следи историята и създадената обява, потвърди реалния Bazar URL. Едва след успешен импорт и видим резултат можеш да смениш `status` на `live`.

## Правила за безопасност
- Не публикувай чернови (`status=draft`), не твърди „Публикувано“ само по GitHub upload.
- Използвай реалните снимки на артикула, не AI-измислени детайли.
- Никога не записвай пароли, лични чатове, непубликувани клиентски данни и телефон в публичен GitHub.
- Пазѝ `external_id` постоянен, за да не се дублират обяви при обновяване.
- Bazar обновява периодично, не моментално; провери резултата в историята.
- При промяна на цена или състояние се консултирай със собственика, ако не са предварително разрешени.
