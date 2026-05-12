import json
import os
import sys
import anthropic

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from keychain import get_secret

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATEGORIES_PATH = os.path.join(BASE_DIR, "categories.json")
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

with open(CATEGORIES_PATH) as f:
    CATEGORIES = json.load(f)

with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

client = anthropic.Anthropic(api_key=get_secret("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """你是一个共同记账系统的语义解析器。

用户会发送飞书群消息，你需要判断消息的意图并提取信息。

分类体系：
{categories}

用户配置：
- W（{w_name}）：低收入方，承担35%
- J（{j_name}）：高收入方，承担65%

请返回 JSON 格式，包含以下字段：
- intent: "expense"（记账）| "query"（查询）| "shopping"（购物意图）| "mode_select"（选择系统模式）| "ignore"（忽略）
- amount: 金额（数字，仅 expense 时有效）
- category: 分类名称（仅 expense 时有效）
- category_type: "共同" | "个人" | "共同不入池"（仅 expense 时有效）
- item: 消费项目描述
- shopping_item: 购物清单项目（仅 shopping 时有效）
- query_type: "balance"（余额）| "monthly"（月度）| "category"（分类）（仅 query 时有效）
- mode: "A" | "B" | "C"（仅 mode_select 时有效）
- dialogue_context: 对话上下文信号（可选）
  - has_justification: 是否包含解释性语言
  - follow_up_needed: 是否需要追踪后续回应

判断规则：
1. 已经发生的消费行为（有金额或可推断金额）→ expense
   - 金额可以是数字、汉字、口语（「八块」「两百多」「人均六七十」）
   - 货币符号 $、¥、USD、CNY 均有效
   - 英文表达同样有效（"28 bucks"、"paid for groceries"）
2. 表达「某样东西需要购买/补充/已经用完/快没了」的意图，尚未发生消费 → shopping
   - 不需要金额，重点是「需要买」这个意图
   - 即使提到预期金额（「大概要花50」）也是 shopping，因为还没买
3. 询问当前余额、本期消费情况 → query
4. 消息中明确表达选择系统模式 → mode_select，mode 字段填 A/B/C
   - A（标准模式）：「选A」「第一个」「标准」等
   - B（安心模式）：「选B」「第二个」「安心」等
   - C（静默模式）：「选C」「第三个」「静默」等
5. 固定支出（房租、水电）只有明确说「交了/付了」才记，不自动记
6. 其他闲聊、技术问题 → ignore

只返回 JSON，不要其他文字。""".format(
    categories=json.dumps(CATEGORIES, ensure_ascii=False, indent=2),
    w_name=CONFIG["users"]["W"],
    j_name=CONFIG["users"]["J"],
)


def parse_message(text: str, sender: str) -> dict:
    """
    解析飞书消息，返回结构化意图。

    Args:
        text: 消息文本
        sender: 发送者 "W" 或 "J"

    Returns:
        dict: 解析结果
    """
    try:
        response = client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=512,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"发送者：{sender}\n消息内容：{text}",
                }
            ],
        )
        raw_text = response.content[0].text.strip()
        # 去掉 markdown 代码块包装
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[-1]
            raw_text = raw_text.rsplit("```", 1)[0].strip()
        result = json.loads(raw_text)
        result["sender"] = sender
        result["raw"] = text
        return result
    except (json.JSONDecodeError, Exception) as e:
        return {
            "intent": "ignore",
            "sender": sender,
            "raw": text,
            "error": str(e),
        }


if __name__ == "__main__":
    # 简单测试
    tests = [
        ("买了猫粮 80", "W"),
        ("洗衣液没了", "J"),
        ("这个月花了多少", "W"),
        ("今天天气真好", "J"),
        ("交了房租 3500", "W"),
        ("打车去医院 45，看病", "J"),
    ]
    for text, sender in tests:
        result = parse_message(text, sender)
        print(f"[{sender}] {text}")
        print(f"  → {result}\n")
