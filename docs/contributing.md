# Contributing

Thanks for considering contributing to dailydotsnek! This project welcomes improvements to documentation, bug fixes, and new features.

Guidelines

- Open an issue to discuss larger changes before implementing.
- Fork the repo and create a topic branch for your change.
- Keep changes small and focused; write tests for new behaviors.

Code style

- Target Python 3.10+.
- Use type hints where helpful.
- Keep public API backwards-compatible.

Testing

Install the package in editable mode, then run the test suite:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

Documentation

Docs are written in Markdown and built with MkDocs. To preview locally:

```bash
python -m pip install mkdocs-material
python -m mkdocs serve
```
