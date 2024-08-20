import sys
import platform
import requests
import markdown
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QTreeWidget, QTreeWidgetItem, QScrollArea, QSizePolicy, QMessageBox
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from PyQt6.QtCore import QObject, pyqtSlot, QUrl, Qt
from PyQt6.QtGui import QDesktopServices, QFont
from PyQt6.QtWebChannel import QWebChannel

# Az importálási figyelmeztetés kezelése
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from pkg_resources import get_distribution, DistributionNotFound


def check_compatibility():
    os_name = platform.system().lower()
    os_version = platform.version()
    architecture = platform.machine().lower()
    python_version = sys.version_info

    required_packages = ['PyQt6', 'requests', 'markdown']
    missing_packages = []
    for package in required_packages:
        try:
            get_distribution(package)
        except DistributionNotFound:
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


class WebBridge(QObject):
    @pyqtSlot(str)
    def open_url(self, url):
        QDesktopServices.openUrl(QUrl(url))


class GitHubMainWindow(QMainWindow):
    GITHUB_RAW_URL = "https://raw.githubusercontent.com/LexyGuru/Warframe_Api_Main/main/"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Warframe Info Hub")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)
        self.web_bridge = WebBridge()
        self.channel = QWebChannel()
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        menu_widget = self.create_menu_widget()
        menu_widget.setFixedWidth(250)
        main_layout.addWidget(menu_widget)

        self.web_view = self.create_web_view()
        main_layout.addWidget(self.web_view, 1)

        self.load_home_page()

    def create_menu_widget(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f0f0f0;
            }
        """)

        tree = QTreeWidget()
        tree.setHeaderHidden(True)
        tree.setFont(QFont("Arial", 13))
        tree.setStyleSheet("""
            QTreeWidget {
                border: none;
                background-color: #f0f0f0;
            }
            QTreeWidget::item { 
                padding: 7px;
                border-bottom: 1px solid #e0e0e0;
            }
            QTreeWidget::item:selected { 
                background-color: #E0E0E0;
            }
            QTreeWidget::branch:has-siblings:!adjoins-item {
                border-image: url(vline.png) 0;
            }
            QTreeWidget::branch:has-siblings:adjoins-item {
                border-image: url(branch-more.png) 0;
            }
            QTreeWidget::branch:!has-children:!has-siblings:adjoins-item {
                border-image: url(branch-end.png) 0;
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

        scroll_area.setWidget(tree)
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

        # Javított rész: javaScriptConsoleMessage tulajdonság beállítása
        web_view.page().javaScriptConsoleMessage = self.log_javascript

        # Javított rész: loadFinished signal kezelése
        web_view.loadFinished.connect(self.onLoadFinished)

        return web_view

    def load_page(self, page_name):
        print(f"Loading page from GitHub: {page_name}")
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
        except Exception as e:
            error_html = f"<html><body><h1>Error loading README</h1><p>{str(e)}</p></body></html>"
            self.web_view.setHtml(error_html)
            print(f"Error loading README: {str(e)}")

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
            print(f"Page loaded successfully: {self.web_view.url().toString()}")
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
            print(f"Page load failed: {self.web_view.url().toString()}")

    def log_javascript(self, level, message, line, source):
        print(f"JavaScript [{level}] {message} at line {line} in {source}")

    def log_javascript_result(self, result):
        print(f"JavaScript result: {result}")

    @staticmethod
    def download_file(filename):
        url = GitHubMainWindow.GITHUB_RAW_URL + filename
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Megjeleníti a kompatibilitási ellenőrzés eredményét
    result, is_compatible = show_compatibility_popup()

    if is_compatible or result == QMessageBox.StandardButton.Ok:
        # Itt folytatódik a fő program
        window = GitHubMainWindow()
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit()