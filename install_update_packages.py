# Copyright (c) 2024 LexyGuru
# This file is part of the API_Warframe_Cross_GUI project, licensed under the MIT License.
# For the full license text, see the LICENSE file in the project root.

import subprocess
import sys

def update_packages():
    packages = """
PyQt6==6.7.1
PyQt6-Qt6==6.7.2
PyQt6-sip==13.8.0
PyQt6-WebEngine==6.7.0
PyQt6-WebEngine-Qt6==6.7.2
PyQt6-WebEngineSubwheel-Qt6==6.7.2
requests==2.32.3
Markdown==3.6
lxml==5.2.2
pyinstaller==6.9.0
pyinstaller-hooks-contrib==2024.7
aiohttp==3.10.0
bcrypt==4.2.0
rich==13.7.1
    """.strip().split('\n')

    for package in packages:
        package_name = package.split('==')[0]
        print(f"Frissítés: {package_name}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package])
        except subprocess.CalledProcessError as e:
            print(f"Hiba történt a(z) {package_name} frissítése közben: {e}")

if __name__ == "__main__":
    update_packages()