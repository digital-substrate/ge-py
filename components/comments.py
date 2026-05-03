from __future__ import annotations

import dsviper
from PySide6.QtWidgets import QFrame, QListWidgetItem, QApplication

from .ui_comments import Ui_CommentsComponent
from model.context import Context
from dsviper_components.ds_commit_store_notifier import DSCommitStoreNotifier
from ge import attachments


class CommentsItem(QListWidgetItem):
    """A list widget item that stores its position in the XArray."""

    def __init__(self, text: str, position: dsviper.ValueUUId, parent=None):
        super().__init__(text, parent)
        self.position = position


class CommentsComponent(QFrame, Ui_CommentsComponent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self._context: Context | None = None
        self._setup_connections()
        self._disable_interaction()

    def set_context(self, context: Context):
        self._context = context

    # MARK: - Slots

    def _setup_connections(self):
        # Notifier
        notifier = DSCommitStoreNotifier.instance()
        notifier.database_did_open.connect(self._store_database_did_open)
        notifier.database_did_close.connect(self._store_database_did_close)
        notifier.state_did_change.connect(self._store_state_did_change)

        # Buttons
        self.w_add_button.clicked.connect(self._add_clicked)
        self.w_assign_button.clicked.connect(self._assign_clicked)
        self.w_remove_button.clicked.connect(self._remove_clicked)

    def _store_database_did_open(self):
        self._enable_interaction()

    def _store_database_did_close(self):
        self._disable_interaction()

    def _store_state_did_change(self):
        self._configure()

    def _enable_interaction(self):
        self.setEnabled(True)

    def _disable_interaction(self):
        self.w_list_widget.blockSignals(True)
        self.w_list_widget.clear()
        self.w_list_widget.blockSignals(False)
        self.w_element_line_edit.clear()
        self.setEnabled(False)

    def _add_clicked(self):
        label = self.w_element_line_edit.text()
        if not label:
            return

        selected_items = self.w_list_widget.selectedItems()
        position = dsviper.ValueUUId.INVALID
        if selected_items:
            position = selected_items[0].position

        comment = label
        self._context.store.dispatch(
            f"Insert Comment '{comment}'",
            lambda m: attachments.graph_graph_comments_insert(
                m, self._context.graph_key, position, dsviper.ValueUUId.create(), comment
            )
        )

        self.w_element_line_edit.clear()

        if QApplication.focusWidget():
            QApplication.focusWidget().clearFocus()

    def _assign_clicked(self):
        selected_items = self.w_list_widget.selectedItems()
        if not selected_items:
            return

        label = self.w_element_line_edit.text()
        if not label:
            return

        item = selected_items[0]
        item_label = item.text()
        new_label = label
        item_position = item.position
        self._context.store.dispatch(
            f"Update Comment '{item_label}' to '{new_label}'",
            lambda m: attachments.graph_graph_comments_update(
                m, self._context.graph_key, item_position, new_label
            )
        )

        self.w_element_line_edit.clear()

        if QApplication.focusWidget():
            QApplication.focusWidget().clearFocus()

    def _remove_clicked(self):
        selected_items = self.w_list_widget.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        item_label = item.text()
        item_position = item.position
        self._context.store.dispatch(
            f"Remove Comment '{item_label}'",
            lambda m: attachments.graph_graph_comments_remove(
                m, self._context.graph_key, item_position
            )
        )

        self.w_element_line_edit.clear()

        if QApplication.focusWidget():
            QApplication.focusWidget().clearFocus()

    # MARK: - Configure

    def _configure(self):
        if not self._context:
            return

        attachment_getting = self._context.store.attachment_getting()
        graph_key = self._context.graph_key

        self.w_list_widget.blockSignals(True)
        self.w_list_widget.clear()

        try:
            opt_comments = attachments.graph_graph_comments_get(attachment_getting, graph_key)
            if opt_comments:
                comments = opt_comments.unwrap()
                for position, element in comments.items():
                    CommentsItem(element, position, self.w_list_widget)
        except Exception as e:
            print(f"CommentsComponent._configure error: {e}")

        self.w_list_widget.blockSignals(False)
