import PyQt6
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata
import os

datas = collect_data_files('PyQt6')
datas += copy_metadata('PyQt6')
hiddenimports = collect_submodules('PyQt6')

# Explicitly add QtWebEngineCore
qtwe_dir = os.path.join(os.path.dirname(PyQt6.__file__), 'Qt6', 'lib', 'QtWebEngineCore.framework')
datas += [(qtwe_dir, 'PyQt6/Qt6/lib/QtWebEngineCore.framework')]