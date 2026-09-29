$ErrorActionPreference = 'Stop'
python -m pip install -r requirements.txt
python -m pip install pyinstaller
pyinstaller --clean --noconfirm build/embedtab.spec
Write-Host 'Build complete: dist/EmbedTab/EmbedTab.exe'
