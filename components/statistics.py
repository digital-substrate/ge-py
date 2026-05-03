from __future__ import annotations

from PySide6.QtWidgets import QFrame, QWidget

from dsviper_components.ds_commit_store_notifier import DSCommitStoreNotifier
from .ui_statistics import Ui_StatisticsComponent
from model.context import Context
import ge.attachments as attachments
import ge.data as data

class StatisticsComponent(QWidget, Ui_StatisticsComponent):
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

    def _store_database_did_open(self):
        self._enable_interaction()

    def _store_database_did_close(self):
        self._disable_interaction()

    def _store_state_did_change(self):
        self._configure()

    def _enable_interaction(self):
        self.setEnabled(True)

    def _disable_interaction(self):
        self.w_vertices_label.setText("-")
        self.w_edges_label.setText("-")
        self.w_min_max_label.setText("-")
        self.setEnabled(False)

    def _configure(self):
        attachment_getting = self._context.store.attachment_getting()
        graph_key = self._context.graph_key

        vertex_keys = data.Set_Graph_VertexKey()
        edge_keys = data.Set_Graph_EdgeKey()
        if opt := attachments.graph_graph_topology_get(attachment_getting, graph_key):
            topology = opt.unwrap()
            vertex_keys = topology.vertex_keys
            edge_keys = topology.edge_keys

        selected_vertex_keys = data.Set_Graph_VertexKey()
        selected_edge_keys = data.Set_Graph_EdgeKey()
        if opt := attachments.graph_graph_selection_get(attachment_getting, graph_key):
            selection = opt.unwrap()
            selected_vertex_keys = selection.vertex_keys
            selected_edge_keys = selection.edge_keys

        self.w_vertices_label.setText(f"{len(selected_vertex_keys):03d}/{len(vertex_keys):03d}")
        self.w_edges_label.setText(f"{len(selected_edge_keys):03d}/{len(edge_keys):03d}")

        values = [opt.unwrap().value for vertex_key in vertex_keys
                  if (opt := attachments.graph_vertex_visual_attributes_get(attachment_getting, vertex_key))]

        if values:
            self.w_min_max_label.setText(f"{min(values):03d}/{max(values):03d}")
        else:
            self.w_min_max_label.setText("-")

