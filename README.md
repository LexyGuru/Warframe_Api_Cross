## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<picture><img alt="Info" height="40" src="https://raw.githubusercontent.com/LexyGuru/Warframe_Api_Main/main/Icons/git/info.svg"><br></picture> 

Cross Platform <br>
``MacOS`` ``Windows`` ``Linux`` <br><br>


# Warframe Info Hub Build Guide

Ez az útmutató segít a Warframe Info Hub alkalmazás build folyamatában Windows, Linux és macOS rendszereken.

## Előfeltételek (minden platformra):

1. Python 3.6 vagy újabb verzió
2. pip (Python csomagkezelő)
3. Git (opcionális, de ajánlott)

## Közös lépések:

1. Klónozza vagy töltse le a projektet:
   ```
   git clone https://github.com/YourUsername/WarframeInfoHub.git
   cd WarframeInfoHub
   ```

2. Hozzon létre és aktiváljon egy virtuális környezetet:
   ```
   python -m venv venv
   source venv/bin/activate  # Linux és macOS
   venv\Scripts\activate     # Windows
   ```

3. Telepítse a szükséges függőségeket:
   ```
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Telepítse a PyInstaller-t és a pyinstaller-hooks-contrib-ot:
   ```
   pip install pyinstaller pyinstaller-hooks-contrib
   ```

## Windows-specifikus build folyamat:

1. Nyissa meg a parancssort és navigáljon a projekt mappájába.

2. Futtassa a következő PyInstaller parancsot:
   ```bash
   pyinstaller --name=WarframeInfoHub --onefile --windowed ^
   --icon=Icons/AppIcon.ico ^
   --add-data "Icons;Icons" ^
   --additional-hooks-dir=. ^
   --hidden-import PyQt6.QtWebEngineWidgets ^
   --hidden-import PyQt6.QtWebEngineCore ^
   --hidden-import PyQt6.QtWebChannel ^
   --hidden-import PyQt6.QtWebEngineCore.QWebEngineSettings ^
   --hidden-import PyQt6.QtWebEngineCore.QWebEngineProfile ^
   --hidden-import PyQt6.QtWebEngineCore.QWebEnginePage ^
   --hidden-import PyQt6.QtNetwork ^
   --hidden-import PyQt6.QtPrintSupport ^
   --add-data "C:\Path\To\PyQt6\Qt6\plugins\platforms;platforms" ^
   --add-data "C:\Path\To\PyQt6\Qt6\plugins\styles;styles" ^
   --add-data "C:\Path\To\PyQt6\Qt6\resources\*;." ^
   --add-data "C:\Path\To\PyQt6\Qt6\translations\*;translations" ^
   --add-binary "C:\Path\To\PyQt6\Qt6\bin\QtWebEngineProcess.exe;." ^
   --collect-all PyQt6 ^
   --collect-all requests ^
   --collect-all markdown ^
   WarframeInfoHub_v2.py
   ```
   Megjegyzés: Cserélje ki a `C:\Path\To\PyQt6\` részt a tényleges PyQt6 telepítési útvonalra.

3. A létrejött .exe fájlt a `dist` mappában találja.

## Linux-specifikus build folyamat:

1. Nyissa meg a terminált és navigáljon a projekt mappájába.

2. Futtassa a következő PyInstaller parancsot:
   ```bash
   pyinstaller --name=WarframeInfoHub --onefile --windowed \
   --icon=Icons/AppIcon.ico \
   --add-data "Icons:Icons" \
   --additional-hooks-dir=. \
   --hidden-import PyQt6.QtWebEngineWidgets \
   --hidden-import PyQt6.QtWebEngineCore \
   --hidden-import PyQt6.QtWebChannel \
   --hidden-import PyQt6.QtWebEngineCore.QWebEngineSettings \
   --hidden-import PyQt6.QtWebEngineCore.QWebEngineProfile \
   --hidden-import PyQt6.QtWebEngineCore.QWebEnginePage \
   --hidden-import PyQt6.QtNetwork \
   --hidden-import PyQt6.QtPrintSupport \
   --add-data "/path/to/PyQt6/Qt6/plugins/platforms:platforms" \
   --add-data "/path/to/PyQt6/Qt6/plugins/styles:styles" \
   --add-data "/path/to/PyQt6/Qt6/resources/*:." \
   --add-data "/path/to/PyQt6/Qt6/translations/*:translations" \
   --collect-all PyQt6 \
   --collect-all requests \
   --collect-all markdown \
   WarframeInfoHub_v2.py
   ```
   Megjegyzés: Cserélje ki a `/path/to/PyQt6/` részt a tényleges PyQt6 telepítési útvonalra.

3. A létrejött bináris fájlt a `dist` mappában találja.

## macOS-specifikus build folyamat:

1. Nyissa meg a Terminal alkalmazást és navigáljon a projekt mappájába.

2. Futtassa a következő PyInstaller parancsot:

   ```bash
   pyinstaller --name=WarframeInfoHub --onefile --windowed \
   --icon=Icons/AppIcon.icns \
   --add-data "Icons:Icons" \
   --additional-hooks-dir=. \
   --hidden-import PyQt6.QtWebEngineWidgets \
   --hidden-import PyQt6.QtWebEngineCore \
   --hidden-import PyQt6.QtWebChannel \
   --hidden-import PyQt6.QtWebEngineCore.QWebEngineSettings \
   --hidden-import PyQt6.QtWebEngineCore.QWebEngineProfile \
   --hidden-import PyQt6.QtWebEngineCore.QWebEnginePage \
   --hidden-import PyQt6.QtNetwork \
   --hidden-import PyQt6.QtPrintSupport \
   --add-data "/path/to/PyQt6/Qt6/plugins/platforms:platforms" \
   --add-data "/path/to/PyQt6/Qt6/plugins/styles:styles" \
   --add-data "/path/to/PyQt6/Qt6/resources/*:." \
   --add-data "/path/to/PyQt6/Qt6/translations/*:translations" \
   --collect-all PyQt6 \
   --collect-all requests \
   --collect-all markdown \
   WarframeInfoHub_v2.py
   ```
   Megjegyzés: Cserélje ki a `/path/to/PyQt6/` részt a tényleges PyQt6 telepítési útvonalra.

3. A létrejött .app fájlt a `dist` mappában találja.

## Tippek és hibaelhárítás:

1. Ha hiányzó modulokat vagy importálási hibákat tapasztal, adja hozzá őket a `--hidden-import` opcióval.

2. Ha DLL vagy so fájlok hiányoznak, használja az `--add-binary` opciót a hiányzó fájlok hozzáadásához.

3. Tesztelje az alkalmazást egy tiszta környezetben, ahol nincs Python telepítve.

4. Ha problémák merülnek fel a QWebEngine-nel, próbálja hozzáadni a QtWebEngineProcess-t is:
   - Windows: `--add-binary "C:\Path\To\PyQt6\Qt6\bin\QtWebEngineProcess.exe;."`
   - Linux/macOS: `--add-binary "/path/to/PyQt6/Qt6/libexec/QtWebEngineProcess:."`

5. Debug információkért használja a `--debug=all` opciót a PyInstaller parancsban.

Kövesse ezeket az utasításokat a megfelelő platformon, és sikeresen elkészítheti a Warframe Info Hub alkalmazás futtatható verzióját Windows, Linux és macOS rendszerekre.