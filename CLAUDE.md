# Shared Expense Tracker 项目说明

## 网页抓取规则

WebFetch 失败时按顺序重试，不让用户手动操作：
1. **curl**：静态页面
2. **Playwright**：JS 渲染 / Cloudflare（`/home/user/.local/share/uv/tools/playwright/bin/python3`）
3. 以上都失败才告知用户，并建议找 PubMed Central / arXiv / ResearchGate 的开放版本

## 项目概览

这是一个基于飞书 bot + Claude API 的共同财务记账系统，设计理念来自亲密关系研究和理财著作。完整设计见 `设计总结.md`。

## 飞书群消息处理规则

**当收到飞书群消息时，必须按以下规则处理，不能随意回复：**

### 财务相关消息 → 调用记账脚本

判断消息是否财务相关（记账/查询/购物意图），如果是，运行：

```bash
cd /home/user/shared-expense-tracker
uv run python scripts/ledger_handler.py "发送者姓名" "消息内容"
```

脚本会返回回复内容，直接把返回内容发回飞书群，不要修改或添加任何内容。

### 非财务消息 → 正常处理

闲聊、技术问题、项目操作等，正常回复。

### 财务消息判断标准

以下属于财务消息：
- 记账：包含金额数字 + 消费描述（"买了猫粮 80"、"打车 45"、"交了房租 3500"）
- 查询：询问余额、消费情况（"还剩多少"、"这个月花了多少"）
- 购物意图：表达需要购买某物（"洗衣液没了"、"要买猫粮"）
- 触发问卷：包含"填问卷"或"开始填写问卷"

以下不属于财务消息：
- 纯闲聊（"你好"、"今天天气好"）
- 技术问题
- 项目开发相关指令

## 核心约定

- 所有财务相关对话必须在飞书群"Shared Expenses"中进行
- 账本数据（data/ledger.csv）和 API keys（.env）不上传 GitHub
- 购物意图写入苹果提醒事项「Inbox」，标题加「🛒」前缀
- assets/ 目录存放设计图（SVG），已上传 GitHub

## 技术栈

- Python 3.12+
- cc-connect（飞书长连接驱动，开机自启）
- Claude API（语义解析）
- 本地 CSV 存储
- AppleScript（苹果提醒事项集成）
- Flask（问卷 HTTP 服务，port 5001）
- macOS Keychain（API keys 存储，via keychain.py）

## 分阶段实现

1. ✅ 核心记账（飞书消息 → Claude 解析 → CSV → 确认回复）
2. ✅ 查询和月报
3. ✅ 购物意图识别 → Inbox
4. ✅ 消费价值观对话系统
5. ✅ 金钱依恋风格问卷（ECR-R + KMSI-R + 系统模式选择）
