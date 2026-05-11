import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODE_PATH = os.path.join(BASE_DIR, "data", "system_mode.json")

MODES = {
    "A": "标准模式",
    "B": "安心模式",
    "C": "静默模式",
}


def get_mode() -> str:
    """返回当前模式，默认 A。"""
    if not os.path.exists(MODE_PATH):
        return "A"
    try:
        with open(MODE_PATH) as f:
            return json.load(f).get("mode", "A").upper()
    except Exception:
        return "A"


def set_mode(mode: str) -> bool:
    """写入模式，返回是否成功。"""
    mode = mode.upper()
    if mode not in MODES:
        return False
    with open(MODE_PATH, "w") as f:
        json.dump({"mode": mode}, f)
    return True


def mode_description() -> str:
    """返回当前模式的说明文字。"""
    mode = get_mode()
    descriptions = {
        "A": "A 标准模式：简短确认，预估超支时提醒",
        "B": "B 安心模式：记账附带余额，15号推送进度，花到70%提醒",
        "C": "C 静默模式：只记录不回复，月报里体现",
    }
    return descriptions[mode]
