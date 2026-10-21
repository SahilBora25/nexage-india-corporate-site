from pathlib import Path

from django.conf import settings
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError

from core.catalogue_images import CATALOGUE_IMAGE_MAPS
from core.models import Industry, Product, Project, Service


# The mapping fills missing paths only. Existing non-empty paths may have been
# selected by an administrator and are preserved even when they differ.
IMAGE_MAPS = {
    Product: CATALOGUE_IMAGE_MAPS['products'],
    Project: CATALOGUE_IMAGE_MAPS['projects'],
    Service: CATALOGUE_IMAGE_MAPS['services'],
    Industry: CATALOGUE_IMAGE_MAPS['industries'],
}


class Command(BaseCommand):
    help = 'Preview or apply canonical image_path mappings; only image_path fields are changed.'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true', help='Apply the image_path updates. Without this flag, only preview changes.')

    def handle(self, *args, **options):
        asset_dir = Path(settings.BASE_DIR).parent / 'public' / 'images'
        referenced = {filename for mapping in IMAGE_MAPS.values() for filename in mapping.values()}
        missing_files = sorted(filename for filename in referenced if not (asset_dir / filename).is_file())
        if missing_files:
            raise CommandError('Cannot sync because these mapped image assets are missing: ' + ', '.join(missing_files))

        changes = []
        unknown = []
        preserved = []
        for model, mapping in IMAGE_MAPS.items():
            for slug, image_path in mapping.items():
                try:
                    obj = model.objects.only('id', 'slug', 'image_path').get(slug=slug)
                except model.DoesNotExist:
                    unknown.append(f'{model.__name__}:{slug} (record not found)')
                    continue
                if not obj.image_path:
                    changes.append((model, obj, obj.image_path, image_path))
                elif obj.image_path != image_path:
                    preserved.append(f'{model.__name__}:{slug} ({obj.image_path})')

        if not changes:
            self.stdout.write(self.style.SUCCESS('No mapped records have an empty image path that needs backfilling.'))
        else:
            for model, obj, old, new in changes:
                self.stdout.write(f'{model.__name__} {obj.slug}: {old or "(empty)"} -> {new}')
            if options['apply']:
                # Apply the mapping as one transaction so a database error cannot leave a partial sync.
                with transaction.atomic():
                    for _model, obj, _old, new in changes:
                        obj.image_path = new
                        obj.save(update_fields=['image_path', 'updated_at'])
                self.stdout.write(self.style.SUCCESS(f'Updated image_path on {len(changes)} existing record(s).'))
            else:
                self.stdout.write(self.style.WARNING(f'Preview only: {len(changes)} update(s) would be made. Re-run with --apply to save them.'))

        if unknown:
            self.stdout.write(self.style.WARNING('No new records were created; these mappings were skipped:'))
            for entry in unknown:
                self.stdout.write(f'  - {entry}')

        if preserved:
            self.stdout.write(self.style.WARNING(
                f'Preserved {len(preserved)} non-empty image path(s); existing values are treated as database-managed.'
            ))
