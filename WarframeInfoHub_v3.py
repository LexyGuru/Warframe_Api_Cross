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

from PyQt6.QtWidgets import (QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem,
                             QScrollArea, QSizePolicy, QMessageBox, QMenuBar, QMenu,
                             QHBoxLayout, QVBoxLayout, QWidget, QPushButton)
from PyQt6.QtGui import QDesktopServices, QFont, QAction, QColor
from PyQt6.QtCore import QObject, pyqtSlot, QUrl, Qt, QCoreApplication, QTimer
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings, QWebEnginePage
from PyQt6.QtWebChannel import QWebChannel

from PyQt6.QtCore import QT_VERSION_STR, PYQT_VERSION_STR

print(f"Qt: v {QT_VERSION_STR}\tPyQt: v {PYQT_VERSION_STR}")

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

def check_pyqt_dependencies():
    required_modules = ['PyQt6.QtWidgets', 'PyQt6.QtGui', 'PyQt6.QtCore', 'PyQt6.QtWebEngineWidgets', 'PyQt6.QtWebEngineCore', 'PyQt6.QtWebChannel']
    missing_modules = []

    for module in required_modules:
        try:
            importlib.import_module(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        print(f"Hiányzó PyQt6 modulok: {', '.join(missing_modules)}")
        print("Kérjük, telepítse ezeket a modulokat a 'pip install PyQt6' paranccsal.")
        return False
    return True

if not check_pyqt_dependencies():
    sys.exit(1)

def check_compatibility():
    os_name = platform.system().lower()
    os_version = platform.version()
    architecture = platform.machine().lower()
    python_version = sys.version_info

    required_packages = ['PyQt6', 'requests', 'markdown']
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
            f"A Python {python_version.major}.{python_version.minor} verzió nem támogatott. Python 3.6 vagy újabb szükséges.")

    return is_compatible, os_name, os_version, architecture, python_version, missing_packages, compatibility_issues

def show_compatibility_popup():
    is_compatible, os_name, os_version, architecture, python_version, missing_packages, compatibility_issues = check_compatibility()

    msg = QMessageBox()
    msg.setWindowTitle("Rendszer Kompatibilitás Ellenőrzés")

    font = QFont()
    font.setPointSize(10)
    msg.setFont(font)

    message = f"Operációs rendszer: {os_name.capitalize()} ({os_version})\n"
    message += f"CPU architektúra: {architecture}\n"
    message += f"Python verzió: {python_version.major}.{python_version.minor}.{python_version.micro}\n\n"

    if missing_packages:
        message += f"Hiányzó függőségek: {', '.join(missing_packages)}\n\n"
    else:
        message += "Minden szükséges függőség telepítve van.\n\n"

    if is_compatible:
        message += "A program kompatibilis a jelenlegi rendszerrel."
        msg.setIcon(QMessageBox.Icon.Information)
    else:
        message += "Kompatibilitási problémák:\n"
        for issue in compatibility_issues:
            message += f"- {issue}\n"
        message += "\nA program futhat, de a teljes funkcionalitás nem garantált."
        msg.setIcon(QMessageBox.Icon.Warning)

    msg.setText(message)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)

    return msg.exec(), is_compatible

def get_platform_specific_settings():
    system = platform.system().lower()
    settings = {
        'font_family': 'Arial',
        'font_size': 10,
        'stylesheet': ''
    }

    if system == 'darwin':  # macOS
        settings['font_family'] = 'SF Pro Text'
        settings['font_size'] = 13
    elif system == 'windows':
        settings['font_family'] = 'Segoe UI'
        settings['font_size'] = 9
    elif system == 'linux':
        settings['font_family'] = 'Ubuntu'
        settings['font_size'] = 11

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

class AnimatedTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAnimated(True)
        self.clicked_item = None
        self.original_color = None

    def mousePressEvent(self, event):
        item = self.itemAt(event.position().toPoint())
        if item:
            self.clicked_item = item
            self.original_color = item.background(0)
            item.setBackground(0, QColor(200, 200, 200))  # Világosszürke háttér
            QTimer.singleShot(200, self.reset_item_color)
        super().mousePressEvent(event)

    def reset_item_color(self):
        if self.clicked_item:
            self.clicked_item.setBackground(0, self.original_color)
            self.clicked_item = None
            self.original_color = None

class GitHubMainWindow(QMainWindow):
    GITHUB_RAW_URL = "https://raw.githubusercontent.com/LexyGuru/Warframe_Api_Main/main/"

    def __init__(self, debug=False):
        super().__init__()
        self.is_dark_theme = False
        self.debug = debug
        self.platform_settings = get_platform_specific_settings()

        self.setWindowTitle("Warframe Info Hub")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)
        self.web_bridge = WebBridge()
        self.channel = QWebChannel()

        self.temp_dir = get_temp_directory()
        self.cache_dir = get_cache_directory()

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        if self.debug:
            print(f"Operating System: {platform.system()} {platform.release()}")
            print(f"Python version: {sys.version}")
            print(f"PyQt version: {PYQT_VERSION_STR}")
            print(f"Qt version: {QT_VERSION_STR}")
            print(f"Working directory: {os.getcwd()}")
            print(f"Temporary directory: {self.temp_dir}")
            print(f"Cache directory: {self.cache_dir}")

        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        menu_widget = self.create_menu_widget()
        left_layout.addWidget(menu_widget)

        self.theme_switch = QPushButton("Sötét/Világos")
        self.theme_switch.clicked.connect(self.toggle_theme)
        left_layout.addWidget(self.theme_switch)

        left_widget.setFixedWidth(250)  # Fix szélesség a bal oldali menünek
        main_layout.addWidget(left_widget)

        self.web_view = self.create_web_view()
        main_layout.addWidget(self.web_view)

        self.load_home_page()

    def create_menu_widget(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #e0e0e0;
            }
        """)

        tree = AnimatedTreeWidget()
        tree.setHeaderHidden(True)
        tree.setFont(QFont("Arial", 13))
        tree.setStyleSheet("""
            QTreeWidget {
                border: none;
                background-color: #e0e0e0;
                color: #333333;
            }
            QTreeWidget::item { 
                padding: 10px;
                border-bottom: 1px solid #c0c0c0;
            }
            QTreeWidget::item:hover {
                background-color: #d0d0d0;
            }
            QTreeWidget::item:selected { 
                background-color: #b0b0b0;
                color: #000000;
            }
        """)

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

        self.create_menu_items(tree, menu_structure)
        tree.expandAll()
        tree.itemClicked.connect(self.on_item_clicked)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(tree)
        #layout.addWidget(self.theme_switch)
        scroll_area.setWidget(container)

        return scroll_area

    def create_menu_items(self, parent, items):
        for item in items:
            if isinstance(item[1], list):
                tree_item = QTreeWidgetItem(parent, [item[0]])
                self.create_menu_items(tree_item, item[1])
            else:
                tree_item = QTreeWidgetItem(parent, [item[0]])
                tree_item.setData(0, Qt.ItemDataRole.UserRole, item[1])

    def on_item_clicked(self, item, column):
        callback = item.data(0, Qt.ItemDataRole.UserRole)
        if callback:
            callback()

    def create_web_view(self):
        web_view = QWebEngineView()
        page = CustomWebEnginePage(self)
        web_view.setPage(page)
        settings = web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
        web_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        web_view.page().setWebChannel(self.channel)
        self.channel.registerObject('pyotherside', self.web_bridge)

        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        web_view.loadFinished.connect(self.onLoadFinished)

        return web_view

    def load_page(self, page_name):
        if self.debug:
            print(f"Debug: Loading page {page_name}")
        try:
            html_content = self.download_file(f"gui/{page_name}.html")
            js_content = self.download_file(f"gui/Script/{page_name}.js")

            css_content = ""
            try:
                css_content = self.download_file(f"gui/Styles/{page_name}_styles.css")
            except requests.RequestException:
                print(f"CSS file not found for {page_name}, using empty CSS")

            full_html = self.create_full_html(html_content, js_content, css_content)
            self.web_view.setHtml(full_html)
        except Exception as e:
            error_html = f"<html><body><h1>Error loading page</h1><p>{str(e)}</p></body></html>"
            self.web_view.setHtml(error_html)
            print(f"Error loading page {page_name}: {str(e)}")

    def load_home_page(self):
        try:
            readme_content = self.download_file("README.md")
            if readme_content is None:
                raise Exception("Failed to download README.md")

            logging.debug(f"README content: {readme_content[:100]}...")  # Print first 100 characters

            html_content = markdown.markdown(readme_content, extensions=['extra', 'codehilite'])
            logging.debug(f"HTML content: {html_content[:100]}...")  # Print first 100 characters

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
                body.light-theme {
                    background-color: white;
                    color: black;
                }
                body.dark-theme {
                    background-color: #2b2b2b;
                    color: #f0f0f0;
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
            logging.debug(f"Full HTML: {full_html[:100]}...")  # Print first 100 characters

            base_url = QUrl(self.GITHUB_RAW_URL)
            self.web_view.setHtml(full_html, base_url)
            logging.info("Home page loaded successfully")
        except Exception as e:
            logging.error(f"Error loading home page: {str(e)}")
            self.show_error_message("Failed to load home page")
            import traceback
            logging.error(traceback.format_exc())

    def show_error_message(self, message):
        error_html = f"<html><body><h1>Error</h1><p>{message}</p></body></html>"
        self.web_view.setHtml(error_html)

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

    def onLoadFinished(self, ok):
        if ok:
            logging.info(f"Page loaded successfully: {self.web_view.url().toString()}")
            self.web_view.page().runJavaScript("""
                console.log("JavaScript executed from Python");
                if (typeof QWebChannel !== 'undefined') {
                    console.log("QWebChannel is defined");
                    new QWebChannel(qt.webChannelTransport, function (channel) {
                        window.pyotherside = channel.objects.pyotherside;
                        console.log("QWebChannel initialized from Python");
                        if (typeof initSearch === 'function') {
                            console.log("Calling initSearch");
                            initSearch();
                        } else {
                            console.log("initSearch is not defined");
                        }
                    });
                } else {
                    console.error("QWebChannel is not defined");
                }
            """, self.log_javascript_result)
        else:
            logging.error(f"Page load failed: {self.web_view.url().toString()}")

    def log_javascript(self, level, message, line, source):
        logging.debug(f"JavaScript [{level}] {message} at line {line} in {source}")

    def log_javascript_result(self, result):
        logging.debug(f"JavaScript result: {result}")

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

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.apply_theme()

    def apply_theme(self):
        if self.is_dark_theme:
            self.setStyleSheet("""
                QMainWindow, QScrollArea, QTreeWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QTreeWidget::item {
                    border-bottom: 1px solid #3a3a3a;
                }
                QTreeWidget::item:hover {
                    background-color: #3a3a3a;
                }
                QTreeWidget::item:selected {
                    background-color: #4a4a4a;
                    color: #ffffff;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow, QScrollArea, QTreeWidget {
                    background-color: #f0f0f0;
                    color: #333333;
                }
                QTreeWidget::item {
                    border-bottom: 1px solid #e0e0e0;
                }
                QTreeWidget::item:hover {
                    background-color: #e0e0e0;
                }
                QTreeWidget::item:selected {
                    background-color: #d0d0d0;
                    color: #000000;
                }
            """)

        # Webview téma frissítése
        self.update_webview_theme()

    def update_webview_theme(self):
        js = f"document.body.className = '{'dark-theme' if self.is_dark_theme else 'light-theme'}';"
        self.web_view.page().runJavaScript(js)


def initialize_application():
    logging.info("Initializing application")
    # Szükséges Qt attribútumok beállítása
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

    # Az alkalmazás létrehozása
    app = QApplication(sys.argv)

    # WebEngine profil beállítása
    profile = QWebEngineProfile.defaultProfile()
    profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)

    # Felhasználói ügynök beállítása
    profile.setHttpUserAgent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

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

        if is_compatible or result == QMessageBox.StandardButton.Ok:
            # Itt folytatódik a fő program
            logging.info("Creating main window")
            window = GitHubMainWindow(debug=debug_mode)
            window.show()

            if debug_mode:
                # Ha debug módban vagyunk, kiírjuk a konzolra
                print("Program started in debug mode")

            logging.info("Entering main event loop")
            sys.exit(app.exec())
        else:
            logging.warning("Exiting due to compatibility issues")
            sys.exit()
    except Exception as e:
        logging.critical(f"Critical error in main program: {str(e)}")
        import traceback

        logging.critical(traceback.format_exc())
        sys.exit(1)