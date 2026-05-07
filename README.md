# Graph Editor (ge-py)

A PySide6 desktop application for graph database visualization and editing, built on the Viper persistence layer.

## Documentation

Full documentation: https://docs.digitalsubstrate.io/reference-apps/ge-py.html

Part of the [DevKit ecosystem](https://docs.digitalsubstrate.io/).

## Prerequisites

- Python 3.14+

## Installation

```bash
pip install -r requirements.txt
```

This installs `dsviper` (the Viper Python binding, from [PyPI](https://pypi.org/project/dsviper/)) along with `PySide6`.

## Usage

Run the application:

```bash
python3 graph_editor.py
```

Open an existing database:

```bash
python3 graph_editor.py path/to/database.db
```

## Building

Generated Qt files (`ui_*.py` and `resources_rc.py`) are committed,
so a fresh clone runs immediately. After editing any `*.ui` or
`resources.qrc`, regenerate with:

```bash
python3 dev/build.py
```

The shared `dsviper_components/` package is sourced from
`dsviper-components`. To pull updates from
that source repository (a maintenance task, not a contributor task):

```bash
python3 dev/sync_dsviper_components.py    # refresh dsviper_components/ from sibling
python3 dev/build.py                       # then regenerate ui_*.py / resources_rc.py
git diff dsviper_components resources_rc.py     # review the bump
```

`PySide6` is pinned in `requirements.txt` to guarantee reproducible
regeneration across contributors.

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE).

## Runtime dependency

At runtime, this project depends on the `dsviper` Python package
(distributed on PyPI), which is **proprietary** (PyPI classifier
`License :: Other/Proprietary License`). See
[https://pypi.org/project/dsviper/](https://pypi.org/project/dsviper/)
for the package's licensing posture and contact information.
