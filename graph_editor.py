#!/usr/bin/env python
from __future__ import annotations

from PySide6.QtCore import QCoreApplication, Qt, QDir, QFileInfo, QTimer, QRect, QKeyCombination, QCommandLineParser, \
    QSize, QEvent, QObject
from PySide6.QtGui import QIcon, QAction, QKeySequence, QGuiApplication, QPalette, QColor
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QDialog, QSplitter, QLineEdit, \
    QStatusBar

from components import CommentsComponent, ListComponent
from dsviper_components.ds_commit_actions import DSCommitActions
from model.context import Context

from dsviper import (
    CommitSynchronizer,
    CommitStoreNotifying,
    CommitDatabase,
    Logging,
    Error,
    ViperError
)
from dsviper import CommitDatabaseSQLite

from dsviper_components import ds_dialog_helper
from dsviper_components.ds_commit_actions_dialog import DSCommitActionsDialog
from dsviper_components.ds_commit_documents_dialog import DSCommitDocumentsDialog
from dsviper_components.ds_commit_program_dialog import DSCommitProgramDialog
from dsviper_components.ds_commit_settings_dialog import DSCommitSettingsDialog
from dsviper_components.ds_commit_store_notifier import DSCommitStoreNotifier
from dsviper_components.ds_commit_sync_log_dialog import DSCommitSyncLogDialog
from dsviper_components.ds_commit_blobs_dialog import DSCommitBlobsDialog
from dsviper_components.ds_commit_synchronizer_thread import DSCommitSynchronizerThread
from dsviper_components.ds_commit_undo_dialog import DSCommitUndoDialog
from dsviper_components.ds_commits_dialog import DSCommitsDialog
from dsviper_components.ds_connect_to_server_dialog import DSConnectToServerDialog
from dsviper_components.ds_code_editor_dialog import DSCodeEditorDialog
from dsviper_components.ds_inspect_dialog import DSInspectDialog
from dsviper_components.ds_logger import DSLogger
from dsviper_components.ds_settings import DSSettings

from dsviper_components import ds_license
import os
import platform
import sys

from components import RenderComponent, StatisticsComponent, TagsComponent, TitleComponent, VertexComponent
from select_graph_dialog import SelectGraphDialog

from ge.data import Graph_Rectangle
from model import graph_topology
from model import graph_bug
from model import graph_killer
from model import graph_integrity
from model import selection_vertices
from model import selection_edges
from model import selection_mixed
from model import random as model_random
from model import edge as model_edge
from model import tools as model_tools
from model import script_delete_selection


class _LineEditUndoRedoFilter(QObject):
    """Prevent QLineEdit from handling Undo/Redo key sequences locally.

    Without this filter, when the application-level undo/redo QActions are
    disabled (nothing to undo in the store), the key event falls through
    to QLineEdit which performs its own local undo/redo.  This mirrors
    AppKit behaviour where NSTextField has no undo manager.
    """

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if isinstance(obj, QLineEdit) and event.type() in (
            QEvent.Type.ShortcutOverride, QEvent.Type.KeyPress
        ):
            from PySide6.QtGui import QKeyEvent
            key_event: QKeyEvent = event  # type: ignore[assignment]
            if key_event.matches(QKeySequence.StandardKey.Undo) or key_event.matches(QKeySequence.StandardKey.Redo):
                event.ignore()
                return True
        return super().eventFilter(obj, event)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bootstrap_database_path: str | None = None

        self._live_enabled = False
        self._live_is_manager = False
        self._databases_path = QDir.homePath() + "/Databases"

        self._inspect_dialog: DSInspectDialog | None = None
        self._inspect_dialog_geometry = QRect()

        self._commits_dialog: DSCommitsDialog | None = None
        self._commits_dialog_geometry = QRect()

        self._commit_documents_dialog: DSCommitDocumentsDialog | None = None
        self._commit_documents_dialog_geometry = QRect()

        self._commit_program_dialog: DSCommitProgramDialog | None = None
        self._commit_program_dialog_geometry = QRect()

        self._commit_undo_dialog: DSCommitUndoDialog | None = None
        self._commit_undo_dialog_geometry = QRect()

        self._commit_actions_dialog: DSCommitActionsDialog | None = None
        self._commit_actions_dialog_geometry = QRect()

        self._commit_sync_log_dialog: DSCommitSyncLogDialog | None = None
        self._commit_sync_log_dialog_geometry = QRect()

        self._commit_blobs_dialog: DSCommitBlobsDialog | None = None
        self._commit_blobs_dialog_geometry = QRect()

        self._code_editor_dialog: DSCodeEditorDialog | None = None
        self._code_editor_dialog_geometry = QRect()

        self._synchronizer: CommitSynchronizer | None = None
        self._sync_logger = DSLogger(Logging.LEVEL_ALL)
        self._sync_logging = Logging.create(self._sync_logger)

        self._setup_setting()

        self._setup_central_widget()
        self._setup_dialog()
        self._setup_action()
        self._setup_menu()
        self._setup_toolbar()

        self._setup_status_bar()
        self._setup_connections()
        self._validate_actions()

        self._configure_window_title()
        self._configure_live_manager_action()
        self._configure_go_live_action()

        self.setWindowIcon(QIcon(":/dsviper_components/images/app.png"))
        self.setMinimumSize(800, 600)

        QTimer.singleShot(100, self, self._bootstrap_timeout)

    # Bootstrap
    def set_bootstrap_database_path(self, database_path: str):
        self._bootstrap_database_path = database_path

    def _bootstrap_timeout(self):
        if self._bootstrap_database_path:
            self._set_database(self._bootstrap_database_path)
        else:
            self._may_reopen_last_database()

    def _setup_setting(self):
        QCoreApplication.setOrganizationName("DigitalSubstrate")
        QCoreApplication.setOrganizationDomain("digitalsubstrate.io")
        QCoreApplication.setApplicationName("GraphEditorPy")

        DSSettings().register_default()

    def _setup_dialog(self):
        store = Context.instance().store
        self._inspect_dialog = DSInspectDialog()
        self._commits_dialog = DSCommitsDialog(store)
        self._commit_documents_dialog = DSCommitDocumentsDialog(store)
        self._commit_program_dialog = DSCommitProgramDialog(store)
        self._commit_undo_dialog = DSCommitUndoDialog(store)
        self._commit_blobs_dialog = DSCommitBlobsDialog(store)
        self._commit_actions_dialog = DSCommitActionsDialog(store)
        self._commit_sync_log_dialog = DSCommitSyncLogDialog()

        # Python Editor
        from dsviper_components.python_editor_model import PythonEditorModel
        from pathlib import Path
        scripts_folder = str(Path(__file__).parent / "scripts")
        os.makedirs(scripts_folder, exist_ok=True)
        self._python_editor_model = PythonEditorModel(
            scripts_folder,
            namespace_vars={
                "ctx": Context.instance(),
                "store": store,
                "render_model": self._render_component,
                "_documents_panel": self._commit_documents_dialog,
            }
        )
        self._code_editor_dialog = DSCodeEditorDialog(self._python_editor_model)
        self._python_editor_model.run_init_script()

    def _setup_action(self):
        dark = "-dark" if QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark else ""

        # File Actions
        self._open_action = QAction(QIcon.fromTheme(QIcon.ThemeIcon.DocumentOpen), "Open", parent=self)
        self._open_action.setShortcuts(QKeySequence.StandardKey.Open)
        self._open_action.setIconVisibleInMenu(False)
        self._open_action.triggered.connect(self._open_database_triggered)

        self._new_action = QAction(QIcon.fromTheme(QIcon.ThemeIcon.DocumentNew), "New", parent=self)
        self._new_action.setShortcuts(QKeySequence.StandardKey.New)
        self._new_action.setIconVisibleInMenu(False)
        self._new_action.triggered.connect(self._new_database_triggered)

        self._close_action = QAction(self.tr("Close"), parent=self)
        self._close_action.setShortcuts(QKeySequence.StandardKey.Close)
        self._close_action.setIconVisibleInMenu(False)
        self._close_action.triggered.connect(self._close_database)

        self._quit_action = QAction(self.tr("Quit"), parent=self)
        self._quit_action.setShortcuts(QKeySequence.StandardKey.Quit)
        self._quit_action.setIconVisibleInMenu(False)
        self._quit_action.triggered.connect(QCoreApplication.quit, type=Qt.ConnectionType.QueuedConnection)

        self._toggle_inspect_dialog_action = QAction(self.tr("Get Info"), parent=self)
        self._toggle_inspect_dialog_action.setShortcut(
            QKeyCombination(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_I))
        self._toggle_inspect_dialog_action.triggered.connect(self._toggle_inspect_dialog_triggered)

        self._reopen_last_database_action = QAction(self.tr("Reopen Last Database"), parent=self)
        self._reopen_last_database_action.setCheckable(True)
        self._reopen_last_database_action.triggered.connect(self._reopen_last_database_triggered)

        # Commit Actions
        self._forward_action = QAction(self.tr("Forward"), parent=self)
        self._forward_action.setIcon(QIcon(f':/dsviper_components/images/arrow.up.circle{dark}'))
        self._forward_action.setIconVisibleInMenu(False)
        self._forward_action.triggered.connect(self._forward_triggered)

        self._merge_heads_action = QAction(self.tr("Merge Heads"), parent=self)
        self._merge_heads_action.setIcon(QIcon(f':/dsviper_components/images/arrow.triangle.merge{dark}'))
        self._merge_heads_action.setIconVisibleInMenu(False)
        self._merge_heads_action.triggered.connect(self._merge_heads_triggered)

        self._fetch_action = QAction(self.tr("Fetch"), parent=self)
        self._fetch_action.setIcon(QIcon(f':/dsviper_components/images/icloud.and.arrow.down{dark}'))
        self._fetch_action.setIconVisibleInMenu(False)
        self._fetch_action.triggered.connect(self._fetch_triggered)

        self._push_action = QAction(self.tr("Push"), parent=self)
        self._push_action.setIcon(QIcon(f':/dsviper_components/images/icloud.and.arrow.up{dark}'))
        self._push_action.setIconVisibleInMenu(False)
        self._push_action.triggered.connect(self._push_triggered)

        self._sync_action = QAction(self.tr("Sync"), parent=self)
        self._sync_action.setIcon(QIcon(f':/dsviper_components/images/link.icloud{dark}'))
        self._sync_action.setIconVisibleInMenu(False)
        self._sync_action.triggered.connect(self._sync_triggered)

        # Live Actions
        self._live_manager_action = QAction(self.tr("Manager"), parent=self)
        self._live_manager_action.setIcon(QIcon(f':/dsviper_components/images/person.icloud{dark}'))
        self._live_manager_action.setIconVisibleInMenu(False)
        self._live_manager_action.triggered.connect(self._toggle_live_manager_triggered)

        self._go_live_action = QAction(self.tr("Go Live"), parent=self)
        self._go_live_action.setIcon(QIcon(f':/dsviper_components/images/arrow.triangle.2.circlepath.icloud{dark}'))
        self._go_live_action.setIconVisibleInMenu(False)
        self._go_live_action.triggered.connect(self._toggle_live_triggered)

        # Edit Actions
        self._undo_action = QAction(self.tr("Undo"), parent=self)
        self._undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self._undo_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self._undo_action.triggered.connect(self._undo_triggered)

        self._redo_action = QAction(self.tr("Redo"), parent=self)
        self._redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self._redo_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self._redo_action.triggered.connect(self._redo_triggered)

        self._delete_action = QAction(self.tr("Delete"), parent=self)
        if platform.system() == "Darwin":
            self._delete_action.setShortcut(QKeySequence.StandardKey.Backspace)
        else:
            self._delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        self._delete_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self._delete_action.triggered.connect(self._delete_triggered)

        self._delete_bugged_action = QAction(self.tr("Delete Bugged"), parent=self)
        if platform.system() == "Darwin":
            self._delete_bugged_action.setShortcut(QKeySequence.StandardKey.Delete)
        self._delete_bugged_action.triggered.connect(self._delete_bugged_triggered)

        self._go_forward_action = QAction(self.tr("Go Forward"), parent=self)
        self._go_forward_action.setShortcut(
            QKeyCombination(Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier, Qt.Key.Key_Right))
        self._go_forward_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self._go_forward_action.triggered.connect(self._go_forward_triggered)

        self._go_back_action = QAction(self.tr("Go Back"), parent=self)
        self._go_back_action.setShortcut(
            QKeyCombination(Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier, Qt.Key.Key_Left))
        self._go_back_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self._go_back_action.triggered.connect(self._go_back_triggered)

        # Admin Actions
        self._toggle_commits_dialog_action = QAction(self.tr("Commits Panel"), parent=self)
        self._toggle_commits_dialog_action.setShortcut(
            QKeyCombination(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_1))
        self._toggle_commits_dialog_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self._toggle_commits_dialog_action.triggered.connect(self._toggle_commits_dialog_triggered)

        self._toggle_commit_documents_dialog_action = QAction(self.tr("Documents"), parent=self)
        self._toggle_commit_documents_dialog_action.setShortcut(
            QKeyCombination(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_2))
        self._toggle_commit_documents_dialog_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self._toggle_commit_documents_dialog_action.triggered.connect(self._toggle_commit_documents_dialog_triggered)

        self._toggle_commit_program_dialog_action = QAction(self.tr("Program Panel"), parent=self)
        self._toggle_commit_program_dialog_action.setShortcut(
            QKeyCombination(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_3))
        self._toggle_commit_program_dialog_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self._toggle_commit_program_dialog_action.triggered.connect(self._toggle_commit_program_dialog_triggered)

        self._toggle_commit_settings_dialog_action = QAction(self.tr("Commit Settings Panel"), parent=self)
        self._toggle_commit_settings_dialog_action.setShortcut(
            QKeyCombination(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_4))
        self._toggle_commit_settings_dialog_action.triggered.connect(self._toggle_commit_settings_dialog_triggered)

        self._toggle_commit_undo_dialog_action = QAction(self.tr("Undo Panel"), parent=self)
        self._toggle_commit_undo_dialog_action.setShortcut(
            QKeyCombination(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_5))
        self._toggle_commit_undo_dialog_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self._toggle_commit_undo_dialog_action.triggered.connect(self._toggle_commit_undo_dialog_triggered)

        self._toggle_commit_sync_log_dialog_action = QAction(self.tr("Synchronizer Log Panel"), self)
        self._toggle_commit_sync_log_dialog_action.setShortcut(
            QKeyCombination(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_6))
        self._toggle_commit_sync_log_dialog_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self._toggle_commit_sync_log_dialog_action.triggered.connect(self._toggle_commit_sync_log_dialog_triggered)

        self._toggle_commit_blobs_dialog_action = QAction(self.tr("Blobs Panel"), self)
        self._toggle_commit_blobs_dialog_action.setShortcut(
            QKeyCombination(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_7))
        self._toggle_commit_blobs_dialog_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self._toggle_commit_blobs_dialog_action.triggered.connect(self._toggle_commit_blobs_dialog_triggered)

        self._toggle_commit_actions_dialog_action = QAction(self.tr("Action Panel"), self)
        self._toggle_commit_actions_dialog_action.setShortcut(
            QKeyCombination(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_8))
        self._toggle_commit_actions_dialog_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self._toggle_commit_actions_dialog_action.triggered.connect(self._toggle_commit_actions_dialog_triggered)

        self._toggle_code_editor_dialog_action = QAction(self.tr("Python &Editor"), parent=self)
        self._toggle_code_editor_dialog_action.setShortcut(
            QKeyCombination(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_0))
        self._toggle_code_editor_dialog_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self._toggle_code_editor_dialog_action.triggered.connect(self._toggle_code_editor_dialog_triggered)

        self._connect_to_server_action = QAction(self.tr("Connect To Server"), parent=self)
        self._connect_to_server_action.setShortcut(QKeyCombination(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_K))
        self._connect_to_server_action.triggered.connect(self._connect_to_server_triggered)

        # Graph Actions
        self._select_graph_action = QAction(self.tr("Select"), parent=self)
        self._select_graph_action.triggered.connect(self._select_graph_triggered)

        self._new_graph_action = QAction(self.tr("New"), parent=self)
        self._new_graph_action.triggered.connect(self._new_graph_triggered)

        self._clear_graph_action = QAction(self.tr("Clear"), parent=self)
        self._clear_graph_action.triggered.connect(self._clear_graph_triggered)

        self._inspect_document_action = QAction(self.tr("Inspect Element"), parent=self)
        self._inspect_document_action.setShortcut(QKeyCombination(Qt.KeyboardModifier.ShiftModifier, Qt.Key.Key_E))
        self._inspect_document_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self._inspect_document_action.triggered.connect(self._inspect_document_triggered)

        self._random_graph_action = QAction(self.tr("Random Graph"), parent=self)
        self._random_graph_action.setIcon(QIcon(":/images/point.3.connected.trianglepath.dotted" + dark))
        self._random_graph_action.setIconVisibleInMenu(False)
        self._random_graph_action.triggered.connect(self._random_graph_triggered)

        self._random_vertex_action = QAction(self.tr("Random Vertex"), parent=self)
        self._random_vertex_action.setIcon(QIcon(":/images/number.circle" + dark))
        self._random_vertex_action.setIconVisibleInMenu(False)
        self._random_vertex_action.triggered.connect(self._random_vertex_triggered)

        self._random_edge_action = QAction(self.tr("Random Edge"), parent=self)
        self._random_edge_action.setIcon(QIcon(":/images/line.diagonal" + dark))
        self._random_edge_action.setIconVisibleInMenu(False)
        self._random_edge_action.triggered.connect(self._random_edge_triggered)

        self._random_tag_action = QAction(self.tr("Random Tag"), parent=self)
        self._random_tag_action.setIcon(QIcon(":/images/tag" + dark))
        self._random_tag_action.setIconVisibleInMenu(False)
        self._random_tag_action.triggered.connect(self._random_tag_triggered)

        self._random_comment_action = QAction(self.tr("Random Comment"), parent=self)
        self._random_comment_action.setIcon(QIcon(":/images/message" + dark))
        self._random_comment_action.setIconVisibleInMenu(False)
        self._random_comment_action.triggered.connect(self._random_comment_triggered)

        self._increment_vertex_value_action = QAction(self.tr("Increment Vertex Value "), parent=self)
        self._increment_vertex_value_action.triggered.connect(self._increment_vertex_value_triggered)

        self._graph_with_missing_vertex_action = QAction(self.tr("Graph With Missing Vertex"), parent=self)
        self._graph_with_missing_vertex_action.triggered.connect(self._graph_with_missing_vertex_triggered)

        self._graph_with_missing_vertex_properties_action = QAction(self.tr("Graph With Missing Vertex Properties"),
                                                                    parent=self)
        self._graph_with_missing_vertex_properties_action.triggered.connect(
            self._graph_with_missing_vertex_properties_triggered)

        self._graph_with_error_action = QAction(self.tr("Graph With Error"), parent=self)
        self._graph_with_error_action.triggered.connect(self._graph_with_error_triggered)

        self._restore_integrity_by_deleting_action = QAction(self.tr("Restore Integrity By Deleting"), parent=self)
        self._restore_integrity_by_deleting_action.triggered.connect(self._restore_integrity_by_deleting_triggered)

        self._restore_integrity_by_restoring_action = QAction(self.tr("Restore Integrity By Restoring"), parent=self)
        self._restore_integrity_by_restoring_action.triggered.connect(self._restore_integrity_by_restoring_triggered)

        self._restore_integrity_by_creating_action = QAction(self.tr("Restore Integrity By Creating"), parent=self)
        self._restore_integrity_by_creating_action.triggered.connect(self._restore_integrity_by_creating_triggered)

        self._killer_action = QAction(self.tr("Oh My God, They have killed Commit"), parent=self)
        self._killer_action.triggered.connect(self._killer_triggered)

        self._select_all_vertices_action = QAction(self.tr("Select All Vertices"), parent=self)
        self._select_all_vertices_action.setShortcut(QKeyCombination(Qt.KeyboardModifier.ShiftModifier, Qt.Key.Key_A))
        self._select_all_vertices_action.triggered.connect(self._select_all_vertices_triggered)

        self._select_all_edges_action = QAction(self.tr("Select All Edges"), parent=self)
        self._select_all_edges_action.setShortcut(QKeyCombination(Qt.KeyboardModifier.AltModifier, Qt.Key.Key_A))
        self._select_all_edges_action.triggered.connect(self._select_all_edges_triggered)

        self._deselect_all_vertices_action = QAction(self.tr("Deselect All Vertices"), parent=self)
        self._deselect_all_vertices_action.triggered.connect(self._deselect_all_vertices_triggered)

        self._deselect_all_edges_action = QAction(self.tr("Deselect All Edges"), parent=self)
        self._deselect_all_edges_action.triggered.connect(self._deselect_all_edges_triggered)

        self._invert_vertices_selection_action = QAction(self.tr("Invert Vertices Selection"), parent=self)
        self._invert_vertices_selection_action.triggered.connect(self._invert_vertices_selection_triggered)

        self._invert_edges_selection_action = QAction(self.tr("Invert Edges Selection"), parent=self)
        self._invert_edges_selection_action.triggered.connect(self._invert_edges_selection_triggered)

        self._select_all_action = QAction(self.tr("Select All"), parent=self)
        self._select_all_action.setShortcut(QKeyCombination(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_A))
        self._select_all_action.triggered.connect(self._select_all_triggered)

        self._deselect_all_vertices_and_edges_action = QAction(self.tr("Deselect All Vertices"), parent=self)
        self._deselect_all_vertices_and_edges_action.triggered.connect(self._deselect_all_vertices_and_edges_triggered)

        self._invert_selection_of_vertices_and_edges_action = QAction(self.tr("Deselect All"), parent=self)
        self._invert_selection_of_vertices_and_edges_action.triggered.connect(
            self._invert_selection_of_vertices_and_edges_triggered)

        self._restore_vertex_selection_action = QAction(self.tr("Restore Vertex Selection"), parent=self)
        self._restore_vertex_selection_action.triggered.connect(self._restore_vertex_selection_triggered)

        # Help Actions
        self._mouse_shortcuts_action = QAction(self.tr("Mouse Shortcuts"), parent=self)
        self._mouse_shortcuts_action.triggered.connect(self._mouse_shortcuts_triggered)

        self._about_action = QAction(self.tr("About Graph Editor..."), parent=self)
        self._about_action.setMenuRole(QAction.MenuRole.NoRole)
        self._about_action.triggered.connect(self._about_triggered)

        self._about_qt_action = QAction(self.tr("About Qt"), parent=self)
        self._about_qt_action.setMenuRole(QAction.MenuRole.NoRole)
        self._about_qt_action.triggered.connect(QApplication.aboutQt)

    def _setup_menu(self):
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(self._open_action)
        file_menu.addAction(self._new_action)
        file_menu.addAction(self._close_action)
        file_menu.addAction(self._toggle_inspect_dialog_action)
        file_menu.addSeparator()
        file_menu.addAction(self._forward_action)
        file_menu.addAction(self._merge_heads_action)
        file_menu.addSeparator()
        file_menu.addAction(self._fetch_action)
        file_menu.addAction(self._push_action)
        file_menu.addAction(self._sync_action)
        file_menu.addSeparator()
        file_menu.addAction(self._reopen_last_database_action)

        if platform.system() != "Darwin":
            file_menu.addSeparator()
            file_menu.addAction(self._quit_action)

        edit_menu = self.menuBar().addMenu(self.tr("&Edit"))
        edit_menu.addAction(self._undo_action)
        edit_menu.addAction(self._redo_action)
        edit_menu.addAction(self._delete_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self._delete_bugged_action)

        graph_menu = self.menuBar().addMenu(self.tr("&Graph"))
        graph_menu.addAction(self._select_graph_action)
        graph_menu.addAction(self._new_graph_action)
        graph_menu.addAction(self._clear_graph_action)
        graph_menu.addSeparator()
        graph_menu.addAction(self._inspect_document_action)
        graph_menu.addSeparator()
        graph_menu.addAction(self._random_graph_action)
        graph_menu.addAction(self._random_vertex_action)
        graph_menu.addAction(self._random_edge_action)
        graph_menu.addAction(self._random_tag_action)
        graph_menu.addAction(self._random_comment_action)
        graph_menu.addSeparator()
        graph_menu.addAction(self._increment_vertex_value_action)
        graph_menu.addSeparator()
        graph_menu.addAction(self._graph_with_missing_vertex_action)
        graph_menu.addAction(self._graph_with_missing_vertex_properties_action)
        graph_menu.addAction(self._graph_with_error_action)
        graph_menu.addSeparator()
        graph_menu.addAction(self._restore_integrity_by_deleting_action)
        graph_menu.addAction(self._restore_integrity_by_restoring_action)
        graph_menu.addAction(self._restore_integrity_by_creating_action)
        graph_menu.addSeparator()
        graph_menu.addAction(self._killer_action)

        selection_menu = self.menuBar().addMenu(self.tr("&Selection"))
        selection_menu.addAction(self._select_all_action)
        selection_menu.addAction(self._deselect_all_vertices_and_edges_action)
        selection_menu.addAction(self._invert_selection_of_vertices_and_edges_action)
        selection_menu.addSeparator()
        selection_menu.addAction(self._select_all_vertices_action)
        selection_menu.addAction(self._deselect_all_vertices_action)
        selection_menu.addAction(self._invert_vertices_selection_action)
        selection_menu.addSeparator()
        selection_menu.addAction(self._select_all_edges_action)
        selection_menu.addAction(self._deselect_all_edges_action)
        selection_menu.addAction(self._invert_edges_selection_action)
        selection_menu.addSeparator()
        selection_menu.addAction(self._restore_vertex_selection_action)

        navigation_menu = self.menuBar().addMenu(self.tr("&Navigation"))
        navigation_menu.addAction(self._go_forward_action)
        navigation_menu.addAction(self._go_back_action)

        # Editor menu — mirrors ge-qml Editor menu structure
        editor = self._code_editor_dialog.editor
        editor_menu = self.menuBar().addMenu(self.tr("&Editor"))

        editor_menu.addAction(editor.open_script_action)
        editor_menu.addAction(editor.save_script_action)
        editor_menu.addSeparator()

        find_submenu = editor_menu.addMenu(self.tr("Find"))
        find_submenu.addAction(editor.find_action)
        find_submenu.addAction(editor.find_next_action)
        find_submenu.addAction(editor.find_previous_action)
        find_submenu.addAction(editor.use_selection_for_find_action)
        find_submenu.addSeparator()
        find_submenu.addAction(editor.find_and_replace_action)

        editor_menu.addSeparator()
        editor_menu.addAction(editor.next_error_action)
        editor_menu.addAction(editor.previous_error_action)
        editor_menu.addSeparator()
        editor_menu.addAction(editor.jump_to_line_action)
        editor_menu.addAction(editor.jump_to_definition_action)
        editor_menu.addSeparator()
        editor_menu.addAction(editor.run_script_action)
        editor_menu.addAction(editor.eval_selection_action)
        editor_menu.addSeparator()
        editor_menu.addAction(editor.show_help_action)
        editor_menu.addAction(editor.show_type_action)
        editor_menu.addAction(editor.show_description_action)
        editor_menu.addSeparator()
        editor_menu.addAction(editor.bigger_font_action)
        editor_menu.addAction(editor.smaller_font_action)
        editor_menu.addSeparator()
        editor_menu.addAction(editor.comment_selection_action)
        editor_menu.addAction(editor.shift_right_action)
        editor_menu.addAction(editor.shift_left_action)
        editor_menu.addAction(editor.move_line_up_action)
        editor_menu.addAction(editor.move_line_down_action)
        editor_menu.addSeparator()
        editor_menu.addAction(editor.refresh_syntax_action)

        admin_menu = self.menuBar().addMenu(self.tr("&Admin"))
        admin_menu.addAction(self._toggle_commits_dialog_action)
        admin_menu.addAction(self._toggle_commit_documents_dialog_action)
        admin_menu.addAction(self._toggle_commit_program_dialog_action)
        admin_menu.addAction(self._toggle_commit_settings_dialog_action)
        admin_menu.addAction(self._toggle_commit_undo_dialog_action)
        admin_menu.addAction(self._toggle_commit_sync_log_dialog_action)
        admin_menu.addAction(self._toggle_commit_blobs_dialog_action)
        admin_menu.addAction(self._toggle_commit_actions_dialog_action)
        admin_menu.addSeparator()
        admin_menu.addAction(self._toggle_code_editor_dialog_action)
        admin_menu.addSeparator()
        admin_menu.addAction(self._connect_to_server_action)

        help_menu = self.menuBar().addMenu(self.tr("&Help"))
        help_menu.addAction(self._mouse_shortcuts_action)
        help_menu.addSeparator()
        help_menu.addAction(self._about_action)
        help_menu.addSeparator()
        help_menu.addAction(self._about_qt_action)

        settings = DSSettings()
        checked = settings.reopen_last_file
        self._reopen_last_database_action.setChecked(checked)

    def _setup_toolbar(self):
        tb = self.addToolBar(self.tr("ToolBar"))
        tb.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        tb.addAction(self._forward_action)
        tb.addAction(self._merge_heads_action)
        tb.addSeparator()
        tb.addAction(self._fetch_action)
        tb.addAction(self._push_action)
        tb.addAction(self._sync_action)
        tb.addSeparator()
        tb.addAction(self._live_manager_action)
        tb.addAction(self._go_live_action)
        tb.addSeparator()
        tb.addAction(self._random_vertex_action)
        tb.addAction(self._random_edge_action)
        tb.addAction(self._random_graph_action)
        tb.addAction(self._random_tag_action)
        tb.addAction(self._random_comment_action)

    def _setup_status_bar(self):
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._current_modifier_hint = None
        self._show_status_bar_hint()

        self._modifier_timer = QTimer(self)
        self._modifier_timer.setInterval(150)
        self._modifier_timer.timeout.connect(self._poll_modifiers)
        self._modifier_timer.start()

    def _poll_modifiers(self):
        modifiers = QGuiApplication.queryKeyboardModifiers()
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            key = Qt.Key.Key_Control
        elif modifiers & Qt.KeyboardModifier.ShiftModifier:
            key = Qt.Key.Key_Shift
        elif modifiers & Qt.KeyboardModifier.AltModifier:
            key = Qt.Key.Key_Alt
        else:
            key = None
        if key != self._current_modifier_hint:
            self._current_modifier_hint = key
            self._show_status_bar_hint(key)

    def _show_status_bar_hint(self, modifier_key=None):
        modifier = "Ctrl" if platform.system() != "Darwin" else "\u2318"
        if modifier_key == Qt.Key.Key_Control or modifier_key == Qt.Key.Key_Meta:
            hint = f"{modifier}+Click: New Vertex  |  {modifier}+Drag: Connect Edge"
        elif modifier_key == Qt.Key.Key_Shift:
            hint = "Shift+Click: Add to Selection"
        elif modifier_key == Qt.Key.Key_Alt:
            hint = "Alt+Click: Remove from Selection  |  Alt+Drag: Move Copy"
        else:
            hint = (f"Click: Select / Deselect  |  {modifier}+Click: New Vertex  |  "
                    f"{modifier}+Drag: Connect  |  Shift+Click: Add to Selection  |  Alt+Click: Remove from Selection")
        self._status_bar.showMessage(hint)

    def _setup_central_widget(self):
        context = Context.instance()

        title_component = TitleComponent()
        title_component.set_context(context)

        list_component = ListComponent()
        list_component.set_context(context)

        comments_component = CommentsComponent()
        comments_component.set_context(context)

        tags_component = TagsComponent()
        tags_component.set_context(context)

        statistics_component = StatisticsComponent()
        statistics_component.set_context(context)

        vertex_component = VertexComponent()
        vertex_component.set_context(context)

        actions_component = DSCommitActions()
        actions_component.set_store(context.store)

        self._render_component = RenderComponent()
        self._render_component.setMinimumSize(QSize(400, 400))
        self._render_component.setMaximumSize(QSize(1000, 1000))
        self._render_component.set_context(context)

        left_spliter = QSplitter(Qt.Orientation.Vertical)
        left_spliter.addWidget(title_component)
        left_spliter.addWidget(list_component)
        left_spliter.addWidget(tags_component)
        left_spliter.addWidget(comments_component)
        left_spliter.addWidget(statistics_component)

        right_spliter = QSplitter(Qt.Orientation.Vertical)
        right_spliter.addWidget(vertex_component)
        right_spliter.addWidget(actions_component)

        main_spliter = QSplitter(Qt.Orientation.Horizontal)
        main_spliter.addWidget(left_spliter)
        main_spliter.addWidget(self._render_component)
        main_spliter.addWidget(right_spliter)

        self.setCentralWidget(main_spliter)

    def _setup_connections(self):
        notifier = DSCommitStoreNotifier.instance()

        # Database
        notifier.database_did_open.connect(self._store_database_did_open)
        notifier.database_did_close.connect(self._store_database_did_close)
        notifier.state_did_change.connect(self._store_state_did_change)
        notifier.definitions_did_change.connect(self._store_definitions_did_change)

        # Dispatch
        notifier.dispatch_error.connect(self._present_error)

        # Live Mode
        notifier.stop_live.connect(self._store_stop_live)

        # Evil
        notifier.reset_database.connect(self._store_reset_database)
        notifier.database_will_reset.connect(self._store_database_will_reset)

        # Message ?
        self._sync_logger.messageReceived.connect(self._commit_sync_log_dialog.print_message)

    # Slots
    def _open_database_triggered(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Database", self._databases_path, "Graph files (*.graph)")
        if not len(filename):
            return

        self._databases_path = QFileInfo(filename).filePath()
        self._set_database(filename)

    def _new_database_triggered(self):
        databases_path = QDir.homePath() + "/Databases/new.graph"
        filename, _ = QFileDialog.getSaveFileName(self, "New Database", databases_path, "Graph files (*.graph)")
        if not len(filename):
            return

        try:
            if os.path.exists(filename):
                os.remove(filename)

            database = Context.instance().create_database(filename)
            Context.instance().use(database)
            self._configure_window_title()
            self._validate_actions()

            settings = DSSettings()
            settings.last_file_url = filename
            settings.sync()
        except ViperError as e:
            self._except_present(e)

    def _close_database(self):
        try:
            Context.instance().close()
            self._configure_window_title()
            self._validate_actions()
        except ViperError as e:
            self._except_present(e)

    # Store Notification
    def _store_database_did_open(self):
        context = Context.instance()
        if context.graph_key.is_valid():
            self._validate_actions()
        self._inspect_database_did_open()

    def _store_database_did_close(self):
        self._validate_actions()
        self._inspect_database_did_close()

    def _store_reset_database(self):
        Context.instance().reset()

    def _store_database_will_reset(self):
        self._disable_live()

    def _store_definitions_did_change(self):
        self._inspect_definitions_did_change()

    def _store_state_did_change(self):
        store = Context.instance().store
        self._undo_action.setEnabled(store.can_undo())
        self._redo_action.setEnabled(store.can_redo())
        self._validate_actions()

    def _store_stop_live(self):
        self._disable_live()

    # Actions Slots
    def _reopen_last_database_triggered(self):
        checked = self._reopen_last_database_action.isChecked()
        settings = DSSettings()
        settings.reopen_last_file = checked
        settings.sync()

    def _forward_triggered(self):
        try:
            Context.instance().store.forward()
        except ViperError as e:
            self._except_present(e)

    def _merge_heads_triggered(self):
        try:
            Context.instance().store.reduce_heads()
        except ViperError as e:
            self._except_present(e)

    def _fetch_triggered(self):
        self._synchronize(CommitSynchronizer.MODE_FETCH)

    def _push_triggered(self):
        self._synchronize(CommitSynchronizer.MODE_PUSH)

    def _sync_triggered(self):
        self._synchronize(CommitSynchronizer.MODE_SYNC)

    def _toggle_live_manager_triggered(self):
        self._live_is_manager = not self._live_is_manager
        self._configure_live_manager_action()

    def _toggle_live_triggered(self):
        if not self._live_enabled:
            self._enable_live()
        else:
            self._disable_live()

    def _undo_triggered(self):
        Context.instance().store.undo()

    def _redo_triggered(self):
        Context.instance().store.redo()

    def _go_forward_triggered(self):
        self._commit_documents_dialog.documents().go_forward()

    def _go_back_triggered(self):
        self._commit_documents_dialog.documents().go_back()

    # Graph
    def _delete_triggered(self):
        context = Context.instance()
        context.store.dispatch("Delete Selection",
                               lambda m: script_delete_selection.delete_selection(m, context.graph_key))

    def _delete_bugged_triggered(self):
        context = Context.instance()
        context.store.dispatch("Delete Bugged Selection",
                               lambda m: script_delete_selection.delete_selection_bugged(m, context.graph_key))

    def _select_graph_triggered(self):
        dialog = SelectGraphDialog(self)
        dialog.exec()

    def _new_graph_triggered(self):
        Context.instance().new_graph()

    def _clear_graph_triggered(self):
        context = Context.instance()
        context.store.dispatch("Clear The Graph",
                               lambda m: graph_topology.clear(m, context.graph_key))

    def _inspect_document_triggered(self):
        vertex_key = self._render_component.pick_vertex()
        if vertex_key:
            self._commit_documents_dialog.documents().use_key(vertex_key.vpr_value)
            self._show_document_dialog()
            return

        edge_key = self._render_component.pick_edge()
        if edge_key:
            self._commit_documents_dialog.documents().use_key(edge_key.vpr_value)
            self._show_document_dialog()
            return

        graph_key = self._render_component.pick_graph()
        if graph_key:
            self._commit_documents_dialog.documents().use_key(graph_key.vpr_value)
            self._show_document_dialog()

    def _show_document_dialog(self):
        if not self._commit_documents_dialog.isVisible():
            ds_dialog_helper.show(self._commit_documents_dialog, self._commit_documents_dialog_geometry)

    def _random_graph_triggered(self):
        context = Context.instance()
        size = self._render_component.render_widget().size()
        rect = Graph_Rectangle()
        rect.x, rect.y, rect.w, rect.h = 0, 0, size.width(), size.height()
        context.store.dispatch("Random Graph",
                               lambda m: model_random.graph(m, context.graph_key, 5, 6, rect))

    def _random_vertex_triggered(self):
        context = Context.instance()
        size = self._render_component.render_widget().size()
        rect = Graph_Rectangle()
        rect.x, rect.y, rect.w, rect.h = 0, 0, size.width(), size.height()
        context.store.dispatch("Random Vertex",
                               lambda m: model_random.add_vertex(m, context.graph_key, rect))

    def _random_edge_triggered(self):
        if not self._has_remaining_edges():
            return

        context = Context.instance()
        topology = model_random.find_edge_topology(context.store.attachment_getting(), context.graph_key)
        if not topology:
            return

        va_label = model_tools.vertex_label(context.store.attachment_getting(), topology.va_key)
        vb_label = model_tools.vertex_label(context.store.attachment_getting(), topology.vb_key)
        label = f"Random Edge '{va_label}' - '{vb_label}'"
        context.store.dispatch(label,
                               lambda m: model_edge.add(m, context.graph_key, topology.va_key, topology.vb_key))

    def _random_tag_triggered(self):
        context = Context.instance()
        context.store.dispatch("Random Tag",
                               lambda m: model_random.tag(m, context.graph_key))

    def _random_comment_triggered(self):
        context = Context.instance()
        context.store.dispatch("Random Comment",
                               lambda m: model_random.comment(m, context.graph_key))

    def _increment_vertex_value_triggered(self):
        context = Context.instance()
        context.store.dispatch("Increment Selection Value",
                               lambda m: selection_vertices.increment_value(m, context.graph_key, 100))

    def _graph_with_missing_vertex_triggered(self):
        context = Context.instance()
        context.store.dispatch("Graph With Missing Vertex",
                               lambda m: graph_bug.create_with_missing_vertex(m, context.graph_key))

    def _graph_with_missing_vertex_properties_triggered(self):
        context = Context.instance()
        context.store.dispatch("Graph With Missing Vertex Properties",
                               lambda m: graph_bug.create_with_missing_vertex_properties(m, context.graph_key))

    def _graph_with_error_triggered(self):
        context = Context.instance()
        context.store.dispatch("Graph With Error",
                               lambda m: graph_bug.create_with_error(m, context.graph_key))

    def _restore_integrity_by_deleting_triggered(self):
        context = Context.instance()
        context.store.dispatch("Restore Integrity by Deleting",
                               lambda m: graph_integrity.restore_by_deleting(m, context.graph_key))

    def _restore_integrity_by_restoring_triggered(self):
        context = Context.instance()
        context.store.dispatch("Restore Integrity By Restoring",
                               lambda m: graph_integrity.restore_by_respawning(m, context.graph_key))

    def _restore_integrity_by_creating_triggered(self):
        context = Context.instance()
        value = model_tools.safe_next_vertex_value(context.store.attachment_getting(), context.graph_key)
        context.store.dispatch("Restore Integrity By Creating",
                               lambda m: graph_integrity.restore_by_creating(m, context.graph_key, value))

    def _killer_triggered(self):
        context = Context.instance()
        context.store.dispatch("They Have Killed Commit",
                               lambda m: graph_killer.shoot(m, context.graph_key, 1000))

    def _select_all_vertices_triggered(self):
        context = Context.instance()
        context.store.dispatch("Select All Vertices",
                               lambda m: selection_vertices.select_all(m, context.graph_key))

    def _select_all_edges_triggered(self):
        context = Context.instance()
        context.store.dispatch("Select All Edges",
                               lambda m: selection_edges.select_all(m, context.graph_key))

    def _deselect_all_vertices_triggered(self):
        context = Context.instance()
        context.store.dispatch("Deselect All Vertices",
                               lambda m: selection_vertices.deselect_all(m, context.graph_key))

    def _deselect_all_edges_triggered(self):
        context = Context.instance()
        context.store.dispatch("Deselect All Edges",
                               lambda m: selection_edges.deselect_all(m, context.graph_key))

    def _invert_vertices_selection_triggered(self):
        context = Context.instance()
        context.store.dispatch("Invert Vertices Selection",
                               lambda m: selection_vertices.invert(m, context.graph_key))

    def _invert_edges_selection_triggered(self):
        context = Context.instance()
        context.store.dispatch("Invert Edges Selection",
                               lambda m: selection_edges.invert(m, context.graph_key))

    def _select_all_triggered(self):
        context = Context.instance()
        context.store.dispatch("Select All",
                               lambda m: selection_mixed.select_all(m, context.graph_key))

    def _deselect_all_vertices_and_edges_triggered(self):
        context = Context.instance()
        context.store.dispatch("Deselect All",
                               lambda m: selection_mixed.deselect_all(m, context.graph_key))

    def _invert_selection_of_vertices_and_edges_triggered(self):
        context = Context.instance()
        context.store.dispatch("Invert Selection",
                               lambda m: selection_mixed.invert(m, context.graph_key))

    def _restore_vertex_selection_triggered(self):
        context = Context.instance()
        context.store.dispatch("Restore Vertex Selection",
                               lambda m: selection_vertices.restore(m, context.graph_key))

    ############################
    def _toggle_inspect_dialog_triggered(self):
        ds_dialog_helper.toggle(self._inspect_dialog, self._inspect_dialog_geometry)

    def _toggle_commits_dialog_triggered(self):
        ds_dialog_helper.toggle(self._commits_dialog, self._commits_dialog_geometry)

    def _toggle_commit_documents_dialog_triggered(self):
        ds_dialog_helper.toggle(self._commit_documents_dialog, self._commit_documents_dialog_geometry)

    def _toggle_commit_program_dialog_triggered(self):
        ds_dialog_helper.toggle(self._commit_program_dialog, self._commit_program_dialog_geometry)

    def _toggle_commit_settings_dialog_triggered(self):
        DSCommitStoreNotifier.instance().notify_stop_live()
        dialog = DSCommitSettingsDialog(self)
        dialog.exec()
        self._validate_actions()

    def _toggle_commit_undo_dialog_triggered(self):
        ds_dialog_helper.toggle(self._commit_undo_dialog, self._commit_undo_dialog_geometry)

    def _toggle_commit_sync_log_dialog_triggered(self):
        ds_dialog_helper.toggle(self._commit_sync_log_dialog, self._commit_sync_log_dialog_geometry)

    def _toggle_commit_blobs_dialog_triggered(self):
        ds_dialog_helper.toggle(self._commit_blobs_dialog, self._commit_blobs_dialog_geometry)

    def _toggle_commit_actions_dialog_triggered(self):
        ds_dialog_helper.toggle(self._commit_actions_dialog, self._commit_actions_dialog_geometry)

    def _toggle_code_editor_dialog_triggered(self):
        ds_dialog_helper.toggle(self._code_editor_dialog, self._code_editor_dialog_geometry)

    def _connect_to_server_triggered(self):
        dialog = DSConnectToServerDialog(self)
        dialog.exec()
        if dialog.result() == QDialog.DialogCode.Rejected:
            return

        try:
            settings = DSSettings()
            host = settings.connect_hostname
            service = settings.connect_service
            socket_path = settings.connect_socket_path
            use_socket_path = settings.connect_use_socket_path

            if use_socket_path:
                db = CommitDatabase.connect_local(socket_path)
            else:
                db = CommitDatabase.connect(host, service)
            Context.instance().use(db)

        except ViperError as e:
            self._except_present(e)

    def _validate_actions(self):
        store = Context.instance().store
        has_database = store.has_database()
        has_sos = DSSettings().has_source_of_synchronization()

        self._open_action.setEnabled(not self._live_enabled)
        self._new_action.setEnabled(not self._live_enabled)
        self._close_action.setEnabled(not self._live_enabled and has_database)
        self._toggle_inspect_dialog_action.setEnabled(has_database)

        self._forward_action.setEnabled(has_database and not self._live_enabled)
        self._merge_heads_action.setEnabled(has_database and not self._live_enabled)

        self._fetch_action.setEnabled(has_database and has_sos and not self._live_enabled)
        self._push_action.setEnabled(has_database and has_sos and not self._live_enabled)
        self._sync_action.setEnabled(has_database and has_sos and not self._live_enabled)

        self._undo_action.setEnabled(store.can_undo())
        self._redo_action.setEnabled(store.can_redo())

        self._delete_action.setEnabled(has_database and self._has_selection())
        self._delete_bugged_action.setEnabled(has_database and self._has_selection())

        self._live_manager_action.setEnabled(has_database)
        self._go_live_action.setEnabled(has_database)

        self._select_graph_action.setEnabled(has_database)
        self._new_graph_action.setEnabled(has_database)
        self._clear_graph_action.setEnabled(has_database)
        self._inspect_document_action.setEnabled(has_database)

        self._random_graph_action.setEnabled(has_database)
        self._random_vertex_action.setEnabled(has_database)
        self._random_edge_action.setEnabled(has_database and self._has_remaining_edges())
        self._random_tag_action.setEnabled(has_database)
        self._random_comment_action.setEnabled(has_database)

        self._increment_vertex_value_action.setEnabled(has_database)
        self._graph_with_missing_vertex_action.setEnabled(has_database)
        self._graph_with_missing_vertex_properties_action.setEnabled(has_database)
        self._graph_with_error_action.setEnabled(has_database)
        self._restore_integrity_by_deleting_action.setEnabled(has_database)
        self._restore_integrity_by_restoring_action.setEnabled(has_database)
        self._restore_integrity_by_creating_action.setEnabled(has_database)
        self._killer_action.setEnabled(has_database)

        self._select_all_vertices_action.setEnabled(has_database and self._has_vertices())
        self._select_all_edges_action.setEnabled(has_database and self._has_edges())
        self._deselect_all_vertices_action.setEnabled(has_database and self._has_selected_vertices())
        self._deselect_all_edges_action.setEnabled(has_database and self._has_selected_edges())
        self._invert_vertices_selection_action.setEnabled(has_database and self._has_vertices())
        self._invert_edges_selection_action.setEnabled(has_database and self._has_edges())
        self._select_all_action.setEnabled(has_database and (self._has_vertices() or self._has_edges()))
        self._deselect_all_vertices_and_edges_action.setEnabled(
            has_database and (self._has_selected_vertices() or self._has_selected_edges()))
        self._invert_selection_of_vertices_and_edges_action.setEnabled(
            has_database and (self._has_vertices() or self._has_edges()))

        self._restore_vertex_selection_action.setEnabled(has_database and self._has_selected_vertices())

    def _configure_window_title(self):
        title = "Graph Editor (PySide)"
        store = Context.instance().store

        if store.has_database():
            filename = os.path.basename(store.database().path())
            title = f'{title} - {filename}'

        self.setWindowTitle(title)

    # Help
    def _mouse_shortcuts_triggered(self):
        modifier = "Ctrl" if platform.system() != "Darwin" else "\u2318 (Cmd)"
        text = (
            "<h3>Click</h3>"
            "<table cellpadding='4'>"
            "<tr><td>Select vertex or edge</td><td><b>Click</b></td></tr>"
            "<tr><td>Deselect all</td><td><b>Click</b> on empty space</td></tr>"
            f"<tr><td>New vertex</td><td><b>{modifier}+Click</b> on empty space</td></tr>"
            "<tr><td>Add to selection</td><td><b>Shift+Click</b></td></tr>"
            "<tr><td>Remove from selection</td><td><b>Alt+Click</b></td></tr>"
            "</table>"
            "<h3>Drag</h3>"
            "<table cellpadding='4'>"
            "<tr><td>Move selection</td><td><b>Drag</b></td></tr>"
            f"<tr><td>Connect edge</td><td><b>{modifier}+Drag</b> from vertex</td></tr>"
            "<tr><td>Duplicate selection</td><td><b>Alt+Drag</b></td></tr>"
            "</table>"
        )
        dialog = QDialog(self)
        dialog.setWindowTitle("Mouse Shortcuts")
        from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton
        layout = QVBoxLayout(dialog)
        label = QLabel(text)
        label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(label)
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        layout.addWidget(ok_button)
        dialog.exec()

    # About
    def _about_triggered(self):
        ds_license.show_about_dialog(self, "Graph Editor", "Graph Editor")

    # Inspect
    def _inspect_database_did_open(self):
        inspect = self._inspect_dialog.inspect()
        database = Context.instance().store.database()
        inspect.set_path(database.path())
        inspect.set_documentation(database.documentation())
        inspect.set_uuid(database.uuid().encoded())
        inspect.set_codec_name(database.codec_name())
        inspect.set_definition_hexdigest(database.definitions_hexdigest())
        inspect.set_definitions(database.definitions())

    def _inspect_database_did_close(self):
        self._inspect_dialog.inspect().clear()

    def _inspect_definitions_did_change(self):
        self._inspect_dialog.inspect().set_definitions(Context.instance().store.definitions())

    # Live Mode
    def _configure_live_manager_action(self):
        dark = "-dark" if QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark else ""
        fill = ".fill" if self._live_is_manager else ""
        self._live_manager_action.setIcon(QIcon(f':/dsviper_components/images/person.icloud{fill}{dark}'))

    def _configure_go_live_action(self):
        dark = "-dark" if QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark else ""
        fill = ".fill" if self._live_enabled else ""
        self._go_live_action.setIcon(QIcon(f':/dsviper_components/images/arrow.triangle.2.circlepath.icloud{fill}{dark}'))

    def _enable_live(self):
        settings = DSSettings()
        live_sync = settings.live_sync_with_source

        try:
            if live_sync:
                path = Context.instance().store.database().path()
                self._synchronizer = settings.create_synchronizer(CommitSynchronizer.MODE_SYNC, path)

            self._live_enabled = True
            self._configure_go_live_action()
            self._schedule_live_timer()

        except ViperError as e:
            self._except_present(e)

    def _disable_live(self):
        self._synchronizer = None
        self._live_enabled = False
        self._live_is_manager = False

        self._configure_go_live_action()
        self._configure_live_manager_action()

    def _schedule_live_timer(self):
        live_interval = DSSettings().live_update_interval
        interval_ms = (live_interval / 10.0) * 1000.0
        QTimer.singleShot(int(interval_ms), self, self._live_timer_timeout)

    def _live_timer_timeout(self):
        if not self._live_enabled:
            return

        if self._synchronizer:
            thread = DSCommitSynchronizerThread(self._synchronizer, self._sync_logging, self)
            thread.syncDone.connect(self._live_synchronization_done)
            thread.finished.connect(thread.deleteLater)
            thread.start()
        else:
            self._live_schedule_if_safe_reduce_forward()

    def _live_synchronization_done(self, success: bool):
        if not success:
            self._disable_live()
            return

        st: DSCommitSynchronizerThread = self.sender()
        if st.info and st.info.updated_definitions():
            Context.instance().store.notify_definitions_did_change()

        self._live_schedule_if_safe_reduce_forward()

    def _live_schedule_if_safe_reduce_forward(self):
        if not self._live_safe_reduce_forward():
            self._disable_live()
        else:
            self._schedule_live_timer()

    def _live_safe_reduce_forward(self) -> bool:
        try:
            store = Context.instance().store
            if self._live_is_manager:
                store.reduce_heads()
            store.forward()
            return True
        except ViperError:
            return False

    # Database
    def _set_database(self, filename: str):
        try:
            database = CommitDatabase.open(filename)
            Context.instance().use(database)
            self._configure_window_title()
            self._validate_actions()

            settings = DSSettings()
            settings.last_file_url = filename
            settings.sync()
        except ViperError as e:
            self._except_present(e)

    def _may_reopen_last_database(self):
        settings = DSSettings()
        reopen = settings.reopen_last_file
        if not reopen:
            return

        filename = settings.last_file_url
        if not os.path.exists(filename):
            return

        self._set_database(filename)

    def _synchronize(self, mode: str):
        try:
            path = Context.instance().store.database().path()
            synchronizer = DSSettings().create_synchronizer(mode, path)
            info = synchronizer.sync(self._sync_logging)

            if info.updated_definitions():
                Context.instance().store.notify_definitions_did_change()

        except ViperError as e:
            self._except_present(e)

    def _except_present(self, e: ViperError):
        self._present_error(Error.parse(str(e)))

    def _present_error(self, error: Error):
        QMessageBox.critical(self, "Error", error.explained(),
                             QMessageBox.StandardButton.Ok,
                             QMessageBox.StandardButton.NoButton)

    def _has_vertices(self) -> bool:
        context = Context.instance()
        return graph_topology.has_vertices(context.store.attachment_getting(), context.graph_key)

    def _has_edges(self) -> bool:
        context = Context.instance()
        return graph_topology.has_edges(context.store.attachment_getting(), context.graph_key)

    def _has_selection(self) -> bool:
        context = Context.instance()
        return selection_mixed.has_selected(context.store.attachment_getting(), context.graph_key)

    def _has_selected_vertices(self) -> bool:
        context = Context.instance()
        return selection_vertices.has_selected(context.store.attachment_getting(), context.graph_key)

    def _has_selected_edges(self) -> bool:
        context = Context.instance()
        return selection_edges.has_selected(context.store.attachment_getting(), context.graph_key)

    def _has_remaining_edges(self) -> bool:
        context = Context.instance()
        return graph_topology.has_remaining_edges(context.store.attachment_getting(), context.graph_key)


def main():
    Error.set_process_name("graph_editor")

    store = Context.instance().store
    notifier = DSCommitStoreNotifier.instance()
    store.set_notifier(CommitStoreNotifying.create(notifier))

    app = QApplication(sys.argv)
    app.setApplicationDisplayName("Graph Editor")
    app.setApplicationName("Graph Editor")
    app.setApplicationVersion(ds_license.VERSION)
    app.setStyle("fusion")
    app.setWindowIcon(QIcon(":/images/ge_icon.png"))

    line_edit_filter = _LineEditUndoRedoFilter(app)
    app.installEventFilter(line_edit_filter)

    if platform.system() == "Windows":
        if QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark:
            p = app.palette()
            p.setColor(QPalette.ColorRole.AlternateBase, QColor(60, 60, 60))
            app.setPalette(p)

    # QGuiApplication.styleHints().setColorScheme(Qt.ColorScheme.Light)

    # Parse
    parser = QCommandLineParser()
    parser.addHelpOption()
    parser.addVersionOption()
    parser.addPositionalArgument("database", "Database to open.", "database")
    parser.process(app)
    arguments = parser.positionalArguments()

    database_path: str | None = None

    if len(arguments) > 1:
        parser.showHelp()
        exit(1)

    # Check if the database is present
    elif len(arguments) == 1:
        database_path = arguments[0]
        if not os.path.exists(database_path):
            print(f'No such file {database_path}.')
            exit(1)
        if not CommitDatabaseSQLite.is_compatible(database_path):
            print(f'The SQL schema is not compatible with a Digital Substrate CommitDatabase.')
            exit(1)

    window = MainWindow()
    if database_path:
        window.set_bootstrap_database_path(database_path)

    window.show()
    app.exec()


if __name__ == '__main__':
    main()
