import csv
import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER_PATH = os.path.join(BASE_DIR, "data", "ledger.csv")
MESSAGES_PATH = os.path.join(BASE_DIR, "data", "messages.jsonl")
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

LEDGER_FIELDS = [
    "timestamp", "sender", "amount", "category",
    "category_type", "item", "raw",
]


def init_ledger():
    """初始化账本文件（如不存在则创建）"""
    if not os.path.exists(LEDGER_PATH):
        with open(LEDGER_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=LEDGER_FIELDS)
            writer.writeheader()


def add_expense(parsed: dict) -> dict:
    """
    写入一条消费记录。

    Args:
        parsed: parser.py 返回的解析结果

    Returns:
        dict: 写入的记录
    """
    init_ledger()
    record = {
        "timestamp": datetime.now().isoformat(),
        "sender": parsed.get("sender", ""),
        "amount": parsed.get("amount", 0),
        "category": parsed.get("category", "未分类"),
        "category_type": parsed.get("category_type", "共同"),
        "item": parsed.get("item", ""),
        "raw": parsed.get("raw", ""),
    }
    with open(LEDGER_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LEDGER_FIELDS)
        writer.writerow(record)

    # 同时写入消息日志
    log_message(parsed)
    return record


def log_message(parsed: dict):
    """写入结构化消息日志（用于对话序列分析）"""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "sender": parsed.get("sender", ""),
        "raw": parsed.get("raw", ""),
        "intent": parsed.get("intent", ""),
        "amount": parsed.get("amount"),
        "category": parsed.get("category"),
        "dialogue_context": {
            "preceding_event": None,
            "follow_up": None,
            "follow_up_pattern": None,
        },
    }
    with open(MESSAGES_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def get_billing_period(now=None):
    """返回当前账期的起止时间（以 push_day 为每月起始日）。"""
    from datetime import timedelta
    now = now or datetime.now()
    start_day = CONFIG.get("report", {}).get("push_day", 12)
    if now.day >= start_day:
        period_start = now.replace(day=start_day, hour=0, minute=0, second=0, microsecond=0)
    else:
        # 上个月的 start_day
        first_of_month = now.replace(day=1)
        prev_month_end = first_of_month - timedelta(days=1)
        period_start = prev_month_end.replace(day=start_day, hour=0, minute=0, second=0, microsecond=0)
    return period_start


def get_monthly_summary(year: int = None, month: int = None) -> dict:
    """
    获取当前账期消费汇总（以 config.json 中 push_day 为每月起始日）。
    year/month 参数保留兼容性但不再使用。
    """
    init_ledger()
    now = datetime.now()
    period_start = get_billing_period(now)

    total = 0
    by_category = {}
    category_counts = {}

    with open(LEDGER_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = datetime.fromisoformat(row["timestamp"])
            if ts < period_start:
                continue
            if row["category_type"] != "共同":
                continue
            amount = float(row["amount"] or 0)
            cat = row["category"]
            total += amount
            by_category[cat] = by_category.get(cat, 0) + amount
            category_counts[cat] = category_counts.get(cat, 0) + 1

    pool = CONFIG["pool_amount"]
    remaining = pool - total

    # 拿铁因子：单次均价 < 100 且出现 >= 5 次的分类
    latte_factors = [
        (cat, category_counts[cat], by_category[cat])
        for cat in by_category
        if category_counts[cat] >= 5 and by_category[cat] / category_counts[cat] < 100
    ]
    latte_factors.sort(key=lambda x: x[2], reverse=True)

    return {
        "period_start": period_start.strftime("%Y-%m-%d"),
        "total": round(total, 2),
        "pool_amount": pool,
        "remaining": round(remaining, 2),
        "by_category": {k: round(v, 2) for k, v in sorted(
            by_category.items(), key=lambda x: x[1], reverse=True
        )},
        "latte_factors": latte_factors,
    }


def get_balance_text() -> str:
    """返回当前余额的简短文字描述"""
    summary = get_monthly_summary()
    return (
        f"本月已花 {summary['total']} 元，"
        f"池子还剩 {summary['remaining']} 元"
        f"（共 {summary['pool_amount']} 元）"
    )
