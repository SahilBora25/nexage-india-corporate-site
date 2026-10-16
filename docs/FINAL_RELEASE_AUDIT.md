# NexAge India Website — Correction Pass Audit

## Scope

This is a targeted correction pass on the existing React/Vite + Django + PostgreSQL project. The application was not rebuilt from scratch, and no database was connected to, modified, reset, or replaced while preparing this package.

## Corrected in this package

- Aligned static catalogue image assignments with both `seed_catalog` and the safe `sync_catalog_images` command for products, projects, services, and industries.
- Corrected project imagery for IoT / PLC Monitoring, Automated Conveyor Systems, and Custom Industrial Solutions so the database mapping matches the static catalogue.
- Corrected the Service catalogue/seed mappings for Installation & Commissioning, Machinery Relocation, and Refurbishment & Troubleshooting.
- Aligned Industry slugs used by the frontend fallback catalogue with Django's slugs (`manufacturing-machinery`, `warehousing-logistics`, and `assembly-production`).
- Aligned the Industry Material Handling image with the existing asset `conveyor-materials.webp`.
- Added a safe database image synchronization command. It performs a dry-run by default, validates that each target file exists, and changes only `image_path` for known existing slugs. Applying changes is wrapped in a database transaction.
- Strengthened production settings validation: rejects short/placeholder Django secret keys and database passwords, validates `DATABASE_URL`, and requires explicit non-placeholder production hosts and CSRF trusted origins.
- Made Docker Compose default to secure cookies and HTTPS redirect for production. The README retains explicit overrides for local HTTP development.
- Confirmed the frontend dependencies are explicitly versioned, the frontend Dockerfile uses `package-lock.json` with `npm ci`, the SEO structured-data logo uses the real `nexage-logo.jpg` file, and Docker ignores virtual environments, generated bundles and nested source ZIPs.
- Added asset/mapping audit tooling and a CSV of the catalogue image assignments.
- Removed `node_modules`, the Windows Python virtual environment, nested ZIP snapshots, caches and other development-only generated files from this release archive. No real `.env` file or passwords are included.

## Validation performed in this environment

- Asset reference audit: **passed** — no missing local image references found in the audited frontend, seed, synchronization and metadata files.
- Catalogue mapping audit: **passed** — static primary assignments match both `seed_catalog` and `sync_catalog_images` for products, projects, services and industries.
- Top-level static PageIntro images: **10 checked; 10 distinct filenames**.
- Python syntax compilation: **passed** for backend `.py` files.
- ZIP integrity: the source archive opened and tested without ZIP corruption; the corrected archive is verified again when built.
- Image decoding: source image assets are checked as part of packaging validation.

## Tests not completed here

- `npm ci` did not complete in this environment because the npm registry/dependency installation timed out. Therefore `npm run build` is **not certified as passed** by this correction pass. Run `npm ci` and `npm run build` on the connected Windows development machine before public deployment.
- Django runtime checks and `python manage.py test core` were not run here because this environment does not have the project's configured Django/PostgreSQL runtime. Run them locally with the backend environment configured.
- No live-browser form submission, SMTP delivery, Docker image build, or production deployment test was performed here.
- The image-sync command was not applied to any database. It must first be previewed against the existing local database and only applied after a database backup.

## Remaining image reuse to review

The source image library does not contain a unique appropriate photograph for every primary, detail, introduction and page-intro role. This pass removes several mismatched mappings and keeps each item’s own primary/detail/intro choices distinct, but it does **not** claim strict global image uniqueness. There are still these repeated primary assignments:

- `industrial-integration.webp`: MRO & Industrial Services solution, Custom Industrial Solutions project, and Line & Process Integration service.
- `maintenance-technician.webp`: Machine Refurbishment project and Refurbishment & Troubleshooting service.
- `pick-to-light.webp`: Pick-to-Light solution and Pick-to-Light project (same application shown in two catalogue contexts).

The remaining role-level reuse is listed by `scripts/audit_assets.py`. These should be replaced with genuinely different, category-appropriate image assets if a strict no-reuse release is required. This package deliberately does not pretend that renamed or cropped copies would count as unique scenes.

## Safe next steps on Windows

1. Back up the existing project and PostgreSQL database before copying this revision into your working folder.
2. In the project root, run `npm ci` and then `npm run build`.
3. In the backend terminal with the project's environment variables active, run `python manage.py check` and `python manage.py test core`.
4. Before touching image paths in the existing database, run `python manage.py sync_catalog_images` (dry-run), review every proposed change, and back up the database. Run `python manage.py sync_catalog_images --apply` only when the preview is correct.
5. Configure fresh production secrets, the real production hostname, CSRF trusted origins, SMTP, HTTPS and the privacy notice before deployment.
