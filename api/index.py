import json
import os
import requests
from flask import Flask, request, render_template, redirect
from upstash_redis import Redis

app = Flask(__name__, template_folder="../templates")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

FORM_DATA_KEY = "form_data"


def get_redis():
    return Redis(url=os.environ["KV_REST_API_URL"], token=os.environ["KV_REST_API_TOKEN"])


def load_form_data():
    try:
        redis = get_redis()
        data = redis.get(FORM_DATA_KEY)
        return json.loads(data) if data else {}
    except Exception:
        return {}


def save_form_data(data):
    redis = get_redis()
    if data:
        redis.set(FORM_DATA_KEY, json.dumps(data), ex=86400)
    else:
        redis.delete(FORM_DATA_KEY)


# ECR-R 36 道题（英文原版，Fraley et al. 2000）
ECR_QUESTIONS = [
    # 焦虑维度 题1-18
    "I'm afraid that I will lose my partner's love.",
    "I often worry that my partner will not want to stay with me.",
    "I often worry that my partner doesn't really love me.",
    "I worry that romantic partners won't care about me as much as I care about them.",
    "I often wish that my partner's feelings for me were as strong as my feelings for him or her.",
    "I worry a lot about my relationships.",
    "When my partner is out of sight, I worry that he or she might become interested in someone else.",
    "When I show my feelings for romantic partners, I'm afraid they will not feel the same about me.",
    "I rarely worry about my partner leaving me.",  # 反向题
    "My romantic partner makes me doubt myself.",
    "I do not often worry about being abandoned.",  # 反向题
    "I find that my partner(s) don't want to get as close as I would like.",
    "Sometimes romantic partners change their feelings about me for no apparent reason.",
    "My desire to be very close sometimes scares people away.",
    "I'm afraid that once a romantic partner gets to know me, he or she won't like who I really am.",
    "It makes me mad that I don't get the affection and support I need from my partner.",
    "I worry that I won't measure up to other people.",
    "My partner only seems to notice me when I'm angry.",
    # 回避维度 题19-36
    "I prefer not to show a partner how I feel deep down.",
    "I feel comfortable sharing my private thoughts and feelings with my partner.",  # 反向题
    "I find it difficult to allow myself to depend on romantic partners.",
    "I am very comfortable being close to romantic partners.",  # 反向题
    "I don't feel comfortable opening up to romantic partners.",
    "I prefer not to be too close to romantic partners.",
    "I get uncomfortable when a romantic partner wants to be very close.",
    "I find it relatively easy to get close to my partner.",  # 反向题
    "It's not difficult for me to get close to my partner.",  # 反向题
    "I usually discuss my problems and concerns with my partner.",  # 反向题
    "It helps to turn to my romantic partner in times of need.",  # 反向题
    "I tell my partner just about everything.",  # 反向题
    "I talk things over with my partner.",  # 反向题
    "I am nervous when partners get too close to me.",
    "I feel comfortable depending on romantic partners.",  # 反向题
    "I find it easy to depend on romantic partners.",  # 反向题
    "It's easy for me to be affectionate with my partner.",  # 反向题
    "My partner really understands me and my needs.",  # 反向题
]

# KMSI-R 32 道题（Klontz & Britt, 2013）
KMSI_QUESTIONS = [
    # Money Avoidance 题1-9
    "I do not deserve a lot of money when others have less than me.",
    "Rich people are greedy.",
    "People get rich by taking advantage of others.",
    "I do not deserve money.",
    "Good people should not care about money.",
    "It is hard to be rich and be a good person.",
    "The less money you have, the better life is.",
    "Money corrupts people.",
    "Being rich means you no longer fit in with old friends and family.",
    # Money Worship 题10-16
    "Things would get better if I had more money.",
    "More money will make you happier.",
    "It is hard to be poor and happy.",
    "You can never have enough money.",
    "Money is power.",
    "Money would solve all my problems.",
    "Money buys freedom.",
    # Money Status 题17-24
    "Most poor people do not deserve to have money.",
    "You can have love or money, but not both.",
    "I will not buy something unless it is new (e.g., car, house).",
    "Poor people are lazy.",
    "Money is what gives life meaning.",
    "Your self-worth equals your net worth.",
    "If something is not considered the 'best,' it is not worth buying.",
    "People are only as successful as the amount of money they earn.",
    # Money Vigilance 题25-32
    "You should not tell others how much money you have or make.",
    "It is wrong to ask others how much money you have or make.",
    "Money should be saved not spent.",
    "It is important to save for a rainy day.",
    "People should work for their money and not be given financial handouts.",
    "I would be a nervous wreck if I did not have money saved for an emergency.",
    "You should always look for the best deal before buying something, even if it takes more time.",
    "It is extravagant to spend money on oneself.",
]

# ECR-R 反向题编号（1-indexed）
ECR_ANXIETY_REVERSE = {9, 11}
ECR_AVOIDANCE_REVERSE = {20, 22, 26, 27, 28, 29, 30, 31, 33, 34, 35, 36}


def calculate_ecr(answers):
    anxiety_scores = []
    for i in range(1, 19):
        score = answers[f"ecr_{i}"]
        if i in ECR_ANXIETY_REVERSE:
            score = 8 - score
        anxiety_scores.append(score)

    avoidance_scores = []
    for i in range(19, 37):
        score = answers[f"ecr_{i}"]
        if i in ECR_AVOIDANCE_REVERSE:
            score = 8 - score
        avoidance_scores.append(score)

    return {
        "anxiety": round(sum(anxiety_scores) / len(anxiety_scores), 2),
        "avoidance": round(sum(avoidance_scores) / len(avoidance_scores), 2),
    }


def calculate_kmsi(answers):
    avoidance = sum(answers[f"kmsi_{i}"] for i in range(1, 10))
    worship = sum(answers[f"kmsi_{i}"] for i in range(10, 17))
    status = sum(answers[f"kmsi_{i}"] for i in range(17, 25))
    vigilance = sum(answers[f"kmsi_{i}"] for i in range(25, 33))
    return {
        "money_avoidance": avoidance,
        "money_worship": worship,
        "money_status": status,
        "money_vigilance": vigilance,
    }


def ecr_label(anxiety, avoidance):
    mid = 4.0
    if anxiety < mid and avoidance < mid:
        return "安全型（低焦虑 + 低回避）"
    elif anxiety >= mid and avoidance < mid:
        return "焦虑/痴迷型（高焦虑 + 低回避）"
    elif anxiety < mid and avoidance >= mid:
        return "回避/疏离型（低焦虑 + 高回避）"
    else:
        return "恐惧型（高焦虑 + 高回避）"


def kmsi_dominant(kmsi):
    normalized = {
        "金钱回避": kmsi["money_avoidance"] / 9,
        "金钱崇拜": kmsi["money_worship"] / 7,
        "金钱地位": kmsi["money_status"] / 8,
        "金钱警觉": kmsi["money_vigilance"] / 8,
    }
    return max(normalized, key=normalized.get)


def build_report(data):
    users = CONFIG["users"]
    lines = ["📊 金钱依恋风格报告\n"]

    for user_key, user_name in users.items():
        if user_key not in data:
            continue
        ecr = data[user_key]["ecr"]
        kmsi = data[user_key]["kmsi"]
        dominant = kmsi_dominant(kmsi)
        label = ecr_label(ecr["anxiety"], ecr["avoidance"])

        lines.append(f"━━━━━━━━")
        lines.append(f"{user_name} 的画像")
        lines.append(f"━━━━━━━━")
        lines.append(f"依恋风格（ECR-R）")
        lines.append(f"  焦虑维度：{ecr['anxiety']}/7")
        lines.append(f"  回避维度：{ecr['avoidance']}/7")
        lines.append(f"  → {label}")
        lines.append(f"")
        lines.append(f"金钱脚本（KMSI-R）")
        lines.append(f"  金钱回避：{kmsi['money_avoidance']}/54")
        lines.append(f"  金钱崇拜：{kmsi['money_worship']}/42")
        lines.append(f"  金钱地位：{kmsi['money_status']}/48")
        lines.append(f"  金钱警觉：{kmsi['money_vigilance']}/48")
        lines.append(f"  → 主导脚本：{dominant}")
        lines.append(f"")

    if len(data) == 2:
        keys = list(data.keys())
        a_ecr = data[keys[0]]["ecr"]
        b_ecr = data[keys[1]]["ecr"]
        lines.append("━━━━━━━━")
        lines.append("组合分析")
        lines.append("━━━━━━━━")

        anxiety_diff = abs(a_ecr["anxiety"] - b_ecr["anxiety"])
        avoidance_diff = abs(a_ecr["avoidance"] - b_ecr["avoidance"])

        if anxiety_diff > 1.5 or avoidance_diff > 1.5:
            lines.append("⚠️ 两人在依恋风格上有明显差异，建议讨论各自的需求。")
        else:
            lines.append("✅ 两人依恋风格较为接近。")

        lines.append("")
        lines.append("请两人看完后讨论：")
        lines.append("这个描述准确吗？你们想选哪个系统模式？")
        lines.append("")
        lines.append("A 标准模式：简短确认，预估超支时提醒")
        lines.append("B 安心模式：记账附带余额，15号推送进度，花到70%提醒")
        lines.append("C 静默模式：只记录不回复，月报里体现")
        lines.append("")
        lines.append("在群里回复「选A」「选B」或「选C」即可生效。")

    return "\n".join(lines)


def send_to_feishu(text):
    app_id = os.environ.get("FEISHU_APP_ID")
    app_secret = os.environ.get("FEISHU_APP_SECRET")
    chat_id = os.environ.get("FEISHU_CHAT_ID")

    token_resp = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": app_id, "app_secret": app_secret},
    ).json()
    token = token_resp.get("tenant_access_token")

    requests.post(
        "https://open.feishu.cn/open-apis/im/v1/messages",
        params={"receive_id_type": "chat_id"},
        headers={"Authorization": f"Bearer {token}"},
        json={
            "receive_id": chat_id,
            "msg_type": "text",
            "content": json.dumps({"text": text}),
        },
    )


@app.route("/form")
def form():
    user = request.args.get("user", "").upper()
    if user not in CONFIG["users"]:
        return "无效的用户参数。请使用 /form?user=W 或 /form?user=J", 400
    user_name = CONFIG["users"][user]
    return render_template(
        "questionnaire.html",
        user=user,
        user_name=user_name,
        ecr_questions=ECR_QUESTIONS,
        kmsi_questions=KMSI_QUESTIONS,
    )


@app.route("/submit", methods=["POST"])
def submit():
    user = request.form.get("user", "").upper()
    if user not in CONFIG["users"]:
        return "无效的用户参数", 400

    answers = {}
    for i in range(1, 37):
        val = request.form.get(f"ecr_{i}")
        if not val:
            return "请完成所有题目", 400
        answers[f"ecr_{i}"] = int(val)
    for i in range(1, 33):
        val = request.form.get(f"kmsi_{i}")
        if not val:
            return "请完成所有题目", 400
        answers[f"kmsi_{i}"] = int(val)

    ecr = calculate_ecr(answers)
    kmsi = calculate_kmsi(answers)

    form_data = load_form_data()
    form_data[user] = {"ecr": ecr, "kmsi": kmsi}
    save_form_data(form_data)

    all_users = set(CONFIG["users"].keys())
    submitted_users = set(form_data.keys())

    if all_users == submitted_users:
        report = build_report(form_data)
        send_to_feishu(report)
        save_form_data({})
        message = "两人都已填写完毕，报告已推送到飞书群！"
    else:
        waiting_for = all_users - submitted_users
        waiting_names = [CONFIG["users"][u] for u in waiting_for]
        message = f"提交成功！等待 {'、'.join(waiting_names)} 填写完毕后，报告将自动推送到飞书群。"

    return render_template("submitted.html", message=message)
