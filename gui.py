import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGroupBox, QRadioButton, QPushButton, 
                             QLineEdit, QLabel, QFileDialog, QGridLayout, QMessageBox,
                             QProgressBar)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon

from conversion_worker import ConversionWorker


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

class LogConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RAW CAN Log Converter 1.0")
        self.setGeometry(100, 100, 600, 400)
        
        icon_path = resource_path('icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Main layout container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        
        # 1. Input Section
        self.setup_input_section()
        
        # 2. Output Section
        self.setup_output_section()
        
        # 3. Action Section (Convert button)
        self.setup_action_section()
        
        # Initialize default selections
        self.current_input_ext = "*.trc"
        self.current_input_label = "Pcan .trc"
        self.input_buttons[0].setChecked(True) # Default to first
        
        self.current_output_ext = ".log"
        self.current_output_label = "SocketCAN .log"
        self.output_buttons[-1].setChecked(True) # Default to last (SocketCAN)

    def setup_input_section(self):
        self.input_group = QGroupBox("Input Log Format")
        self.input_layout = QVBoxLayout()
        
        self.input_types = [
            ("Pcan .trc", "*.trc"),
            ("CSS .csv", "*.csv"),
            ("CSS CLx000 .txt", "*.txt"),
            ("MF4 Log .mf4", "*.mf4"),
            ("Busmaster .log", "*.log"),
            ("Motec CAN Inspector .asc", "*.asc"),
            ("Kvaser .asc", "*.asc"),
            ("Racelogic .asc", "*.asc"),
            ("RaceKeeper .csv", "*.csv"),
            ("SocketCAN .log", "*.log")
        ]
        
        button_grid = QGridLayout()
        self.input_buttons = []
        
        row = 0
        col = 0
        for i, (label, ext) in enumerate(self.input_types):
            rb = QRadioButton(label)
            rb.toggled.connect(lambda checked, e=ext, l=label: self.on_input_type_changed(checked, e, l))
            button_grid.addWidget(rb, row, col)
            self.input_buttons.append(rb)
            
            col += 1
            if col > 1: # 2 columns
                col = 0
                row += 1
                
        self.input_layout.addLayout(button_grid)
        
        file_select_layout = QHBoxLayout()
        self.input_path_line = QLineEdit()
        self.input_path_line.setPlaceholderText("Select an input file...")
        self.input_path_line.setReadOnly(True)
        
        browse_btn = QPushButton("Browse Input File")
        browse_btn.clicked.connect(self.browse_input)
        
        file_select_layout.addWidget(self.input_path_line)
        file_select_layout.addWidget(browse_btn)
        
        self.input_layout.addLayout(file_select_layout)
        self.input_group.setLayout(self.input_layout)
        self.layout.addWidget(self.input_group)

    def setup_output_section(self):
        self.output_group = QGroupBox("Output Format")
        self.output_layout = QVBoxLayout()
        
        self.output_types = [
            ("Pcan .trc", ".trc"),
            ("CSS .csv", ".csv"),
            ("CSS CLx000 .txt", ".txt"),
            ("MF4 Log .mf4", ".mf4"),
            ("Busmaster .log", ".log"),
            ("Motec CAN Inspector .asc", ".asc"),
            ("Kvaser .asc", ".asc"),
            ("Racelogic .asc", ".asc"),
            ("RaceKeeper .csv", ".csv"),
            ("SocketCAN .log", ".log")
        ]
        
        button_grid = QGridLayout()
        self.output_buttons = []
        
        row = 0
        col = 0
        for i, (label, ext) in enumerate(self.output_types):
            rb = QRadioButton(label)
            rb.toggled.connect(lambda checked, e=ext, l=label: self.on_output_type_changed(checked, e, l))
            button_grid.addWidget(rb, row, col)
            self.output_buttons.append(rb)
            
            col += 1
            if col > 1: # 2 columns
                col = 0
                row += 1
                
        # Set default selection manually since we added items asynchronously
        if len(self.output_buttons) > 8:
            self.output_buttons[8].setChecked(True)
                
        self.output_layout.addLayout(button_grid)
        
        info_label = QLabel("Output files will be automatically generated with '_out' appended\nin the same directory as the input file(s).")
        self.output_layout.addWidget(info_label)
        
        self.output_group.setLayout(self.output_layout)
        self.layout.addWidget(self.output_group)

    def setup_action_section(self):
        action_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        action_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        action_layout.addWidget(self.status_label)
        
        self.convert_btn = QPushButton("Convert")
        self.convert_btn.setMinimumHeight(40)
        self.convert_btn.clicked.connect(self.run_conversion) 
        action_layout.addWidget(self.convert_btn)
        
        self.layout.addLayout(action_layout)

    def on_input_type_changed(self, checked, ext, label):
        if checked:
            self.current_input_ext = ext
            self.current_input_label = label

    def on_output_type_changed(self, checked, ext, label):
        if checked:
            self.current_output_ext = ext
            self.current_output_label = label

    def browse_input(self):
        file_filter = f"Log Files ({self.current_input_ext});;All Files (*)"
        filenames, _ = QFileDialog.getOpenFileNames(self, "Select Input Log File(s)", "", file_filter)
        if filenames:
            self.input_paths = filenames
            self.input_path_line.setText("; ".join([os.path.basename(f) for f in filenames]))

    def run_conversion(self):
        if not hasattr(self, 'input_paths') or not self.input_paths:
            QMessageBox.warning(self, "Missing Info", "Please select input files.")
            return

        existing_files = []
        for input_file in self.input_paths:
            base, _ = os.path.splitext(input_file)
            ext = self.current_output_ext
            output_file = f"{base}_out{ext}"
            if os.path.exists(output_file):
                existing_files.append(os.path.basename(output_file))
                
        if existing_files:
            msg = QMessageBox(self)
            msg.setWindowTitle("File Exists")
            text = f"The following file(s) already exist and will be overwritten:\n{', '.join(existing_files[:3])}"
            if len(existing_files) > 3: text += " ..."
            msg.setText(text)
            msg.setInformativeText("Do you want to overwrite them?")
            msg.setIcon(QMessageBox.Icon.Warning)
            
            overwrite_btn = msg.addButton("Overwrite", QMessageBox.ButtonRole.AcceptRole)
            cancel_btn = msg.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
            
            msg.exec()
            
            if msg.clickedButton() == cancel_btn:
                return

        self.convert_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        
        # Start dots animation
        self.dots_timer = QTimer(self)
        self.dots_timer.timeout.connect(self.update_dots)
        self.dots_timer.start(750)
        self.dots_count = 0
        self.base_status_text = "Converting..."
        
        input_type = getattr(self, 'current_input_label', "Pcan .trc")
        output_type = getattr(self, 'current_output_label', "SocketCAN .log")

        self.worker = ConversionWorker(self.input_paths, input_type, output_type)
        self.worker.progress_update.connect(self.update_progress)
        self.worker.status_update.connect(self.update_status_text)
        self.worker.finished.connect(self.conversion_finished)
        self.worker.error.connect(self.conversion_error)
        self.worker.file_in_use_signal.connect(self.handle_file_in_use)
        self.worker.start()

    def update_dots(self):
        self.dots_count = (self.dots_count + 1) % 4
        self.status_label.setText(self.base_status_text + "." * self.dots_count)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status_text(self, text):
        self.base_status_text = text
        self.status_label.setText(text)

    def handle_file_in_use(self, filename):
        self.dots_timer.stop()
        self.status_label.setText("Error: File in use")
        QMessageBox.critical(self, "File In Use", f"The file is currently open in another program:\n{filename}\n\nPlease close it and try again.")
        self.convert_btn.setEnabled(True)

    def conversion_finished(self):
        self.dots_timer.stop()
        self.progress_bar.setValue(100)
        self.status_label.setText("Conversion Complete")
        self.convert_btn.setEnabled(True)
        QMessageBox.information(self, "Success", "File conversion completed successfully!")

    def conversion_error(self, err_msg):
        self.dots_timer.stop()
        self.status_label.setText("Conversion Failed")
        self.convert_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", f"An error occurred during conversion:\n{err_msg}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LogConverterApp()
    window.show()
    sys.exit(app.exec())
