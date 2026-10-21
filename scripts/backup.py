#!/usr/bin/env python3
"""Create a protected PostgreSQL and private-media backup with Docker Compose."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DATABASE_COMMAND = [
    "compose", "exec", "-T", "db", "sh", "-ec",
    'PGPASSWORD="$POSTGRES_PASSWORD" pg_dump --host=127.0.0.1 --format=custom --no-owner --no-acl -U "$POSTGRES_USER" "$POSTGRES_DB"',
]
MEDIA_COMMAND = [
    "compose", "exec", "-T", "backend", "sh", "-ec",
    "tar -C /app/backend/private_media -czf - .",
]


def default_output_directory():
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return base / "NexAge" / "backups"
    base = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    return base / "nexage" / "backups"


def resolve_output_directory(value):
    directory = Path(value).expanduser().resolve()
    repository = REPOSITORY_ROOT.resolve()
    try:
        directory.relative_to(repository)
    except ValueError:
        return directory
    raise ValueError("Backup output must be outside the repository.")


def protect_run_directory(directory):
    if os.name == "nt":
        identity = subprocess.run(
            ["whoami"], check=True, capture_output=True, text=True
        ).stdout.strip()
        result = subprocess.run(
            [
                "icacls", str(directory), "/inheritance:r", "/grant:r",
                f"{identity}:(OI)(CI)F",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode:
            raise RuntimeError("Could not restrict backup folder permissions.")
    else:
        os.chmod(directory, 0o700)


def _run_compose_to_file(arguments, path):
    with path.open("xb") as output:
        if os.name != "nt":
            os.chmod(path, 0o600)
        result = subprocess.run(
            ["docker", *arguments],
            cwd=REPOSITORY_ROOT,
            stdout=output,
            stderr=subprocess.PIPE,
            check=False,
        )
        output.flush()
        os.fsync(output.fileno())
    if result.returncode:
        raise RuntimeError(
            f"Docker Compose backup command failed with exit code {result.returncode}; "
            "diagnostic output was suppressed."
        )


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_backup(output_directory):
    docker = shutil.which("docker")
    if not docker:
        raise RuntimeError("Docker CLI was not found.")

    output_directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_directory = output_directory / f"nexage-{stamp}-{uuid.uuid4().hex[:8]}"
    run_directory.mkdir(mode=0o700)
    created_paths = []
    try:
        protect_run_directory(run_directory)
        database_partial = run_directory / "database.dump.partial"
        media_partial = run_directory / "private-media.tar.gz.partial"
        database_file = run_directory / "database.dump"
        media_file = run_directory / "private-media.tar.gz"
        manifest_partial = run_directory / "manifest.json.partial"
        manifest_file = run_directory / "manifest.json"

        for path in (
            database_partial, media_partial, database_file, media_file,
            manifest_partial, manifest_file,
        ):
            created_paths.append(path)

        _run_compose_to_file(DATABASE_COMMAND, database_partial)
        _run_compose_to_file(MEDIA_COMMAND, media_partial)
        os.replace(database_partial, database_file)
        os.replace(media_partial, media_file)

        manifest = {
            "format_version": 1,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "files": {
                database_file.name: {
                    "size_bytes": database_file.stat().st_size,
                    "sha256": _sha256(database_file),
                },
                media_file.name: {
                    "size_bytes": media_file.stat().st_size,
                    "sha256": _sha256(media_file),
                },
            },
        }
        with manifest_partial.open("x", encoding="utf-8", newline="\n") as output:
            json.dump(manifest, output, indent=2)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        if os.name != "nt":
            os.chmod(manifest_partial, 0o600)
        os.replace(manifest_partial, manifest_file)
        return run_directory
    except Exception:
        for path in created_paths:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
        try:
            run_directory.rmdir()
        except OSError:
            pass
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Back up PostgreSQL and private media to a unique, access-restricted "
            "directory outside this repository. The files are not encrypted by this script."
        )
    )
    parser.add_argument(
        "--output-dir",
        default=str(default_output_directory()),
        help="Approved protected storage root outside the repository.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the destination and describe the operations without running Docker.",
    )
    args = parser.parse_args(argv)

    try:
        output_directory = resolve_output_directory(args.output_dir)
        if args.dry_run:
            print("Dry run only. No Docker command ran and no backup was created.")
            print(f"Protected output root: {output_directory}")
            print("Would create a PostgreSQL custom dump and private-media archive.")
            return 0
        run_directory = create_backup(output_directory)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"Backup failed: {exc}", file=sys.stderr)
        return 1

    print(f"Backup set created: {run_directory}")
    print("Move it to approved encrypted off-host storage; this script does not encrypt files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
