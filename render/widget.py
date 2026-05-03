from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QColor, QMouseEvent, QGuiApplication
from PySide6.QtWidgets import QWidget

from model.context import Context
from dsviper_components.ds_commit_store_notifier import DSCommitStoreNotifier
from transient_notifier import TransientNotifier
from ge.data import Graph_GraphKey, Graph_VertexKey, Graph_EdgeKey, Graph_Position
from ge import attachments
from .graph import RenderGraph
from .vertex import RenderVertex
from . import graph_builder
import colors

from model import selection_vertices
from model import selection_edges
from model import selection_mixed
from model import vertex as model_vertex
from model import edge as model_edge
from model import random as model_random
from model import tools


class RenderWidget(QWidget):
    """Widget for rendering the graph visualization."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._graph_key: Optional[Graph_GraphKey] = None
        self._render_graph: Optional[RenderGraph] = None
        self._is_drag_canceled = False

        self._setup_connections()

    def _setup_connections(self):
        transient_notifier = TransientNotifier.instance()
        transient_notifier.vertex_value_changed.connect(self._vertex_value_changed)
        transient_notifier.vertex_position_changed.connect(self._vertex_position_changed)
        transient_notifier.vertex_color_changed.connect(self._vertex_color_changed)

    def reset(self):
        """Reset the render widget state."""
        self._render_graph = None
        self.update()

    def set_graph_key(self, graph_key: Graph_GraphKey):
        """Set the graph key to render."""
        context = Context.instance()
        if context and context.store.has_database():
            attachment_getting = context.store.attachment_getting()
            try:
                graph = graph_builder.build(attachment_getting, graph_key)
                self._graph_key = graph_key
                self._render_graph = graph
            except Exception:
                pass
        else:
            self._render_graph = None

        self.update()

    def graph_key(self) -> Optional[Graph_GraphKey]:
        """Get the current graph key."""
        return self._graph_key

    def render_graph(self) -> Optional[RenderGraph]:
        """Get the render graph."""
        return self._render_graph

    def paintEvent(self, event):
        """Paint the widget."""
        if not self._render_graph:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.fillRect(self.rect(), colors.background())
            return

        self._render_graph.draw(self)

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events."""
        context = Context.instance()
        if not context or not context.store.has_database():
            return

        attachment_getting = context.store.attachment_getting()

        modifiers = QGuiApplication.keyboardModifiers()
        is_shift_pressed = bool(modifiers & Qt.KeyboardModifier.ShiftModifier)
        is_control_pressed = bool(modifiers & Qt.KeyboardModifier.ControlModifier)
        is_alt_pressed = bool(modifiers & Qt.KeyboardModifier.AltModifier)

        self._is_drag_canceled = False

        location = event.pos()
        vertex = self._render_graph.pick_vertex(QPointF(location))

        if vertex:
            if is_control_pressed:
                return
            elif is_shift_pressed:
                if not self._render_graph.is_selected_vertex(vertex):
                    context.store.dispatch(
                        f"Add Vertex '{vertex.label()}' To Selection",
                        lambda m: selection_vertices.combine(m, self._graph_key, vertex.vertex_key, True)
                    )
                return
            elif is_alt_pressed:
                if self._render_graph.is_selected_vertex(vertex):
                    context.store.dispatch(
                        f"Remove Vertex '{vertex.label()}' From Selection",
                        lambda m: selection_vertices.combine(m, self._graph_key, vertex.vertex_key, False)
                    )
                return
            else:
                if not (len(self._render_graph.selected_vertex_keys) == 1 and
                        self._render_graph.is_selected_vertex(vertex) and
                        not self._render_graph.has_selected_edges()):
                    context.store.dispatch(
                        f"Set Vertex Selection To '{vertex.label()}'",
                        lambda m: selection_vertices.select(m, self._graph_key, vertex.vertex_key)
                    )
                return

        edge = self._render_graph.pick_edge(self.rect(), QPointF(location))
        if edge:
            edge_label = tools.safe_edge_label(attachment_getting, edge.edge_key)
            if is_control_pressed:
                return
            elif is_shift_pressed:
                if not self._render_graph.is_selected_edge(edge):
                    context.store.dispatch(
                        f"Add Edge '{edge_label}' To Selection",
                        lambda m: selection_edges.combine(m, self._graph_key, edge.edge_key, True)
                    )
                return
            elif is_alt_pressed:
                if self._render_graph.is_selected_edge(edge):
                    context.store.dispatch(
                        f"Remove Edge '{edge_label}' From Selection",
                        lambda m: selection_edges.combine(m, self._graph_key, edge.edge_key, False)
                    )
                return
            else:
                if not (len(self._render_graph.selected_edge_keys) == 1 and
                        self._render_graph.is_selected_edge(edge) and
                        not self._render_graph.has_selected_vertices()):
                    context.store.dispatch(
                        f"Set Selection To Edge '{edge_label}'",
                        lambda m: selection_edges.select(m, self._graph_key, edge.edge_key)
                    )
                return

        if is_control_pressed:
            value = tools.next_vertex_value(attachment_getting, self._render_graph.graph_key)
            label = f"New Vertex '{value}'"
            position = Graph_Position()
            position.x = location.x()
            position.y = self.height() - location.y()
            color = model_random.make_color()
            context.store.dispatch(
                label,
                lambda m: model_vertex.add(m, self._graph_key, value, position, color)
            )
            return

        if is_shift_pressed:
            return

        if self._render_graph.has_selected_edges() or self._render_graph.has_selected_vertices():
            context.store.dispatch(
                "Deselect All",
                lambda m: selection_mixed.deselect_all(m, self._graph_key)
            )
            return

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events."""
        if not self._render_graph:
            return
        if self._is_drag_canceled:
            return

        location = QPointF(event.pos())
        modifiers = QGuiApplication.keyboardModifiers()
        is_control_pressed = bool(modifiers & Qt.KeyboardModifier.ControlModifier)
        is_alt_pressed = bool(modifiers & Qt.KeyboardModifier.AltModifier)

        if is_control_pressed or self._render_graph.connector_vertex_key:
            self._drag_connector_at_location(location)
        elif self._render_graph.has_selection():
            if not self._render_graph.has_vertex_to_move():
                if is_alt_pressed:
                    self._render_graph.move_copy_start(location)
                else:
                    self._render_graph.move_start(location)

            self._render_graph.move_drag(location)
            TransientNotifier.instance().notify_vertices_move(
                self._render_graph.interactive_vertex_keys,
                self._render_graph.interactive_drag_offset
            )

            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release events."""
        context = Context.instance()
        if not self._render_graph:
            return
        if self._is_drag_canceled:
            return

        attachment_getting = context.store.attachment_getting()

        connector_vertex_key = self._render_graph.connector_vertex_key
        picked_vertex = self._render_graph.pick_vertex(QPointF(event.pos()))

        if connector_vertex_key and picked_vertex and picked_vertex.vertex_key != connector_vertex_key:
            if not self._render_graph.has_edge(picked_vertex.vertex_key, connector_vertex_key):
                edge_label = tools.safe_edge_label_from_vertices(attachment_getting, picked_vertex.vertex_key, connector_vertex_key)
                context.store.dispatch(
                    f"New Edge '{edge_label}'",
                    lambda m: model_edge.add(m, self._graph_key, picked_vertex.vertex_key, connector_vertex_key)
                )

        if self._render_graph.interactive_vertex_keys:
            x = int(self._render_graph.interactive_drag_offset.x())
            y = int(self._render_graph.interactive_drag_offset.y())
            import math
            length = math.sqrt(x * x + y * y)
            offset = Graph_Position()
            offset.x = x
            offset.y = -y
            s_offset = f" By ({x},{y})"

            if self._render_graph.move_copy_data:
                if length > 30:
                    from model import script_move_copy
                    move_copy_data = self._render_graph.move_copy_data
                    graph_key = self._graph_key
                    context.store.dispatch(
                        f"Move/Copy Selection{s_offset}",
                        lambda m: script_move_copy.run(m, graph_key, move_copy_data, offset)
                    )
            else:
                from model import graph_vertices
                context.store.dispatch(
                    f"Move Selection{s_offset}",
                    lambda m: graph_vertices.move(m, self._render_graph.interactive_vertex_keys, offset)
                )

        self._render_graph.move_end()
        self.update()

    def _drag_connector_at_location(self, location: QPointF):
        """Drag the connector to the given location."""
        if not self._render_graph:
            return

        if not self._render_graph.connector_vertex_key:
            self._render_graph.pick_connector_vertex(location)

        if self._render_graph.connector_vertex_key:
            self._render_graph.interactive_start_location = location
            self.update()

    def pick_vertex(self, location) -> Optional[Graph_VertexKey]:
        """Pick a vertex at the given location."""
        if self._render_graph:
            vertex = self._render_graph.pick_vertex(QPointF(location))
            if vertex:
                return vertex.vertex_key
        return None

    def pick_edge(self, location) -> Optional[Graph_EdgeKey]:
        """Pick an edge at the given location."""
        if self._render_graph:
            edge = self._render_graph.pick_edge(self.rect(), QPointF(location))
            if edge:
                return edge.edge_key
        return None

    # MARK: - Transient Notification

    def _vertex_value_changed(self, key: Graph_VertexKey, value: int):
        if self._render_graph:
            vertex = self._render_graph.vertex_map.get(key)
            if vertex:
                vertex.value = value
                self.update()

    def _vertex_color_changed(self, key: Graph_VertexKey, color: QColor):
        if self._render_graph:
            vertex = self._render_graph.vertex_map.get(key)
            if vertex:
                vertex.color = color
                self.update()

    def _vertex_position_changed(self, key: Graph_VertexKey, position: QPointF):
        if self._render_graph:
            vertex = self._render_graph.vertex_map.get(key)
            if vertex:
                vertex.position = position
                self.update()
