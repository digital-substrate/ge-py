from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QItemSelectionModel
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QWidget, QListWidgetItem

from model.context import Context
from ge import attachments
from ge.data import Graph_GraphKey

from ui_select_graph_dialog import Ui_SelectGraphDialog


@dataclass
class _Item:
    label: str
    graph_key: Graph_GraphKey


class SelectGraphDialog(QDialog):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_SelectGraphDialog()
        self.ui.setupUi(self)

        self._saved_graph_key = Context.instance().graph_key
        self._items: list[_Item] = []

        self._setup_connections()
        self._configure()
        self._configure_graph_selection()

        self.setWindowIcon(QIcon(":/dsviper_components/images/app.png"))
        self.setWindowTitle("Select a Graph")

    def _setup_connections(self):
        self.ui.w_list_widget.itemSelectionChanged.connect(self._item_selection_changed)
        self.ui.w_select_button.clicked.connect(self._select_clicked)
        self.ui.w_cancel_button.clicked.connect(self._cancel_clicked)

    def _configure(self):
        context = Context.instance()
        if not context.store.has_database():
            return

        attachment_getting = context.store.attachment_getting()

        self.ui.w_list_widget.blockSignals(True)
        self.ui.w_list_widget.clear()
        self._items.clear()

        try:
            graph_keys = attachments.graph_graph_description_keys(attachment_getting)
            for graph_key in graph_keys:
                opt = attachments.graph_graph_description_get(attachment_getting, graph_key)
                if not opt:
                    continue
                description = opt.unwrap()
                self._items.append(_Item(label=description.name, graph_key=graph_key))

            self._items.sort(key=lambda item: item.label)

            for item in self._items:
                QListWidgetItem(item.label, self.ui.w_list_widget)

            self.ui.w_count_label.setText(str(len(self._items)))

        except Exception as e:
            print(f"SelectGraphDialog._configure error: {e}")

        self.ui.w_list_widget.blockSignals(False)

    def _configure_graph_selection(self):
        self.ui.w_list_widget.blockSignals(True)
        for i, item in enumerate(self._items):
            if item.graph_key == self._saved_graph_key:
                self.ui.w_list_widget.setCurrentRow(i, QItemSelectionModel.SelectionFlag.SelectCurrent)
                break
        self.ui.w_list_widget.blockSignals(False)

    def _item_selection_changed(self):
        selected_items = self.ui.w_list_widget.selectedItems()
        if not selected_items:
            return

        row = self.ui.w_list_widget.indexFromItem(selected_items[0]).row()
        Context.instance().graph_key = self._items[row].graph_key
        Context.instance().store.notify_state_did_change()

    def _select_clicked(self):
        if self._saved_graph_key != Context.instance().graph_key:
            Context.instance().store.reset_undo_redo()
            Context.instance().store.notify_state_did_change()
        self.accept()

    def _cancel_clicked(self):
        Context.instance().graph_key = self._saved_graph_key
        Context.instance().store.notify_state_did_change()
        self.reject()
