#!/bin/bash

# Állítsuk be, hogy a script kilépjen hiba esetén
set -e

echo "Starting build process for WarframeInfoHub..."

# Először töröljük a korábbi build és dist mappákat
echo "Cleaning up previous build artifacts..."
rm -rf build dist

# Keressük meg a QtWebEngineProcess pontos helyét
echo "Locating QtWebEngineProcess..."
QTWEBENGINEPROCESS=$(find /Library/Frameworks/Python.framework -name QtWebEngineProcess)
echo "QtWebEngineProcess location: $QTWEBENGINEPROCESS"

# Keressük meg a QtWebEngineCore.framework mappát
QTWEBENGINECORE=$(dirname $(dirname $QTWEBENGINEPROCESS))
echo "QtWebEngineCore location: $QTWEBENGINECORE"

# Módosított PyInstaller parancs
echo "Running PyInstaller..."
pyinstaller --name=WarframeInfoHub \
  --onefile \
  --windowed \
  --icon=Icons/AppIcon.icns \
  --add-data "Icons:Icons" \
  --add-data "Qt.conf:." \
  --collect-all PyQt6 \
  --collect-all requests \
  --collect-all markdown \
  WarframeInfoHub_v2.py

# Az alkalmazás futtatása előtt
echo "Setting execute permissions..."
chmod +x dist/WarframeInfoHub

# Ellenőrizzük a létrehozott alkalmazás tartalmát
echo "Checking for QtWebEngineProcess in the built application..."
find dist/WarframeInfoHub.app -name QtWebEngineProcess

# Ha a QtWebEngineProcess még mindig hiányzik, másoljuk be manuálisan
if [ -z "$(find dist/WarframeInfoHub.app -name QtWebEngineProcess)" ]; then
  echo "QtWebEngineProcess not found in the built application. Copying manually..."
  DEST_DIR="dist/WarframeInfoHub.app/Contents/Frameworks/QtWebEngineCore.framework/Helpers/QtWebEngineProcess.app/Contents/MacOS"
  mkdir -p "$DEST_DIR"
  cp "$QTWEBENGINEPROCESS" "$DEST_DIR/"
  echo "Manually copied QtWebEngineProcess to $DEST_DIR"
fi

# Ellenőrizzük újra
echo "Verifying QtWebEngineProcess after manual copy..."
find dist/WarframeInfoHub.app -name QtWebEngineProcess

echo "Build process completed. Please check the 'dist' folder for the built application."
Last edited 1 hour ago


Publish