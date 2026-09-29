import json
from pathlib import Path
from typing import Dict, List


class PresetManager:
    def __init__(self, path: str = "presets.json") -> None:
        self.path = Path(path)

    def load_all(self) -> Dict[str, dict]:
        if not self.path.exists():
            return {}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except (OSError, ValueError):
            return {}

    def save(self, name: str, preset: dict) -> None:
        data = self.load_all()
        data[str(name)] = preset
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def get(self, name: str):
        return self.load_all().get(name)

    def delete(self, name: str) -> bool:
        data = self.load_all()
        if name not in data:
            return False
        del data[name]
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
