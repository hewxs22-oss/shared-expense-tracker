# Shared Expense Tracker — Design Summary

## Account Model (Example)

The amounts below are illustrative. Replace with your actual figures when setting up.

- One joint bank account (held by W); J is added as a supplementary cardholder
- On the 10th of each month: J transfers in a fixed amount, W transfers in a fixed amount — contributions split 35% / 65% by income ratio
- All day-to-day shared expenses are paid from this account

## Configuration (Example)

Replace the values below with your actual setup.

- Feishu group name: Shared Expenses
- W (lower earner): covers 35%
- J (higher earner): covers 65%
- The ratio is fixed and does not adjust with income changes

## Category System

| Category | Type | Includes |
|----------|------|----------|
| Food & Dining | Shared | Breakfast, lunch, dinner, takeout, fruit & snacks |
| Rent & Utilities | Shared | Rent, electricity, gas, water |
| Household Supplies | Shared | Toiletries, tissues, trash bags, kitchen items, bottled water |
| Pets | Shared | Daily supplies, treats |
| Pet Medical | Personal | Each person covers their own pet's vet bills; not pooled |
| Transportation | Shared | Subway, rideshare |
| Allowance | Shared | ¥500 each |
| AI / Tools | Personal (not pooled) | API tokens, subscriptions, web services — each pays their own |
| Medical | Personal | Doctor visits, checkups, medication |
| Social | Personal | Dining out with friends, gifts, travel |
| Courses / Communities | Shared (not pooled) | Online courses, paid communities — default split 50/50 unless one person volunteers to cover it; settled by direct transfer, not through the joint account |
| Large Purchases | Personal | Insurance, devices |

## Settlement Logic

- Normal: all shared expenses come out of the pool; at month-end, review total spend, remaining balance, and category breakdown
- Overage: any amount beyond the pool total is topped up by each person at the 35/65 ratio
- Misuse: if a personal expense is accidentally charged to the joint account, that person reimburses the pool at month-end

## Expense Logging

- Say anything in the Feishu group "Shared Expenses" — the bot parses and logs it automatically
- The payer is inferred from who sent the message (W or J); this records who handled the transaction, not who bears the cost
- Fixed expenses (rent, utilities) are only logged when explicitly mentioned — they are not auto-recorded

### Ground Rules

**All shared-finance conversations must happen in the Feishu group "Shared Expenses" — not by voice, WeChat, or any other channel.** Reasons:

1. The system depends on group chat text to log expenses, run analysis, and collect behavioral signals (e.g. for attachment style inference)
2. A dedicated space for money talk keeps it separate from everyday conversation, reducing the psychological weight of "talking about money"
3. Everything is on record and traceable — no missed messages, no memory gaps

## Shopping Intent Detection

- Intent is inferred semantically — no fixed phrasing required
- "We're out of laundry detergent" / "Almost out of cat food" → writes a 🛒 reminder to the configured Apple Reminders list (e.g. "🛒 Cat food"); visible to both; not logged as an expense
- "Bought laundry detergent ¥50" → logged as an expense; no reminder created

---

## Financial Analysis

- On demand: ask "how much have we spent this month" in the Feishu group; the bot replies immediately
- Automatic: a monthly spending report is pushed to the Feishu group on the 10th of each month (format details below)

### Design Principle A: Relationship First (from attachment theory)

Sources: Gottman, *The Seven Principles for Making Marriage Work*; Sue Johnson, *Hold Me Tight*

Gottman's research found that in conflict discussions, stable long-term couples maintain a positive-to-negative interaction ratio of at least 5:1 — that's a floor, not an average, and it applies specifically to conflict, not everyday interaction. The three stable couple types he studied (conflict-avoiding, validating, volatile) look very different from each other, but all maintain this ratio during disagreements. Sue Johnson's attachment framework adds that arguments about money are fundamentally attachment bids: "do you still care about me?"

Based on this research, the system's financial reporting follows these principles:

1. **Neutral tone in monthly reports** — pure data analysis (how much was spent, category breakdown, trends); no judgment, no warnings, no pressure. Avoid becoming an "emotional withdrawal" in the relationship.
2. **Warm, brief bot responses** — each expense confirmation is kept short and friendly. The act of logging an expense is itself a signal of "I'm taking care of us"; the bot's reply is a turn-toward that signal.
3. **One open-ended question at the end of each monthly report** — turns the report into a conversation starter, creating a monthly ritual. Examples: "Was there anything you spent money on this month that felt especially worth it?" or "Is there something you'd like us to spend on together next month?"

### Design Principle B: Money Serves the Relationship (from couples + money research)

Sources: Myra Strober, *Money and Love*; Ed Coambs, *The Healthy Love and Money Way*; Pooling Finances and Relationship Satisfaction (2022, N=38,534); Common Cents (2023, Eli Finkel, Northwestern); Feeling Appreciated (2022)

Research shows that pooling finances improves relationship satisfaction through three mechanisms:

- **Financial Harmony**: greater satisfaction with "how we handle money together"; fewer conflicts
- **Communal Strength**: pooling reinforces the psychological sense of "we're a unit"
- **Transparency**: a joint account naturally creates financial visibility; visibility reduces suspicion

Additionally, even when contributions are unequal, relationship satisfaction doesn't decline as long as the other person feels seen and appreciated (Feeling Appreciated study).

Based on this research, the system follows these principles:

1. **Low-friction design** — logging should be as effortless as possible; "managing money" shouldn't become a burden (Financial Harmony)
2. **Full data transparency** — both partners see exactly the same information; no "manager / managed" dynamic (Transparency)
3. **"We" framing to reinforce team identity** — monthly reports say "we spent ¥XX this month" rather than reporting each person's spending separately (Communal Strength)
4. **Discuss before large shared purchases** — small everyday expenses can be auto-logged; larger shared costs like courses should involve a quick check-in before buying (5C decision framework)
5. **Unequal contributions don't need system compensation** — the 35/65 split won't damage the relationship on its own; what matters is everyday appreciation and acknowledgment, which is outside the system's scope

### Design Principle C: Practical Analysis Framework (from personal finance books)

Sources: Ramit Sethi, *Money for Couples*; David Bach, *Smart Couples Finish Rich*; Vicki Robin, *Your Money or Your Life*

Based on these books, the monthly report covers the following dimensions:

1. **Structural analysis** — shows the ratio of fixed costs (rent, utilities) to discretionary spending (food, transport, allowance); assesses whether the spending structure is healthy (Ramit Sethi's CSP framework)
2. **Latte factor identification** — highlights the monthly cumulative total of high-frequency small purchases (takeout, coffee, rideshare), making invisible spending visible (David Bach)
3. **Spending satisfaction reflection** — the open-ended question at the end of the report prompts the thought "was this worth the hours I worked for it?" — not a system judgment, but a personal one (Vicki Robin)

---

## Spending Values Dialogue System

The system includes a structured values conversation flow to help both partners understand each other's relationship with money and reduce friction from differing spending philosophies.

Theoretical basis: Myra Strober's 5C framework (Clarify → Communicate → Choices → Check in → Consequences); Modigliani's Life-Cycle Hypothesis (a person's financial behavior across a lifetime reduces to five directions: consumption, saving, investment, borrowing, and transfers)

### 7 Macro Dimensions

Healthcare is separated from everyday spending because it's a non-negotiable need — unlike discretionary expenses, it can't be adjusted away. This follows Dave Ramsey and Elizabeth Warren, both of whom treat healthcare as a standalone necessity.

Reference framework: Elizabeth Warren's *All Your Worth* 50/30/20 rule — after-tax income split into three buckets, **savings bucket 20% deducted first**, then needs 50% and wants 30%. Sub-dimension percentages = bucket percentage × share within bucket.

Note: Housing is the single largest item in the needs bucket and often takes 25%+ of after-tax income in practice — it's calculated separately. The remaining needs are distributed within what's left (i.e. the 50% needs bucket minus housing). Healthcare is a hard need, protected first, with no fixed percentage; costs beyond the everyday range draw from the savings bucket. In high-cost cities where the needs bucket runs short, compress the wants bucket before cutting hard needs.

| Dimension | Sub-dimension | Core question | Bucket | Suggested share within bucket | As % of after-tax income |
|-----------|---------------|---------------|--------|-------------------------------|--------------------------|
| **Daily Spending** | Food & dining | How many meals a week do you cook at home, order in, or eat out? What's your typical spend per occasion? | Needs (50%) | ~16% | ~8% |
| | Groceries / household quality | When buying groceries or household items, do you go for the cheapest, mid-range, or quality option? | Needs (50%) | ~10% | ~5% |
| | **Housing** (calculated separately) | What percentage of monthly income feels reasonable for rent? Is there a ceiling? | Needs (50%) | Typically 25–35% of after-tax income, calculated separately | ~25–35% |
| | Clothing / appearance | How much do you spend on clothes, skincare, and haircuts in a year? | Wants (30%) | ~15% | ~4.5% |
| | Entertainment | How much do you spend on entertainment per month (movies, shows, games…)? | Wants (30%) | ~15% | ~4.5% |
| | Phone / digital subscriptions | What subscriptions do you currently have? What's the monthly total? Which feel worth it, and which could go? | Needs (50%) | ~6% | ~3% |
| | Irregular large expenses | What's your first reaction to an unexpected cost (repairs, replacing an appliance)? Do you keep a buffer? | Savings (20%) | ~15% | ~3% |
| **Transportation** | Daily commute | How many times a week do you take a rideshare for commuting or errands? Typical cost per trip? How do you decide between subway and rideshare? | Needs (50%) | ~16% | ~8% |
| | Long-distance / travel | How many long trips do you take per year? Are you willing to pay more for comfort (high-speed rail / flights / business class)? | Wants (30%) | ~20% | ~6% |
| | Car ownership | Do you plan to buy a car now or in the next 3 years? What monthly ownership cost could you accept? | Needs (50%) | Varies; compress other items | — |
| **Healthcare** | Routine medical / preventive | How long do you wait before seeing a doctor when you're sick? How much do you spend on medical care and medication per year? Do you have regular checkups or a fitness routine? | Needs (50%) | Hard need, protected first; excess draws from savings bucket | — |
| | Insurance | What insurance do you currently have? Approximate annual premiums? What do you feel is missing? | Needs (50%) | ~8% | ~4% |
| **Growth** | Courses / professional development | How many courses, books, or communities do you buy per year? How much did you spend on professional growth last year? What makes something worth buying? | Wants (30%) | ~25% | ~7.5% |
| | Experiences | How many trips per year? Typical budget per trip? Are you willing to pay more for the experience itself? | Wants (30%) | ~10% | ~3% |
| **Savings / Security** | Saving behavior | How much do you save each month? What are you saving for? How many months of living expenses do you need as a buffer to feel secure? | Savings (20%) | ~75% | ~15% |
| | Feelings about "not having money" | Below what account balance do you start to feel anxious? Where does that number come from? | — | — | — |
| **Risk / Investment** | Risk tolerance | What do you do with spare cash? Savings account, wealth management products, index funds, or stocks? Can you accept losing principal? | Savings (20%) | ~25% | ~5% |
| | Large purchases / debt | Above what amount do you think carefully before buying? Are you open to loans or installment plans? Under what circumstances? | — | — | — |
| **Giving / Relationships** | Partner | How much do you spend on your partner per year (gifts, dates…)? What feels like a reasonable ceiling? | Wants (30%) | ~15% | ~4.5% |
| | Family | How much do you give family each month? Is it a fixed amount or as-needed? Is there a ceiling? | Needs (50%) | Varies; compress other items | — |
| | Friends / social | How much do you spend per month on group dinners, gifts, and treating people? Does that feel right to you? | Wants (30%) | ~10% | ~3% |
| **Personal Boundaries** | Decision threshold | Below what amount can you spend without mentioning it to your partner? Above what amount should you decide together? | — | — | — |
| | Personal spending | Are there expenses you consider "your own business" that don't need explaining? | — | — | — |

**Bucket verification (housing calculated separately):**
- Needs bucket (50%) excluding housing: food 16% + groceries 10% + phone/subscriptions 6% + transport 16% + insurance 8% = **56%** ✅ (housing separately takes ~25–35% of after-tax income; combined total ~53–63%, which may exceed the 50% bucket in high-cost cities — compress the wants bucket to compensate)
- Wants bucket (30%): clothing 15% + entertainment 15% + travel transport 20% + courses 25% + experiences 10% + partner 15% + social 10% = **110%** — this is the full wish list, not a simultaneous target; prioritize accordingly. Suggested priority: professional development > travel > partner > entertainment > clothing > experiences > social
- Savings bucket (20%): emergency fund / savings 75% + investment 25% = **100%** ✅

### Three Levels of Financial Depth

Levels don't unlock automatically over time — both partners decide together "we're ready" before moving to the next. The deeper you go, the more it feels like a game you're unlocking together.

| Level | Unlock condition | Dimensions covered |
|-------|------------------|--------------------|
| **Shallow integration** | Start living together | Daily spending (food / groceries / housing / clothing / entertainment / subscriptions), daily transportation, personal boundaries |
| **Mid integration** | Stable cohabitation with shared planning intent | Add: healthcare, growth (courses / experiences), savings / security, giving / relationships |
| **Deep integration** | Long-term commitment, joint asset planning | Add: risk / investment, car ownership, irregular large expenses; plus deep-integration-only topics: home purchase, wedding, children, retirement (these go beyond the 7 dimensions and are expanded separately once unlocked) |

### Conversation Format

- **Input**: each partner answers open-ended questions in natural language — no format required, as much or as little as they want
- **AI processing**: semantic analysis maps each dimension's attitude to one of the four KMSI-R money scripts (Money Avoidance / Money Worship / Money Status / Money Vigilance); each person may show different scripts across different dimensions
- **Output**: a structured comparison report (styled like a health checkup)

### Comparison Report Structure

```
Spending Values Comparison Report · Shallow Integration (Round 1)
Generated: YYYY-MM-DD

✅ Aligned areas (no discussion needed)
  - Food & dining: both W and J prefer cooking at home, with occasional takeout

💬 Divergent areas (worth a conversation)
  - Household goods quality
    ├ W: functional is fine; brand doesn't matter
    └ J: willing to pay more for quality; comfort matters
    → Possible directions:
      a) Buy quality for shared items; each person chooses their own personal items
      b) Set a shared household budget ceiling; free choice within it

📌 Note
  Divergence doesn't mean conflict — it just means different.
  After reading this, talk about:
  "Of these differences, is there one where you feel we need to reach an agreement?"

🔄 Suggested next review: in 6 months
```

- Divergent areas are framed as "worth a conversation," not "conflicts"; possible negotiation directions are offered (Choices)
- Both partners review the report together (Check in), then consider long-term implications (Consequences)
- Default reminder to revisit every 6 months; triggered proactively when income changes or the relationship stage shifts

---

## Money Attachment Style Skill

Helps both partners understand their individual money psychology patterns; the system uses the results to adjust its notification behavior.

### Measurement Tools (from original academic sources, not custom-built)

#### ECR-R (Experiences in Close Relationships – Revised)
Fraley, Waller & Brennan (2000). 36 items, 7-point Likert scale. Measures two dimensions:

- **Anxiety dimension** (items 1–18): fear of abandonment, need for repeated reassurance. Example item: "I'm afraid that I will lose my partner's love." (Reverse-scored: 9, 11)
- **Avoidance dimension** (items 19–36): discomfort with closeness or depending on others. Example item: "I prefer not to show a partner how I feel deep down." (Reverse-scored: 20, 22, 26–31, 33–36)

Scoring: average score per dimension (1–7); higher scores indicate stronger expression of that dimension. **Output is two continuous dimension scores, not a type label** — attachment style is a continuous distribution, not a discrete category.

Four quadrants (for reference only; no labels applied): low anxiety + low avoidance = secure; high anxiety + low avoidance = anxious / preoccupied; low anxiety + high avoidance = avoidant / dismissing; high anxiety + high avoidance = fearful.

#### SAAM (State Adult Attachment Measure)
Gillath et al. (2009). 21 items, 7-point Likert scale. Measures **current state** rather than stable trait — it asks "how are you feeling right now?" Example item: "I feel secure and close to other people."

#### KMSI-R (Klontz Money Script Inventory – Revised)
Brad Klontz & Sonya Britt (2013). 32 items, 6-point Likert scale (1 = strongly disagree, 6 = strongly agree). Measures four money belief patterns:

| Money Script | Items | Core belief | Behavioral expression | Score interpretation |
|---|---|---|---|---|
| Money Avoidance | 1–9 | "Money is bad / I don't deserve money" | Ignoring bills, avoiding financial topics | 9–18: no concern; 37–54: high risk |
| Money Worship | 10–16 | "Money solves everything / more is always better" | Overworking, buying things to relieve anxiety | 7–14: no concern; 39–49: high risk |
| Money Status | 17–24 | "Money = success = self-worth" | Using spending to prove status, caring about others' perceptions | 8–16: no concern; 33–48: high risk |
| Money Vigilance | 25–32 | "Be careful, save, don't waste" | Frugal, guilt around spending, reluctant to discuss income | 8–16: no concern; high scores not necessarily problematic |

Example items:
- Money Avoidance: "Rich people are greedy." (item 2)
- Money Worship: "More money will make you happier." (item 11)
- Money Status: "Your self-worth equals your net worth." (item 22)
- Money Vigilance: "It is important to save for a rainy day." (item 28)

**How the three scales are used:**

| Scale | What it measures | When used |
|-------|-----------------|-----------|
| ECR-R | Stable trait (typical attachment style) | Once at setup; determines attachment style; outputs anxiety and avoidance dimension scores |
| KMSI-R | Money belief patterns | Once at setup; determines money script type |
| SAAM | Current state (how you feel right now) | Optional after monthly report; tracks the immediate effect of financial information on felt security |

### Process

1. **Initialization**: both partners complete ECR-R (36 items) + KMSI-R independently; AI calculates scores and outputs an initial profile
2. **Behavioral calibration**: after one month of use, conversation sequence data is used to cross-validate the questionnaire results. Valid signals are **behavioral patterns across messages**, not individual word choices — for example: does the person drop the topic after receiving a balance confirmation (secure), or keep asking (anxious)? How do they respond to overage alerts — calmly, anxiously, or not at all? Behavioral signals don't directly determine type; they only contribute descriptive material to the report.
3. **Report output**: each partner's profile (ECR-R two-dimension scores + KMSI-R money scripts) + combined pattern analysis + system mode recommendation
4. **Joint decision**: both partners see the full report; they discuss and choose a system mode together

### Three System Modes

| Feature | A. Standard | B. Reassurance | C. Silent |
|---------|-------------|----------------|-----------|
| Best for | Secure + secure | Includes anxious attachment | Includes avoidant attachment |
| Expense confirmation | Brief confirmation | Confirmation + current balance | Records only; no reply |
| Mid-month check-in | None | 15th: "¥XX left in the pool — on track" | None |
| Overage alert | Alert when overage is projected | Alert at 70% of pool | Reflected in monthly report only |
| Monthly report style | Data + trends + open question | Same as Standard + "this month's pace is healthy" qualitative note | Numbers only; no commentary |

- Mode is chosen jointly and can be changed at any time
- Reassessment recommended after 6 months — people change

---

## Research Backing

| # | Book / Study | Author | Key contribution |
|---|---|---|---|
| 1 | *Money for Couples* | Ramit Sethi | CSP four-bucket framework (fixed costs / investments / savings / guilt-free spending); income-proportional splitting; 4 key numbers |
| 2 | *Smart Couples Finish Rich* | David Bach | Latte factor — the compounding effect of small recurring expenses; automated saving; couples setting financial goals together |
| 3 | *Money and Love* | Myra Strober & Abby Davisson (Stanford) | 5C decision framework (Clarify / Communicate / Choices / Check in / Consequences); every financial decision is a relationship decision |
| 4 | *The Healthy Love and Money Way* | Ed Coambs | Attachment theory × money behavior; four types: secure / anxious / avoidant / fearful; understanding each other's money personality |
| 5 | Pooling Finances and Relationship Satisfaction (2022) | University of Colorado, N=38,534 | Couples who pool finances report significantly higher relationship satisfaction; three mechanisms: Financial Harmony / Communal Strength / Transparency |
| 6 | Common Cents: Bank Account Structure and Couples' Relationship Dynamics (2023) | Eli Finkel, Northwestern | First causal study: newlyweds with joint accounts showed no decline in relationship quality over the first two years; those with separate accounts showed the normal decay |
| 7 | Feeling Appreciated (2022) | Academic study | Even with unequal contributions, relationship satisfaction doesn't decline as long as the other person feels seen and appreciated |
| 8 | *The Seven Principles for Making Marriage Work* | John Gottman | Emotional bank account; turning toward vs. turning away; shared meaning system — the "Drucker" of relationship research |
| 9 | *Your Money or Your Life* | Vicki Robin | Money = life energy; for every purchase, ask "was this worth the hours I worked for it?" |
| 10 | *Hold Me Tight* | Sue Johnson | Arguments about money are fundamentally asking "do you still care about me?" — the classic attachment theory text |
| 11 | ECR-R (Experiences in Close Relationships – Revised) | Fraley, Waller & Brennan (2000) | 36 items; measures anxiety and avoidance as two continuous dimensions, not type labels; original items verified against Fraley's lab website |
| 12 | SAAM (State Adult Attachment Measure) | Gillath et al. (2009) | 21 items; measures current state rather than stable trait; optional after monthly report to track the immediate effect of financial information on felt security; original items verified |
| 13 | KMSI-R (Klontz Money Script Inventory – Revised) | Brad Klontz & Sonya Britt (2013) | 32 items, 6-point scale; measures four money belief patterns (avoidance / worship / status / vigilance); original items verified via Scribd |
| 14 | Life-Cycle Hypothesis | Franco Modigliani | Macro-level framework for a person's financial behavior across a lifetime: consumption / saving / investment / borrowing / transfers |
| 15 | *All Your Worth* | Elizabeth Warren & Amelia Warren Tyagi | 50/30/20 rule: 20% savings deducted first, 50% needs, 30% wants; the three-bucket framework is the proportional basis for the spending values dialogue system |

---

## Technical Configuration

### System Architecture

```
Feishu group message
        ↓
cc-connect (persistent WebSocket, auto-starts on login)
        ↓
Claude Code (CLAUDE.md routing rules)
        ↓
scripts/ledger_handler.py (financial message processing)
        ↓
Claude API (semantic parsing: expense / query / shopping intent)
        ↓
data/ledger.csv (ledger storage)
        ↓
Scheduled tasks (monthly report on the 10th / Mode B mid-month push on the 15th)
```

### File Structure

```
shared-expense-tracker/
├── CLAUDE.md                  # Project instructions (for Claude Code)
├── config.json                # Config: usernames, open_id, split ratio, pool amount
├── categories.json            # Category definitions
├── pyproject.toml             # Dependency management via uv
├── scripts/
│   ├── bot.py                 # Feishu WebSocket bot (fallback; currently driven by cc-connect)
│   ├── ledger_handler.py      # Financial message processing entry point (called by cc-connect)
│   ├── parser.py              # Claude API semantic parsing
│   ├── ledger.py              # Ledger read/write
│   ├── report.py              # Monthly report generation
│   ├── reminders.py           # Apple Reminders integration (AppleScript)
│   ├── form_server.py         # Questionnaire HTTP server (ECR-R + KMSI-R)
│   ├── system_mode.py         # System mode persistence (A Standard / B Reassurance / C Silent)
│   └── keychain.py            # macOS Keychain secret management
├── templates/
│   ├── index.html             # Questionnaire landing page (User 1 / User 2 selection)
│   ├── questionnaire.html     # Questionnaire page
│   └── submitted.html         # Submission confirmation page
├── data/
│   ├── ledger.csv             # Ledger (gitignored; not pushed to GitHub)
│   ├── messages.jsonl         # Structured message log (gitignored)
│   ├── learnings.jsonl        # Cross-session memory (AI development log)
│   └── system_mode.json       # Current system mode
├── .env.example               # Environment variable template
└── 设计总结.md
```

### Dependencies and Accounts

| Tool | Purpose | Cost |
|------|---------|------|
| Feishu Open Platform | Create bot; obtain App ID + App Secret | Free |
| cc-connect | Feishu persistent connection driver; auto-starts via launchd | Free |
| Claude API (Anthropic) | Semantic parsing for expenses, shopping intent, monthly reports | Pay-per-use; ~a few yuan/month for typical usage |
| Python 3.12 + uv | Run all scripts; dependency management | Free |
| macOS Keychain | Store API keys without writing them to files | Free |

### Shopping Intent Sync

When the bot detects a shopping intent, it writes to the configured Apple Reminders list via AppleScript, with a 🛒 prefix on the title (e.g. "🛒 Cat food").

**Why write to a dedicated list instead of creating a new shopping list:** The configured list is already the unified catch-all for "things not yet done" — shopping needs fit that definition exactly. The 🛒 prefix makes shopping tasks visually distinct from other tasks at a glance, without requiring a separate list to check. Shopping tasks can also be directly scheduled into today's flexible time by Boss Plan.

**One-time manual setup:**
- The Inbox list has been shared with both participants (W + J) via iCloud
- Both have notifications enabled for "item added" and "item completed"
- Once shared, any shopping task the bot writes will trigger a notification on both phones

**Known AppleScript limitations:**
- Cannot initiate list sharing invitations via script — must be done manually (already done)
- Cannot set repeat properties on reminders — must be set manually if needed
- Date objects must be constructed independently each time; references cannot be reused

### Data Storage Strategy

Feishu group messages are **stored in structured form**, not as raw full-text logs. Reason: full-text storage is noisy (casual chat, emoji, filler words) and interferes with behavioral signal analysis; structured storage is more query-efficient and more private.

**What's stored:** all messages the bot identifies as having financial intent, structured as follows:

```json
{
  "timestamp": "2026-05-11T14:32:00",
  "sender": "W",
  "raw": "bought cat food 80",
  "intent": "expense",
  "amount": 80,
  "category": "Pets",
  "dialogue_context": {
    "preceding_event": null,
    "follow_up": null,
    "follow_up_pattern": null
  }
}
```

**The `raw` field preserves the original message** because the values dialogue system needs original language for semantic analysis, and behavioral pattern analysis needs the original text for reprocessing.

**`dialogue_context` field notes:**
- `preceding_event`: context that triggered this message (e.g. "a large expense was just logged")
- `follow_up`: the user's next message after the bot replied
- `follow_up_pattern`: the follow-up behavior pattern (`dropped` = let it go after confirmation / `continued` = kept asking / `no_response` = no reply)

**Important:** dialogue_context records **conversation sequences**, not single-message sentiment. Individual word choices ("is that enough?", "spending again") can't determine attachment type — the same phrase means different things from different people. Only cross-message behavioral patterns (does the person drop it after getting confirmation?) have reference value, and even then only as supplementary material for validating questionnaire results, not as direct type judgments.

**What's not stored:** messages the bot classifies as having no financial intent (casual chat) are not written to storage.

### Implementation Status

| Phase | Feature | Description | Status |
|-------|---------|-------------|--------|
| Phase 1 | Core expense logging | Feishu message → Claude parsing → CSV write → confirmation reply | ✅ Done |
| Phase 2 | Queries and monthly report | On-demand balance / category queries + auto monthly report on the 10th | ✅ Done |
| Phase 3 | Shopping intent detection | Detect shopping needs → write to configured Apple Reminders list | ✅ Done |
| Phase 4 | Spending values dialogue system | ECR-R (36 items) + KMSI-R (32 items) questionnaire + comparison report pushed to Feishu | ✅ Done (pending completion) |
| Phase 5 | Money attachment style | Reply "选A/B/C" in group to switch system mode; bot behavior changes accordingly | ✅ Done (pending questionnaire results) |

- ledger.csv is local only; gitignored and not pushed to GitHub
- GitHub holds only config and code (CLAUDE.md, scripts, categories.json)
