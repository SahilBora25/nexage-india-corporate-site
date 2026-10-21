#!/usr/bin/env python3
"""Validate local image references and compare the public catalogue with database image mappings."""
from collections import Counter
from pathlib import Path
import ast
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT / 'public' / 'images'
SOURCE_FILES = [
    ROOT / 'src' / 'data.ts',
    ROOT / 'src' / 'catalogue-images.json',
    ROOT / 'src' / 'components' / 'Site.tsx',
    ROOT / 'src' / 'pages' / 'HomePage.tsx',
    ROOT / 'src' / 'pages' / 'ContentPages.tsx',
    ROOT / 'src' / 'styles.css',
    ROOT / 'backend' / 'core' / 'management' / 'commands' / 'seed_catalog.py',
    ROOT / 'backend' / 'core' / 'management' / 'commands' / 'sync_catalog_images.py',
    ROOT / 'index.html',
]
IMAGE_PATTERN = re.compile(r'''["']([^"']+\.(?:webp|png|jpe?g|svg|ico))(?:[?#][^"']*)?["']''', re.I)
catalogue_image_maps = json.loads((ROOT / 'src' / 'catalogue-images.json').read_text(encoding='utf-8'))

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
    source_name = {
        'products': 'productDefinitions',
        'projects': 'projectDefinitions',
        'industries': 'industryDefinitions',
        'services': 'serviceDefinitions',
    }.get(collection, collection)
    match = re.search(r'(?:export )?const ' + re.escape(source_name) + r'(?::[^=]+)?\s*=\s*\[(.*?)\n\];', data_source, flags=re.S)
    if not match:
        return []
    rows = []
    for obj in re.findall(r'\{[^{}]*\}', match.group(1), flags=re.S):
        title_match = re.search(r"\btitle:\s*'([^']+)'", obj)
        slug_match = re.search(r"\bslug:\s*'([^']+)'", obj)
        image_match = re.search(r"\bimage:\s*'([^']+)'", obj)
        slug = slug_match.group(1) if slug_match else ''
        image = image_match.group(1) if image_match else catalogue_image_maps.get(collection, {}).get(slug)
        if title_match and image:
            rows.append((title_match.group(1), slug, image))
    return rows

def parse_sync_maps():
    source = (ROOT / 'backend' / 'core' / 'management' / 'commands' / 'sync_catalog_images.py').read_text(encoding='utf-8')
    tree = ast.parse(source)
    assignment = next((node for node in tree.body if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'IMAGE_MAPS' for t in node.targets)), None)
    if assignment is None or not isinstance(assignment.value, ast.Dict):
        raise ValueError('IMAGE_MAPS dictionary not found')
    result = {}
    for key, value in zip(assignment.value.keys, assignment.value.values):
        if not isinstance(key, ast.Name):
            continue
        if isinstance(value, ast.Dict):
            result[key.id] = ast.literal_eval(value)
        elif (
            isinstance(value, ast.Subscript)
            and isinstance(value.value, ast.Name)
            and value.value.id == 'CATALOGUE_IMAGE_MAPS'
            and isinstance(value.slice, ast.Constant)
        ):
            result[key.id] = catalogue_image_maps.get(value.slice.value, {})
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

# The shared JSON manifest is the source for all public and database defaults.
mapping_errors = []
collection_model_keys = {'products': 'Product', 'projects': 'Project', 'services': 'Service', 'industries': 'Industry'}
expected_maps = {model: catalogue_image_maps[collection] for collection, model in collection_model_keys.items()}
frontend_code = data_source
for collection in collection_model_keys:
    definition = {'products': 'productDefinitions', 'projects': 'projectDefinitions', 'services': 'serviceDefinitions', 'industries': 'industryDefinitions'}[collection]
    mapping_call = f'withCatalogueImages({definition}, catalogueImages.{collection} as Record<string, string>)'
    if mapping_call not in frontend_code:
        mapping_errors.append(f'Frontend {collection} list is not using the shared image manifest.')
    static_slugs = {slug for _title, slug, _image in parse_collection(data_source, collection) if slug}
    mapped_slugs = set(expected_maps[collection_model_keys[collection]])
    if static_slugs != mapped_slugs:
        mapping_errors.append(f'{collection}: frontend slugs do not match manifest slugs.')

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

# Parse seed slugs and verify each Django collection reads image paths from the manifest.
def rows_between(source_text, start_marker, end_marker):
    start = source_text.find(start_marker)
    if start < 0:
        raise ValueError(f'missing seed section marker: {start_marker}')
    end = source_text.find(end_marker, start + len(start_marker))
    if end < 0:
        raise ValueError(f'missing seed section end marker: {end_marker}')
    return source_text[start:end]

def seed_slugs(block):
    results = set()
    for line in block.splitlines():
        line = line.strip()
        if not line.startswith('('):
            continue
        fields = re.findall(r"'([^']*)'", line)
        if len(fields) >= 2:
            results.add(fields[1])
    return results

try:
    seed = (ROOT / 'backend' / 'core' / 'management' / 'commands' / 'seed_catalog.py').read_text(encoding='utf-8')
    backend_dockerfile = (ROOT / 'backend' / 'Dockerfile').read_text(encoding='utf-8')
    seed_sections = {
        'Product': ('products', 'product_rows = [', '        for title, slug, cat, desc, owner, features in product_rows', "CATALOGUE_IMAGE_MAPS['products'][slug]"),
        'Project': ('projects', 'project_rows = [', '        for title, slug, cat, desc in project_rows', "CATALOGUE_IMAGE_MAPS['projects'][slug]"),
        'Service': ('services', 'for title, slug, desc in [', ']: Service.objects', "CATALOGUE_IMAGE_MAPS['services'][slug]"),
        'Industry': ('industries', 'for name, slug, desc in [', ']: Industry.objects', "CATALOGUE_IMAGE_MAPS['industries'][slug]"),
    }
    for model_key, (collection, start, end, lookup) in seed_sections.items():
        seeded_slugs = seed_slugs(rows_between(seed, start, end))
        expected_slugs = set(expected_maps[model_key])
        if seeded_slugs != expected_slugs:
            mapping_errors.append(f'{model_key}: seed slugs do not match manifest slugs.')
        if lookup not in seed:
            mapping_errors.append(f'{model_key}: seed command is not using the shared image manifest.')
    if "import catalogueImages from './catalogue-images.json'" not in frontend_code:
        mapping_errors.append('Frontend catalogue image manifest import is missing.')
    if 'COPY src/catalogue-images.json /app/src/catalogue-images.json' not in backend_dockerfile:
        mapping_errors.append('Backend image does not include the shared catalogue image manifest.')
except Exception as exc:
    mapping_errors.append(f'Unable to audit seed catalogue mappings: {exc}')

if mapping_errors:
    print('\nCATALOGUE / DATABASE IMAGE MAPPING MISMATCHES:')
    for error in mapping_errors:
        print('  ' + error)
else:
    print('Frontend catalogue lists, seed defaults, and sync mappings use the same image manifest.')

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
