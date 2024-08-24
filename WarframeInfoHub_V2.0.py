# Copyright (c) 2024 LexyGuru
# This file is part of the API_Warframe_Cross_GUI project, licensed under the MIT License.
# For the full license text, see the LICENSE file in the project root.

import sys
import platform
import requests
import markdown
import warnings
import os
import tempfile
import logging
import argparse
import importlib.metadata
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
                             QScrollArea, QSizePolicy, QMessageBox, QPushButton, QLabel, QColorDialog, QDialog)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings
from PyQt5.QtCore import QObject, pyqtSlot, QUrl, Qt, QCoreApplication, QSettings
from PyQt5.QtGui import QDesktopServices, QFont, QFontDatabase, QColor
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR

# Próbáljuk importálni a QWebEngineProfile-t, ha elérhető
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineProfile
except ImportError:
    QWebEngineProfile = None

print("Qt: v", QT_VERSION_STR, "\tPyQt: v", PYQT_VERSION_STR)

def get_platform_specific_styles():
    base_style = """
        QMainWindow {
            background-color: #f5f5f5;
        }
        QLabel {
            font-size: 14px;
        }
    """

    if sys.platform == 'darwin':  # macOS
        return base_style + """
            QTreeWidget {
                font-size: 13px;
            }
            QPushButton {
                border-radius: 5px;
            }
        """
    elif sys.platform == 'win32':  # Windows
        return base_style + """
            QTreeWidget {
                font-size: 11px;
            }
            QPushButton {
                border-radius: 3px;
            }
        """
    else:  # Linux és egyéb
        return base_style

# Figyelmeztetések kezelése
warnings.filterwarnings("ignore", category=DeprecationWarning)

# InsecureRequestWarning kezelése
try:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
except ImportError:
    try:
        from urllib3.exceptions import InsecureRequestWarning
    except ImportError:
        class InsecureRequestWarning(Warning):
            pass

warnings.filterwarnings("ignore", category=InsecureRequestWarning)

# Naplózás beállítása
logging.basicConfig(level=logging.DEBUG if '--debug' in sys.argv else logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def check_compatibility():
    os_name = platform.system().lower()
    os_version = platform.version()
    architecture = platform.machine().lower()
    python_version = sys.version_info

    required_packages = ['PyQt5', 'requests', 'markdown']
    missing_packages = []
    for package in required_packages:
        try:
            importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            missing_packages.append(package)

    is_compatible = True
    compatibility_issues = []

    if os_name not in ['windows', 'linux', 'darwin']:
        is_compatible = False
        compatibility_issues.append(f"A(z) {os_name.capitalize()} operációs rendszer nem támogatott.")

    supported_architectures = ['x86_64', 'amd64', 'arm64', 'armv7l']
    if architecture not in supported_architectures:
        is_compatible = False
        compatibility_issues.append(f"A(z) {architecture} architektúra nem támogatott.")

    if python_version.major != 3 or python_version.minor < 6:
        is_compatible = False
        compatibility_issues.append(
            f"A Python {python_version.major}.{python_version.minor}"
            f" verzió nem támogatott. Python 3.6 vagy újabb szükséges.")

    return is_compatible, os_name, os_version, architecture, python_version, missing_packages, compatibility_issues

def show_compatibility_popup():
    is_compatible, os_name, os_version, architecture, python_version, missing_packages, compatibility_issues = (
        check_compatibility())

    msg = QMessageBox()
    msg.setWindowTitle("Rendszer Kompatibilitás Ellenőrzés")

    font = QFont()
    font.setPointSize(10)
    msg.setFont(font)

    message = f"Operációs rendszer: {os_name.capitalize()} ({os_version})\n"
    message += f"CPU architektúra: {architecture}\n"
    message += f"Python verzió: {python_version.major}.{python_version.minor}.{python_version.micro}\n\n"

    if missing_packages:
        if sys.platform == 'darwin':
            message += f"Hiányzó függőségek: {', '.join(missing_packages)}\n\n"
            message += "Ettöl függetlenül müködik hiba eseten forditsad le az appot a gepeden\n\n"
        if sys.platform == 'win32':
            message += f"Hiányzó függőségek: {', '.join(missing_packages)}\n\n"
    else:
        message += "Minden szükséges függőség telepítve van.\n\n"

    if is_compatible:
        message += "A program kompatibilis a jelenlegi rendszerrel."
        msg.setIcon(QMessageBox.Information)
    else:
        message += "Kompatibilitási problémák:\n"
        for issue in compatibility_issues:
            message += f"- {issue}\n"
        message += "\nA program futhat, de a teljes funkcionalitás nem garantált."
        msg.setIcon(QMessageBox.Warning)

    msg.setText(message)
    msg.setStandardButtons(QMessageBox.Ok)

    return msg.exec_(), is_compatible

def get_platform_specific_settings():
    system = platform.system().lower()
    settings = {
        'font_family': 'Arial',
        'font_size': 10,
        'stylesheet': ''
    }

    if system == 'darwin':  # macOS
        settings['font_family'] = '.AppleSystemUIFont'  # Ez egy általános rendszer betűtípus macOS-en
        settings['font_size'] = 13
    elif system == 'windows':
        settings['font_family'] = 'Segoe UI'
        settings['font_size'] = 9
    elif system == 'linux':
        settings['font_family'] = 'Ubuntu'
        settings['font_size'] = 11

    # Ellenőrizzük, hogy a kiválasztott betűtípus elérhető-e
    available_fonts = QFontDatabase().families()
    if settings['font_family'] not in available_fonts:
        # Ha nem elérhető, használjunk egy alapértelmezett betűtípust
        settings['font_family'] = 'Arial'

    settings['stylesheet'] = f"""
        QWidget {{
            font-family: {settings['font_family']};
            font-size: {settings['font_size']}pt;
        }}
    """

    return settings

def get_temp_directory():
    return tempfile.gettempdir()

def get_cache_directory():
    system = platform.system().lower()
    if system == 'windows':
        return os.path.join(os.environ.get('LOCALAPPDATA'), 'WarframeInfoHub')
    elif system == 'darwin':
        return os.path.expanduser('~/Library/Caches/WarframeInfoHub')
    else:  # Linux és egyéb
        return os.path.expanduser('~/.cache/WarframeInfoHub')

class WebBridge(QObject):
    @pyqtSlot(str)
    def open_url(self, url):
        QDesktopServices.openUrl(QUrl(url))

class CustomWebEnginePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        print(f"JS Console: {message} (line {lineNumber}, source: {sourceID})")

class ThemeSelector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.light_dark_layout = QHBoxLayout()
        self.light_button = QPushButton("Világos téma")
        self.dark_button = QPushButton("Sötét téma")
        self.light_dark_layout.addWidget(self.light_button)
        self.light_dark_layout.addWidget(self.dark_button)
        self.layout.addLayout(self.light_dark_layout)

        self.custom_button = QPushButton("Egyéni téma")
        self.layout.addWidget(self.custom_button)

        self.light_button.clicked.connect(lambda: self.set_theme("light"))
        self.dark_button.clicked.connect(lambda: self.set_theme("dark"))
        self.custom_button.clicked.connect(self.open_custom_theme_dialog)

        self.settings = QSettings("WarframeInfoHub", "ThemeSettings")
        self.load_theme()

    def set_theme(self, theme):
        if theme == "light":
            stylesheet = """
                QWidget { background-color: #ffffff; color: #000000; }
                QPushButton { background-color: #e0e0e0; border: 1px solid #b0b0b0; padding: 5px; }
                QTreeWidget { 
                    border: 1px solid #d0d0d0;
                    background-color: #f0f0f0;
                    color: #333333;
                }
                QTreeWidget::item { 
                    padding: 5px;
                    border-bottom: 1px solid #e0e0e0;
                }
                QTreeWidget::item:selected { 
                    background-color: #a0a0a0;
                    color: #ffffff;
                }
                QScrollArea { background-color: #f0f0f0; }
                QWebEngineView { background-color: #ffffff; }
            """
        elif theme == "dark":
            stylesheet = """
                QWidget { background-color: #2b2b2b; color: #ffffff; }
                QPushButton { background-color: #3b3b3b; border: 1px solid #505050; padding: 5px; }
                QTreeWidget { 
                    border: 1px solid #505050;
                    background-color: #1b1b1b;
                    color: #e0e0e0;
                }
                QTreeWidget::item { 
                    padding: 5px;
                    border-bottom: 1px solid #3b3b3b;
                }
                QTreeWidget::item:selected { 
                    background-color: #505050;
                    color: #ffffff;
                }
                QScrollArea { background-color: #1b1b1b; }
                QWebEngineView { background-color: #2b2b2b; }
            """
        else:  # custom theme
            custom_theme = self.load_custom_theme()
            if custom_theme:
                stylesheet = self.create_stylesheet_from_theme(custom_theme)
            else:
                stylesheet = """
                    /* ... (light téma stílus) ... */
                """
                theme = "light"

        QApplication.instance().setStyleSheet(stylesheet)
        self.settings.setValue("theme", theme)
        self.settings.setValue("stylesheet", stylesheet)
        if theme == "custom" and custom_theme:
            self.settings.setValue("custom_theme", json.dumps(custom_theme))
        else:
            self.settings.remove("custom_theme")
        self.settings.sync()  # Azonnal mentsük a beállításokat

        # Frissítjük a WebEngineView tartalmát és a felhasználói felületet
        main_window = self.window()  # Get the main window
        if hasattr(main_window, 'current_theme'):
            main_window.current_theme = theme
        if hasattr(main_window, 'custom_theme'):
            main_window.custom_theme = custom_theme if theme == "custom" else None
        if hasattr(main_window, 'refresh_ui'):
            main_window.refresh_ui()
    def load_theme(self):
        theme = self.settings.value("theme", "light")
        stylesheet = self.settings.value("stylesheet", "")
        if stylesheet:
            QApplication.instance().setStyleSheet(stylesheet)
        else:
            self.set_theme(theme)

    def open_custom_theme_dialog(self):
        dialog = CustomThemeDialog(self)
        if dialog.exec_():
            custom_theme = dialog.get_theme()
            self.save_custom_theme(custom_theme)
            self.set_theme("custom")

    def save_custom_theme(self, theme):
        with open('custom_theme.json', 'w') as f:
            json.dump(theme, f)

    def load_custom_theme(self):
        try:
            with open('custom_theme.json', 'r') as f:
                theme = json.load(f)
            # Ellenőrizzük, hogy minden szükséges kulcs megvan-e
            required_keys = ['background', 'text', 'button', 'border', 'highlight']
            if all(key in theme for key in required_keys):
                return theme
            else:
                print("Custom theme file is missing required keys. Using default theme.")
                return None
        except FileNotFoundError:
            print("Custom theme file not found. Using default theme.")
            return None
        except json.JSONDecodeError:
            print("Invalid JSON in custom theme file. Using default theme.")
            return None

    def create_stylesheet_from_theme(self, theme):
        return f"""
            QWidget {{ background-color: {theme['background']}; color: {theme['text']}; }}
            QPushButton {{ background-color: {theme['button']}; border: 1px solid {theme['border']}; padding: 5px; }}
            QTreeWidget {{ 
                border: none;
                background-color: {theme['background']};
                color: {theme['text']};
            }}
            QTreeWidget::item {{ 
                padding: 10px;
                border-bottom: 1px solid {theme['border']};
            }}
            QTreeWidget::item:hover {{
                background-color: {theme['highlight']};
            }}
            QTreeWidget::item:selected {{ 
                background-color: {theme['highlight']};
                color: {theme['text']};
            }}
            QScrollArea {{ background-color: {theme['background']}; }}
            QWebEngineView {{ background-color: {theme['background']}; }}
        """


class CustomThemeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Egyéni téma beállítások")
        self.layout = QVBoxLayout(self)

        self.color_pickers = {}
        for color_name in ["Háttér", "Szöveg", "Gomb", "Keret", "Kijelölés"]:
            hbox = QHBoxLayout()
            hbox.addWidget(QLabel(f"{color_name} szín:"))
            color_button = QPushButton()
            color_button.clicked.connect(lambda _, cn=color_name: self.pick_color(cn))
            hbox.addWidget(color_button)
            self.layout.addLayout(hbox)
            self.color_pickers[color_name.lower()] = color_button

        self.buttons = QHBoxLayout()
        self.save_button = QPushButton("Mentés")
        self.cancel_button = QPushButton("Mégse")
        self.buttons.addWidget(self.save_button)
        self.buttons.addWidget(self.cancel_button)
        self.layout.addLayout(self.buttons)

        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def pick_color(self, color_name):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_pickers[color_name.lower()].setStyleSheet(f"background-color: {color.name()}")

    def get_theme(self):
        return {
            "background": self.color_pickers["háttér"].palette().button().color().name(),
            "text": self.color_pickers["szöveg"].palette().button().color().name(),
            "button": self.color_pickers["gomb"].palette().button().color().name(),
            "border": self.color_pickers["keret"].palette().button().color().name(),
            "highlight": self.color_pickers["kijelölés"].palette().button().color().name()
        }


class GitHubMainWindow(QMainWindow):
    GITHUB_RAW_URL = "https://raw.githubusercontent.com/LexyGuru/Warframe_Api_Main/main/"

    def __init__(self, debug=False):
        super().__init__()
        self.debug = debug
        self.platform_settings = get_platform_specific_settings()
        self.settings = QSettings("WarframeInfoHub", "ThemeSettings")
        self.current_theme = self.settings.value("theme", "light")
        self.current_page = "home"  # Alapértelmezett oldal

        custom_theme_str = self.settings.value("custom_theme", "{}")
        try:
            self.custom_theme = json.loads(custom_theme_str)
        except json.JSONDecodeError:
            self.custom_theme = None

        # Az alapértelmezett stíluslap beállítása az alkalmazás szintjén
        app = QApplication.instance()
        stylesheet = self.settings.value("stylesheet", "")
        if stylesheet:
            app.setStyleSheet(stylesheet)
        else:
            app.setStyleSheet(self.platform_settings['stylesheet'])

        app_font = QFont(self.platform_settings['font_family'], self.platform_settings['font_size'])
        app.setFont(app_font)

        self.setWindowTitle("Warframe Info Hub")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)
        self.web_bridge = WebBridge()
        self.channel = QWebChannel()
        self.channel.registerObject('pyotherside', self.web_bridge)

        self.temp_dir = get_temp_directory()
        self.cache_dir = get_cache_directory()

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        self.menu_layout = QVBoxLayout()
        self.theme_selector = ThemeSelector(self)
        self.menu_layout.addWidget(self.theme_selector)

        if self.debug:
            print(f"Operating System: {platform.system()} {platform.release()}")
            print(f"Python version: {sys.version}")
            print(f"PyQt version: {PYQT_VERSION_STR}")
            print(f"Qt version: {Qt.qVersion()}")
            print(f"Working directory: {os.getcwd()}")
            print(f"Temporary directory: {self.temp_dir}")
            print(f"Cache directory: {self.cache_dir}")

        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)

        self.menu_widget = self.create_menu_widget()
        self.menu_widget.setFixedWidth(250)
        self.main_layout.addWidget(self.menu_widget)

        self.web_view = self.create_web_view()
        self.main_layout.addWidget(self.web_view, 1)

        self.load_home_page()

    def create_menu_widget(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #e0e0e0;
            }
        """)

        menu_content = QWidget()
        menu_content.setLayout(self.menu_layout)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setFont(QFont("Arial", 13))
        self.update_tree_style()

        menu_structure = [
            ("Kezdőlap", self.load_home_page),
            ("Keresés", lambda: self.load_page("search")),
            ("Ciklusok", [
                ("Ciklusok", lambda: self.load_page("cycles")),
                ("Sortie", lambda: self.load_page("sortie")),
                ("Arcon Hunt", lambda: self.load_page("archon")),
                ("Arbitration", lambda: self.load_page("arbitration")),
                ("Nightwave", lambda: self.load_page("nightwave")),
                ("Void Fissures", lambda: self.load_page("fissures")),
                ("Baro Ki'Teer", lambda: self.load_page("baro")),
            ]),
            ("Események", lambda: self.load_page("events")),
            ("Git Update Info", lambda: self.load_page("info_git")),
        ]

        self.create_menu_items(self.tree, menu_structure)
        self.tree.expandAll()
        self.tree.itemClicked.connect(self.on_item_clicked)

        self.menu_layout.addWidget(self.tree)
        menu_content.setLayout(self.menu_layout)
        scroll_area.setWidget(menu_content)
        return scroll_area

    def create_menu_items(self, parent, items):
        for item in items:
            if isinstance(item[1], list):
                tree_item = QTreeWidgetItem(parent, [item[0]])
                self.create_menu_items(tree_item, item[1])
            else:
                tree_item = QTreeWidgetItem(parent, [item[0]])
                tree_item.setData(0, Qt.UserRole, item[1])

    def on_item_clicked(self, item, column):
        callback = item.data(0, Qt.UserRole)
        if callback:
            callback()

    def create_web_view(self):
        web_view = QWebEngineView()
        page = CustomWebEnginePage(self)
        web_view.setPage(page)
        settings = QWebEngineSettings.globalSettings()

        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)

        web_view.page().setWebChannel(self.channel)

        return web_view

    def update_tree_style(self):
        theme = self.current_theme
        if theme == "light":
            tree_style = """
                QTreeWidget {
                    border: none;
                    background-color: #f0f0f0;
                    color: #333333;
                }
                QTreeWidget::item { 
                    padding: 10px;
                    border-bottom: 1px solid #e0e0e0;
                }
                QTreeWidget::item:hover {
                    background-color: #e0e0e0;
                }
                QTreeWidget::item:selected { 
                    background-color: #a0a0a0;
                    color: #ffffff;
                }
            """
        elif theme == "dark":
            tree_style = """
                QTreeWidget {
                    border: none;
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QTreeWidget::item { 
                    padding: 10px;
                    border-bottom: 1px solid #3b3b3b;
                }
                QTreeWidget::item:hover {
                    background-color: #3b3b3b;
                }
                QTreeWidget::item:selected { 
                    background-color: #505050;
                    color: #ffffff;
                }
            """
        else:  # custom theme
            if isinstance(self.custom_theme, dict) and all(key in self.custom_theme for key in ['background', 'text', 'border', 'highlight']):
                tree_style = f"""
                    QTreeWidget {{
                        border: none;
                        background-color: {self.custom_theme['background']};
                        color: {self.custom_theme['text']};
                    }}
                    QTreeWidget::item {{ 
                        padding: 10px;
                        border-bottom: 1px solid {self.custom_theme['border']};
                    }}
                    QTreeWidget::item:hover {{
                        background-color: {self.custom_theme['highlight']};
                    }}
                    QTreeWidget::item:selected {{ 
                        background-color: {self.custom_theme['highlight']};
                        color: {self.custom_theme['text']};
                    }}
                """
            else:
                # Fallback to light theme if custom theme is not set correctly
                tree_style = """
                    QTreeWidget {
                        border: none;
                        background-color: #f0f0f0;
                        color: #333333;
                    }
                    QTreeWidget::item { 
                        padding: 10px;
                        border-bottom: 1px solid #e0e0e0;
                    }
                    QTreeWidget::item:hover {
                        background-color: #e0e0e0;
                    }
                    QTreeWidget::item:selected { 
                        background-color: #a0a0a0;
                        color: #ffffff;
                    }
                """
        self.tree.setStyleSheet(tree_style)

    def refresh_ui(self):
        self.update_tree_style()
        if self.current_page == "home":
            self.load_home_page()
        else:
            self.load_page(self.current_page)
        self.update_web_content_theme(self.current_theme)

    def update_web_content_theme(self, theme):
        self.current_theme = theme
        js_code = f"""
        (function() {{
            var style = document.createElement('style');
            style.type = 'text/css';
            style.innerHTML = `
                body {{ 
                    background-color: {('#ffffff' if theme == 'light' else '#2b2b2b')};
                    color: {('#000000' if theme == 'light' else '#ffffff')};
                }}
                a {{ color: {('#0066cc' if theme == 'light' else '#4da6ff')}; }}
                pre, code {{ 
                    background-color: {('#f0f0f0' if theme == 'light' else '#3b3b3b')};
                    border-color: {('#d0d0d0' if theme == 'light' else '#505050')};
                }}
            `;
            document.head.appendChild(style);
        }})();
        """
        self.web_view.page().runJavaScript(js_code)

    def load_page(self, page_name):
        self.current_page = page_name
        if self.debug:
            print(f"Debug: Loading page {page_name}")
        try:
            html_content = self.download_file(f"gui/{page_name}.html")
            if html_content is None:
                raise Exception(f"Failed to download {page_name}.html")

            js_content = self.download_file(f"gui/Script/{page_name}.js") or ""
            css_content = self.download_file(f"gui/Styles/{page_name}_styles.css") or ""

            full_html = self.create_full_html(html_content, js_content, css_content)
            self.web_view.setHtml(full_html, QUrl(self.GITHUB_RAW_URL))

            self.update_web_content_theme(self.current_theme)
        except Exception as e:
            error_html = f"<html><body><h1>Error loading page</h1><p>{str(e)}</p></body></html>"
            self.web_view.setHtml(error_html)
            print(f"Error loading page {page_name}: {str(e)}")

    def load_home_page(self):
        self.current_page = "home"
        try:
            readme_content = self.download_file("README.md")
            if readme_content is None:
                raise Exception("Failed to download README.md")

            html_content = markdown.markdown(readme_content, extensions=['extra', 'codehilite'])

            css_content = """
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    padding: 20px;
                    max-width: 800px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    color: #333333;
                }
                h1, h2, h3, h4, h5, h6 {
                    color: #2c3e50;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 10px;
                }
                img {
                    display: block;
                    margin: 20px auto;
                    max-width: 100%;
                    height: auto;
                }
                pre {
                    background-color: #f8f8f8;
                    border: 1px solid #ddd;
                    border-radius: 3px;
                    padding: 10px;
                    overflow-x: auto;
                }
                code {
                    font-family: 'Courier New', Courier, monospace;
                    background-color: #f8f8f8;
                    padding: 2px 4px;
                    border-radius: 3px;
                }
                a {
                    color: #3498db;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
                ul, ol {
                    padding-left: 30px;
                }
                table {
                    border-collapse: collapse;
                    width: 100%;
                    margin-bottom: 20px;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }
                th {
                    background-color: #f2f2f2;
                }
                .center {
                    text-align: center;
                }
            """

            js_content = """
                document.addEventListener('DOMContentLoaded', function() {
                    var links = document.getElementsByTagName('a');
                    for (var i = 0; i < links.length; i++) {
                        links[i].addEventListener('click', function(event) {
                            event.preventDefault();
                            window.pyotherside.open_url(this.href);
                        });
                    }
                });
            """

            full_html = self.create_full_html(html_content, js_content, css_content)
            self.web_view.setHtml(full_html, QUrl(self.GITHUB_RAW_URL))
            logging.info("Home page loaded successfully")

            self.update_web_content_theme(self.current_theme)

        except Exception as e:
            logging.error(f"Error loading README: {str(e)}")
            error_html = f"<html><body><h1>Error loading README</h1><p>{str(e)}</p></body></html>"
            self.web_view.setHtml(error_html)
            import traceback
            logging.error(traceback.format_exc())

    @staticmethod
    def create_full_html(html_content, js_content, css_content):
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Warframe Info Hub</title>
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
            <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
            <style>{css_content}</style>
            <script>
            console.log("HTML content loaded");
            {js_content}
            function initWebChannel() {{
                if (typeof QWebChannel === "undefined") {{
                    console.log("QWebChannel not available yet, retrying...");
                    setTimeout(initWebChannel, 100);
                    return;
                }}
                new QWebChannel(qt.webChannelTransport, function (channel) {{
                    window.pyotherside = channel.objects.pyotherside;
                    console.log("QWebChannel initialized");
                    if (typeof initSearch === "function") {{
                        initSearch();
                    }}
                }});
            }}
            document.addEventListener("DOMContentLoaded", function() {{
                console.log("DOM fully loaded");
                initWebChannel();
            }});
            </script>
        </head>
        <body>
            {html_content}
            <script>
            console.log("Body content loaded");
            </script>
        </body>
        </html>
        """

    @staticmethod
    def download_file(filename):
        url = GitHubMainWindow.GITHUB_RAW_URL + filename
        try:
            response = requests.get(url, timeout=10, verify=True)
            response.raise_for_status()
            logging.debug(f"Successfully downloaded {filename}")
            return response.text
        except requests.exceptions.RequestException as e:
            logging.error(f"Error downloading file {filename}: {str(e)}")
            return None


def initialize_application():
    logging.info("Initializing application")
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)

    # Alapértelmezett téma betöltése
    settings = QSettings("WarframeInfoHub", "ThemeSettings")
    theme = settings.value("theme", "light")
    stylesheet = settings.value("stylesheet", "")

    if not stylesheet:
        # Ha nincs mentett stíluslap, állítsunk be egy alapértelmezettet
        default_stylesheet = """
            QWidget { background-color: #ffffff; color: #000000; }
            QPushButton { background-color: #e0e0e0; border: 1px solid #b0b0b0; padding: 5px; }
            QTreeWidget {
                border: 1px solid #d0d0d0;
                background-color: #f0f0f0;
                color: #333333;
            }
            QTreeWidget::item {
                padding: 5px;
                border-bottom: 1px solid #e0e0e0;
            }
            QTreeWidget::item:selected {
                background-color: #a0a0a0;
                color: #ffffff;
            }
            QScrollArea { background-color: #f0f0f0; }
            QWebEngineView { background-color: #ffffff; }
        """
        stylesheet = default_stylesheet
        settings.setValue("stylesheet", default_stylesheet)
        settings.setValue("theme", "light")
        settings.sync()

    app.setStyleSheet(stylesheet)

    if QWebEngineProfile is not None:
        profile = QWebEngineProfile.defaultProfile()
        profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)

        profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36")

    logging.info("Application initialized successfully")
    return app


if __name__ == "__main__":
    try:
        logging.info("Starting Warframe Info Hub")
        app = initialize_application()

        # Parse command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('--debug', action='store_true', help='Enable debug mode')
        args = parser.parse_args()

        # Ellenőrizzük, hogy a program debug módban fut-e
        debug_mode = args.debug
        logging.info(f"Debug mode: {debug_mode}")

        # Megjeleníti a kompatibilitási ellenőrzés eredményét
        result, is_compatible = show_compatibility_popup()
        logging.info(f"Compatibility check result: {is_compatible}")

        if is_compatible or result == QMessageBox.Ok:
            # Itt folytatódik a fő program
            logging.info("Creating main window")
            window = GitHubMainWindow(debug=debug_mode)
            window.show()

            if debug_mode:
                # Ha debug módban vagyunk, kiírjuk a konzolra
                print("Program started in debug mode")

            logging.info("Entering main event loop")
            sys.exit(app.exec_())
        else:
            logging.warning("Exiting due to compatibility issues")
            sys.exit()
    except Exception as e:
        logging.critical(f"Critical error in main program: {str(e)}")
        import traceback

        logging.critical(traceback.format_exc())
        sys.exit(1)