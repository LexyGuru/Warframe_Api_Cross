## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.



# WarframeInfoHub Felhasználói Útmutató
> <img alt="Info" height="40" src="https://raw.githubusercontent.com/LexyGuru/Warframe_Api_Main/main/Icons/git/note.svg"><br> 
> ## Bevezetés: 
> A WarframeInfoHub V2.0 egy Python alapú eszköz, 
> amely a Warframe játékban elérhető különböző információk gyors és egyszerű lekérdezését teszi lehetővé. 
> Ez a szkript integrálja a Warframe API-kat, hogy valós idejű adatokat szolgáltasson a játékon belüli eseményekről,
> tárgyakról, bolygókról és egyéb fontos elemekről.


> <img alt="Info" height="40" src="https://raw.githubusercontent.com/LexyGuru/Warframe_Api_Main/main/Icons/git/info.svg"><br> 
> ## Fő Funkciók:
> ### Játékbeli Események Lekérdezése:
> A szkript képes valós idejű adatokat lekérdezni a jelenleg futó játékon belüli eseményekről, 
> például időkorlátos missziókról, felfedezésekről, és különleges kihívásokról. 
> ### Tárgyinformációk Kérése: 
> Lehetőség van specifikus Warframe tárgyak adatainak lekérdezésére, beleértve azok árát, előfordulását, és ritkaságát.
> ### Bolygó és Misszió Részletek: 
> A felhasználók megtekinthetik a különböző bolygókhoz kapcsolódó missziók és egyéb tevékenységek részleteit.
> ### Keresztplatformos Adatkezelés: 
> A szkript a több platformot támogató adatokat is kezeli, így a játékosok a legfrissebb információkhoz férhetnek hozzá, 
> függetlenül attól, hogy melyik platformon játszanak.
> ### Zárszó: 
> A WarframeInfoHub V2.0 egy rendkívül hasznos eszköz minden Warframe játékos számára, 
> aki naprakész szeretne maradni a játékon belüli eseményekkel és információkkal kapcsolatban. 
> A szkript egyszerűsége és hatékonysága révén gyorsan hozzáférhetők a szükséges adatok, ami megkönnyíti a játékélményt.


# Warframe Info Hub Build Guide

> <img alt="Info" height="" src="https://raw.githubusercontent.com/LexyGuru/Warframe_Api_Main/main/Icons/git/example.svg"><br>
> Windows <br>
>```bash 
>    pyinstaller --name=WarframeInfoHub --onefile --windowed --add-data=custom_theme.json:. --icon=Icons/Appicon.ico WarframeInfoHub_V2.0.py
>    ```

> ### Egyebb függösegek hozzáadása javasolt
> **EZ CSAK EGY MINTA HIBA ESETEN EZEKKEL PROBÁLKOZZ<br><br>**
> pyinstaller --name=WarframeInfoHub --onefile ^<br>
--windowed --icon=Icons/AppIcon.ico ^<br>
--add-data "Icons;Icons" ^<br>
--add-data=custom_theme.json:.<br>
--hidden-import PyQt5 ^<br>
--hidden-import PyQt5.QtCore ^<br>
--hidden-import PyQt5.QtGui ^<br>
--hidden-import PyQt5.QtWidgets ^<br>
--hidden-import PyQt5.QtWebEngineWidgets ^<br>
--hidden-import PyQt5.QtWebEngineCore ^<br>
--hidden-import PyQt5.QtWebChannel ^<br>
--hidden-import requests ^<br>
--hidden-import markdown ^<br>
--collect-all PyQt5 ^<br>
--collect-all requests ^<br>
--collect-all markdown ^<br>
WarframeInfoHub_v2.py


> <img alt="Info" height="" src="https://raw.githubusercontent.com/LexyGuru/Warframe_Api_Main/main/Icons/git/example.svg"><br>
> MacOS
>```bash 
>    pyinstaller --name=WarframeInfoHub --onefile --windowed --add-data=custom_theme.json:. --icon=Icons/Appicon.icns WarframeInfoHub_V2.0.py
>    ```

> <img alt="Info" height="" src="https://raw.githubusercontent.com/LexyGuru/Warframe_Api_Main/main/Icons/git/example.svg"><br>
> Linux
>``` 
>   JELENELEG NINCS INFO 
>    ```



