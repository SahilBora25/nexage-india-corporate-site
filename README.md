# NexAge India — Corporate Website

A responsive industrial-engineering website for **NexAge India Pvt. Ltd.** The company profile supplied with the brief is treated as the source for company facts. The photographs in the site are newly generated industrial visuals; the original company-profile photographs are not used. The supplied NexAge logo artwork is used for the brand mark.

This repository is a deployable codebase, not a live deployment. Before launch, configure secrets, database credentials, SMTP, a real domain/HTTPS proxy, and any authorized third-party logo assets.

## What is included

- React + TypeScript + Vite frontend with responsive desktop/mobile navigation and all requested page families: Home, About, Solutions and solution details, Products and product details, Industries, Projects and application details, Partners, Services, Awards, Contact, Request a Quote, Search, and Admin.
- A curated library of industrial images optimized as WebP assets under `public/images/`, with the supplied NexAge logo preserved.
- Dynamic product, project, service, partner, award and industry lists backed by PostgreSQL APIs. Static company-profile-backed content remains available as a frontend fallback until the API is seeded.
- Contact and quote forms with client- and server-side validation, a honeypot field, rate limits, attachment extension/signature checks, and backend persistence.
- Private uploaded-document storage, with downloads restricted to authorized staff.
- A News & Company Updates feature lets staff publish company news, project updates, achievements, events and technology notes in Django Admin, with direct photo upload and YouTube/Vimeo embeds. Draft and future-dated items remain hidden publicly.
- Django session authentication with staff-only access to enquiry management. The custom dashboard supports status changes and internal notes; Django Admin provides create/edit/publish management for products, projects, categories, partners, services, awards, industries, media assets and uploaded documents. Public media assets are served only through a published-asset endpoint; quote attachments remain private.
- Email notifications use environment-configured SMTP. A failed delivery does not discard an enquiry already stored in the database; PII-free errors are written to backend logs for follow-up. Delivery is not automatically retried.
- PostgreSQL schema/migration, an initial catalogue seed command, basic backend tests, robots/sitemap, Dockerfiles, Nginx and Docker Compose configuration.

## Routes

The frontend includes the main routes requested in the brief, including `/solutions/industrial-automation`, `/solutions/conveyor-material-handling`, `/solutions/smart-manufacturing`, `/solutions/pick-to-light`, `/solutions/jidoka-poka-yoke`, `/solutions/special-purpose-machines`, `/solutions/engineering`, `/solutions/mro-services`, `/products/jidoka`, `/products/wireless-tx-rx`, `/products/pick-to-light`, `/products/cranes-hoists`, `/products/industrial-tools`, `/products/custom-machines`, and project-detail routes under `/projects/:slug`.

## Quick start with Docker Compose

1. Install Docker Desktop / Docker Engine and Docker Compose.
2. Copy `.env.example` to `.env`.
3. For a **local HTTP run**, change the copied environment values to:
   - `DJANGO_DEBUG=true`
   - `COOKIE_SECURE=false`
   - `SECURE_SSL_REDIRECT=false`
   - `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,web,backend`
   - `CSRF_TRUSTED_ORIGINS=http://localhost:8080`
   - `CORS_ALLOWED_ORIGINS=http://localhost:8080,http://localhost:5173,http://127.0.0.1:5173`
   - `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` (for local runs without sending mail)
   - Replace `POSTGRES_PASSWORD` with a strong local password.
4. Run `docker compose up --build` from the project root.
5. In a second terminal, create the initial editable catalogue and a staff login:

   ```bash
   docker compose --profile maintenance run --rm catalogue-seed
   docker compose exec backend python manage.py createsuperuser
   ```

6. Open `http://localhost:8080`. The custom enquiry dashboard is at `/admin`. Use `/backend-admin/` for the built-in content-management interface.

The catalogue seed procedure is repeatable. It creates missing starter records and preserves existing records and admin edits. Review seeded entries before publishing.

### Database and private-media backups

With the Compose application running, create a uniquely named backup outside the repository:

```bash
python scripts/backup.py
```

The script writes a PostgreSQL custom dump and a private-media archive under the current user's local application-data directory. It restricts access to the backup set, records file sizes and SHA-256 checksums, suppresses database command diagnostics, and does not encrypt the files. Store a copy in company-approved encrypted off-host storage. Backups contain enquiry records and potentially sensitive customer attachments.

The database and media archive are captured sequentially, not as one atomic snapshot. Run during a quiet or approved maintenance window if uploads or document deletions could occur while the backup is running.

Exercise a backup in an isolated restore environment:

```bash
python scripts/restore_test.py "C:\path\to\nexage-backup-set"
```

The restore test verifies the manifest and checksums, safely extracts private media to a restricted temporary directory, and restores the database into a throwaway PostgreSQL container with no network, no published ports, and a temporary filesystem. It does not connect to the application's database or mount its named volumes. The media extraction limit is 20 GiB by default and can be adjusted with `--max-media-gib`. The required `postgres:16-alpine` image must already be present locally; the script does not pull images. A backup is not considered restore-verified until this command completes successfully against that backup.

The included Nginx configuration replaces incoming `X-Forwarded-For` with the address Nginx observed. If a hosting ingress or load balancer sits in front, confirm its trusted source ranges and configure the real-client-IP handling at that boundary before deployment. Without that provider-specific configuration, throttling remains spoof-resistant but may group visitors under the ingress address. The HTTPS ingress must also overwrite `X-Forwarded-Proto`; the bundled Nginx currently passes that header to Django so secure-request detection depends on the trusted ingress.

For an existing database that already contains your catalogue, do **not** rerun `seed_catalog` just to update image paths. Preview the safe image-path-only sync first, then apply it only after reviewing the listed changes:

```bash
cd backend
python manage.py sync_catalog_images
python manage.py sync_catalog_images --apply
```

The image-sync command updates only `image_path` for recognized existing slugs. It does not create/delete catalogue rows or change titles, descriptions, ownership, categories, or publication status. Back up the database first.

## Development without Docker

Frontend:

```bash
npm ci
npm run dev
```

Backend requires Python 3.12+ and PostgreSQL. Redis is optional for a local non-Docker run; the project uses a local-memory cache when `REDIS_URL` is not set. Set the variables listed in `.env.example` in the backend process environment, then run:

```bash
cd backend
python -m venv .venv
# Activate the environment, then:
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_catalog
python manage.py createsuperuser
python manage.py runserver
```

When running Vite separately at `http://localhost:5173`, the Vite config proxies `/api`, `/backend-admin`, `/static` and `/healthz` to Django on `127.0.0.1:8000`. Add `http://localhost:5173` to `CSRF_TRUSTED_ORIGINS` for session-based admin login. A same-origin Nginx proxy is preferred for deployment.

## Backend endpoints

- `POST /api/enquiries/contact/` — persists a contact enquiry.
- `POST /api/enquiries/quote/` — persists a quote request and optional private attachment. The website sends an optional `Idempotency-Key`; retries with the same key and form data return the original response while its 24-hour cache entry is retained.
- `GET /api/products/`, `/api/projects/`, `/api/services/`, `/api/partners/`, `/api/awards/`, `/api/industries/`, `/api/media/`, `/api/news/` — public published catalogue/media/news data.
- `GET /api/news/<id>/image/` — serves a news photo only after its update is published and its publication date is reached.
- `GET /api/media/<id>/file/` — serves a published image asset. Unpublished assets require staff access.
- `GET /api/auth/csrf/`, `POST /api/auth/login/`, `POST /api/auth/logout/` — CSRF-aware session authentication.
- `GET /api/admin/dashboard/`, `GET /api/admin/enquiries/`, `PATCH /api/admin/enquiries/{contact|quote}/<id>/`, and `GET /api/admin/enquiries/export.csv` — staff-only enquiry management and filtered CSV export.
- `GET /api/admin/documents/<id>/download/` — staff-only private document download.

## Production checklist

- Configure a long random `DJANGO_SECRET_KEY`, unique PostgreSQL password, valid `DJANGO_ALLOWED_HOSTS`, and a real mail provider. Do not commit `.env` files.
- Set `DJANGO_DEBUG=false`, `COOKIE_SECURE=true`, `SECURE_SSL_REDIRECT=true`, and the HTTPS site in `CSRF_TRUSTED_ORIGINS` / `CORS_ALLOWED_ORIGINS`.
- Terminate HTTPS at a trusted ingress/load balancer and have it overwrite `X-Forwarded-Proto` accurately. The bundled Nginx listens on HTTP and does not itself provision certificates.
- Verify email delivery from the deployment environment and test form submission, private downloads, session expiry and rate limits.
- Review all starter catalogue records before publishing. Case-study content intentionally avoids unsupported customer-specific results and performance statistics.
- Replace the textual partner-name placeholders with authorized official partner-logo assets only if NexAge is permitted to publish them. No imitation partner logos are included.
- Review legal/privacy copy and add a production privacy notice before collecting real customer data.
- Schedule `python scripts/backup.py`, move copies to approved encrypted off-host storage, and periodically run `python scripts/restore_test.py` against a selected backup. Keep backup retention and encryption keys under company policy; the script does not encrypt or delete backups.
- Confirm the hosting provider's trusted proxy CIDRs and configure Nginx real-client-IP handling before relying on per-client throttling behind an ingress.
- Enable monitoring, logs, alerting and a documented update/rollback process for the production environment.

## Local quality checks

From the repository root in PowerShell, run:

```powershell
.\scripts\quality-check.ps1
```

This runs the frontend TypeScript check and production build, Django system checks and core tests against an in-memory SQLite database, migration consistency, the catalogue/asset audit, source-level keyboard/accessibility guardrails, repository script tests, a Compose configuration-only check when Docker is installed, and `git diff --check`. It does not start containers or connect to a configured PostgreSQL database. Browser keyboard interaction still needs a manual check in a running site.
