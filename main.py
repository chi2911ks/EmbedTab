import logging
import sys
import threading
import traceback

from flask import Flask, jsonify, request
from PyQt5.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget

from GUI.embed_tab_ui import Ui_FormView
from config import load_settings
from core import EmbedManager, LayoutManager, PresetManager, WindowDragEmbedController, WindowManager, WindowMonitor
from logging_config import configure_logging

settings = load_settings()
configure_logging(settings.log_level)
log = logging.getLogger("embedtab")
app = Flask(__name__)


class MainEmbed(QWidget, QObject):
    command_received = pyqtSignal(object)

    def __init__(self) -> None:
        super().__init__()
        self.ui = Ui_FormView()
        self.ui.setupUi(self)
        self.window_manager = WindowManager()
        self.embed_manager = EmbedManager(self.ui.scrollAreaWidgetContents, settings.max_height)
        self.layout_manager = LayoutManager(self.ui.gridLayout_2, settings.columns)
        self.preset_manager = PresetManager(settings.preset_file)
        self.monitor = WindowMonitor(self.window_manager, settings.monitor_interval_ms, self)
        self.monitor.changed.connect(self._on_windows_lost)
        self.drag_embed = WindowDragEmbedController(self, self.window_manager, self)
        self.drag_embed.dropped.connect(self._on_window_dropped)
        self.drag_embed.dragging_changed.connect(self._on_dragging_changed)
        self.drag_embed.start()
        self.command_received.connect(self._handle_command)
        self._auto_attach_timer = QTimer(self)
        self._auto_attach_timer.timeout.connect(self._auto_attach_tick)
        self._auto_attach_title = ""
        self._auto_attach_limit = 0
        self._auto_reconnect = True
        self.monitor.start()
        threading.Thread(target=self._run_server, daemon=True, name="EmbedTab-Flask").start()

    def _run_server(self):
        app.run(settings.host, settings.port, threaded=True, use_reloader=False)

    def _dispatch(self, action: str, **payload):
        event = threading.Event()
        command = {"action": action, "event": event, "payload": payload, "result": None}
        self.command_received.emit(command)
        if not event.wait(timeout=10):
            return {"status": False, "msg": "Qt command timeout"}
        return command["result"]

    @pyqtSlot(object)
    def _handle_command(self, command: dict) -> None:
        try:
            action, p = command["action"], command["payload"]
            handlers = {
                "embed": lambda: self._embed(int(p["handle"]), p.get("index"), bool(p.get("new"))),
                "remove": lambda: self._remove(int(p["index"])),
                "clear": self._clear,
                "list": self._list,
                "focus": lambda: self._focus(int(p["index"])),
                "layout": lambda: self._layout(int(p["columns"])),
                "auto_attach": lambda: self._auto_attach(p.get("title", ""), int(p.get("max_windows", 0))),
                "auto_attach_stop": self._auto_attach_stop,
                "preset_save": lambda: self._preset_save(p["name"]),
                "preset_load": lambda: self._preset_load(p["name"]),
                "preset_delete": lambda: self.preset_manager.delete(p["name"]),
            }
            if action not in handlers:
                raise ValueError(f"Unknown action: {action}")
            command["result"] = handlers[action]()
        except Exception:
            log.exception("Qt command failed")
            command["result"] = {"status": False, "msg": "Qt command error", "error": traceback.format_exc()}
        finally:
            command["event"].set()

    def _reflow(self):
        self.layout_manager.reflow(self.embed_manager.containers())

    def _on_window_dropped(self, hwnd: int) -> None:
        result = self._embed(hwnd, new=True)
        if result.get("status"):
            self.setWindowTitle("EmbedTab - Window embedded")
        else:
            log.warning("Dropped window was not embedded: %s", result)

    def _on_dragging_changed(self, dragging: bool) -> None:
        self.setWindowTitle("EmbedTab - Release here to embed window" if dragging else "EmbedTab")

    def _embed(self, handle: int, index=None, new=False):
        if not self.window_manager.validate(handle):
            return {"status": False, "msg": "handle not found!"}
        existing = self.embed_manager.find_by_hwnd(handle)
        if existing:
            return {"status": True, "msg": "already embedded", "index": existing.index, "hwnd": handle}
        if new:
            item = self.embed_manager.create_and_attach(handle)
        else:
            if index is None:
                return {"status": False, "msg": "Please enter index!"}
            if not self.embed_manager.contains(index):
                return {"status": False, "msg": "No indexes have been created for this tab!"}
            item = self.embed_manager.attach(index, handle)
        self._reflow()
        info = next((x for x in self.window_manager.find() if x.hwnd == item.hwnd), None)
        self.monitor.track(item.index, item.hwnd, info.title if info else "")
        return {"status": True, "msg": "success", "index": item.index, "hwnd": item.hwnd}

    def _remove(self, index):
        self.monitor.untrack(index)
        ok = self.embed_manager.remove(index)
        self._reflow()
        return {"status": ok, "index": index}

    def _clear(self):
        count = self.embed_manager.clear()
        self.monitor._tracked.clear()
        self._reflow()
        return {"status": True, "removed": count}

    def _list(self):
        return {"status": True, "windows": self.embed_manager.snapshot(self.window_manager)}

    def _focus(self, index):
        item = self.embed_manager.get(index)
        return {"status": bool(item and self.window_manager.focus(item.hwnd))}

    def _layout(self, columns):
        value = self.layout_manager.set_columns(columns)
        self._reflow()
        return {"status": True, "columns": value}

    def _auto_attach(self, title, max_windows):
        self._auto_attach_title = title
        self._auto_attach_limit = max_windows
        self._auto_attach_tick()
        self._auto_attach_timer.start(1000)
        return {"status": True, "title": title, "max_windows": max_windows, "running": True}

    def _auto_attach_stop(self):
        self._auto_attach_timer.stop()
        return {"status": True, "running": False}

    def _auto_attach_tick(self):
        current = len(self.embed_manager.indexes())
        if self._auto_attach_limit and current >= self._auto_attach_limit:
            return
        for info in self.window_manager.find(self._auto_attach_title):
            if self.embed_manager.find_by_hwnd(info.hwnd):
                continue
            if self._auto_attach_limit and len(self.embed_manager.indexes()) >= self._auto_attach_limit:
                break
            self._embed(info.hwnd, new=True)

    def _on_windows_lost(self, indexes):
        for index in indexes:
            item = self.embed_manager.get(index)
            if not item:
                continue
            metadata = self.monitor.metadata(index)
            title = metadata.get("title", "")
            log.info("Embedded window lost: index=%s hwnd=%s title=%s", index, item.hwnd, title)
            self.monitor.untrack(index)
            if not self._auto_reconnect:
                continue
            candidates = self.window_manager.find(title, limit=5) if title else []
            candidates = [x for x in candidates if not self.embed_manager.find_by_hwnd(x.hwnd)]
            if candidates:
                self.embed_manager.attach(index, candidates[0].hwnd)
                self.monitor.track(index, candidates[0].hwnd, candidates[0].title)
                self._reflow()

    def _preset_save(self, name):
        windows = []
        for item in self.embed_manager.snapshot(self.window_manager):
            if item["valid"]:
                info = next((x for x in self.window_manager.find() if x.hwnd == item["hwnd"]), None)
                windows.append({"hwnd": item["hwnd"], "title": info.title if info else ""})
        self.preset_manager.save(name, {"columns": self.layout_manager.columns, "windows": windows})
        return {"status": True, "name": name, "windows": len(windows)}

    def _preset_load(self, name):
        preset = self.preset_manager.get(name)
        if not preset:
            return {"status": False, "msg": "Preset not found"}
        self._layout(int(preset.get("columns", settings.columns)))
        loaded = 0
        for item in preset.get("windows", []):
            hwnd = int(item.get("hwnd", 0))
            if self.window_manager.validate(hwnd):
                self._embed(hwnd, new=True)
                loaded += 1
            elif item.get("title"):
                matches = self.window_manager.find(item["title"], limit=1)
                if matches:
                    self._embed(matches[0].hwnd, new=True)
                    loaded += 1
        return {"status": True, "name": name, "loaded": loaded}

    def embed(self):
        try:
            handle = int(request.args["handle"])
            new = request.args.get("new", "false").lower() == "true"
            index_raw = request.args.get("index")
            index = int(index_raw) if index_raw not in (None, "") else None
            return jsonify(self._dispatch("embed", handle=handle, index=index, new=new))
        except (KeyError, TypeError, ValueError):
            return jsonify({"status": False, "msg": "Invalid handle or index"}), 400


main = None


@app.route("/embed", methods=["GET"])
def embed_route():
    return main.embed()


@app.route("/api/v1/windows", methods=["GET"])
def windows_route():
    return jsonify(main._dispatch("list"))


@app.route("/api/v1/windows/embed", methods=["POST"])
def windows_embed_route():
    data = request.get_json(silent=True) or {}
    try:
        result = main._dispatch("embed", handle=int(data["hwnd"]), index=data.get("index"), new=bool(data.get("new", False)))
        return jsonify(result), 200 if result.get("status") else 400
    except (KeyError, TypeError, ValueError):
        return jsonify({"status": False, "msg": "hwnd is required and must be an integer"}), 400


@app.route("/api/v1/windows/<int:index>", methods=["DELETE"])
def remove_window_route(index):
    return jsonify(main._dispatch("remove", index=index))


@app.route("/api/v1/windows/clear", methods=["POST"])
def clear_windows_route():
    return jsonify(main._dispatch("clear"))


@app.route("/api/v1/windows/<int:index>/focus", methods=["POST"])
def focus_window_route(index):
    return jsonify(main._dispatch("focus", index=index))


@app.route("/api/v1/layout", methods=["POST"])
def layout_route():
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(main._dispatch("layout", columns=int(data["columns"])))
    except (KeyError, TypeError, ValueError):
        return jsonify({"status": False, "msg": "columns must be an integer"}), 400


@app.route("/api/v1/auto-attach", methods=["POST"])
def auto_attach_route():
    data = request.get_json(silent=True) or {}
    return jsonify(main._dispatch("auto_attach", title=data.get("title", ""), max_windows=int(data.get("max_windows", 0))))


@app.route("/api/v1/auto-attach/stop", methods=["POST"])
def auto_attach_stop_route():
    return jsonify(main._dispatch("auto_attach_stop"))


@app.route("/api/v1/presets", methods=["POST"])
def preset_save_route():
    data = request.get_json(silent=True) or {}
    return jsonify(main._dispatch("preset_save", name=str(data.get("name", "default"))))


@app.route("/api/v1/presets/load", methods=["POST"])
def preset_load_route():
    data = request.get_json(silent=True) or {}
    return jsonify(main._dispatch("preset_load", name=str(data.get("name", "default"))))


@app.route("/api/v1/presets/<name>", methods=["DELETE"])
def preset_delete_route(name):
    return jsonify(main._dispatch("preset_delete", name=name))


if __name__ == "__main__":
    qt_app = QApplication(sys.argv)
    main = MainEmbed()
    main.show()
    sys.exit(qt_app.exec_())
