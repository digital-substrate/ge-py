from __future__ import annotations

from PySide6.QtWidgets import QFrame, QTreeWidgetItem, QApplication

from .ui_tags import Ui_TagsComponent
from model.context import Context
from dsviper_components.ds_commit_store_notifier import DSCommitStoreNotifier
from ge import attachments
from ge.data import Map_string_to_string, Set_string


class TagsComponent(QFrame, Ui_TagsComponent):
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

        # Tree widget
        self.w_tree_widget.itemSelectionChanged.connect(self._item_selection_changed)

        # Buttons
        self.w_set_button.clicked.connect(self._set_clicked)
        self.w_update_button.clicked.connect(self._update_clicked)
        self.w_unset_button.clicked.connect(self._unset_clicked)

    def _store_database_did_open(self):
        self._enable_interaction()

    def _store_database_did_close(self):
        self._disable_interaction()

    def _store_state_did_change(self):
        self._configure()

    def _item_selection_changed(self):
        selected_items = self.w_tree_widget.selectedItems()

        self.w_set_button.setEnabled(len(selected_items) <= 1)
        self.w_update_button.setEnabled(len(selected_items) <= 1)
        self.w_unset_button.setEnabled(len(selected_items) >= 1)

        if len(selected_items) == 1:
            item = selected_items[0]
            self.w_key_line_edit.setText(item.text(0))
            self.w_value_line_edit.setText(item.text(1))
        elif len(selected_items) > 1:
            self.w_key_line_edit.clear()
            self.w_value_line_edit.clear()

    def _set_clicked(self):
        key = self.w_key_line_edit.text()
        value = self.w_value_line_edit.text()
        if not key or not value:
            return

        if QApplication.focusWidget():
            QApplication.focusWidget().clearFocus()

        self._context.store.dispatch(
            f"Set Tag '{key}':'{value}'",
            lambda m: attachments.graph_graph_tags_union(
                m, self._context.graph_key, Map_string_to_string({key: value})
            )
        )

    def _update_clicked(self):
        key = self.w_key_line_edit.text()
        value = self.w_value_line_edit.text()
        if not key or not value:
            return

        if QApplication.focusWidget():
            QApplication.focusWidget().clearFocus()

        self._context.store.dispatch(
            f"Update Tag '{key}':'{value}'",
            lambda m: attachments.graph_graph_tags_update(
                m, self._context.graph_key, Map_string_to_string({key: value})
            )
        )

    def _unset_clicked(self):
        selected_items = self.w_tree_widget.selectedItems()
        if not selected_items:
            return

        keys = set()
        for item in selected_items:
            keys.add(item.text(0))

        if QApplication.focusWidget():
            QApplication.focusWidget().clearFocus()

        self._context.store.dispatch(
            "Unset Tag",
            lambda m: attachments.graph_graph_tags_subtract(
                m, self._context.graph_key, Set_string(keys)
            )
        )

    # MARK: - Interaction

    def _enable_interaction(self):
        self.setEnabled(True)

    def _disable_interaction(self):
        self.w_tree_widget.blockSignals(True)
        self.w_tree_widget.clear()
        self.w_tree_widget.blockSignals(False)

        self.w_key_line_edit.clear()
        self.w_value_line_edit.clear()

        self.setEnabled(False)

    # MARK: - Configure

    def _configure(self):
        if not self._context:
            return

        attachment_getting = self._context.store.attachment_getting()
        graph_key = self._context.graph_key

        self.w_unset_button.setEnabled(False)
        self.w_tree_widget.blockSignals(True)
        self.w_tree_widget.clear()

        try:
            opt_tags = attachments.graph_graph_tags_get(attachment_getting, graph_key)
            if opt_tags:
                tags = opt_tags.unwrap()
                for key, value in tags.items():
                    QTreeWidgetItem(self.w_tree_widget, [key, value])
        except Exception as e:
            print(f"TagsComponent._configure error: {e}")

        self.w_tree_widget.blockSignals(False)
