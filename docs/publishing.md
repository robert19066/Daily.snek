# Publishing a release

Build and validate distributions locally before uploading. **TestPyPI and PyPI are separate services with separate API tokens.** A token created on one service does not authenticate with the other.

## Build and inspect

From the project root, build the source and wheel distributions:

```powershell
python -m pip install --upgrade build twine
python -m build
python -m twine check dist\dailydotsnek-1.1.0*
```

The PNG used in this README and the MkDocs source are included in the source archive.

## Test on TestPyPI first

Create an API token at [test.pypi.org](https://test.pypi.org/manage/account/token/). Use that **TestPyPI token only** for this upload:

```powershell
python -m twine upload --repository testpypi --username __token__ dist\dailydotsnek-1.1.0*
```

Twine prompts for a password if one has not been configured. Enter the TestPyPI token at the prompt; do not paste it into a command or commit it to the project.

Install from TestPyPI in a clean virtual environment and verify the package:

```powershell
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ dailydotsnek==1.1.0
```

## Publish to PyPI

After validating the TestPyPI release, create or use a separate token from [pypi.org](https://pypi.org/manage/account/token/). Use the **PyPI token only** for the production upload:

```powershell
python -m twine upload --username __token__ dist\dailydotsnek-1.1.0*
```

Never reuse the TestPyPI token for the production upload, or the PyPI token for TestPyPI. Keep both tokens private and revoke any token that has been disclosed.

## Before each release

- Update `project.version` in `pyproject.toml` to a version not already published.
- Update both changelog files.
- Run the unit tests and build validation.
- Check the package name, README rendering, dependencies, and release files.

For CI publishing, use PyPI's trusted publishing where supported, or store narrowly scoped API tokens in the CI secret store. Never put credentials in the repository.

## Automated release helper

From a clean checkout on a branch with an `origin` remote, run:

```powershell
python release.py
```

The interactive release planner asks for the version change, a user-facing summary, categorized features/improvements/fixes/breaking changes and migration guidance, validation performed, and a Git commit title. It previews the version and notes before writing release files. The helper then builds and validates the distributions, asks before publishing to the production PyPI repository, and only after a successful upload commits the release files and pushes the selected branch to `origin`.

The working tree must be clean before starting so unrelated changes cannot be included in the release commit. A successful push to `main` also triggers the repository's GitHub release workflow. Use `python release.py --dry-run` to preview the survey and generated exports without requiring Git credentials or changing, publishing, committing, or pushing anything.
