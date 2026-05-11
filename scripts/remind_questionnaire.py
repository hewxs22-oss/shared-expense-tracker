"""
定时推送问卷提醒到飞书群。
由 launchd 在指定日期触发。
"""
import json
import os
import sys
from datetime import datetime, timezone, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "scripts"))

from bot import send_message, CONFIG

if __name__ == "__main__":
    cst = timezone(timedelta(hours=8))
    now = datetime.now(cst).strftime("%Y年%m月%d日")
    base_url = CONFIG.get("form", {}).get("vercel_url", "").rstrip("/")
    w_name = CONFIG["users"]["W"]
    j_name = CONFIG["users"]["J"]

    msg = (
        f"📋 六个月到了，是时候重新填一次金钱依恋风格问卷了（{now}）\n\n"
        f"上次填完后你们的风格可能有所变化，重测可以看到成长。\n\n"
        f"请各自独立填写：\n"
        f"{w_name}：{base_url}/form?user=W\n"
        f"{j_name}：{base_url}/form?user=J"
    )
    send_message(msg)
    print(f"[{now}] 问卷提醒已推送")
