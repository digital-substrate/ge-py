from __future__ import annotations

from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QIntValidator, QPixmap
from PySide6.QtWidgets import QFrame, QColorDialog, QApplication

from .ui_vertex import Ui_VertexComponent
from model.context import Context
from dsviper_components.ds_commit_store_notifier import DSCommitStoreNotifier
from transient_notifier import TransientNotifier
from ge import attachments
from ge.data import Graph_VertexKey, Graph_Color, Graph_Position


class VertexComponent(QFrame, Ui_VertexComponent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self._context: Context | None = None
        self._vertex_key: Graph_VertexKey | None = None
        self._value: int = 0
        self._color: QColor = QColor(255, 255, 255)
        self._location: QPointF = QPointF()

        self._configure_ui()
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

        # Value
        self.w_value_line_edit.returnPressed.connect(self._value_line_edit_return_pressed)

        # Color
        self.w_color_button.clicked.connect(self._color_clicked)

        # Position
        self.w_x_line_edit.returnPressed.connect(self._x_line_edit_return_pressed)
        self.w_x_slider.sliderMoved.connect(self._x_slider_moved)
        self.w_x_slider.sliderReleased.connect(self._x_slider_released)

        self.w_y_line_edit.returnPressed.connect(self._y_line_edit_return_pressed)
        self.w_y_slider.sliderMoved.connect(self._y_slider_moved)
        self.w_y_slider.sliderReleased.connect(self._y_slider_released)

        # Transient Notifier
        transient_notifier = TransientNotifier.instance()
        transient_notifier.vertices_moved.connect(self._vertices_moved)

    def _store_database_did_open(self):
        self._enable_interaction()

    def _store_database_did_close(self):
        self._disable_interaction()

    def _store_state_did_change(self):
        self._configure()

    def _enable_interaction(self):
        self.setEnabled(True)

    def _disable_interaction(self):
        self.setEnabled(False)

    # MARK: - Value

    def _value_line_edit_return_pressed(self):
        if not self._vertex_key:
            return

        if QApplication.focusWidget():
            QApplication.focusWidget().clearFocus()

        self._set_vertex_value(self._vertex_key, int(self.w_value_line_edit.text()))

    # MARK: - Color

    def _color_clicked(self):
        if not self._vertex_key:
            return

        dialog = QColorDialog(self._color, self)
        dialog.currentColorChanged.connect(self._color_current_color_changed)
        dialog.exec()

        if dialog.result() == QColorDialog.DialogCode.Accepted:
            self._set_vertex_color(self._vertex_key, dialog.currentColor())
        else:
            TransientNotifier.instance().notify_vertex_color(self._vertex_key, self._color)

    def _color_current_color_changed(self, color: QColor):
        if not self._vertex_key:
            return
        TransientNotifier.instance().notify_vertex_color(self._vertex_key, color)

    # MARK: - Position

    def _x_line_edit_return_pressed(self):
        if not self._vertex_key:
            return

        if QApplication.focusWidget():
            QApplication.focusWidget().clearFocus()

        self._set_vertex_position_x(self._vertex_key, int(self.w_x_line_edit.text()))

    def _x_slider_moved(self, value: int):
        if not self._vertex_key:
            return

        self.w_x_line_edit.blockSignals(True)
        self.w_x_line_edit.setText(str(value))
        self.w_x_line_edit.blockSignals(False)

        TransientNotifier.instance().notify_vertex_position(
            self._vertex_key, QPointF(value, self._location.y())
        )

    def _x_slider_released(self):
        if not self._vertex_key:
            return

        value = self.w_x_slider.value()
        if value == self._location.x():
            return

        self._set_vertex_position_x(self._vertex_key, value)

    def _y_line_edit_return_pressed(self):
        if not self._vertex_key:
            return

        if QApplication.focusWidget():
            QApplication.focusWidget().clearFocus()

        self._set_vertex_position_y(self._vertex_key, int(self.w_y_line_edit.text()))

    def _y_slider_moved(self, value: int):
        if not self._vertex_key:
            return

        self.w_y_line_edit.blockSignals(True)
        self.w_y_line_edit.setText(str(value))
        self.w_y_line_edit.blockSignals(False)

        TransientNotifier.instance().notify_vertex_position(
            self._vertex_key, QPointF(self._location.x(), value)
        )

    def _y_slider_released(self):
        if not self._vertex_key:
            return

        value = self.w_y_slider.value()
        if value == self._location.y():
            return

        self._set_vertex_position_y(self._vertex_key, value)

    def _vertices_moved(self, keys, offset: QPointF):
        if not self._vertex_key:
            return

        if self._vertex_key in keys:
            p = QPointF(self._location.x() + offset.x(), self._location.y() - offset.y())
            self._position_configure(p)

    # MARK: - Configure

    def _configure_ui(self):
        self.w_value_line_edit.setValidator(QIntValidator(0, 1000, self))
        self.w_x_line_edit.setValidator(QIntValidator(0, 1000, self))
        self.w_y_line_edit.setValidator(QIntValidator(0, 1000, self))

    def _configure(self):
        if not self._context:
            return

        attachment_getting = self._context.store.attachment_getting()
        graph_key = self._context.graph_key

        try:
            vertex_keys = set()
            opt_selection = attachments.graph_graph_selection_get(attachment_getting, graph_key)
            if opt_selection:
                selection = opt_selection.unwrap()
                vertex_keys = set(selection.vertex_keys)

            if len(vertex_keys) == 1:
                self._vertex_key = next(iter(vertex_keys))
                self._configure_vertex()
                self._controls_enable(True)
            else:
                self._vertex_key = None
                self._controls_reset()
                self._controls_enable(False)

        except Exception as e:
            print(f"VertexComponent._configure error: {e}")

    def _controls_reset(self):
        self._value_block_signal(True)
        self._value_configure(0)
        self._value_block_signal(False)

        self._color_block_signal(True)
        self._color_configure(QColor(255, 255, 255))
        self._color_block_signal(False)

        self._position_block_signal(True)
        self._position_configure(QPointF())
        self._position_block_signal(False)

    def _configure_vertex(self):
        if not self._context or not self._vertex_key:
            return

        attachment_getting = self._context.store.attachment_getting()

        try:
            self._value = 0
            self._color = QColor(255, 255, 255)
            opt_visual = attachments.graph_vertex_visual_attributes_get(attachment_getting, self._vertex_key)
            if opt_visual:
                visual = opt_visual.unwrap()
                self._value = visual.value
                self._color = QColor(
                    int(visual.color.red * 255),
                    int(visual.color.green * 255),
                    int(visual.color.blue * 255)
                )

            self._location = QPointF()
            opt_render = attachments.graph_vertex_render_2d_attributes_get(attachment_getting, self._vertex_key)
            if opt_render:
                render = opt_render.unwrap()
                self._location = QPointF(render.position.x, render.position.y)

            self._controls_configure()
            self._controls_enable(True)

        except Exception as e:
            print(f"VertexComponent._configure_vertex error: {e}")

    def _controls_configure(self):
        self._value_configure(self._value)
        self._color_configure(self._color)
        self._position_configure(self._location)

    # MARK: - Value Controls

    def _value_enable(self, enabled: bool):
        self.w_value_line_edit.setEnabled(enabled)

    def _value_block_signal(self, enabled: bool):
        self.w_value_line_edit.blockSignals(enabled)

    def _value_configure(self, value: int):
        self._value_block_signal(True)
        self.w_value_line_edit.setText(str(value))
        self._value_block_signal(False)

    # MARK: - Color Controls

    def _color_enable(self, enabled: bool):
        self.w_color_button.setEnabled(enabled)

    def _color_block_signal(self, enabled: bool):
        self.w_color_button.blockSignals(enabled)

    def _color_configure(self, color: QColor):
        pixmap = QPixmap(32, 32)
        pixmap.fill(color)
        self.w_color_button.setIcon(pixmap)

    # MARK: - Position Controls

    def _position_enable(self, enabled: bool):
        self.w_x_line_edit.setEnabled(enabled)
        self.w_x_slider.setEnabled(enabled)
        self.w_y_line_edit.setEnabled(enabled)
        self.w_y_slider.setEnabled(enabled)

    def _position_block_signal(self, enabled: bool):
        self.w_x_line_edit.blockSignals(enabled)
        self.w_x_slider.blockSignals(enabled)
        self.w_y_line_edit.blockSignals(enabled)
        self.w_y_slider.blockSignals(enabled)

    def _position_configure(self, position: QPointF):
        self._position_block_signal(True)
        self.w_x_line_edit.setText(str(int(position.x())))
        self.w_x_slider.setValue(int(position.x()))
        self.w_y_line_edit.setText(str(int(position.y())))
        self.w_y_slider.setValue(int(position.y()))
        self._position_block_signal(False)

    def _controls_enable(self, enabled: bool):
        self._color_enable(enabled)
        self._value_enable(enabled)
        self._position_enable(enabled)

    # MARK: - Dispatch

    def _set_vertex_value(self, vertex_key: Graph_VertexKey, value: int):
        label = f"Set Value '{value}' For Vertex '{self._value}'"
        self._context.store.dispatch(
            label,
            lambda m: attachments.graph_vertex_visual_attributes_set_value(m, vertex_key, value)
        )

    def _set_vertex_color(self, vertex_key: Graph_VertexKey, value: QColor):
        color = Graph_Color()
        color.red = value.redF()
        color.green = value.greenF()
        color.blue = value.blueF()

        label = f"Set Color For Vertex '{self._value}'"
        self._context.store.dispatch(
            label,
            lambda m: attachments.graph_vertex_visual_attributes_set_color(m, vertex_key, color)
        )

    def _set_vertex_position_x(self, vertex_key: Graph_VertexKey, value: int):
        self._location = QPointF(value, self._location.y())
        position = Graph_Position()
        position.x = int(self._location.x())
        position.y = int(self._location.y())

        label = f"Set Position.X To {value} For Vertex '{self._value}'"
        self._context.store.dispatch(
            label,
            lambda m: attachments.graph_vertex_render_2d_attributes_set_position(m, vertex_key, position)
        )

    def _set_vertex_position_y(self, vertex_key: Graph_VertexKey, value: int):
        self._location = QPointF(self._location.x(), value)
        position = Graph_Position()
        position.x = int(self._location.x())
        position.y = int(self._location.y())

        label = f"Set Position.Y To {value} For Vertex '{self._value}'"
        self._context.store.dispatch(
            label,
            lambda m: attachments.graph_vertex_render_2d_attributes_set_position(m, vertex_key, position)
        )
