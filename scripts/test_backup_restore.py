import hashlib
import io
import json
import tarfile
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from backup import resolve_output_directory
from restore_test import (
    extract_private_media,
    inspect_media_archive,
    main as restore_main,
    verify_backup_set,
)


class BackupRestoreSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def _make_archive(self, path, name, content=b"private test content"):
        with tarfile.open(path, mode="w:gz") as archive:
            info = tarfile.TarInfo(name)
            info.size = len(content)
            archive.addfile(info, io.BytesIO(content))

    def test_backup_destination_inside_repository_is_rejected(self):
        repository_output = Path(__file__).resolve().parents[1] / "test-backup-output"
        with self.assertRaisesRegex(ValueError, "outside the repository"):
            resolve_output_directory(repository_output)

    def test_backup_manifest_checks_sizes_and_hashes(self):
        database = self.root / "database.dump"
        media = self.root / "private-media.tar.gz"
        database.write_bytes(b"test database dump")
        self._make_archive(media, "./attachment.pdf")
        manifest = {
            "format_version": 1,
            "created_at_utc": "2026-01-01T00:00:00+00:00",
            "files": {
                path.name: {"size_bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                for path in (database, media)
            },
        }
        (self.root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

        directory, files = verify_backup_set(self.root)

        self.assertEqual(directory, self.root.resolve())
        self.assertEqual(set(files), {"database.dump", "private-media.tar.gz"})

    def test_private_media_is_extracted_under_destination(self):
        archive = self.root / "media.tar.gz"
        self._make_archive(archive, "./customer/attachment.txt")
        destination = self.root / "restored-media"

        count = extract_private_media(archive, destination)

        self.assertEqual(count, 1)
        self.assertEqual(
            (destination / "customer" / "attachment.txt").read_bytes(),
            b"private test content",
        )

    def test_archive_path_traversal_is_rejected_before_extraction(self):
        archive = self.root / "unsafe.tar.gz"
        self._make_archive(archive, "../escape.txt")
        destination = self.root / "restored-media"

        with self.assertRaisesRegex(ValueError, "Unsafe path"):
            extract_private_media(archive, destination)

        self.assertFalse((self.root / "escape.txt").exists())
        self.assertFalse(destination.exists())

    def test_archive_symlinks_are_rejected(self):
        archive = self.root / "symlink.tar.gz"
        with tarfile.open(archive, mode="w:gz") as output:
            info = tarfile.TarInfo("./customer-link")
            info.type = tarfile.SYMTYPE
            info.linkname = "../outside"
            output.addfile(info)

        with self.assertRaisesRegex(ValueError, "link or unsupported"):
            inspect_media_archive(archive)

    def test_restore_dry_run_validates_backup_without_starting_docker(self):
        database = self.root / "database.dump"
        media = self.root / "private-media.tar.gz"
        database.write_bytes(b"test database dump")
        self._make_archive(media, "./attachment.pdf")
        manifest = {
            "format_version": 1,
            "created_at_utc": "2026-01-01T00:00:00+00:00",
            "files": {
                path.name: {"size_bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                for path in (database, media)
            },
        }
        (self.root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        output = StringIO()

        with redirect_stdout(output):
            result = restore_main([str(self.root), "--dry-run"])

        self.assertEqual(result, 0)
        self.assertIn("no extraction or database restore ran", output.getvalue())


if __name__ == "__main__":
    unittest.main()
