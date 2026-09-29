import requests


class EmbedAPI:
    def __init__(self, port: int = 5000, timeout: float = 10):
        self.domain = f"http://127.0.0.1:{port}"
        self.timeout = timeout

    def _request(self, method, path, **kwargs):
        response = requests.request(method, self.domain + path, timeout=self.timeout, **kwargs)
        response.raise_for_status()
        return response.json()

    def embed_tab(self, handle, **kwargs): return self._request("GET", "/embed", params={"handle": handle, **kwargs})
    def embed(self, hwnd: int, index=None, new: bool = False):
        payload = {"hwnd": int(hwnd), "new": bool(new)}
        if index is not None: payload["index"] = int(index)
        return self._request("POST", "/api/v1/windows/embed", json=payload)
    def windows(self): return self._request("GET", "/api/v1/windows")
    def remove(self, index: int): return self._request("DELETE", f"/api/v1/windows/{int(index)}")
    def clear(self): return self._request("POST", "/api/v1/windows/clear")
    def focus(self, index: int): return self._request("POST", f"/api/v1/windows/{int(index)}/focus")
    def set_columns(self, columns: int): return self._request("POST", "/api/v1/layout", json={"columns": int(columns)})
    def swap(self, first: int, second: int): return self._request("POST", "/api/v1/layout/swap", json={"first": int(first), "second": int(second)})
    def save_preset(self, name: str): return self._request("POST", "/api/v1/presets", json={"name": name})
    def load_preset(self, name: str): return self._request("POST", "/api/v1/presets/load", json={"name": name})
    def auto_attach(self, title: str = "", max_windows: int = 0): return self._request("POST", "/api/v1/auto-attach", json={"title": title, "max_windows": max_windows})
    def stop_auto_attach(self): return self._request("POST", "/api/v1/auto-attach/stop")
