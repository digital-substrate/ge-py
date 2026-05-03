from __future__ import annotations

from PySide6.QtWidgets import QApplication, QWidget

from dsviper_components.ds_commit_store_notifier import DSCommitStoreNotifier
from .ui_title import Ui_TitleComponent
from model.context import Context
import ge.attachments as attachments


class TitleComponent(QWidget, Ui_TitleComponent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self._context: Context | None = None
        self._setup_connections()
        self._disable_interaction()

    def set_context(self, context: Context):
        self._context = context

    def _setup_connections(self):
        notifier = DSCommitStoreNotifier.instance()
        notifier.database_did_open.connect(self._store_database_did_open)
        notifier.database_did_close.connect(self._store_database_did_close)
        notifier.state_did_change.connect(self._store_state_did_change)

        self.w_title_line_edit.returnPressed.connect(self._title_return_pressed)

    def _store_database_did_open(self):
        self._enable_interaction()

    def _store_database_did_close(self):
        self._disable_interaction()

    def _store_state_did_change(self):
        self._configure()

    def _title_return_pressed(self):
        new_label = self.w_title_line_edit.text()

        if new_label != self._label:
            label = f"Set Title To '{new_label}'"
            self._context.store.dispatch(label,
                                         lambda m: attachments.graph_graph_description_set_name(m,
                                                                                                self._context.graph_key,
                                                                                                new_label))

        if QApplication.focusWidget():
            QApplication.focusWidget().clearFocus()

    def _enable_interaction(self):
        self.setEnabled(True)

    def _disable_interaction(self):
        self._label = ""
        self.w_title_line_edit.clear()
        self.setEnabled(False)

    def _configure(self):
        graph_key = self._context.graph_key
        attachment_getting = self._context.store.attachment_getting()

        self.w_title_line_edit.blockSignals(True)
        try:
            opt = attachments.graph_graph_description_get(attachment_getting, graph_key)
            if opt:
                description = opt.unwrap()
                self._label = description.name
                self.w_title_line_edit.setText(self._label)
        except Exception as e:
            print(f"TitleComponent._configure error: {e}")
        self.w_title_line_edit.blockSignals(False)
