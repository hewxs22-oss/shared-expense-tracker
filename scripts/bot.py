import json
import os
import threading
import schedule
import time
import lark_oapi as lark
from lark_oapi.api.im.v1 import (
    P2ImMessageReceiveV1,
    CreateMessageRequest,
    CreateMessageRequestBody,
    ReplyMessageRequest,
    ReplyMessageRequestBody,
)

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from keychain import get_secret
from parser import parse_message
from ledger import add_expense, get_balance_text, get_monthly_summary
from report import build_monthly_report
from reminders import add_shopping_item
from system_mode import get_mode, set_mode, MODES

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

FEISHU_APP_ID = get_secret("FEISHU_APP_ID_JIZHANGMIAO")
FEISHU_APP_SECRET = get_secret("FEISHU_APP_SECRET_JIZHANGMIAO")
FEISHU_CHAT_ID = get_secret("FEISHU_CHAT_ID_JIZHANGMIAO")

# 已处理的消息 ID（防止重复处理）
processed_message_ids = set()

# 飞书 client（用于发送消息）
feishu_client = lark.Client.builder() \
    .app_id(FEISHU_APP_ID) \
    .app_secret(FEISHU_APP_SECRET) \
    .build()


def get_sender_key(open_id: str) -> str:
    """根据飞书 open_id 返回 W 或 J"""
    mapping = CONFIG.get("open_id_mapping", {})
    return mapping.get(open_id, "W")


def send_message(text: str):
    """主动发送消息到飞书群"""
    request = CreateMessageRequest.builder() \
        .receive_id_type("chat_id") \
        .request_body(
            CreateMessageRequestBody.builder()
            .receive_id(FEISHU_CHAT_ID)
            .msg_type("text")
            .content(json.dumps({"text": text}))
            .build()
        ).build()
    feishu_client.im.v1.message.create(request)


def reply_message(message_id: str, text: str):
    """回复某条消息"""
    request = ReplyMessageRequest.builder() \
        .message_id(message_id) \
        .request_body(
            ReplyMessageRequestBody.builder()
            .msg_type("text")
            .content(json.dumps({"text": text}))
            .build()
        ).build()
    feishu_client.im.v1.message.reply(request)


def handle_message(data: P2ImMessageReceiveV1) -> None:
    """处理飞书消息事件"""
    message = data.event.message
    message_id = message.message_id

    # 防重复处理
    if message_id in processed_message_ids:
        return
    processed_message_ids.add(message_id)

    # 只处理群消息
    if message.chat_type != "group":
        return

    # 提取文本
    try:
        content = json.loads(message.content)
        text = content.get("text", "").strip()
        # 去掉 @机器人 的部分
        if "@_user_" in text:
            import re
            text = re.sub(r'@_user_\S+\s*', '', text).strip()
    except Exception:
        return

    if not text:
        return

    # 获取发送者
    open_id = data.event.sender.sender_id.open_id
    sender = get_sender_key(open_id)
    mode = get_mode()

    # 模式选择
    import re
    mode_match = re.match(r'^选([ABC])$', text.strip())
    if mode_match:
        chosen = mode_match.group(1)
        set_mode(chosen)
        reply_message(message_id, f"✓ 已切换到{MODES[chosen]}，下次记账起生效。")
        return

    # 解析意图
    parsed = parse_message(text, sender)
    intent = parsed.get("intent", "ignore")

    if intent == "expense":
        record = add_expense(parsed)
        cat_type = record["category_type"]
        amount = record["amount"]
        category = record["category"]
        item = record["item"] or text

        # C 静默模式：只记录不回复
        if mode == "C":
            return

        if cat_type == "共同":
            reply = f"✓ 记好了\n{item} {amount} 元 · {category}"
        elif cat_type == "共同不入池":
            reply = f"✓ 记好了（不入池）\n{item} {amount} 元 · {category}\n记得和对方结算 AA"
        else:
            reply = f"✓ 记好了（个人）\n{item} {amount} 元 · {category}"

        # B 安心模式：附带当前余额
        if mode == "B" and cat_type == "共同":
            reply += f"\n{get_balance_text()}"

        # 超支预警
        if cat_type == "共同":
            summary = get_monthly_summary()
            pool = summary["pool_amount"]
            ratio = summary["total"] / pool if pool > 0 else 0
            if mode == "A" and ratio >= 0.9:
                reply += f"\n⚠️ 本月已用 {round(ratio*100)}%，接近超支"
            elif mode == "B" and ratio >= 0.7:
                reply += f"\n⚠️ 本月已用 {round(ratio*100)}%，注意节奏"

        reply_message(message_id, reply)

    elif intent == "shopping":
        item = parsed.get("shopping_item", text)
        success = add_shopping_item(item)
        if success:
            reply_message(message_id, f"✓ 已加入暂存库：🛒 {item}")
        else:
            reply_message(message_id, f"✓ 记下了：{item}（提醒事项写入失败，请手动添加）")

    elif intent == "query":
        query_type = parsed.get("query_type", "balance")
        if query_type == "balance":
            reply_message(message_id, get_balance_text())
        elif query_type == "monthly":
            summary = get_monthly_summary()
            lines = [f"本月消费 {summary['total']} 元，剩余 {summary['remaining']} 元"]
            for cat, amount in list(summary["by_category"].items())[:5]:
                lines.append(f"  {cat}：{amount} 元")
            reply_message(message_id, "\n".join(lines))

    elif intent == "ignore":
        if "开始填写问卷" in text or "填问卷" in text:
            base_url = CONFIG.get("form", {}).get("vercel_url", "").rstrip("/")
            if not base_url:
                host = CONFIG.get("form", {}).get("host", "127.0.0.1")
                port = CONFIG.get("form", {}).get("port", 5001)
                base_url = f"http://{host}:{port}"
            w_name = CONFIG["users"]["W"]
            j_name = CONFIG["users"]["J"]
            reply_message(
                message_id,
                f"请各自独立填写，不要互相讨论：\n"
                f"{w_name}：{base_url}/form?user=W\n"
                f"{j_name}：{base_url}/form?user=J",
            )


# ─── 定时任务 ─────────────────────────────────────────────

def monthly_report_job():
    from datetime import datetime
    now = datetime.now()
    if now.day == CONFIG["report"]["push_day"]:
        month = now.month - 1 if now.month > 1 else 12
        year = now.year if now.month > 1 else now.year - 1
        report = build_monthly_report(year, month)
        send_message(report)


def mid_month_checkin_job():
    """B 安心模式：每月15号推送余额进度"""
    from datetime import datetime
    now = datetime.now()
    if now.day == 15 and get_mode() == "B":
        summary = get_monthly_summary()
        pool = summary["pool_amount"]
        remaining = summary["remaining"]
        ratio = summary["total"] / pool if pool > 0 else 0
        send_message(
            f"📊 月中进度\n"
            f"池子还剩 {remaining} 元（已用 {round(ratio*100)}%），节奏正常 ✓"
        )


def run_scheduler():
    schedule.every().day.at("10:00").do(monthly_report_job)
    schedule.every().day.at("10:00").do(mid_month_checkin_job)
    while True:
        schedule.run_pending()
        time.sleep(60)


# ─── 启动 ─────────────────────────────────────────────────

def main():
    # 启动定时任务线程
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    # 注册消息事件处理器
    event_handler = lark.EventDispatcherHandler.builder("", "") \
        .register_p2_im_message_receive_v1(handle_message) \
        .build()

    # 启动长连接客户端
    ws_client = lark.ws.Client(
        FEISHU_APP_ID,
        FEISHU_APP_SECRET,
        event_handler=event_handler,
        log_level=lark.LogLevel.INFO,
    )

    print("记账喵启动中，使用长连接模式...")
    ws_client.start()


if __name__ == "__main__":
    main()
