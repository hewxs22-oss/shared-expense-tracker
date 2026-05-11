import subprocess
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

LIST_NAME = CONFIG["reminders"]["list_name"]
PREFIX = CONFIG["reminders"]["shopping_prefix"]


def add_shopping_item(item: str) -> bool:
    """
    将购物项目写入苹果提醒事项暂存库。

    Args:
        item: 购物项目名称（如"猫粮"）

    Returns:
        bool: 是否成功
    """
    title = f"{PREFIX} {item}"
    script = f'''
tell application "Reminders"
    set targetList to list "{LIST_NAME}"
    set newReminder to make new reminder at end of targetList
    set name of newReminder to "{title}"
end tell
'''
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except Exception:
        return False


def get_shopping_list() -> list:
    """
    获取暂存库中所有购物项目（以 🛒 开头的）。

    Returns:
        list: 购物项目名称列表
    """
    script = f'''
tell application "Reminders"
    set targetList to list "{LIST_NAME}"
    set allReminders to reminders of targetList whose completed is false
    set result to {{}}
    repeat with r in allReminders
        set rName to name of r
        if rName starts with "{PREFIX}" then
            set end of result to rName
        end if
    end repeat
    return result
end tell
'''
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            items = result.stdout.strip().split(", ")
            return [i.replace(f"{PREFIX} ", "").strip() for i in items if i.strip()]
        return []
    except Exception:
        return []


if __name__ == "__main__":
    # 测试
    success = add_shopping_item("猫粮")
    print(f"添加购物项目：{'成功' if success else '失败'}")
    items = get_shopping_list()
    print(f"当前购物清单：{items}")
