from PyQt5.QtWidgets import (QComboBox, QLineEdit, QPushButton, QTextEdit,
                            QLabel, QGridLayout, QHBoxLayout)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
from datetime import datetime, timezone, timedelta
from Emperor.ui.styled_widget import StyledWidget


class ControlPanel(StyledWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        layout = QGridLayout(self)

        # Faction selector
        faction_label = QLabel("Faction:")
        faction_label.setFont(QFont('Arial', 10, QFont.Bold))
        self.faction_selector = QComboBox()
        self.faction_selector.addItems(["Light Side", "Dark Side"])

        # Range input
        range_label = QLabel("Range:")
        range_label.setFont(QFont('Arial', 10, QFont.Bold))
        self.range_input = QLineEdit()
        self.range_input.setPlaceholderText("Enter range (1-80)")

        # Next range label
        self.next_range_label = QLabel("Next range will be: --")
        self.next_range_label.setStyleSheet("color: #666;")

        # Add widgets to layout
        layout.addWidget(faction_label, 0, 0)
        layout.addWidget(self.faction_selector, 0, 1)
        layout.addWidget(range_label, 0, 2)
        layout.addWidget(self.range_input, 0, 3)
        layout.addWidget(self.next_range_label, 1, 0, 1, 4)

        # Connect signals
        self.range_input.textChanged.connect(self.update_next_range)
        self.faction_selector.currentTextChanged.connect(self.on_faction_changed)

    def update_next_range(self):
        try:
            current_range = int(self.range_input.text())
            if 1 <= current_range <= 80:
                next_start = current_range + 1
                next_end = min(next_start + current_range - 1, 80)
                self.next_range_label.setText(f"Next range will be: {next_start}-{next_end}")
            else:
                self.next_range_label.setText("Range must be between 1-80")
        except ValueError:
            self.next_range_label.setText("Please enter a valid number")

    def on_faction_changed(self, faction):
        self.main_window.config_manager.save_faction(faction)


class StatsPanel(StyledWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        layout = QGridLayout(self)

        self.stats_labels = {
            'current_range': QLabel("Current Range: --"),
            'recruits': QLabel("Recruits: 0"),
            'processed': QLabel("Total Processed: 0"),
            'failed': QLabel("Failed Invites: 0"),
            'status': QLabel("Status: Stopped")
        }

        row = 0
        for label in self.stats_labels.values():
            label.setFont(QFont('Arial', 9))
            layout.addWidget(label, row, 0)
            row += 1

    def update_stats(self, stats):
        for key, value in stats.items():
            if key in self.stats_labels:
                self.stats_labels[key].setText(f"{key.replace('_', ' ').title()}: {value}")


class ButtonPanel(StyledWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        layout = QHBoxLayout(self)

        self.start_button = QPushButton("Start (Alt+F10)")
        self.stop_button = QPushButton("Stop (Alt+F11)")
        self.pause_button = QPushButton("Pause (Alt+F12)")

        for button in [self.start_button, self.stop_button, self.pause_button]:
            button.setMinimumWidth(120)
            button.setStyleSheet("""
                QPushButton {
                    padding: 8px;
                    background-color: #fff;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
                QPushButton:pressed {
                    background-color: #e0e0e0;
                }
            """)
            layout.addWidget(button)


class LogConsole(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setReadOnly(True)
        self.setFont(QFont('Consolas', 9))
        self.setStyleSheet("""
            QTextEdit {
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        self.max_lines = 100

    def log_message(self, message, color="black"):
        current_time = datetime.now(timezone(timedelta(hours=-4))).strftime("%m/%d/%Y %I:%M:%S %p")
        formatted_message = f"[{current_time}] {message}"

        colors = {
            "black": "#000000",
            "red": "#FF0000",
            "green": "#008000",
            "yellow": "#808000"
        }

        self.setTextColor(QColor(colors.get(color, "#000000")))
        self.append(formatted_message)

        # Limit to 100 lines
        text = self.toPlainText()
        lines = text.split('\n')
        if len(lines) > self.max_lines:
            self.setPlainText('\n'.join(lines[-self.max_lines:]))