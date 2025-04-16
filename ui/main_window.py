from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QShortcut)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence
from Emperor.ui.panels import ControlPanel, StatsPanel, ButtonPanel, LogConsole
from Emperor.utils.config_manager import ConfigManager
import pygetwindow as gw


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SWTOR Guild Recruiter")
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setMinimumSize(600, 400)

        # Initialize configuration
        self.config_manager = ConfigManager()

        # Initialize state variables
        self.is_running = False
        self.is_paused = False
        self.current_range = None
        self.recruits_count = 0
        self.total_processed = 0
        self.failed_invites = 0

        self.init_ui()
        self.setup_hotkeys()
        self.setup_connections()
        self.setup_timers()
        self.restore_window_state()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Initialize panels
        self.control_panel = ControlPanel(self)
        self.stats_panel = StatsPanel(self)
        self.button_panel = ButtonPanel(self)
        self.log_console = LogConsole(self)

        # Add panels to main layout
        main_layout.addWidget(self.control_panel)
        main_layout.addWidget(self.stats_panel)
        main_layout.addWidget(self.button_panel)
        main_layout.addWidget(self.log_console)

    def setup_hotkeys(self):
        QShortcut(QKeySequence("Alt+F10"), self).activated.connect(self.start_recruitment)
        QShortcut(QKeySequence("Alt+F11"), self).activated.connect(self.stop_recruitment)
        QShortcut(QKeySequence("Alt+F12"), self).activated.connect(self.toggle_pause)

    def setup_connections(self):
        # Connect button signals
        self.button_panel.start_button.clicked.connect(self.start_recruitment)
        self.button_panel.stop_button.clicked.connect(self.stop_recruitment)
        self.button_panel.pause_button.clicked.connect(self.toggle_pause)

    def setup_timers(self):
        # Game window monitoring timer
        self.game_check_timer = QTimer()
        self.game_check_timer.timeout.connect(self.check_game_window)
        self.game_check_timer.start(1000)  # Check every second

        # Auto-save timer
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(30000)  # Save every 30 seconds

    def start_recruitment(self):
        if not self.validate_input():
            return

        self.is_running = True
        self.is_paused = False
        self.update_status()
        self.log_console.log_message("Recruitment started", "green")

    def stop_recruitment(self):
        self.is_running = False
        self.is_paused = False
        self.update_status()
        self.log_console.log_message("Recruitment stopped", "yellow")

    def toggle_pause(self):
        if self.is_running:
            self.is_paused = not self.is_paused
            status = "paused" if self.is_paused else "resumed"
            self.log_console.log_message(f"Recruitment {status}", "yellow")
            self.update_status()

    def validate_input(self):
        try:
            range_value = int(self.control_panel.range_input.text())
            if not 1 <= range_value <= 80:
                self.log_console.log_message("Range must be between 1 and 80", "red")
                return False
            return True
        except ValueError:
            self.log_console.log_message("Please enter a valid number for the range", "red")
            return False

    def update_status(self):
        status = "Paused" if self.is_paused else "Running" if self.is_running else "Stopped"
        stats = {
            'current_range': self.current_range or '--',
            'recruits': self.recruits_count,
            'processed': self.total_processed,
            'failed': self.failed_invites,
            'status': status
        }
        self.stats_panel.update_stats(stats)

    def check_game_window(self):
        if self.is_running and not self.is_paused:
            swtor_window = None
            try:
                for window in gw.getWindowsWithTitle("Star Wars™: The Old Republic™"):
                    if "Star Wars™: The Old Republic™" in window.title:
                        swtor_window = window
                        break

                if not swtor_window or not swtor_window.isActive:
                    self.toggle_pause()
                    self.log_console.log_message("Game window lost focus - Paused", "yellow")
            except Exception as e:
                self.log_console.log_message(f"Error checking game window: {str(e)}", "red")

    def auto_save(self):
        if self.is_running or self.is_paused:
            self.config_manager.save_state({
                'is_running': self.is_running,
                'is_paused': self.is_paused,
                'current_range': self.current_range,
                'recruits_count': self.recruits_count,
                'total_processed': self.total_processed,
                'failed_invites': self.failed_invites
            })

    def closeEvent(self, event):
        self.config_manager.save_window_geometry(self.pos(), self.size())
        super().closeEvent(event)

    def restore_window_state(self):
        geometry = self.config_manager.get_window_geometry()
        if geometry:
            self.setGeometry(*geometry)