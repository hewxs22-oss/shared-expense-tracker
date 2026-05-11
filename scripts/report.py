import json
import os
import random
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger import get_monthly_summary

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

# 月报末尾的开放式问题（随机选一个）
OPEN_QUESTIONS = [
    "这个月有没有哪笔花得特别值？",
    "下个月有没有想一起花的钱？",
    "这个月的消费节奏感觉怎么样？",
    "有没有哪个分类你觉得可以调整一下？",
]


def build_monthly_report(year: int = None, month: int = None) -> str:
    """
    生成月度消费报告文字。

    Returns:
        str: 飞书消息文字
    """
    now = datetime.now()
    year = year or now.year
    month = month or now.month
    summary = get_monthly_summary(year, month)

    lines = [f"📊 {year}年{month}月 消费报告\n"]

    # 总览
    pool = summary["pool_amount"]
    total = summary["total"]
    remaining = summary["remaining"]
    usage_pct = round(total / pool * 100, 1) if pool > 0 else 0

    lines.append(f"我们这个月花了 {total} 元")
    lines.append(f"池子共 {pool} 元，剩余 {remaining} 元（已用 {usage_pct}%）")
    lines.append("")

    # 分类明细
    if summary["by_category"]:
        lines.append("── 分类明细 ──")
        for cat, amount in summary["by_category"].items():
            pct = round(amount / total * 100, 1) if total > 0 else 0
            lines.append(f"  {cat}：{amount} 元（{pct}%）")
        lines.append("")

    # 拿铁因子
    if summary["latte_factors"]:
        lines.append("── 拿铁因子（高频小额）──")
        for cat, count, amount in summary["latte_factors"]:
            avg = round(amount / count, 1)
            lines.append(f"  {cat}：{count} 次，共 {amount} 元（均价 {avg} 元）")
        lines.append("")

    # 结构分析（固定 vs 弹性）
    fixed_cats = {"房租水电"}
    fixed = sum(v for k, v in summary["by_category"].items() if k in fixed_cats)
    flexible = total - fixed
    if total > 0:
        lines.append("── 消费结构 ──")
        lines.append(f"  固定开支：{fixed} 元（{round(fixed/total*100, 1)}%）")
        lines.append(f"  弹性消费：{flexible} 元（{round(flexible/total*100, 1)}%）")
        lines.append("")

    # 开放式问题
    question = random.choice(OPEN_QUESTIONS)
    lines.append(f"💬 {question}")

    return "\n".join(lines)


if __name__ == "__main__":
    print(build_monthly_report())
