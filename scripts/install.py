"""Install the complete Learn It bundle into a coding agent's skill directory."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import stat
import sys
import tempfile
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
SKILLS = ("learn-start", "learn-progress", "learn-next", "learn-test", "learn-review")
PROJECT_PATHS = {
    "codex": ".agents/skills",
    "claude-code": ".claude/skills",
    "cursor": ".cursor/skills",
    "github-copilot": ".github/skills",
    "opencode": ".opencode/skills",
}
USER_PATHS = {**PROJECT_PATHS, "github-copilot": ".copilot/skills", "opencode": ".config/opencode/skills"}
MANIFEST = ".learn-it-install.json"
SOURCE = "https://github.com/JuliossJunk/learn-it-skill"


def linked(path: Path) -> bool:
    """Include Windows directory junctions in link detection."""
    try:
        info = path.lstat()
        return path.is_symlink() or bool(getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    except FileNotFoundError:
        return False


def guard_root(root: Path) -> None:
    for path in (root, *root.parents):
        if linked(path):
            raise ValueError(f"Linked destination: {path}. Use the tool that created it or a regular directory.")
    if root.exists() and not root.is_dir():
        raise ValueError(f"Skill directory is not a directory: {root}")


def child(root: Path, name: str) -> Path:
    if name not in (*SKILLS, MANIFEST):
        raise ValueError("Unexpected installation entry")
    target = root / name
    if linked(target) or target.resolve().parent != root.resolve():
        raise ValueError(f"Linked or escaping installation entry: {target}")
    return target


def snapshot(directory: Path) -> dict[str, str]:
    if linked(directory) or not directory.is_dir():
        raise ValueError(f"Expected a regular skill directory: {directory}")
    result = {}
    for path in sorted(directory.rglob("*")):
        relative = path.relative_to(directory)
        if linked(path):
            raise ValueError(f"Linked skill content: {path}")
        if "__pycache__" in relative.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        if path.is_file():
            result[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def source_snapshots(repository: Path) -> dict:
    result = {}
    for name in SKILLS:
        result[name] = snapshot(repository / "skills" / name)
        if "SKILL.md" not in result[name]:
            raise ValueError(f"Missing source SKILL.md: {name}")
    return result


def load_manifest(root: Path) -> dict | None:
    path = child(root, MANIFEST)
    if not path.exists():
        return None
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if (not isinstance(manifest, dict) or manifest.get("schema_version") != 1
            or manifest.get("source") != SOURCE or not isinstance(manifest.get("skills"), dict)
            or set(manifest["skills"]) != set(SKILLS)):
        raise ValueError(f"Unrecognized installation manifest: {path}")
    for files in manifest["skills"].values():
        if not isinstance(files, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in files.items()):
            raise ValueError(f"Invalid installation manifest: {path}")
    return manifest


def inspect(root: Path, expected: dict) -> tuple[dict | None, list[dict]]:
    guard_root(root)
    manifest = load_manifest(root)
    rows = []
    for name in SKILLS:
        path = child(root, name)
        if not path.exists():
            status = "missing"
            actual = None
        else:
            actual = snapshot(path)
            if manifest and actual != manifest["skills"][name]:
                status = "modified"
            elif actual == expected[name]:
                status = "current" if manifest else "identical-unmanaged"
            elif manifest:
                status = "update-available"
            else:
                status = "conflict"
        rows.append({"skill": name, "status": status, "actual": actual})
    return manifest, rows


def apply(root: Path, repository: Path, action: str, update: bool = False, dry_run: bool = False) -> dict:
    expected = source_snapshots(repository)
    manifest, rows = inspect(root, expected)
    report = {"destination": str(root), "action": action, "dry_run": dry_run,
              "skills": [{"skill": row["skill"], "status": row["status"]} for row in rows]}
    if action == "check":
        report["ok"] = all(row["status"] == "current" for row in rows)
        return report
    conflicts = [row["skill"] for row in rows if row["status"] in {"modified", "conflict"}]
    if conflicts:
        raise ValueError("Local changes or conflicting skills: " + ", ".join(conflicts)
                         + ". Compare and preserve them before continuing; nothing was changed.")
    if action == "uninstall":
        if not manifest:
            raise ValueError("No Learn It installation manifest; refusing to remove unmanaged skills")
    elif not update and any(row["status"] == "update-available" for row in rows):
        raise ValueError("An older managed installation exists; rerun install with --update")
    report["ok"] = True
    if dry_run:
        return report
    if action == "install" and manifest and all(row["status"] == "current" for row in rows):
        return report

    root.mkdir(parents=True, exist_ok=True)
    guard_root(root)
    # Stage beside the destination so renames stay on the same filesystem.
    with tempfile.TemporaryDirectory(prefix=".learn-it-stage-", dir=root.parent) as temporary:
        staging = Path(temporary)
        fresh, previous = staging / "fresh", staging / "previous"
        fresh.mkdir()
        previous.mkdir()
        if action == "install":
            for name in SKILLS:
                shutil.copytree(repository / "skills" / name, fresh / name,
                                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
                if snapshot(fresh / name) != expected[name]:
                    raise ValueError(f"Staged source changed during copy: {name}")
            (fresh / MANIFEST).write_text(json.dumps({"schema_version": 1, "source": SOURCE, "skills": expected}, indent=2) + "\n", encoding="utf-8")
        # Recheck the whole bundle before touching any installed files.
        current_manifest, current_rows = inspect(root, expected)
        if current_manifest != manifest or current_rows != rows:
            raise ValueError("Installation changed during preparation; rerun the command")
        moved = []
        try:
            for name in (*SKILLS, MANIFEST):
                destination = child(root, name)
                backup = previous / name
                existed = destination.exists()
                if existed:
                    # child() verifies the resolved path stays under the exact skill root.
                    destination.rename(backup)
                moved.append((destination, backup, existed))
                if action == "install":
                    (fresh / name).rename(destination)
        except Exception:
            # Restore the prior bundle if a normal filesystem operation fails.
            for destination, backup, existed in reversed(moved):
                if destination.exists():
                    destination.rename(fresh / destination.name)
                if existed:
                    backup.rename(destination)
            raise
    return report


def destination(agent: str, scope: str, project: Path | None = None, home: Path | None = None) -> Path:
    if scope == "project":
        if project is None or not project.is_dir():
            raise ValueError("Project scope requires --project pointing to an existing directory")
        return project.absolute() / PROJECT_PATHS[agent]
    return (home or Path.home()) / USER_PATHS[agent]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("install", "check", "uninstall"))
    parser.add_argument("--agent", choices=PROJECT_PATHS, required=True)
    parser.add_argument("--scope", choices=("user", "project"), default="user")
    parser.add_argument("--project", type=Path, help="Existing project directory; required for project scope")
    parser.add_argument("--dry-run", action="store_true", help="Show the plan without writing files")
    parser.add_argument("--update", action="store_true", help="Replace an unchanged managed installation with this checkout")
    args = parser.parse_args()
    try:
        if args.scope == "user" and args.project is not None:
            raise ValueError("--project applies only to --scope project")
        if args.update and args.action != "install":
            raise ValueError("--update applies only to install")
        root = destination(args.agent, args.scope, args.project)
        result = apply(root, REPOSITORY, args.action, args.update, args.dry_run)
        print(json.dumps(result, indent=2, ensure_ascii=True))
        return 0 if result["ok"] else 1
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
