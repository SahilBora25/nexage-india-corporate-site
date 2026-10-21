#!/usr/bin/env python3
"""Validate and exercise a backup in an isolated, disposable restore target."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import uuid
from pathlib import Path, PurePosixPath


REQUIRED_FILES = {"database.dump", "private-media.tar.gz"}
POSTGRES_IMAGE = "postgres:16-alpine"
MAX_MEDIA_BYTES_DEFAULT = 20 * 1024 * 1024 * 1024


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_backup_set(value):
    original = Path(value).expanduser()
    if original.is_symlink():
        raise ValueError("Backup-set directory must not be a symbolic link.")
    directory = original.resolve(strict=True)
    if not directory.is_dir():
        raise ValueError("Backup-set path is not a directory.")

    manifest_path = directory / "manifest.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ValueError("Backup manifest is missing or is a symbolic link.")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("Backup manifest could not be read.") from exc
    if manifest.get("format_version") != 1 or not isinstance(manifest.get("files"), dict):
        raise ValueError("Unsupported or malformed backup manifest.")
    if set(manifest["files"]) != REQUIRED_FILES:
        raise ValueError("Backup manifest must contain exactly the expected database and media files.")

    files = {}
    for name in sorted(REQUIRED_FILES):
        path = directory / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Backup file is missing or is a symbolic link: {name}")
        metadata = manifest["files"][name]
        if not isinstance(metadata, dict):
            raise ValueError(f"Malformed manifest entry for {name}.")
        expected_size = metadata.get("size_bytes")
        expected_hash = metadata.get("sha256")
        if type(expected_size) is not int or expected_size < 0:
            raise ValueError(f"Malformed size in manifest for {name}.")
        if (
            not isinstance(expected_hash, str)
            or len(expected_hash) != 64
            or any(character not in "0123456789abcdef" for character in expected_hash.lower())
        ):
            raise ValueError(f"Malformed checksum in manifest for {name}.")
        if path.stat().st_size != expected_size or _sha256(path) != expected_hash.lower():
            raise ValueError(f"Backup checksum or size verification failed for {name}.")
        files[name] = path
    return directory, files


def _safe_member_target(root, member):
    name = member.name
    relative = PurePosixPath(name)
    if (
        not name
        or "\\" in name
        or ":" in name
        or relative.is_absolute()
        or any(part == ".." for part in relative.parts)
    ):
        raise ValueError(f"Unsafe path in private-media archive: {name!r}")
    target = root.joinpath(*relative.parts)
    try:
        target.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"Private-media archive path escapes the restore directory: {name!r}") from exc
    return target


def inspect_media_archive(archive_path, max_bytes=MAX_MEDIA_BYTES_DEFAULT):
    files = 0
    total_bytes = 0
    seen = set()
    with tarfile.open(archive_path, mode="r:gz") as archive:
        for member in archive.getmembers():
            target = _safe_member_target(Path(tempfile.gettempdir()), member)
            normalized = target.as_posix()
            if normalized in seen:
                raise ValueError("Private-media archive contains duplicate paths.")
            seen.add(normalized)
            if member.isdir():
                continue
            if not member.isreg():
                raise ValueError("Private-media archive contains a link or unsupported file type.")
            if member.size < 0:
                raise ValueError("Private-media archive contains a negative file size.")
            files += 1
            total_bytes += member.size
            if total_bytes > max_bytes:
                raise ValueError(
                    f"Private-media archive exceeds the {max_bytes} byte restore-test limit."
                )
    return files, total_bytes


def _protect_directory(directory):
    if os.name == "nt":
        identity = subprocess.run(
            ["whoami"], check=True, capture_output=True, text=True
        ).stdout.strip()
        result = subprocess.run(
            ["icacls", str(directory), "/inheritance:r", "/grant:r", f"{identity}:(OI)(CI)F"],
            capture_output=True,
            text=True,
        )
        if result.returncode:
            raise RuntimeError("Could not restrict temporary restore-media permissions.")
    else:
        os.chmod(directory, 0o700)


def extract_private_media(archive_path, destination, max_bytes=MAX_MEDIA_BYTES_DEFAULT):
    expected_files, _ = inspect_media_archive(archive_path, max_bytes=max_bytes)
    destination.mkdir(mode=0o700, parents=False, exist_ok=False)
    _protect_directory(destination)
    extracted_files = 0
    with tarfile.open(archive_path, mode="r:gz") as archive:
        for member in archive.getmembers():
            target = _safe_member_target(destination, member)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() or target.is_symlink():
                raise ValueError("Private-media archive contains duplicate or conflicting paths.")
            source = archive.extractfile(member)
            if source is None:
                raise ValueError("Could not read a regular file from the private-media archive.")
            with source, target.open("xb") as output:
                shutil.copyfileobj(source, output, length=1024 * 1024)
                output.flush()
                os.fsync(output.fileno())
            if os.name != "nt":
                os.chmod(target, 0o600)
            extracted_files += 1
    if extracted_files != expected_files:
        raise ValueError("Private-media archive extraction did not match the validated file count.")
    return extracted_files


def _run_docker(arguments, **kwargs):
    return subprocess.run(
        [shutil.which("docker") or "docker", *arguments],
        capture_output=True,
        **kwargs,
    )


def restore_database_isolated(database_dump):
    if not shutil.which("docker"):
        raise RuntimeError("Docker CLI was not found.")
    engine = _run_docker(["info"], text=True)
    if engine.returncode:
        raise RuntimeError("Docker Engine is unavailable; no restore ran.")
    image = _run_docker(["image", "inspect", POSTGRES_IMAGE], text=True)
    if image.returncode:
        raise RuntimeError(
            f"Required local image {POSTGRES_IMAGE} is unavailable; the script will not pull it."
        )

    container_name = f"nexage-restore-test-{uuid.uuid4().hex[:12]}"
    created = False
    try:
        create = _run_docker(
            [
                "create",
                "--name", container_name,
                "--network", "none",
                "--tmpfs", "/var/lib/postgresql/data:rw,noexec,nosuid,size=512m",
                "--env", "POSTGRES_DB=restore_test",
                "--env", "POSTGRES_USER=restore_test",
                "--env", "POSTGRES_PASSWORD=restore_test",
                POSTGRES_IMAGE,
            ],
            text=True,
        )
        if create.returncode:
            raise RuntimeError(f"Could not create isolated restore container (exit {create.returncode}).")
        created = True

        inspection = _run_docker(
            ["inspect", "--format", "{{json .Mounts}}", container_name],
            text=True,
        )
        if inspection.returncode:
            raise RuntimeError("Could not inspect isolated restore-container mounts.")
        try:
            mounts = json.loads(inspection.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Could not validate isolated restore-container mounts.") from exc
        if any(mount.get("Type") == "volume" for mount in mounts):
            raise RuntimeError("Restore container unexpectedly has a Docker volume; refusing to start it.")
        if not any(
            mount.get("Type") == "tmpfs"
            and mount.get("Destination") == "/var/lib/postgresql/data"
            for mount in mounts
        ):
            raise RuntimeError("Restore container data directory is not on the expected temporary filesystem.")

        started = _run_docker(["start", container_name], text=True)
        if started.returncode:
            raise RuntimeError(f"Could not start isolated restore container (exit {started.returncode}).")

        deadline = time.monotonic() + 60
        ready = False
        while time.monotonic() < deadline:
            check = _run_docker(
                ["exec", container_name, "pg_isready", "-U", "restore_test", "-d", "restore_test"],
                text=True,
            )
            if check.returncode == 0:
                ready = True
                break
            time.sleep(1)
        if not ready:
            raise RuntimeError("Timed out waiting for isolated PostgreSQL to become ready.")

        with database_dump.open("rb") as source:
            restored = _run_docker(
                [
                    "exec", "-i", container_name, "pg_restore",
                    "--exit-on-error", "--single-transaction", "--no-owner", "--no-acl",
                    "-U", "restore_test", "-d", "restore_test",
                ],
                stdin=source,
                stdout=subprocess.DEVNULL,
                text=False,
            )
        if restored.returncode:
            raise RuntimeError(f"Isolated database restore failed (exit {restored.returncode}).")

        table_count = _run_docker(
            [
                "exec", container_name, "psql", "-X", "-v", "ON_ERROR_STOP=1",
                "-U", "restore_test", "-d", "restore_test", "-Atc",
                "SELECT count(*) FROM information_schema.tables "
                "WHERE table_schema NOT IN ('pg_catalog', 'information_schema') "
                "AND table_type = 'BASE TABLE';",
            ],
            text=True,
        )
        if table_count.returncode:
            raise RuntimeError("Could not verify restored database tables.")
        try:
            count = int(table_count.stdout.strip())
        except ValueError as exc:
            raise RuntimeError("Isolated PostgreSQL returned an invalid table count.") from exc
        if count < 1:
            raise RuntimeError("The isolated restore completed without any application tables.")
        return count
    finally:
        if created:
            removed = _run_docker(["rm", "--force", container_name], text=True)
            if removed.returncode:
                raise RuntimeError(
                    f"Could not remove isolated restore container {container_name}; no volume-delete command ran."
                )


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Verify a backup and restore it only into an isolated throwaway database. "
            "No application database or Docker volume is mounted."
        )
    )
    parser.add_argument("backup_set", help="Directory containing database.dump, private-media.tar.gz, and manifest.json.")
    parser.add_argument(
        "--max-media-gib",
        type=int,
        default=20,
        help="Maximum uncompressed private-media size for this test (default: 20 GiB).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Verify checksums and archive paths without extracting media or running Docker.",
    )
    args = parser.parse_args(argv)
    if args.max_media_gib < 1:
        parser.error("--max-media-gib must be at least 1.")

    try:
        backup_directory, files = verify_backup_set(args.backup_set)
        max_bytes = args.max_media_gib * 1024 * 1024 * 1024
        media_file_count, media_bytes = inspect_media_archive(
            files["private-media.tar.gz"],
            max_bytes=max_bytes,
        )
        if args.dry_run:
            print("Dry run only. Checksums and archive paths passed; no extraction or database restore ran.")
            print(f"Private-media archive: {media_file_count} files, {media_bytes} uncompressed bytes.")
            return 0

        with tempfile.TemporaryDirectory(prefix="nexage-restore-test-") as temporary_directory:
            media_destination = Path(temporary_directory) / "private-media"
            extracted_files = extract_private_media(
                files["private-media.tar.gz"],
                media_destination,
                max_bytes=max_bytes,
            )
            table_count = restore_database_isolated(files["database.dump"])
        print(
            f"Isolated restore test passed: {table_count} application tables and "
            f"{extracted_files} private-media files checked from {backup_directory.name}."
        )
        return 0
    except (OSError, ValueError, RuntimeError, tarfile.TarError, subprocess.SubprocessError) as exc:
        print(f"Restore test failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
