from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files('PyQt6')
hiddenimports = collect_submodules('PyQt6')