import sys
import subprocess
import tempfile
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QPlainTextEdit, QLabel, QMessageBox, QComboBox,
    QMenuBar, QMenu, QAction, QFrame, QSizePolicy
)
from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView

DARK_STYLESHEET = '''
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #23243a, stop:1 #2e2f4f);
    border-radius: 32px;
}
QWidget {
    background: transparent;
}
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4f8cff, stop:1 #6a5cff);
    color: #fff;
    border: none;
    border-radius: 18px;
    padding: 10px 24px;
    font-size: 1.1em;
    font-weight: 600;
    margin: 0 8px;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6a5cff, stop:1 #4f8cff);
}
QPlainTextEdit {
    background: #23243a;
    color: #e0e6ff;
    border-radius: 18px;
    font-family: 'Fira Mono', 'Consolas', monospace;
    font-size: 1.1em;
    padding: 16px;
}
QTabBar::tab {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4f8cff, stop:1 #6a5cff);
    color: #fff;
    border-radius: 18px;
    min-width: 120px;
    min-height: 36px;
    margin: 6px;
    font-size: 1.1em;
    padding: 8px 20px;
}
QTabBar::tab:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6a5cff, stop:1 #4f8cff);
    color: #fff;
}
QTabWidget::pane {
    border: none;
    border-radius: 24px;
    margin: 0px 0px 0px 0px;
}
QFrame#Sidebar {
    background: #23243a;
    border-radius: 24px;
    min-width: 70px;
    max-width: 120px;
    margin-right: 18px;
}
QLabel#SidebarLabel {
    color: #bfc6e0;
    font-size: 1.2em;
    font-weight: 600;
    padding: 24px 0 0 0;
    text-align: center;
}
'''

LIGHT_STYLESHEET = DARK_STYLESHEET.replace('#23243a', '#f4f6fa').replace('#2e2f4f', '#e0e6f6').replace('#e0e6ff', '#23243a').replace('#bfc6e0', '#23243a')

class RoundedTabWidget(QTabWidget):
    def __init__(self):
        super().__init__()

class FuturIDE(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FuturIDE Desktop")
        self.resize(1100, 700)
        self.theme = 'dark'
        self.setStyleSheet(DARK_STYLESHEET)
        self.init_ui()

    def init_ui(self):
        # Menu bar
        menubar = self.menuBar()
        menubar.setStyleSheet('QMenuBar { font-size: 1.1em; background: transparent; color: #e0e6ff; } QMenuBar::item:selected { background: #4f8cff; border-radius: 8px; }')
        file_menu = menubar.addMenu('File')
        edit_menu = menubar.addMenu('Edit')
        selection_menu = menubar.addMenu('Selection')
        view_menu = menubar.addMenu('View')
        run_menu = menubar.addMenu('Run')
        terminal_menu = menubar.addMenu('Terminal')
        # Example actions
        file_menu.addAction('Open', self.open_file)
        file_menu.addAction('Save', self.save_file)
        file_menu.addSeparator()
        file_menu.addAction('Exit', self.close)
        run_menu.addAction('Run', self.run_code)

        # Central widget with sidebar and main area
        central = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName('Sidebar')
        self.sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        sidebar_label = QLabel('☰')
        sidebar_label.setObjectName('SidebarLabel')
        sidebar_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        sidebar_layout.addWidget(sidebar_label)
        sidebar_layout.addStretch()
        self.sidebar.setLayout(sidebar_layout)
        main_layout.addWidget(self.sidebar)

        # Main vertical layout (top bar + tabs + output)
        main_vbox = QVBoxLayout()
        main_vbox.setContentsMargins(24, 24, 24, 24)
        main_vbox.setSpacing(18)

        # Top bar with file, run, and theme switcher
        top_bar = QHBoxLayout()
        self.open_btn = QPushButton("Open")
        self.save_btn = QPushButton("Save")
        self.run_btn = QPushButton("Run")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.setCurrentIndex(0)
        self.theme_combo.setStyleSheet('''
            QComboBox {
                border-radius: 12px;
                padding: 6px 18px;
                font-size: 1.05em;
                background: #23243a;
                color: #fff;
            }
            QComboBox QAbstractItemView {
                background: #23243a;
                color: #fff;
                border-radius: 12px;
            }
        ''')
        top_bar.addWidget(self.open_btn)
        top_bar.addWidget(self.save_btn)
        top_bar.addWidget(self.run_btn)
        top_bar.addStretch()
        top_bar.addWidget(QLabel("Theme:"))
        top_bar.addWidget(self.theme_combo)
        main_vbox.addLayout(top_bar)

        # Tabs for C, Python, HTML
        self.tabs = RoundedTabWidget()
        self.editors = {}
        self.html_view = QWebEngineView()
        for lang in ["Python", "C", "HTML"]:
            editor = QPlainTextEdit()
            editor.setPlaceholderText(f"Write your {lang} code here...")
            self.editors[lang] = editor
            tab = QWidget()
            tab_layout = QVBoxLayout()
            tab_layout.addWidget(editor)
            if lang == "HTML":
                tab_layout.addWidget(self.html_view)
            tab.setLayout(tab_layout)
            self.tabs.addTab(tab, lang)
        main_vbox.addWidget(self.tabs)

        # Output area
        self.output_label = QLabel("Output will appear here.")
        self.output_label.setStyleSheet('''
            background: #181c20;
            color: #bfc6e0;
            border-radius: 18px;
            padding: 16px;
            font-size: 1.05em;
        ''')
        main_vbox.addWidget(self.output_label)

        main_layout.addLayout(main_vbox)
        central.setLayout(main_layout)
        self.setCentralWidget(central)

        # Connect buttons
        self.open_btn.clicked.connect(self.open_file)
        self.save_btn.clicked.connect(self.save_file)
        self.run_btn.clicked.connect(self.run_code)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.theme_combo.currentIndexChanged.connect(self.switch_theme)

    def switch_theme(self, idx):
        if idx == 0:
            self.theme = 'dark'
            self.setStyleSheet(DARK_STYLESHEET)
            self.output_label.setStyleSheet('''
                background: #181c20;
                color: #bfc6e0;
                border-radius: 18px;
                padding: 16px;
                font-size: 1.05em;
            ''')
            self.theme_combo.setStyleSheet('''
                QComboBox {
                    border-radius: 12px;
                    padding: 6px 18px;
                    font-size: 1.05em;
                    background: #23243a;
                    color: #fff;
                }
                QComboBox QAbstractItemView {
                    background: #23243a;
                    color: #fff;
                    border-radius: 12px;
                }
            ''')
        else:
            self.theme = 'light'
            self.setStyleSheet(LIGHT_STYLESHEET)
            self.output_label.setStyleSheet('''
                background: #f4f6fa;
                color: #23243a;
                border-radius: 18px;
                padding: 16px;
                font-size: 1.05em;
            ''')
            self.theme_combo.setStyleSheet('''
                QComboBox {
                    border-radius: 12px;
                    padding: 6px 18px;
                    font-size: 1.05em;
                    background: #fff;
                    color: #23243a;
                }
                QComboBox QAbstractItemView {
                    background: #fff;
                    color: #23243a;
                    border-radius: 12px;
                }
            ''')

    def open_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Python (*.py);;C (*.c);;HTML (*.html)")
        if fname:
            with open(fname, 'r', encoding='utf-8', errors='replace') as f:
                code = f.read()
            current_lang = self.tabs.tabText(self.tabs.currentIndex())
            self.editors[current_lang].setPlainText(code)
            if current_lang == "HTML":
                self.html_view.setHtml(code)

    def save_file(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*);;Python (*.py);;C (*.c);;HTML (*.html)")
        if fname:
            current_lang = self.tabs.tabText(self.tabs.currentIndex())
            code = self.editors[current_lang].toPlainText()
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(code)

    def run_code(self):
        current_lang = self.tabs.tabText(self.tabs.currentIndex())
        code = self.editors[current_lang].toPlainText()
        if current_lang == "Python":
            self.run_python(code)
        elif current_lang == "C":
            self.run_c(code)
        elif current_lang == "HTML":
            self.html_view.setHtml(code)
            self.output_label.setText("HTML preview updated below.")

    def run_python(self, code):
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.py') as f:
            f.write(code)
            fname = f.name
        try:
            proc = subprocess.run([sys.executable, fname], capture_output=True, text=True, timeout=5)
            output = proc.stdout
            error = proc.stderr
            if error:
                self.output_label.setText(f"<b>Error:</b>\n{error}")
            else:
                self.output_label.setText(f"<b>Output:</b>\n{output}")
        except Exception as e:
            self.output_label.setText(f"<b>Exception:</b> {str(e)}")
        finally:
            os.unlink(fname)

    def run_c(self, code):
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.c') as f:
            f.write(code)
            cfile = f.name
        exefile = cfile[:-2] + ('.exe' if os.name == 'nt' else '')
        try:
            compile_proc = subprocess.run(['gcc', cfile, '-o', exefile], capture_output=True, text=True, timeout=5)
            if compile_proc.returncode != 0:
                self.output_label.setText(f"<b>Compile Error:</b>\n{compile_proc.stderr}")
            else:
                run_proc = subprocess.run([exefile], capture_output=True, text=True, timeout=5)
                output = run_proc.stdout
                error = run_proc.stderr
                if error:
                    self.output_label.setText(f"<b>Error:</b>\n{error}")
                else:
                    self.output_label.setText(f"<b>Output:</b>\n{output}")
        except Exception as e:
            self.output_label.setText(f"<b>Exception:</b> {str(e)}")
        finally:
            if os.path.exists(cfile):
                os.unlink(cfile)
            if os.path.exists(exefile):
                try:
                    os.unlink(exefile)
                except Exception:
                    pass

    def on_tab_changed(self, idx):
        current_lang = self.tabs.tabText(idx)
        if current_lang == "HTML":
            code = self.editors["HTML"].toPlainText()
            self.html_view.setHtml(code)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FuturIDE()
    window.show()
    sys.exit(app.exec_()) 