from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules("win32") + ["PyQt5.sip"]
block_cipher = None

a = Analysis(["main.py"], pathex=["."], binaries=[], datas=[("GUI/embed_tab.ui", "GUI")], hiddenimports=hiddenimports, hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[], win_no_prefer_redirects=False, win_private_assemblies=False, cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name="EmbedTab", debug=False, strip=False, upx=True, console=False)
