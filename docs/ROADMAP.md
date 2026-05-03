# Graph Editor Python - Roadmap

## Project Context

Graph Editor Python (ge-py) is a port of the Objective-C/AppKit reference implementation to Python/PySide6, aiming for
cross-platform support without compilation.

### Evolution

```
Objective-C/AppKit (reference)     Qt/C++ (ge-qt)           Python/PySide6 (ge-py)
├── NSTableView animations    →    ├── Cross-platform   →   ├── Cross-platform
├── Python Editor                  ├── No Python Editor     ├── No Python Editor (TODO)
├── Python embedded                ├── No embedded          ├── Native Python
└── macOS only                     └── Requires compilation └── No compilation
```

## Current Status

### Completed (100%)

| Component            | Files            | LOC    | Status     |
|----------------------|------------------|--------|------------|
| Document Browser     | ds_documents*.py | ~1,500 | ✓ Complete |
| Commit History       | ds_commits*.py   | ~700   | ✓ Complete |
| Definition Inspector | ds_inspect*.py   | ~180   | ✓ Complete |
| UI Components        | components/*.py  | ~800   | ✓ Complete |
| Render Engine        | render/*.py      | ~600   | ✓ Complete |
| Model Layer          | model/*.py       | ~500   | ✓ Complete |

### Remaining Work

| Component              | Priority | Estimated Effort |
|------------------------|----------|------------------|
| Python Script Editor   | HIGH     | 2-3 weeks        |
| DSM Syntax Highlighter | MEDIUM   | 3-5 days         |
| Transient Controls     | LOW      | 3-5 days         |
| Animations             | LOW      | 1-2 weeks        |

---

## Phase 1: Python Script Editor

### Objective

Port the Python script editor from Objective-C DSComponent to Python/PySide6.

### Existing Python Libraries to Consider

Before implementing from scratch, evaluate these mature solutions:

#### Option A: QScintilla (Recommended)

[QScintilla](https://qscintilla.com/) is a port of the Scintilla editor to Qt.

**Features included:**

- Syntax highlighting (Python, 70+ languages)
- Line numbers
- Code folding
- Auto-completion
- Brace matching
- Error indicators

**Installation:**

```bash
pip install PyQt6-QScintilla
# Note: Official bindings are PyQt6, may need adaptation for PySide6
```

**Pros:**

- Battle-tested (used by many IDEs)
- All features built-in
- Minimal code required

**Cons:**

- PyQt6 bindings (not PySide6 native)
- Large dependency
- Less customizable for Viper types

#### Option B: Pygments + QSyntaxHighlighter

[Pygments](https://pygments.org/) is a Python syntax highlighting library.

**Features:**

- 500+ language lexers
- Python lexer with full syntax support
- Themeable

**Integration approach:**

```python
from pygments.lexers import PythonLexer
from pygments import lex
from PySide6.QtGui import QSyntaxHighlighter


class PygmentsHighlighter(QSyntaxHighlighter):
    def highlightBlock(self, text):
        tokens = lex(text, PythonLexer())
        for token_type, token_value in tokens:
            # Apply formatting based on token_type
            pass
```

**Pros:**

- Pure Python
- PySide6 native
- Highly customizable (can add Viper types)

**Cons:**

- Need to implement line numbers separately
- Need to implement auto-completion separately

#### Option C: PyQCodeEditor

[PyQCodeEditor](https://github.com/zimolab/PyQCodeEditor) is a ready-to-use code editor widget.

**Features:**

- Line numbers
- Syntax highlighting
- Works with PySide6 (via qtpy)

**Pros:**

- Quick integration
- Maintained

**Cons:**

- May need customization for Viper types

### Recommendation

**Hybrid approach:**

1. Use **Pygments** for syntax highlighting (customizable for Viper types)
2. Implement **line numbers** with QPlainTextEdit (simple, ~50 LOC)
3. Use **jedi** or custom completion for auto-completion

This gives full control while leveraging mature lexing.

### Components to Implement

| Component                 | Objective-C       | Python Approach                |
|---------------------------|-------------------|--------------------------------|
| DSPythonSyntaxHighlighter | 560 LOC, 28 regex | Pygments + custom Viper tokens |
| DSLineNumberRulerView     | 69 LOC            | QPlainTextEdit with line area  |
| DSPythonCompletionBuffer  | 64 LOC            | jedi or custom                 |
| DSPythonErrorManager      | 63 LOC            | Parse stderr, navigate         |
| DSPythonLexicon           | 60 LOC            | Pygments handles this          |

### Estimated Effort with Libraries

| Task                | Without Libraries | With Libraries |
|---------------------|-------------------|----------------|
| Syntax Highlighting | 3-4 days          | 1 day          |
| Line Numbers        | 1-2 days          | 0.5 day        |
| Auto-completion     | 2-3 days          | 1 day          |
| Error Navigation    | 1-2 days          | 1 day          |
| **Total**           | **7-11 days**     | **3-4 days**   |

---

## Phase 2: DSM Editor

### Objective

Syntax highlighting for DSM (Digital Substrate Model) language files.

### Approach

Create a custom Pygments lexer for DSM syntax, then reuse the same highlighter infrastructure from Phase 1.

```python
from pygments.lexer import RegexLexer


class DSMLexer(RegexLexer):
    name = 'DSM'
    tokens = {
        'root': [
            (r'\b(concept|attachment|collection)\b', Keyword),
            # ... DSM-specific patterns
        ]
    }
```

**Estimated Effort:** 2-3 days

---

## Phase 3: Transient Controls

### Objective

Real-time feedback controls for vertex editing (color, position, value).

### Components

| Control              | Objective-C                 | Python/PySide6                   |
|----------------------|-----------------------------|----------------------------------|
| DSTransientSlider    | QSlider + signal on move    | QSlider.sliderMoved              |
| DSTransientStepper   | QSpinBox + signal           | QSpinBox.valueChanged            |
| DSTransientColorWell | QColorDialog + live preview | QColorDialog.currentColorChanged |

### Note

These are mostly already implemented in `vertex_component.py`. Review for completeness.

**Estimated Effort:** 1-2 days (review + polish)

---

## Phase 4: Animations (Optional)

### Objective

Bring the polish of NSTableView animations to PySide6.

### Challenges

Qt doesn't have built-in table animations like NSTableView. Options:

1. **QPropertyAnimation** - Animate row insertion/deletion
2. **QGraphicsView** - Custom animated list
3. **QML** - Use Qt Quick for fluid animations

### Recommendation

Defer to later. Focus on functionality first.

**Estimated Effort:** 1-2 weeks (if pursued)

---

## Timeline Summary

| Phase | Description          | Effort    | Priority |
|-------|----------------------|-----------|----------|
| 1     | Python Script Editor | 3-4 days  | HIGH     |
| 2     | DSM Editor           | 2-3 days  | MEDIUM   |
| 3     | Transient Controls   | 1-2 days  | LOW      |
| 4     | Animations           | 1-2 weeks | OPTIONAL |

**Total estimated effort: 1-2 weeks** (excluding animations)

---

## References

- [QScintilla](https://qscintilla.com/)
- [Pygments](https://pygments.org/)
- [PyQCodeEditor](https://github.com/zimolab/PyQCodeEditor)
- [Qt Syntax Highlighter Example](https://doc.qt.io/qtforpython-6/examples/example_widgets_richtext_syntaxhighlighter.html)
- [jedi - Python autocompletion](https://github.com/davidhalter/jedi)
