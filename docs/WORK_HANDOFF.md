# Handoff to ChatGPT Work — finish Bazar.bg integration

## Current truth
- Public GitHub Pages is active: https://ggcompanya-lab.github.io/bazar-ai-feed/
- GitHub project: https://github.com/ggcompanya-lab/bazar-ai-feed
- products.json contains a **draft** item `SAS-JACKET-001`, Saint + Sinner, new/unused with tag, mens size L, **39.90 EUR**, Bazar category **311**.
- Seller has explicitly said: **do not publish until "Качвай".** No such command has been issued.
- `feed.xml` intentionally does not exist yet. Do not configure Bazar importer with missing URL.
- Basic workflow auto-runs `preflight.py`, then attempts `build_feed.py` only when approved items exist.

## Work actions to complete with authorized browser access
1. Open the user's signed-in Bazar account, `https://bazar.bg/user/import`. If not signed in, ask the user to sign in themselves; do not request passwords in chat.
2. Open 'Формат и полета', choose category 311, inspect exact XML specs. Verify whether 311 is indeed the chosen men's jacket category and specific requirements for `sizes=L`, `condition`, `type`, `delivery`, `price_type`, `allow_offers`, and `images` separators. Update `category_registry.json` to `verified` **only after checking**.
3. Determine user's seller contact/location **from Bazar profile**, without sharing it in chat or committing non-public details to a public repository. Where Bazar allows profile fallbacks, omit fields from feed.
4. Take the FOUR original jacket photos from this conversation / supplied files (not synthetic product images). Host them on stable public HTTPS URLs approved by the seller, preferably the existing GitHub Pages repository under `images/SAS-JACKET-001/`. Use file upload through computer browser if connector cannot write binary. Verify URLs return actual JPEG images.
5. Update draft product with verified field names and URLs. Validate `build_feed.py` with a safe local dry run and XML parser; update generator's photo format if Bazar requires another format.
6. Do not mark product `approved` or create live `feed.xml` until user's explicit, specific "Качвай" after seeing the final listing. Read the latest draft before applying any approval.
7. Once approved, generate/verify public feed URL. In Bazar user/import add one automatic feed. Map categories, finalize import. Only claim live publication once the listing is confirmed live in Bazar; a GitHub commit alone is not Bazar publication.
8. Check whether Premium is active before proceeding, and do not buy a plan without the user's express authorization. Do not submit payments or set up automatic paid renewal without consent.

## Important caution
Bazar sync is periodic, not instantaneous. AI assistant may prepare code and approved feed directly from GitHub connector; authenticated Bazar UI interaction must happen in Work/Computer Use. All operations must remain scoped to Bazar.bg.
