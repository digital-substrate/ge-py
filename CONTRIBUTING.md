# Contributing to Graph Editor (ge-py)

Thanks for your interest in contributing.

## Reporting issues

Use [GitHub Issues](https://github.com/digital-substrate/ge-py/issues) and pick the appropriate template (bug report or feature request).

## Submitting pull requests

1. Fork the repository and create a feature branch from `main`
2. Make your changes (see "Running locally" below)
3. Verify the app still launches and the flows you touched still work
4. Open a pull request with a clear description of what changed and why

## Running locally

Requires Python 3.14+.

```bash
pip install -r requirements.txt          # PySide6 and deps
pip install dsviper                      # Viper Python binding
python3 graph_editor.py                  # Launch
python3 graph_editor.py path/to/db.db    # Open an existing database
```

Database server (for remote sync):

```bash
python3 commit_database_server.py [-v] [--host HOST] [--port PORT] database.db
```

## Regenerating Qt artifacts

```bash
pyside6-uic some_component.ui -o ui_some_component.py   # .ui → Python
pyside6-rcc resources.qrc -o resources_rc.py             # Qt resources
```

## Architecture note

This app depends on `dsviper`, the pre-built Viper Python binding (distributed on PyPI). All persistence and commit operations go through it — don't attempt to port Viper.

## License

This project is licensed under the MIT License (see [LICENSE](LICENSE)). By submitting a pull request, you agree that your contribution is provided under the same license (inbound = outbound). No CLA is required.
