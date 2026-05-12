# Shared Expense Tracker 项目说明

## 网页抓取规则

WebFetch 失败时按顺序重试，不让用户手动操作：
1. **curl**：静态页面
2. **Playwright**：JS 渲染 / Cloudflare（`~/.local/share/uv/tools/playwright/bin/python3`）
3. 以上都失败才告知用户，并建议找 PubMed Central / arXiv / ResearchGate 的开放版本

## 项目概览

这是一个基于飞书 bot + Claude API 的共同财务记账系统，设计理念来自亲密关系研究和理财著作。完整设计见 `设计总结.md`。

## 飞书群消息处理规则

**收到飞书群消息时，无论内容是什么，都必须先运行记账脚本：**

```bash
cd /path/to/shared-expense-tracker
uv run python scripts/ledger_handler.py "发送者姓名" "消息内容"
```

- 脚本返回非空内容 → 把返回内容原样发回飞书群，不要修改或添加任何内容
- 脚本返回空字符串 → 说明是闲聊或无需处理，正常回复即可

脚本内部已用 Claude API 做语义识别，会自动判断是记账、查询、购物意图还是忽略。**不要在调用脚本之前自行判断是否财务相关。**

## 核心约定

- 所有财务相关对话必须在飞书群（群名在 config.json 中配置）中进行
- 账本数据（data/ledger.csv）和 API keys（.env）不上传 GitHub
- 购物意图写入苹果提醒事项（列表名在 config.json 中配置），标题加「🛒」前缀
- assets/ 目录存放设计图（SVG），已上传 GitHub

## 技术栈

- Python 3.12+
- cc-connect（飞书长连接驱动，开机自启）
- Claude API（语义解析）
- 本地 CSV 存储
- AppleScript（苹果提醒事项集成）
- Flask（问卷服务，Vercel 部署；本地 form_server.py 备用）
- Vercel + Upstash Redis（问卷云端部署与数据存储）
- lark-oapi SDK（飞书 bot 备用驱动）
- macOS Keychain（API keys 存储，via keychain.py）

## 分阶段实现

1. ✅ 核心记账（飞书消息 → Claude 解析 → CSV → 确认回复）
2. ✅ 查询和月报
3. ✅ 购物意图识别 → 提醒事项列表
4. ✅ 消费价值观对话系统
5. ✅ 金钱依恋风格问卷（ECR-R + KMSI-R + 系统模式选择）
