from pathlib import Path

from django.conf import settings
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError

from core.models import Industry, Product, Project, Service


# Intentionally updates only image_path for records with a known slug. It does not
# create/delete records or overwrite descriptions, category, ownership, or publication state.
IMAGE_MAPS = {
    Product: {
        'jidoka': 'jidoka-poka-yoke.webp',
        'wireless-tx-rx': 'wireless-tx-rx.webp',
        'pick-to-light': 'pick-to-light-rack.webp',
        'cranes-hoists': 'chain-hoist.webp',
        'industrial-tools': 'tools-product-line.webp',
        'custom-machines': 'custom-press-cell.webp',
        'torque-tools': 'tools-product-detail.webp',
        'battery-tools': 'industrial-tools.webp',
        'jigs-fixtures': 'jig-fixture.webp',
        'material-handling-equipment': 'guided-trolley.webp',
        'rail-systems': 'lifting-hardware.webp',
        'tightening-solutions': 'electric-torque-tool.webp',
    },
    Project: {
        'pick-to-light-kitting': 'pick-to-light.webp',
        'jidoka-workstation': 'electronics-testing.webp',
        'iot-plc-monitoring': 'control-cabinet.webp',
        'conveyor-lift-table': 'lift-table.webp',
        'tightening-machine': 'tool-in-use.webp',
        'servo-cartesian-spm': 'robotic-cell-inspection.webp',
        'hoist-rail-installation': 'overhead-crane.webp',
        'machine-relocation': 'machine-relocation.webp',
        'condition-monitoring': 'plc-monitoring.webp',
        'automated-conveyor-systems': 'roller-conveyor-detail.webp',
        'jigs-fixtures-project': 'precision-manufacturing.webp',
        'sealing-pressing-solutions': 'pressing-machine.webp',
        'machine-refurbishment': 'maintenance-technician.webp',
        'material-handling-systems': 'manipulator.webp',
        'custom-industrial-solutions': 'industrial-integration.webp',
    },
    Service: {
        'preventive-maintenance': 'condition-monitoring.webp',
        'installation-commissioning': 'commissioning-team.webp',
        'machinery-relocation': 'warehouse-logistics.webp',
        'refurbishment-troubleshooting': 'maintenance-technician.webp',
        'fabrication-pipeline': 'fabrication.webp',
        'line-process-integration': 'industrial-integration.webp',
    },
    Industry: {
        'automotive': 'automotive-industry.webp',
        'manufacturing-machinery': 'conveyor-line.webp',
        'warehousing-logistics': 'warehouse-fulfillment.webp',
        'assembly-production': 'assembly-line-overview.webp',
        'food-beverage': 'food-beverage.webp',
        'engineering-machinery': 'engineering-design.webp',
        'material-handling': 'conveyor-materials.webp',
        'industrial-services': 'hero-factory.webp',
    },
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
        for model, mapping in IMAGE_MAPS.items():
            for slug, image_path in mapping.items():
                try:
                    obj = model.objects.only('id', 'slug', 'image_path').get(slug=slug)
                except model.DoesNotExist:
                    unknown.append(f'{model.__name__}:{slug} (record not found)')
                    continue
                if obj.image_path != image_path:
                    changes.append((model, obj, obj.image_path, image_path))

        if not changes:
            self.stdout.write(self.style.SUCCESS('All existing mapped catalogue records already use canonical image paths.'))
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
