# Publishing News & Company Updates

The News & Company Updates feature adds a dedicated `/news` page and a latest-updates section on the homepage. It uses the existing Django Admin and PostgreSQL setup. Existing product, project, enquiry, media, authentication and database configuration are not changed by this feature.

## Add an update

1. Open `/backend-admin/` and sign in with an existing Django staff/superuser account.
2. Open **News & company updates** and select **Add**.
3. Enter a title. The slug is suggested from the title; adjust it if needed.
4. Choose a category, enter a short summary and the full update content. Separate paragraphs with a blank line.
5. Optionally upload a JPG, JPEG, PNG or WebP cover photo (maximum 10 MB and 32 megapixels), add meaningful alt text, and paste a public HTTPS YouTube or Vimeo URL. Photo files are uploaded directly; videos are embedded from the supplied video URL.
6. Set **Published at**. Leave **Is published** unchecked to save a draft. Check it to publish when the date/time has arrived.
7. Save. Visit `/news` to view published updates. The homepage shows the latest three.

## API

- `GET /api/news/` returns only published updates whose publication date/time has arrived.
- `GET /api/news/<id>/` returns a public update only when it is published and due.
- `GET /api/news/<id>/image/` serves its cover photo under the same publication rule.

The public API is read-only. Create, edit and publish updates only through authenticated Django Admin. Raw MP4 upload is not included; use a public YouTube or Vimeo link for video embedding.

## Database migration

The existing Docker backend startup already runs `python manage.py migrate --noinput`. For a local backend, run the existing environment's migration command from `backend/`: `python manage.py migrate`. The new migration creates one `NewsUpdate` table and does not alter existing tables. Back up your database before applying any schema migration to production.
