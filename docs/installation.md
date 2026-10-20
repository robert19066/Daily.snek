# Installation

## Requirements

- Python **3.10 or later**
- A daily.dev API token for authenticated endpoints

The package installs its `requests` and `python-dotenv` dependencies automatically.

## Install from PyPI

```console
python -m pip install dailydotsnek
```

## Configure your API token

For local development, create a `.env` file in the directory from which your program runs:

```dotenv
DAILY_DEV_KEY=your_daily_dev_api_token
```

`AutoApiToken` loads this value with `python-dotenv`. You can instead set `DAILY_DEV_KEY` in your process environment, or use `ManualApiToken` to supply the value yourself.

!!! warning "Keep credentials private"
    Add `.env` to `.gitignore`. Do not commit, publish, or log your API token.

## Install from a source checkout

From the project root, use an editable install:

```console
python -m pip install -e .
```

To preview the documentation site:

```console
python -m pip install mkdocs-material
python -m mkdocs serve
```
