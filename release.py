

#!/usr/bin/env python3
"""Automated Python package preparation and PyPI release."""

from __future__ import annotations

import argparse
import ast
import importlib.metadata
import re
import subprocess
import sys
import tempfile
import tomllib
from datetime import date
from pathlib import Path

import tomlkit

from map_src import map_src, package_directories


ROOT = Path(__file__).resolve().parent
DEFAULT_SRC = ROOT / "src"
PROJECT_FILE = ROOT / "pyproject.toml"
CHANGELOG_FILE = ROOT / "CHANGELOG.md"

RELEASE_TYPES = ("PATCH", "MINOR", "MEDIUM", "MAJOR")

# Import name -> PyPI distribution name.
KNOWN_DISTRIBUTIONS = {
    "PIL": "Pillow",
    "cv2": "opencv-python",
    "yaml": "PyYAML",
    "sklearn": "scikit-learn",
    "bs4": "beautifulsoup4",
    "dotenv": "python-dotenv",
    "Crypto": "pycryptodome",
    "fitz": "PyMuPDF",
    "dateutil": "python-dateutil",
    "serial": "pyserial",
    "magic": "python-magic",
    "attr": "attrs",
    "gi": "PyGObject",
    "wx": "wxPython",
    "OpenGL": "PyOpenGL",
    "google": "google-api-python-client",
}


def run(command: list[str]) -> None:
    """Run a subprocess and stop on failure."""
    print("\n$", " ".join(command))
    subprocess.run(command, check=True, cwd=ROOT)


def load_project(path: Path) -> tomlkit.TOMLDocument:
    """Load a TOML project file."""
    if not path.is_file():
        raise FileNotFoundError(f"Missing project file: {path}")

    return tomlkit.parse(path.read_text(encoding="utf-8"))


def current_version(document: tomlkit.TOMLDocument) -> str:
    """Read and validate a static project version."""
    project = document.get("project")

    if not project or not isinstance(project.get("version"), str):
        raise ValueError(
            "pyproject.toml must define a static [project].version."
        )

    version = project["version"]

    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError(
            f"Expected MAJOR.MINOR.PATCH, got {version!r}."
        )

    return version


def bump_version(version: str, release_type: str) -> str:
    """Calculate the next stable semantic version."""
    major, minor, patch = map(int, version.split("."))

    if release_type == "PATCH":
        patch += 1
    elif release_type in {"MINOR", "MEDIUM"}:
        minor += 1
        patch = 0
    elif release_type == "MAJOR":
        major += 1
        minor = patch = 0
    else:
        raise ValueError(f"Unknown release type: {release_type}")

    return f"{major}.{minor}.{patch}"


def python_files(src: Path) -> list[Path]:
    """Find Python files while excluding common generated directories."""
    ignored = {
        ".git", ".venv", "venv", "build", "dist",
        "node_modules", "__pycache__", ".tox",
        ".pytest_cache", ".mypy_cache",
    }

    result = []

    for path in src.rglob("*.py"):
        if any(part in ignored for part in path.parts):
            continue
        if path.is_file():
            result.append(path)

    return sorted(result)


def local_module_names(src: Path) -> set[str]:
    """Collect local module and package names."""
    names = set()

    for path in python_files(src):
        if path.name != "__init__.py":
            names.add(path.stem)

        try:
            relative = path.relative_to(src)
        except ValueError:
            continue

        parts = list(relative.parts)

        if parts[-1] == "__init__.py":
            parts.pop()
        else:
            parts[-1] = Path(parts[-1]).stem

        if parts:
            names.add(parts[0])

    return names


def discover_imports(src: Path) -> set[str]:
    """Find external top-level imports using the Python AST."""
    imports: set[str] = set()

    for path in python_files(src):
        try:
            tree = ast.parse(
                path.read_text(encoding="utf-8"),
                filename=str(path),
            )
        except (SyntaxError, UnicodeDecodeError) as exc:
            raise ValueError(
                f"Cannot scan {path}: {exc}"
            ) from exc

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])

            elif isinstance(node, ast.ImportFrom):
                # Relative imports refer to the current package.
                if node.level == 0 and node.module:
                    imports.add(node.module.split(".")[0])

    imports.difference_update(sys.stdlib_module_names)
    imports.difference_update(local_module_names(src))

    return imports


def normalize_distribution(name: str) -> str:
    """Normalize a distribution name for case-insensitive comparison."""
    return re.sub(r"[-_.]+", "-", name).lower()


def installed_import_mapping() -> dict[str, set[str]]:
    """Map import packages to distributions installed in this environment."""
    result: dict[str, set[str]] = {}

    try:
        mapping = importlib.metadata.packages_distributions()
    except Exception:
        mapping = {}

    for import_name, distributions in mapping.items():
        result[import_name] = set(distributions)

    return result


def dependency_candidates(
    imports: set[str],
) -> tuple[dict[str, str], list[str]]:
    """Resolve import names to distributions where possible."""
    installed = installed_import_mapping()
    resolved: dict[str, str] = {}
    unknown: list[str] = []

    for name in sorted(imports):
        if name in KNOWN_DISTRIBUTIONS:
            resolved[name] = KNOWN_DISTRIBUTIONS[name]
            continue

        candidates = installed.get(name, set())

        if len(candidates) == 1:
            resolved[name] = next(iter(candidates))
        elif len(candidates) > 1:
            print(
                f"\nImport {name!r} maps to multiple installed "
                f"distributions: {', '.join(sorted(candidates))}"
            )
            chosen = input(
                f"Enter the correct PyPI distribution for {name} "
                "(blank to skip): "
            ).strip()
            if chosen:
                resolved[name] = chosen
        else:
            unknown.append(name)

    return resolved, unknown


def resolve_unknown_imports(
    unknown: list[str],
    resolved: dict[str, str],
) -> None:
    """Ask about unresolved imports instead of guessing their names."""
    if not unknown:
        return

    print(
        "\nSome imports could not be mapped automatically. "
        "They may be local, optional, or third-party modules."
    )

    for name in unknown:
        answer = input(
            f"PyPI distribution for import {name!r} "
            "(blank to skip): "
        ).strip()

        if answer:
            resolved[name] = answer


def update_dependencies(
    document: tomlkit.TOMLDocument,
    src: Path,
) -> list[str]:
    """Add discovered dependencies without deleting existing requirements."""
    project = document.get("project")

    if project is None:
        raise ValueError("pyproject.toml has no [project] section.")

    if "dynamic" in project and "dependencies" in project["dynamic"]:
        raise ValueError(
            "Dependencies are dynamically configured. "
            "Update the backend configuration manually."
        )

    if "dependencies" in project:
        existing = project["dependencies"]
        if not isinstance(existing, list):
            raise ValueError("[project].dependencies must be an array.")
    else:
        existing = tomlkit.array()
        project["dependencies"] = existing

    imports = discover_imports(src)
    resolved, unknown = dependency_candidates(imports)
    resolve_unknown_imports(unknown, resolved)

    existing_names = set()

    for requirement in existing:
        match = re.match(r"\s*([A-Za-z0-9_.-]+)", str(requirement))
        if match:
            existing_names.add(
                normalize_distribution(match.group(1))
            )

    added: list[str] = []

    for import_name, distribution in sorted(resolved.items()):
        normalized = normalize_distribution(distribution)

        if normalized in existing_names:
            print(f"already declared: {distribution}")
            continue

        # Bare names avoid inventing version constraints.
        existing.append(distribution)
        existing_names.add(normalized)
        added.append(distribution)

        print(
            f"dependency discovered: {import_name} -> {distribution}"
        )

    return added


def update_changelog(
    path: Path,
    version: str,
    notes: list[str],
) -> None:
    """Prepend a dated release entry."""
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    heading = re.match(r"(?m)^# .+\n*", old)

    section = (
        f"## [{version}] - {date.today().isoformat()}\n\n"
        + "".join(f"- {note}\n" for note in notes)
        + "\n"
    )

    if heading:
        updated = (
            old[:heading.end()]
            + "\n"
            + section
            + old[heading.end():].lstrip("\n")
        )
    elif old.strip():
        updated = "# Changelog\n\n" + section + old
    else:
        updated = "# Changelog\n\n" + section

    path.write_text(updated.rstrip() + "\n", encoding="utf-8")


def collect_notes() -> list[str]:
    """Collect a release summary, categorized changes, and validation notes."""
    print("\n== Release details ==")
    print("Write notes for users; press Enter on a blank line to skip a category.")

    summary = input("\nRelease summary: ").strip()
    if not summary:
        raise ValueError("A release summary is required.")

    notes = [f"Summary: {summary}"]

    categories = (
        ("Features", "Feature"),
        ("Improvements", "Improvement"),
        ("Bug fixes", "Fix"),
        ("Breaking changes", "Breaking change"),
        ("Migration guidance", "Migration"),
    )

    for heading, label in categories:
        print(f"\n{heading} (blank line to finish):")
        while True:
            note = input("  - ").strip()
            if not note:
                break
            notes.append(f"{label}: {note.lstrip('-* ').strip()}")

    validation = input("\nTests and validation performed: ").strip()
    if not validation:
        raise ValueError("Describe the tests or validation performed.")
    notes.append(f"Validation: {validation}")

    return notes


def collect_commit_name() -> str:
    """Ask for the commit subject to use after the package is published."""
    print("\n== GitHub commit ==")
    print("Use a short, descriptive commit title (for example: Release 1.3.0).")
    commit_name = input("Commit title: ").strip()

    if not commit_name:
        raise ValueError("A commit title is required.")

    return commit_name


def confirm(message: str) -> bool:
    """Require an explicit yes."""
    return input(f"{message} [y/N]: ").strip().lower() in {
        "y", "yes"
    }


def git_output(arguments: list[str]) -> str:
    """Run a Git query and return its output with an actionable error."""
    result = subprocess.run(
        ["git", *arguments],
        check=False,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    if result.returncode:
        details = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(
            f"git {' '.join(arguments)} failed"
            + (f": {details}" if details else ".")
        )

    return result.stdout.strip()


def prepare_git_release() -> tuple[str, str]:
    """Ensure this release can be committed and pushed without other changes."""
    status = git_output(["status", "--porcelain"])
    if status:
        raise ValueError(
            "The working tree is not clean. Commit or stash existing changes "
            "before running a release so they are not included accidentally."
        )

    branch = git_output(["branch", "--show-current"])
    if not branch:
        raise ValueError("A release cannot be pushed from a detached HEAD.")

    git_output(["remote", "get-url", "origin"])
    return branch, "origin"


def git_release_paths(
    src: Path,
    project_path: Path,
    changelog_path: Path,
) -> list[str]:
    """Return the release-owned paths to stage, relative to the repository."""
    generated_exports = [
        directory / "__init__.py"
        for directory in package_directories(src)
    ]
    paths = [project_path, changelog_path, *generated_exports]
    relative_paths = []

    for path in paths:
        try:
            relative_paths.append(
                path.resolve().relative_to(ROOT).as_posix()
            )
        except ValueError as exc:
            raise ValueError(
                f"Release file is outside the repository: {path}"
            ) from exc

    return sorted(set(relative_paths))


def build_and_validate(output: Path) -> list[Path]:
    """Build fresh distributions and validate metadata."""
    run([
        sys.executable, "-m", "build",
        "--outdir", str(output),
    ])

    artifacts = sorted(
        path for path in output.iterdir()
        if path.name.endswith(".whl")
        or path.name.endswith(".tar.gz")
    )

    wheels = [p for p in artifacts if p.name.endswith(".whl")]
    sdists = [p for p in artifacts if p.name.endswith(".tar.gz")]

    if len(wheels) != 1 or len(sdists) != 1:
        raise RuntimeError(
            "Expected one wheel and one source archive."
        )

    run([
        sys.executable, "-m", "twine", "check",
        *[str(path) for path in artifacts],
    ])

    return artifacts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", type=Path, default=DEFAULT_SRC)
    parser.add_argument("--project-file", type=Path, default=PROJECT_FILE)
    parser.add_argument("--changelog", type=Path, default=CHANGELOG_FILE)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview preparation and release without writing or publishing.",
    )
    args = parser.parse_args()

    try:
        src = args.src.resolve()
        project_path = args.project_file.resolve()
        changelog_path = args.changelog.resolve()

        if not src.is_dir():
            raise NotADirectoryError(f"Source directory not found: {src}")

        git_context = (
            None if args.dry_run else prepare_git_release()
        )

        document = load_project(project_path)
        old_version = current_version(document)

        # Prepare package exports before dependency scanning.
        print("\n== Generating package exports ==")
        map_src(src, dry_run=args.dry_run)

        # Discover dependencies and update project metadata.
        print("\n== Scanning dependencies ==")
        added = update_dependencies(document, src)

        print("\nNew dependencies:", ", ".join(added) if added else "none")

        print("\n+------------------------------------------------------------+")
        print("|                    RELEASE PLANNER                        |")
        print("+------------------------------------------------------------+")
        print(f"  Current version: {old_version}")
        print("  Choose the size of the public change:")
        print("    1. PATCH  - backward-compatible bug fixes or small polish")
        print("    2. MINOR  - backward-compatible features and improvements")
        print("    3. MEDIUM - legacy name; same version bump as MINOR")
        print("    4. MAJOR  - breaking changes that may need migration")

        choice = input("Release type (1-4 or name): ").strip().upper()

        if choice.isdigit():
            index = int(choice)
            if index not in range(1, 5):
                raise ValueError("Select 1, 2, 3, or 4.")
            release_type = RELEASE_TYPES[index - 1]
        else:
            release_type = choice

        if release_type not in RELEASE_TYPES:
            raise ValueError(f"Invalid release type: {release_type}")

        new_version = bump_version(old_version, release_type)
        notes = collect_notes()
        commit_name = collect_commit_name()

        print("\n+----------------------- RELEASE PREVIEW --------------------+")
        print(f"  Version:      {old_version} -> {new_version}")
        print(f"  Release type: {release_type}")
        print(f"  Commit title: {commit_name}")
        print("  Release notes:")
        for note in notes:
            print(f"    - {note}")
        print("+------------------------------------------------------------+")

        if args.dry_run:
            print(
                "\nDry run: no files written, published, committed, or pushed."
            )
            print("New dependency declarations:", added)
            return 0

        if git_context is None:
            raise RuntimeError("Git release context was not prepared.")
        branch, remote = git_context
        release_paths = git_release_paths(
            src,
            project_path,
            changelog_path,
        )

        if not confirm(
            "Write release files, publish to PyPI, then commit and push "
            f"to {remote}/{branch}?"
        ):
            print("Cancelled.")
            return 0

        # Re-load the document and apply all TOML changes together.
        document["project"]["version"] = new_version
        project_path.write_text(
            tomlkit.dumps(document),
            encoding="utf-8",
        )
        update_changelog(changelog_path, new_version, notes)

        print("\n== Building and validating ==")

        with tempfile.TemporaryDirectory(
            prefix="python-release-"
        ) as temp:
            artifacts = build_and_validate(Path(temp))

            for artifact in artifacts:
                print("Validated:", artifact.name)

            print("\nThis will publish to the real PyPI repository.")
            if not confirm(f"Publish {new_version} to PyPI?"):
                print("Upload cancelled. Local changes remain.")
                return 0

            run([
                sys.executable, "-m", "twine", "upload",
                "--repository", "pypi",
                *[str(path) for path in artifacts],
            ])

        print(f"\nSuccessfully published version {new_version} to PyPI.")
        try:
            run(["git", "add", "--", *release_paths])
            run(["git", "commit", "-m", commit_name])
            run(["git", "push", remote, branch])
        except (OSError, subprocess.CalledProcessError, RuntimeError) as exc:
            print(
                "\nPyPI publication succeeded, but the GitHub commit/push "
                f"failed: {exc}\n"
                "Resolve the Git issue, then finish committing and pushing "
                "the release files manually as needed.",
                file=sys.stderr,
            )
            return 1

        print(
            f"Committed '{commit_name}' and pushed to {remote}/{branch}."
        )
        return 0

    except (
        OSError,
        ValueError,
        RuntimeError,
        subprocess.CalledProcessError
    ) as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
