from core.preset_manager import PresetManager


def test_preset_roundtrip(tmp_path):
    manager = PresetManager(str(tmp_path / "presets.json"))
    manager.save("demo", {"columns": 2, "windows": [{"title": "Chrome"}]})
    assert manager.get("demo")["columns"] == 2
    assert manager.delete("demo") is True
    assert manager.get("demo") is None
