# EmbedTab

Embed and manage existing Windows application windows inside a PyQt5 desktop application.

EmbedTab is designed for HWND-based applications such as **Chrome, LDPlayer and other Windows applications**. It provides a Qt grid UI, a local REST API and a Python SDK so windows can be embedded manually or controlled programmatically.

## Highlights

- Embed an existing Windows window by **HWND**`n- Drag a running Chrome/Windows application window into EmbedTab to embed it automatically
- Remove one window or clear the whole grid
- Focus an embedded window
- Dynamic **1..N column** layout
- Auto-attach windows by title
- Monitor embedded HWNDs and automatically reconnect when a window is recreated
- Save and restore window layouts as JSON presets
- Local REST API v1
- Python SDK through `EmbedAPI`
- Environment-based configuration
- Structured logging
- Unit tests with pytest
- PyInstaller build configuration
- Backward-compatible legacy `/embed` API

## Architecture

```text
                 ┌──────────────────────┐
                 │   Chrome / LDPlayer  │
                 │   Other HWND apps    │
                 └──────────┬───────────┘
                            │ HWND
                            ▼
                 ┌──────────────────────┐
                 │   WindowManager      │
                 │ find / validate /    │
                 │ focus / PID / title  │
                 └──────────┬───────────┘
                            │
                            ▼
┌──────────────┐    ┌──────────────────────┐
│ REST / SDK   │───▶│    MainEmbed         │
└──────────────┘    │      Qt UI           │
                    └──────────┬───────────┘
                               │
                  ┌────────────┼────────────┐
                  ▼            ▼            ▼
           EmbedManager  LayoutManager  WindowMonitor
                  │            │            │
                  └────────────┴────────────┘
                               │
                               ▼
                    QWidget.createWindowContainer
                               │
                               ▼
                     Embedded Windows Grid
```

### Core modules

| Module | Responsibility |
|---|---|
| `core/window_manager.py` | Find, validate and control native Windows HWNDs |
| `core/embed_manager.py` | Create, attach, remove and track embedded Qt containers |
| `core/layout_manager.py` | Manage grid columns and reflow embedded windows |
| `core/preset_manager.py` | Save/load/delete JSON presets |
| `core/monitor.py` | Monitor HWND validity and notify the UI when windows disappear |
| `config.py` | Application configuration and environment overrides |
| `logging_config.py` | Logging setup |
| `EmbedAPI/embed.py` | Python client for the local REST API |
| `main.py` | Qt application, Flask API and orchestration |

## Project structure

```text
EmbedTab/
├── core/
│   ├── __init__.py
│   ├── window_manager.py
│   ├── embed_manager.py
│   ├── layout_manager.py
│   ├── preset_manager.py
│   └── monitor.py
├── EmbedAPI/
│   ├── __init__.py
│   └── embed.py
├── GUI/
│   ├── embed_tab.ui
│   └── embed_tab_ui.py
├── utils/
│   ├── __init__.py
│   └── find_handle.py
├── tests/
│   ├── __init__.py
│   ├── test_window_manager.py
│   └── test_preset_manager.py
├── build/
│   ├── embedtab.spec
│   └── build.ps1
├── config.py
├── logging_config.py
├── main.py
├── chrome_testing.py
├── ldplayer_testing.py
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Requirements

- Windows
- Python 3.10+
- PyQt5
- Flask
- Requests
- pywin32
- pytest for tests
- PyInstaller for packaging

The application uses Windows APIs because embedding is based on native HWND handles.

## Installation

```powershell
python -m pip install -r requirements.txt
```

## Run

```powershell
python main.py
```

The local REST API listens by default on:

```text
http://127.0.0.1:5000
```

The Flask server runs in a background thread while the Qt GUI remains responsible for all UI operations.

# Embedding windows

## Drag and drop

EmbedTab supports dragging an already-running Windows application directly into the main view. This works at the Windows HWND level, so the source can be Chrome, LDPlayer or another valid top-level Windows window.

While the left mouse button is held on a valid source window, move the cursor into EmbedTab. The drop target displays a translucent highlight that covers the complete view using the target's current `width` and `height`, with a dashed border and a `Release here to embed window` message.

```text
          Drag running window
                  │
                  ▼
        ┌──────────────────────┐
        │   EmbedTab view      │
        │                      │
        │ Release here to      │
        │ embed window         │
        │                      │
        └──────────────────────┘
          ↑ width / height ↑
```

The overlay is resized with the target view and does not intercept mouse events. Releasing the mouse outside the view cancels the drop; releasing inside the highlighted area embeds the source HWND into a new slot.

## By HWND

```python
from EmbedAPI.embed import EmbedAPI

client = EmbedAPI()

hwnd = 123456
client.embed(hwnd, new=True)
```

The target HWND must belong to a valid Windows window.

## List embedded windows

```python
windows = client.windows()
print(windows)
```

## Focus a window

```python
client.focus(0)
```

## Remove one window

```python
client.remove(0)
```

## Clear all windows

```python
client.clear()
```

# Dynamic layout

The grid supports a configurable number of columns.

```python
client.set_columns(4)
```

With four columns, embedded windows are automatically reflowed:

```text
┌────────┬────────┬────────┬────────┐
│ Window │ Window │ Window │ Window │
├────────┼────────┼────────┼────────┤
│ Window │ Window │ Window │ Window │
└────────┴────────┴────────┴────────┘
```

The layout implementation is isolated in `LayoutManager`, so changing the layout strategy does not require rewriting window discovery or embedding logic.

# Auto attach

Auto attach searches for windows matching a title and embeds them automatically.

```python
client.auto_attach("LDPlayer", max_windows=6)
```

Parameters:

- `title`: title text used to find candidate windows
- `max_windows`: maximum number of windows to attach; `0` means no explicit limit

Stop auto attach:

```python
client.stop_auto_attach()
```

This is useful for applications such as multiple LDPlayer instances.

# Automatic reconnect

Embedded windows are monitored periodically.

If an embedded HWND becomes invalid because the original application was closed, restarted or recreated, EmbedTab can search for a replacement window using the stored title and reconnect the slot.

```text
Embedded HWND
     │
     ▼
WindowMonitor
     │
     ├── valid ──────▶ keep embedding
     │
     └── invalid
           │
           ▼
     find replacement
           │
           ▼
       re-embed
```

The monitor interval can be configured with `EMBED_MONITOR_MS`.

# Presets

Presets store the current layout and embedded-window information in JSON.

Save:

```python
client.save_preset("six-player")
```

Load:

```python
client.load_preset("six-player")
```

Delete:

```text
DELETE /api/v1/presets/{name}
```

By default, presets are stored in `presets.json`. The location can be changed with `EMBED_PRESETS`.

A preset contains enough information to restore the layout and attempt to locate the target windows again.

# REST API

## Window operations

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/windows` | List embedded windows |
| POST | `/api/v1/windows/embed` | Embed a HWND |
| DELETE | `/api/v1/windows/{index}` | Remove a window |
| POST | `/api/v1/windows/clear` | Clear all windows |
| POST | `/api/v1/windows/{index}/focus` | Focus a window |

### Embed example

```json
POST /api/v1/windows/embed

{
  "hwnd": 123456,
  "new": true
}
```

## Layout

```text
POST /api/v1/layout
```

Example:

```json
{
  "columns": 4
}
```

## Auto attach

Start:

```text
POST /api/v1/auto-attach
```

Example:

```json
{
  "title": "LDPlayer",
  "max_windows": 6
}
```

Stop:

```text
POST /api/v1/auto-attach/stop
```

## Presets

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/presets` | Save a preset |
| POST | `/api/v1/presets/load` | Load a preset |
| DELETE | `/api/v1/presets/{name}` | Delete a preset |

# Python SDK

The SDK wraps the local REST API so another Python application does not need to construct HTTP requests manually.

```python
from EmbedAPI.embed import EmbedAPI

client = EmbedAPI()

client.embed(hwnd, new=True)
print(client.windows())

client.focus(0)
client.remove(0)
client.clear()

client.set_columns(4)

client.auto_attach("LDPlayer", max_windows=6)
client.stop_auto_attach()

client.save_preset("six-player")
client.load_preset("six-player")
```

The SDK also keeps the original API:

```python
client.embed_tab(hwnd, new=True)
```

# Configuration

Default settings are defined in `config.py`.

| Variable | Default | Description |
|---|---:|---|
| `EMBED_HOST` | `127.0.0.1` | Flask bind address |
| `EMBED_PORT` | `5000` | REST API port |
| `EMBED_COLUMNS` | `3` | Initial grid columns |
| `EMBED_MAX_HEIGHT` | `500` | Maximum embedded area height |
| `EMBED_MONITOR_MS` | `1000` | HWND monitor interval |
| `EMBED_PRESETS` | `presets.json` | Preset file |
| `EMBED_LOG_LEVEL` | `INFO` | Logging level |

Example:

```powershell
$env:EMBED_PORT = "5050"
$env:EMBED_COLUMNS = "4"
$env:EMBED_MONITOR_MS = "1500"

python main.py
```

# Threading model

Flask request handling is separated from Qt UI operations.

```text
Flask / REST request
        │
        ▼
 command_received signal
        │
        ▼
Qt main thread
        │
        ├── EmbedManager
        ├── LayoutManager
        ├── WindowMonitor
        └── UI widgets
```

Qt widgets are therefore manipulated from the Qt main thread rather than directly from Flask worker threads.

The API command dispatcher waits for the Qt operation to complete instead of relying on arbitrary `sleep()` delays.

# Error handling

HTTP requests from `EmbedAPI` use a timeout and raise errors for unsuccessful HTTP responses.

Windows handles are validated before embedding.

Typical invalid conditions include:

- HWND does not exist
- HWND is no longer valid
- Duplicate HWND is already embedded
- Requested embedded index does not exist
- Invalid layout column count
- Missing or invalid preset name

# Testing

Run the test suite:

```powershell
python -m pytest -q
```

Run Python compilation checks:

```powershell
python -m compileall -q main.py core utils EmbedAPI tests
```

The current tests cover core behavior such as:

- Window manager behavior
- Preset persistence

# Build

The project includes a PyInstaller specification and PowerShell build script.

```powershell
powershell -ExecutionPolicy Bypass -File build/build.ps1
```

The script installs dependencies, installs PyInstaller and builds the executable using `build/embedtab.spec`.

Expected output:

```text
dist/EmbedTab/EmbedTab.exe
```

The build is configured as a Windows GUI application without a console window.

# Backward compatibility

The original SDK method remains available:

```python
from EmbedAPI.embed import EmbedAPI

client = EmbedAPI()
client.embed_tab(hwnd, new=True)
```

The legacy endpoint is also preserved:

```text
GET /embed
```

New integrations should use the versioned `/api/v1` endpoints.

# Development notes

## UI files

`GUI/embed_tab.ui` is the Qt Designer source.

`GUI/embed_tab_ui.py` is the generated Python UI module.

Business logic should remain outside the generated UI file. Core functionality belongs in the `core/` package or the application controller in `main.py`.

## Window discovery

`utils/find_handle.py` remains available for compatibility, while the main implementation uses `WindowManager`.

## Testing applications

The repository includes:

- `chrome_testing.py` for Chrome-related HWND testing
- `ldplayer_testing.py` for LDPlayer window discovery/testing

# Implementation status

- [x] HWND window discovery and validation
- [x] Window embedding`n- [x] OS-level drag-and-drop window embedding
- [x] Window removal
- [x] Window focus
- [x] Clear all
- [x] Dynamic grid columns
- [x] Auto attach
- [x] HWND monitoring
- [x] Automatic reconnect by window title
- [x] JSON presets
- [x] REST API v1
- [x] Python SDK
- [x] Environment configuration
- [x] Logging
- [x] Unit tests
- [x] PyInstaller packaging
- [x] Legacy API compatibility

The project is now structured so additional features can be added without coupling window discovery, embedding, layout management and persistence into a single module.
