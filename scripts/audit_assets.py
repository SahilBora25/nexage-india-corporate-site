#!/usr/bin/env python3
"""Validate local image references and compare the public catalogue with database image mappings."""
from collections import Counter
from pathlib import Path
import ast
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT / 'public' / 'images'
SOURCE_FILES = [
    ROOT / 'src' / 'data.ts',
    ROOT / 'src' / 'components' / 'Site.tsx',
    ROOT / 'src' / 'pages' / 'HomePage.tsx',
    ROOT / 'src' / 'pages' / 'ContentPages.tsx',
    ROOT / 'src' / 'styles.css',
    ROOT / 'backend' / 'core' / 'management' / 'commands' / 'seed_catalog.py',
    ROOT / 'backend' / 'core' / 'management' / 'commands' / 'sync_catalog_images.py',
    ROOT / 'index.html',
]
IMAGE_PATTERN = re.compile(r'''["']([^"']+\.(?:webp|png|jpe?g|svg|ico))(?:[?#][^"']*)?["']''', re.I)

def local_image_path(token: str):
    if token.lower().startswith(('http://', 'https://', 'data:')):
        return None
    if token.startswith('/images/'):
        return token[len('/images/'):]
    if token.startswith('public/images/'):
        return token[len('public/images/'):]
    # Plain file names and partner subpaths are relative to public/images.
    if '/' not in token or (IMAGE_DIR / token).is_file():
        return token
    # Ignore CSS or URL fragments outside this app's public image library.
    return None

def parse_collection(data_source: str, collection: str):
    match = re.search(r'export const ' + re.escape(collection) + r'(?::[^=]+)?\s*=\s*\[(.*?)\n\];', data_source, flags=re.S)
    if not match:
        return []
    rows = []
    for obj in re.findall(r'\{[^{}]*\}', match.group(1), flags=re.S):
        title_match = re.search(r"\btitle:\s*'([^']+)'", obj)
        slug_match = re.search(r"\bslug:\s*'([^']+)'", obj)
        image_match = re.search(r"\bimage:\s*'([^']+)'", obj)
        if title_match and image_match:
            rows.append((title_match.group(1), slug_match.group(1) if slug_match else '', image_match.group(1)))
    return rows

def parse_sync_maps():
    source = (ROOT / 'backend' / 'core' / 'management' / 'commands' / 'sync_catalog_images.py').read_text(encoding='utf-8')
    tree = ast.parse(source)
    assignment = next((node for node in tree.body if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'IMAGE_MAPS' for t in node.targets)), None)
    if assignment is None or not isinstance(assignment.value, ast.Dict):
        raise ValueError('IMAGE_MAPS dictionary not found')
    result = {}
    for key, value in zip(assignment.value.keys, assignment.value.values):
        if isinstance(key, ast.Name) and isinstance(value, ast.Dict):
            result[key.id] = ast.literal_eval(value)
    return result

missing = []
refs = []
for file in SOURCE_FILES:
    source = file.read_text(encoding='utf-8')
    for token in IMAGE_PATTERN.findall(source):
        path = local_image_path(token)
        if path is None:
            continue
        refs.append((file.relative_to(ROOT).as_posix(), token))
        if not (IMAGE_DIR / path).is_file():
            missing.append((file.relative_to(ROOT).as_posix(), token, path))

print(f'Image folder: {IMAGE_DIR}')
print(f'Local image references checked: {len(refs)}')
if missing:
    print('\nMISSING IMAGE REFERENCES:')
    for source, token, path in sorted(set(missing)):
        print(f'  {source}: {token} -> public/images/{path}')
else:
    print('Missing local image references: 0')

# Count exact reuse in catalogue roles and report it rather than incorrectly calling it a build failure.
data_source = (ROOT / 'src' / 'data.ts').read_text(encoding='utf-8')
role_counts = Counter(re.findall(r"(?:image|detailImage|introImage):\s*'([^']+\.(?:webp|png|jpe?g))'", data_source, flags=re.I))
print('\nRepeated image role assignments (review contextual reuse):')
for filename, count in sorted(((k, v) for k, v in role_counts.items() if v > 1), key=lambda item: (-item[1], item[0])):
    print(f'  {filename}: {count} assignments')

# Top-level page intros should not duplicate one another.
page_text = (ROOT / 'src' / 'pages' / 'ContentPages.tsx').read_text(encoding='utf-8')
intro_names = re.findall(r'<PageIntro\b[^>]*\bimage="([^"{]+\.(?:webp|png|jpe?g))"', page_text, flags=re.I)
intro_counts = Counter(intro_names)
intro_dupes = {name: count for name, count in intro_counts.items() if count > 1}
print(f'\nStatic top-level PageIntro images checked: {len(intro_names)}; distinct filenames: {len(intro_counts)}')
if intro_dupes:
    print('Repeated top-level PageIntro assignments: ' + ', '.join(f'{name} ({count})' for name, count in sorted(intro_dupes.items())))

# Build the expected primary-image maps from the static TS catalogue.
mapping_errors = []
service_slug_by_title = {
    'Preventive Maintenance & AMC': 'preventive-maintenance',
    'Installation & Commissioning': 'installation-commissioning',
    'Machinery Relocation': 'machinery-relocation',
    'Refurbishment & Troubleshooting': 'refurbishment-troubleshooting',
    'Fabrication & Pipeline Jobs': 'fabrication-pipeline',
    'Line & Process Integration': 'line-process-integration',
}
expected_maps = {}
for collection, model_key in [('products', 'Product'), ('projects', 'Project'), ('industries', 'Industry')]:
    expected_maps[model_key] = {slug: image for _, slug, image in parse_collection(data_source, collection) if slug}
expected_maps['Service'] = {
    service_slug_by_title[title]: image
    for title, _slug, image in parse_collection(data_source, 'services')
    if title in service_slug_by_title
}

try:
    sync_maps = parse_sync_maps()
    for model_key, expected in expected_maps.items():
        actual = sync_maps.get(model_key, {})
        for slug, image in expected.items():
            mapped = actual.get(slug)
            if mapped != image:
                mapping_errors.append(f'{model_key}:{slug}: static={image}, sync={mapped or "(missing)"}')
except Exception as exc:
    sync_maps = {}
    mapping_errors.append(f'Unable to audit canonical sync mappings: {exc}')

# Parse seed catalogue row literals and compare their image paths to the same static map.
def rows_between(source_text, start_marker, end_marker):
    start = source_text.find(start_marker)
    if start < 0:
        raise ValueError(f'missing seed section marker: {start_marker}')
    end = source_text.find(end_marker, start + len(start_marker))
    if end < 0:
        raise ValueError(f'missing seed section end marker: {end_marker}')
    return source_text[start:end]

def seed_rows(block):
    results = {}
    for line in block.splitlines():
        line = line.strip()
        if not line.startswith('('):
            continue
        fields = re.findall(r"'([^']*)'", line)
        image_names = re.findall(r"'([^']+\.(?:webp|png|jpe?g))'", line, flags=re.I)
        if len(fields) >= 2 and image_names:
            results[fields[1]] = image_names[-1]
    return results

try:
    seed = (ROOT / 'backend' / 'core' / 'management' / 'commands' / 'seed_catalog.py').read_text(encoding='utf-8')
    seed_expected = {
        'Product': seed_rows(rows_between(seed, 'product_rows = [', '        for title, slug, cat, desc, owner, image, features in product_rows')),
        'Project': seed_rows(rows_between(seed, 'project_rows = [', '        for title, slug, cat, desc, image in project_rows')),
        'Service': seed_rows(rows_between(seed, 'for title, slug, desc, image in [', ']: Service.objects')),
        'Industry': seed_rows(rows_between(seed, 'for name, slug, desc, image in [', ']: Industry.objects')),
    }
    for model_key, expected in expected_maps.items():
        for slug, image in expected.items():
            seeded = seed_expected.get(model_key, {}).get(slug)
            if seeded != image:
                mapping_errors.append(f'{model_key}:{slug}: static={image}, seed={seeded or "(missing)"}')
except Exception as exc:
    mapping_errors.append(f'Unable to audit seed catalogue mappings: {exc}')

if mapping_errors:
    print('\nCATALOGUE / DATABASE IMAGE MAPPING MISMATCHES:')
    for error in mapping_errors:
        print('  ' + error)
else:
    print('Static catalogue primary images match both seed_catalog and sync_catalog_images mappings.')

# Catalogue primary image collisions are reported separately from detail/intro reuse.
primary_assignments = []
for collection in ('solutions', 'products', 'projects', 'industries', 'services'):
    for title, _slug, image in parse_collection(data_source, collection):
        primary_assignments.append((collection, title, image))
primary_counts = Counter(image for _, _, image in primary_assignments)
primary_reused = {image: count for image, count in primary_counts.items() if count > 1}
print(f'\nCatalogue primary images: {len(primary_assignments)} roles / {len(primary_counts)} distinct files.')
if primary_reused:
    print('Repeated primary assignments that need new distinct photography for a strict no-reuse release:')
    for image, count in sorted(primary_reused.items(), key=lambda item: (-item[1], item[0])):
        descriptions = ', '.join(f'{collection}:{title}' for collection, title, assigned in primary_assignments if assigned == image)
        print(f'  {image} ({count} roles): {descriptions}')

exit_code = 1 if missing or mapping_errors or intro_dupes else 0
sys.exit(exit_code)
