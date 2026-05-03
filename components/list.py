from __future__ import annotations

from typing import Union

from PySide6.QtCore import QItemSelectionModel
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QListWidgetItem

from .ui_list import Ui_ListComponent
from model.context import Context
from dsviper_components.ds_commit_store_notifier import DSCommitStoreNotifier
from ge import attachments
from ge.data import (
    Graph_VertexKey,
    Graph_EdgeKey,
    Set_Graph_VertexKey,
    Set_Graph_EdgeKey,
)
from model import selection_mixed
from list.element import ListVertex, ListEdge
from list.vertex_widget import ListVertexWidget
from list.edge_widget import ListEdgeWidget
from graph_sorted_by_value import GraphSortedByValue


ListElement = Union[ListVertex, ListEdge]


class ListComponent(QFrame, Ui_ListComponent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self._context: Context | None = None
        self._elements: list[ListElement] = []
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

        # List widget
        self.w_list_widget.itemSelectionChanged.connect(self._item_selection_changed)

    def _store_database_did_open(self):
        self._enable_interaction()

    def _store_database_did_close(self):
        self._disable_interaction()

    def _store_state_did_change(self):
        self._configure()

    def _item_selection_changed(self):
        selected_items = self.w_list_widget.selectedItems()

        selected_vertices = Set_Graph_VertexKey()
        selected_edges = Set_Graph_EdgeKey()

        for item in selected_items:
            row = self.w_list_widget.indexFromItem(item).row()
            if row < len(self._elements):
                element = self._elements[row]

                if isinstance(element, ListVertex):
                    selected_vertices.add(element.vertex_key)
                elif isinstance(element, ListEdge):
                    selected_edges.add(element.edge_key)

        self._context.store.dispatch(
            "Set Selection",
            lambda m: selection_mixed.set_selection(
                m, self._context.graph_key, selected_vertices, selected_edges
            )
        )

    # MARK: - Interaction

    def _enable_interaction(self):
        self.setEnabled(True)

    def _disable_interaction(self):
        self.w_list_widget.blockSignals(True)
        self.w_list_widget.clear()
        self.w_list_widget.blockSignals(False)
        self.setEnabled(False)

    # MARK: - Configure

    def _configure(self):
        if not self._context:
            return

        lw = self.w_list_widget
        self._elements = self._build()

        # Save scroll position
        scroll_value = lw.verticalScrollBar().value()

        lw.blockSignals(True)
        lw.clear()

        # Build items
        for element in self._elements:
            item = QListWidgetItem(lw)

            widget = None
            if isinstance(element, ListVertex):
                widget = ListVertexWidget(element)
            elif isinstance(element, ListEdge):
                widget = ListEdgeWidget(element)

            if widget:
                item.setSizeHint(widget.sizeHint())
                lw.setItemWidget(item, widget)

        # Build selection
        selected_rows = self._build_selection()
        if selected_rows:
            lw.setCurrentRow(selected_rows[0], QItemSelectionModel.SelectionFlag.SelectCurrent)

        for row in selected_rows:
            item = lw.item(row)
            if item:
                item.setSelected(True)

        lw.blockSignals(False)

        # Restore scroll position
        lw.verticalScrollBar().setValue(scroll_value)

    def _build(self) -> list[ListElement]:
        """Build the list of elements from the graph."""
        if not self._context:
            return []

        attachment_getting = self._context.store.attachment_getting()
        graph_key = self._context.graph_key

        result: list[ListElement] = []

        try:
            sorted_graph = GraphSortedByValue.build(attachment_getting, graph_key)

            # Get topology vertex keys
            vertex_keys = Set_Graph_VertexKey()
            opt_topology = attachments.graph_graph_topology_get(attachment_getting, graph_key)
            if opt_topology:
                vertex_keys = opt_topology.unwrap().vertex_keys

            for sorted_vertex in sorted_graph.sorted_vertices():
                list_vertex = self._create_list_vertex(
                    attachment_getting, sorted_vertex.vertex_key, vertex_keys
                )
                result.append(list_vertex)

                for sorted_edge in sorted_vertex.edges:
                    list_edge = self._create_list_edge(
                        attachment_getting,
                        sorted_edge.edge_key,
                        sorted_vertex.vertex_key,
                        sorted_edge.vertex_key,
                        vertex_keys
                    )
                    result.append(list_edge)

        except Exception as e:
            print(f"ListComponent._build error: {e}")

        return result

    def _build_selection(self) -> list[int]:
        """Build the list of selected row indices."""
        if not self._context:
            return []

        result: list[int] = []
        attachment_getting = self._context.store.attachment_getting()
        graph_key = self._context.graph_key

        try:
            vertex_keys = Set_Graph_VertexKey()
            edge_keys = Set_Graph_EdgeKey()
            opt_selection = attachments.graph_graph_selection_get(attachment_getting, graph_key)
            if opt_selection:
                selection = opt_selection.unwrap()
                vertex_keys = selection.vertex_keys
                edge_keys = selection.edge_keys

            for i, element in enumerate(self._elements):
                if isinstance(element, ListVertex):
                    if element.vertex_key in vertex_keys:
                        result.append(i)
                elif isinstance(element, ListEdge):
                    if element.edge_key in edge_keys:
                        result.append(i)

        except Exception as e:
            print(f"ListComponent._build_selection error: {e}")

        return result

    def _create_list_vertex(self, getting, vertex_key: Graph_VertexKey,
                            vertex_keys: Set_Graph_VertexKey) -> ListVertex:
        """Create a ListVertex from a vertex key."""
        opt_attrs = attachments.graph_vertex_visual_attributes_get(getting, vertex_key)
        if opt_attrs:
            attrs = opt_attrs.unwrap()
            value = attrs.value
            color = QColor(
                int(attrs.color.red * 255),
                int(attrs.color.green * 255),
                int(attrs.color.blue * 255)
            )
        else:
            value = -1
            color = QColor(255, 0, 0)

        exists = vertex_key in vertex_keys
        return ListVertex.make(vertex_key, value, color, exists)

    def _create_list_edge(self, getting, edge_key: Graph_EdgeKey,
                          va_key: Graph_VertexKey, vb_key: Graph_VertexKey,
                          vertex_keys: Set_Graph_VertexKey) -> ListEdge:
        """Create a ListEdge from an edge key."""
        va = self._create_list_vertex(getting, va_key, vertex_keys)
        vb = self._create_list_vertex(getting, vb_key, vertex_keys)
        return ListEdge.make(edge_key, va, vb)
