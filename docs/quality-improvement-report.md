# NexAge website quality improvement report

## Audit scope

The supplied workspace is the project itself; no ZIP archive was present in its root. A pre-edit backup is available as `backup-before-quality-improvements.zip`. The app is a Vite/React 19/TypeScript frontend with React Router and a Django REST Framework backend. Existing API routes include public catalogue/news endpoints, contact and quote submissions, and protected enquiry/admin document endpoints. PostgreSQL is configured through environment variables. The custom `/admin` route remains distinct from Django `/backend-admin/`.

## Changes

- Replaced the homepage's autoplaying MP4 hero with a four-image manual slider using real Pexels photographs. Previous/next buttons, indicators, accessible names, arrow-key handling while controls are focused, and touch swipes are implemented. First image is preloaded; slides do not autoplay. Reduced motion disables the image transition.
- Added on-page stock-photo disclosure and linked photographer credits for each hero slide. The photography is illustrative and is not represented as NexAge project work. Full photo and license references are in [`stock-image-sources.md`](stock-image-sources.md).
- Reduced the hero overlay so the photographs retain more visible color and detail. No AI upscaling, synthetic retouching, or other edits were applied to the downloaded source photos.
- Removed the former 9,595,062-byte hero MP4 after a repository-wide reference scan found no remaining code or configuration references.
- Clarified the homepage sequence by adding CMS-backed industry and profile-recorded award previews, placing industries before projects, recognition after projects, and partner logos after the project/recognition sections.
- Added page-specific news metadata, dynamic Open Graph URL, and `/news` in the public sitemap. The custom `/admin` route also receives `noindex,nofollow` metadata.
- Added factual privacy and website terms pages at `/privacy` and `/terms`, linked from the footer and included in the sitemap. Contact and quote forms link to the privacy notice. The copy describes form fields and purposes without asserting a compliance certification.
- Left the backend, database configuration, models, migrations, inquiry APIs, and existing media files unchanged.

## Image inventory and authenticity

The existing image collection still needs a full provenance review; its source and license metadata were not supplied. The homepage hero now uses four real stock photographs from Pexels, each with a visible credit link and a clear stock disclosure. These do not establish or imply NexAge project provenance. The per-file inventory is maintained in [`image-inventory.csv`](image-inventory.csv).

Repeated catalogue assignments are recorded in `image-inventory.csv` and the existing `CATALOGUE_IMAGE_MAPPING.csv`. The most frequent same-file reuse is `control-cabinet.webp` (six assignments), followed by `custom-press-cell.webp` (five) and several related tools/material-handling images (four each). These are shared across closely related capability, product, and project descriptions. No exact duplicate binary files were found. Visual near-duplicate detection was not available, so the photographs still need a human visual review. Common content references are centralized in `src/data.ts`; shared logo and partner brand assets are intentional.

## Interaction and navigation review

The homepage quote and solutions calls to action retain their existing `/quote` and `/solutions` routes. The slider's controls update the selected slide; the same control buttons are keyboard-operable and swipes are recognized. Static route declarations were reviewed, including both admin interfaces. A source scan found no `href="#"`, `to="#"`, or empty click handlers. This was not a full browser click-through of every page, form, external URL, admin action, or protected API.

A local Vite HTTP smoke check returned 200 for the SPA routes `/`, `/about`, `/solutions`, `/products`, `/projects`, `/contact`, `/quote`, `/news`, `/privacy`, `/terms`, and `/admin`. That earlier check covered the prior hero assets; the four replacement JPEGs were added afterward and were checked as files, but have not yet been rechecked over HTTP. No browser automation surface was available in this environment.

## Verification

- `npm run build`: TypeScript passed, but Vite could not clear the existing `dist/images` output (`EPERM`).
- `npm exec tsc -- --noEmit`: passed.
- `npm exec vite -- build --outDir dist-image-check --emptyOutDir`: passed; generated 75.82 kB CSS and 376.88 kB JavaScript (gzip 16.28 kB and 110.79 kB). Vite reported an existing mixed static/dynamic import warning for `src/api.ts`.
- The earlier local Vite HTTP smoke check covered the SPA routes and transformed HomePage/style modules. It predates the new hero JPEGs, so image delivery and browser rendering after this photo update have not been rechecked. No browser automation surface was available here.
- `python manage.py check`: passed (0 issues).
- `makemigrations --check --dry-run`: passed, no changes detected, with an in-memory SQLite override; migrations were not applied.
- `python manage.py test core --noinput`: 5 tests passed using in-memory SQLite and locmem email. This includes contact persistence in the isolated test DB, quote validation, upload validation, and news publication visibility. PostgreSQL itself was not contacted.
- Read-only anonymous checks to dashboard, enquiry list, CSV export, and private document download returned 403 using in-memory SQLite. Authenticated admin workflows and real PostgreSQL persistence were not exercised.
- Lighthouse, browser console review, interactive browser tests, SMTP delivery, and viewport/device tests were unavailable here. No performance score or full accessibility compliance claim is made.

## Modified files

`src/pages/HomePage.tsx`, `src/components/Site.tsx`, `src/data.ts`, `src/pages/ContentPages.tsx`, `src/main.tsx`, `src/styles.css`, `index.html`, `public/sitemap.xml`, this report, `docs/image-inventory.csv`, and `docs/stock-image-sources.md`.

Removed: `public/videos/industrial-hero-loop.mp4` (9,595,062 bytes; verified unreferenced after the hero replacement).

## Remaining work

Provide verified company-owned or licensed photo assets and source records; run Django system checks and backend tests with a safe test database; complete click-through, form, API authorization, device, and performance audits in a configured runtime. The standard build's existing output-folder permission issue should be resolved before relying on `dist/` as a release build.
