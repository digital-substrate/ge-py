from __future__ import annotations

from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QFrame, QHBoxLayout

from .ui_render import Ui_RenderComponent
from model.context import Context
from dsviper_components.ds_commit_store_notifier import DSCommitStoreNotifier
from render.widget import RenderWidget
from ge.data import Graph_GraphKey, Graph_VertexKey, Graph_EdgeKey


class RenderComponent(QFrame, Ui_RenderComponent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self._context: Context | None = None

        # Create render widget
        self._render_widget = RenderWidget()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._render_widget)
        self.setLayout(layout)

        self._setup_connections()

    def set_context(self, context: Context):
        self._context = context

    def render_widget(self) -> RenderWidget:
        """Get the render widget."""
        return self._render_widget

    # MARK: - Slots

    def _setup_connections(self):
        notifier = DSCommitStoreNotifier.instance()
        notifier.database_did_open.connect(self._store_database_did_open)
        notifier.database_did_close.connect(self._store_database_did_close)
        notifier.state_did_change.connect(self._store_state_did_change)

    def _store_database_did_open(self):
        pass

    def _store_database_did_close(self):
        self._render_widget.reset()

    def _store_state_did_change(self):
        if self._context:
            self._render_widget.set_graph_key(self._context.graph_key)

    # MARK: - Picking

    def pick_vertex(self) -> Graph_VertexKey | None:
        """Pick a vertex at the current cursor position."""
        if self._render_widget.render_graph():
            location = self._render_widget.mapFromGlobal(QCursor.pos())
            return self._render_widget.pick_vertex(location)
        return None

    def pick_edge(self) -> Graph_EdgeKey | None:
        """Pick an edge at the current cursor position."""
        if self._render_widget.render_graph():
            location = self._render_widget.mapFromGlobal(QCursor.pos())
            return self._render_widget.pick_edge(location)
        return None

    def pick_graph(self) -> Graph_GraphKey | None:
        """Pick a graph at the current cursor position."""
        if self._render_widget.render_graph():
            mouse_pos = self._render_widget.mapFromGlobal(QCursor.pos())
            if self._render_widget.rect().contains(mouse_pos):
                return self._render_widget.graph_key()
        return None
