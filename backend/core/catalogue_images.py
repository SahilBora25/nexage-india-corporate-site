"""Shared catalogue image manifest used by the website and Django commands."""

import json
from pathlib import Path


MANIFEST_PATH = Path(__file__).resolve().parents[2] / 'src' / 'catalogue-images.json'
CATALOGUE_IMAGE_MAPS = json.loads(MANIFEST_PATH.read_text(encoding='utf-8'))
