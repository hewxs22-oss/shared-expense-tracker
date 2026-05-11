"""
命令行入口：供 Kiro（CC-Connect）调用处理财务消息。

用法：
    uv run python scripts/ledger_handler.py "W" "买了猫粮 80" "msg_xxx"

输出：
    直接打印回复内容，Kiro 把这段内容发回飞书群。
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parser import parse_message
from ledger import add_expense, get_balance_text, get_monthly_summary
from reminders import add_shopping_item
from system_mode import get_mode, set_mode, MODES

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

# 发送者姓名 → W/J 映射（从 config.json 读取，避免硬编码）
NAME_TO_KEY = {name: key for key, name in CONFIG["users"].items()}


def handle(sender_name: str, text: str) -> str:
    """处理一条财务消息，返回回复文字。"""
    sender = NAME_TO_KEY.get(sender_name, "W")
    mode = get_mode()

    parsed = parse_message(text, sender)
    intent = parsed.get("intent", "ignore")

    if intent == "mode_select":
        chosen = parsed.get("mode", "").upper()
        if chosen in MODES:
            set_mode(chosen)
            return f"✓ 已切换到{MODES[chosen]}，下次记账起生效。"

    elif intent == "expense":
        record = add_expense(parsed)
        cat_type = record["category_type"]
        amount = record["amount"]
        category = record["category"]
        item = record["item"] or text

        # C 静默模式：只记录不回复
        if mode == "C":
            return ""

        if cat_type == "共同":
            reply = f"✓ 记好了\n{item} {amount} 元 · {category}"
        elif cat_type == "共同不入池":
            reply = f"✓ 记好了（不入池）\n{item} {amount} 元 · {category}\n记得和对方结算 AA"
        else:
            reply = f"✓ 记好了（个人）\n{item} {amount} 元 · {category}"

        # B 安心模式：附带当前余额
        if mode == "B" and cat_type == "共同":
            balance = get_balance_text()
            reply += f"\n{balance}"

        # 超支预警
        if cat_type == "共同":
            from ledger import get_monthly_summary
            summary = get_monthly_summary()
            pool = summary["pool_amount"]
            total = summary["total"]
            ratio = total / pool if pool > 0 else 0
            if mode == "A" and ratio >= 0.9:
                reply += f"\n⚠️ 本月已用 {round(ratio*100)}%，接近超支"
            elif mode == "B" and ratio >= 0.7:
                reply += f"\n⚠️ 本月已用 {round(ratio*100)}%，注意节奏"

        return reply

    elif intent == "shopping":
        item = parsed.get("shopping_item", text)
        success = add_shopping_item(item)
        if success:
            list_name = CONFIG["reminders"]["list_name"]
            return f"✓ 已加入{list_name}：🛒 {item}"
        else:
            return f"✓ 记下了：{item}（提醒事项写入失败，请手动添加）"

    elif intent == "query":
        query_type = parsed.get("query_type", "balance")
        if query_type == "balance":
            return get_balance_text()
        elif query_type == "monthly":
            summary = get_monthly_summary()
            lines = [f"本月消费 {summary['total']} 元，剩余 {summary['remaining']} 元"]
            for cat, amount in list(summary["by_category"].items())[:5]:
                lines.append(f"  {cat}：{amount} 元")
            return "\n".join(lines)

    elif intent == "ignore":
        if "开始填写问卷" in text or "填问卷" in text:
            base_url = CONFIG.get("form", {}).get("vercel_url", "").rstrip("/")
            if not base_url:
                host = CONFIG.get("form", {}).get("host", "127.0.0.1")
                port = CONFIG.get("form", {}).get("port", 5001)
                base_url = f"http://{host}:{port}"
            w_name = CONFIG["users"]["W"]
            j_name = CONFIG["users"]["J"]
            return (
                f"请各自独立填写，不要互相讨论：\n"
                f"{w_name}：{base_url}/form?user=W\n"
                f"{j_name}：{base_url}/form?user=J"
            )

    return ""


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法：python ledger_handler.py <发送者姓名> <消息内容>", file=sys.stderr)
        sys.exit(1)

    sender_name = sys.argv[1]
    text = sys.argv[2]

    result = handle(sender_name, text)
    if result:
        print(result)
