
#!/usr/bin/env python3
"""Generate __init__.py files and explicit __all__ exports for src/."""

from __future__ import annotations

import argparse
import ast
import keyword
import sys
from pathlib import Path


IGNORED_DIRS = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "node_modules",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
    "build",
    "dist",
}

INIT_DOCSTRING = '"""Automatically generated package exports."""'


def is_ignored(path: Path, root: Path) -> bool:
    """Return whether a path contains an ignored directory."""
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        parts = path.parts

    return any(part in IGNORED_DIRS for part in parts)


def python_files(directory: Path, root: Path) -> list[Path]:
    """Return Python modules directly inside a directory."""
    return sorted(
        path
        for path in directory.iterdir()
        if path.is_file()
        and path.suffix == ".py"
        and path.name != "__init__.py"
        and not is_ignored(path, root)
    )


def find_symbols(path: Path) -> list[str]:
    """Find public top-level functions, classes, and constants."""
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (SyntaxError, UnicodeDecodeError, OSError) as exc:
        print(
            f"warning: could not inspect {path}: {exc}",
            file=sys.stderr,
        )
        return []

    symbols: set[str] = set()

    def add(name: str) -> None:
        if (
            not name.startswith("_")
            and not keyword.iskeyword(name)
        ):
            symbols.add(name)

    def inspect_target(target: ast.expr) -> None:
        if isinstance(target, ast.Name):
            # Only uppercase module-level assignments are treated
            # as constants to avoid exporting implementation variables.
            if target.id.isupper() and not target.id.startswith("_"):
                add(target.id)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for element in target.elts:
                inspect_target(element)

    for node in tree.body:
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
            ),
        ):
            add(node.name)

        elif isinstance(node, ast.Assign):
            for target in node.targets:
                inspect_target(target)

        elif isinstance(node, ast.AnnAssign):
            inspect_target(node.target)

    return sorted(symbols)


def package_directories(src: Path) -> list[Path]:
    """Find directories containing Python modules or nested packages."""
    directories: set[Path] = set()

    for current, dirs, files in __import__("os").walk(src):
        current_path = Path(current)
        dirs[:] = sorted(
            name
            for name in dirs
            if name not in IGNORED_DIRS
            and not is_ignored(current_path / name, src)
        )

        if any(
            name.endswith(".py") and name != "__init__.py"
            for name in files
        ):
            directories.add(current_path)

    # Include parents so nested modules can be imported as packages.
    for directory in list(directories):
        current = directory.parent
        while current != src.parent and current.is_relative_to(src):
            directories.add(current)
            if current == src:
                break
            current = current.parent

    return sorted(directories, key=lambda path: (len(path.parts), str(path)))


def module_import(module: str, symbols: list[str]) -> str:
    """Build a relative import statement."""
    if symbols:
        names = ", ".join(symbols)
        return f"from .{module} import {names}"

    return f"from . import {module}"


def generate_init(directory: Path, src: Path) -> str:
    """Generate __init__.py contents with explicit __all__."""
    files = python_files(directory, src)
    package_dirs = set(package_directories(src))

    lines = [INIT_DOCSTRING, ""]
    exports: set[str] = set()

    for file in files:
        module = file.stem
        symbols = find_symbols(file)

        lines.append(module_import(module, symbols))

        if symbols:
            exports.update(symbols)
        else:
            # Expose the module if no public symbols were detected.
            exports.add(module)

    child_packages = sorted(
        child.name
        for child in directory.iterdir()
        if child.is_dir()
        and child in package_dirs
        and not is_ignored(child, src)
    )

    for package in child_packages:
        lines.append(f"from . import {package}")
        exports.add(package)

    if files or child_packages:
        lines.append("")

    lines.append("__all__ = [")
    for name in sorted(exports):
        lines.append(f"    {name!r},")
    lines.extend(("]", ""))

    return "\n".join(lines)


def map_src(src: Path, *, dry_run: bool = False) -> None:
    """Generate package initializers under the given source directory."""
    src = src.resolve()

    if not src.exists():
        raise FileNotFoundError(f"Source directory does not exist: {src}")

    if not src.is_dir():
        raise NotADirectoryError(f"Not a directory: {src}")

    directories = package_directories(src)

    if not directories:
        print(f"No Python packages found in {src}")
        return

    for directory in directories:
        init_file = directory / "__init__.py"
        content = generate_init(directory, src)

        if dry_run:
            print(f"\n### {init_file}")
            print(content)
            continue

        init_file.write_text(content, encoding="utf-8")
        print(f"generated {init_file}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate __init__.py exports for a Python src/ tree."
    )
    parser.add_argument(
        "src",
        nargs="?",
        type=Path,
        default=Path("src"),
        help="Source directory (default: src)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print generated files without modifying anything.",
    )

    args = parser.parse_args()

    try:
        map_src(args.src, dry_run=args.dry_run)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
