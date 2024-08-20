## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<picture><img alt="Info" height="40" src="https://raw.githubusercontent.com/LexyGuru/Warframe_Api_Main/main/Icons/git/info.svg"><br></picture> 

Cross Platform <br>
``MacOS`` ``Windows`` ``Linux`` <br><br>


Windows rendszerre:
```bash
pyinstaller --onefile --windowed --add-data "gui:gui" --add-data "gui/Script:gui/Script" --add-data "gui/Styles:gui/Styles" --icon=Icons/AppIcon.ico main_qt6.py
```

macOS rendszerre:
```bash
pyinstaller --onefile --windowed --add-data "gui:gui" --add-data "gui/Script:gui/Script" --add-data "gui/Styles:gui/Styles" --icon=Icons/AppIcon.icns main_qt6.py
```

Linux rendszerre:
```bash
pyinstaller --onefile --windowed --add-data "gui:gui" --add-data "gui/Script:gui/Script" --add-data "gui/Styles:gui/Styles" --icon=Icons/AppIcon.png main_qt6.py
```
