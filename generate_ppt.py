from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import copy

# ─── Colour palette ────────────────────────────────────────────────────────────
BG_DARK      = RGBColor(0x0D, 0x0F, 0x1A)   # near-black navy
ACCENT_PURPLE= RGBColor(0x86, 0x3B, 0xFF)   # brand purple
ACCENT_BLUE  = RGBColor(0x47, 0xBF, 0xFF)   # brand cyan
WHITE        = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY   = RGBColor(0xCC, 0xCC, 0xDD)
YELLOW       = RGBColor(0xFF, 0xD7, 0x00)
GREEN        = RGBColor(0x3D, 0xD6, 0x8C)
RED          = RGBColor(0xFF, 0x5C, 0x5C)
CARD_BG      = RGBColor(0x1A, 0x1D, 0x2E)

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)

prs = Presentation()
prs.slide_width  = SLIDE_W
prs.slide_height = SLIDE_H

blank_layout = prs.slide_layouts[6]   # completely blank


# ═══════════════════════════════════════════════════════════════════════════════
# Helper utilities
# ═══════════════════════════════════════════════════════════════════════════════

def set_bg(slide, color: RGBColor):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_rect(slide, l, t, w, h, color: RGBColor, alpha=None):
    shape = slide.shapes.add_shape(1, Inches(l), Inches(t), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape


def add_text(slide, text, l, t, w, h,
             font_size=18, bold=False, color=WHITE,
             align=PP_ALIGN.LEFT, italic=False, wrap=True):
    txBox = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = txBox.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return txBox


def add_multiline(slide, lines, l, t, w, h,
                  font_size=15, color=WHITE, bold_first=False, spacing=Pt(6)):
    txBox = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = txBox.text_frame
    tf.word_wrap = True
    first = True
    for line in lines:
        if first:
            p = tf.paragraphs[0]
            first = False
        else:
            p = tf.add_paragraph()
        p.space_before = spacing
        run = p.add_run()
        run.text = line
        run.font.size = Pt(font_size)
        run.font.color.rgb = color
        if bold_first and line == lines[0]:
            run.font.bold = True


def accent_bar(slide, color=ACCENT_PURPLE, t=0.82, h=0.07):
    add_rect(slide, 0, t, 13.33, h, color)


def slide_header(slide, title, subtitle=None, title_color=WHITE, sub_color=LIGHT_GRAY):
    accent_bar(slide, ACCENT_PURPLE, t=0.72, h=0.06)
    add_text(slide, title, 0.5, 0.15, 12.0, 0.7,
             font_size=36, bold=True, color=title_color, align=PP_ALIGN.LEFT)
    if subtitle:
        add_text(slide, subtitle, 0.5, 0.82, 12.0, 0.45,
                 font_size=16, color=sub_color, align=PP_ALIGN.LEFT)


def card(slide, l, t, w, h, bg=CARD_BG):
    return add_rect(slide, l, t, w, h, bg)


def bullet_block(slide, title, bullets, l, t, w, h,
                 title_color=ACCENT_BLUE, bullet_color=LIGHT_GRAY,
                 title_size=17, bullet_size=14):
    card(slide, l, t, w, h)
    add_text(slide, title, l+0.15, t+0.12, w-0.3, 0.35,
             font_size=title_size, bold=True, color=title_color)
    add_multiline(slide, bullets, l+0.15, t+0.5, w-0.3, h-0.6,
                  font_size=bullet_size, color=bullet_color, spacing=Pt(4))


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — Title
# ═══════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(blank_layout)
set_bg(sl, BG_DARK)

# big gradient band
add_rect(sl, 0, 2.2, 13.33, 3.5, CARD_BG)
add_rect(sl, 0, 2.2, 0.18, 3.5, ACCENT_PURPLE)

add_text(sl, "MarketMind", 0.6, 2.4, 12, 1.1,
         font_size=58, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
add_text(sl, "AI-Powered Stock Analysis Platform", 0.6, 3.55, 12, 0.7,
         font_size=26, color=ACCENT_BLUE, align=PP_ALIGN.LEFT)
add_text(sl, "XGBoost  ·  SHAP  ·  FinBERT  ·  Rule-Based Fundamentals",
         0.6, 4.25, 12, 0.5, font_size=17, color=LIGHT_GRAY, align=PP_ALIGN.LEFT)

add_rect(sl, 0.6, 5.2, 4.5, 0.07, ACCENT_PURPLE)
add_text(sl, "Technical Deep-Dive  |  Architecture  |  Market Comparison",
         0.6, 5.35, 12, 0.4, font_size=14, color=LIGHT_GRAY, italic=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — Agenda
# ═══════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(blank_layout)
set_bg(sl, BG_DARK)
slide_header(sl, "What We'll Cover", "A complete walkthrough of MarketMind's internals")

topics = [
    ("01", "SHAP & Its Role",           "What SHAP does and where it runs"),
    ("02", "Confidence Score",           "How confidence is calculated and its accuracy"),
    ("03", "XGBoost Internals",          "How the ML model was trained and how it predicts"),
    ("04", "FinBERT Internals",          "How financial NLP sentiment scoring works"),
    ("05", "Rule-Based System",          "Fundamentals scorer — rules, data, normalization"),
    ("06", "How All Three Collaborate",  "End-to-end pipeline from ticker to verdict"),
    ("07", "Black Box vs SHAP",          "Why XGBoost is opaque and how SHAP opens it"),
    ("08", "Market Comparison",          "Differences and advantages over commercial tools"),
]

cols = [(0.35, 1.5), (6.85, 1.5), (0.35, 3.5), (6.85, 3.5),
        (0.35, 5.5), (6.85, 5.5), (0.35, 6.8), (6.85, 6.8)]

for i, (num, title, desc) in enumerate(topics):
    lx, ty = cols[i % 8]
    if i > 5:
        ty = [6.55, 6.55][i-6]
    card(sl, lx, ty, 6.1, 0.85)
    add_text(sl, num, lx+0.15, ty+0.08, 0.55, 0.4,
             font_size=20, bold=True, color=ACCENT_PURPLE)
    add_text(sl, title, lx+0.7, ty+0.08, 4.5, 0.35,
             font_size=15, bold=True, color=WHITE)
    add_text(sl, desc, lx+0.7, ty+0.42, 5.2, 0.35,
             font_size=12, color=LIGHT_GRAY)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — What is SHAP
# ═══════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(blank_layout)
set_bg(sl, BG_DARK)
slide_header(sl, "SHAP — SHapley Additive exPlanations",
             "Turning XGBoost's black-box output into human-readable reasons")

add_text(sl, "Where it runs in the code:", 0.5, 1.35, 9, 0.35,
         font_size=14, bold=True, color=ACCENT_BLUE)

# code block
add_rect(sl, 0.5, 1.72, 12.3, 1.45, RGBColor(0x10, 0x14, 0x24))
code = (
    "_explainer = shap.TreeExplainer(_model)         # once at server startup\n"
    "shap_values = _explainer.shap_values(latest)    # per /analyze call\n"
    "contributions = list(zip(FEATURES, shap_values[0]))\n"
    'reasons.append(f"{FEATURE_LABELS[feature]} {direction} (SHAP value: {value:.3f})")'
)
add_text(sl, code, 0.65, 1.78, 12.0, 1.35,
         font_size=11, color=GREEN, align=PP_ALIGN.LEFT)

# 3 role cards
roles = [
    ("📥  Input", "Same 6 technical indicator values that XGBoost just used"),
    ("⚙️  Process", "Shapley values — game-theory attribution per feature"),
    ("📤  Output", "Top 3 human-readable reason strings — not a score"),
]
for i, (t, d) in enumerate(roles):
    x = 0.5 + i * 4.3
    card(sl, x, 3.4, 4.0, 1.25)
    add_text(sl, t, x+0.2, 3.5, 3.6, 0.4, font_size=15, bold=True, color=ACCENT_PURPLE)
    add_text(sl, d, x+0.2, 3.92, 3.6, 0.6, font_size=13, color=LIGHT_GRAY)

add_text(sl, "Key fact: SHAP adds ZERO to the score — it only explains the prediction already made by XGBoost",
         0.5, 4.85, 12.3, 0.45, font_size=14, bold=True, color=YELLOW, align=PP_ALIGN.CENTER)

# flow
add_text(sl, "XGBoost → proba_up=0.68   →   SHAP → 'RSI pushed prediction UP (0.142)'   →   UI: Why this verdict? panel",
         0.5, 5.45, 12.3, 0.45, font_size=13, color=LIGHT_GRAY, align=PP_ALIGN.CENTER)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — Confidence Score
# ═══════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(blank_layout)
set_bg(sl, BG_DARK)
slide_header(sl, "Confidence Score — How It's Calculated",
             "A heuristic conviction meter, not a statistically calibrated probability")

add_text(sl, "The Formula  (combiner.py  L21)", 0.5, 1.32, 9, 0.35,
         font_size=14, bold=True, color=ACCENT_BLUE)
add_rect(sl, 0.5, 1.68, 12.3, 0.65, RGBColor(0x10, 0x14, 0x24))
add_text(sl, "confidence = round(min(abs(final_score) × 2,  1.0),  2)",
         0.65, 1.74, 12.0, 0.55, font_size=15, bold=True, color=GREEN)

# truth table
headers = ["final_score", "Calculation", "confidence", "Verdict"]
rows = [
    ["0.00  (dead neutral)", "min(0.0 × 2, 1.0)", "0%",    "Hold"],
    ["0.25  (just Buy)",     "min(0.25 × 2, 1.0)", "50%",  "Buy"],
    ["0.50",                 "min(0.5 × 2, 1.0)",  "100%", "Buy"],
    ["0.80",                 "min(0.8 × 2, 1.0) → capped", "100%", "Buy"],
    ["-0.30  (Avoid)",       "min(0.3 × 2, 1.0)",  "60%",  "Avoid"],
]
col_w = [2.9, 3.1, 1.6, 1.8]
col_x = [0.5, 3.42, 6.54, 8.16]
add_rect(sl, 0.5, 2.52, 9.65, 0.38, ACCENT_PURPLE)
for ci, h in enumerate(headers):
    add_text(sl, h, col_x[ci]+0.1, 2.56, col_w[ci], 0.32,
             font_size=13, bold=True, color=WHITE)
for ri, row in enumerate(rows):
    bg = CARD_BG if ri % 2 == 0 else RGBColor(0x14, 0x17, 0x28)
    add_rect(sl, 0.5, 2.92+ri*0.42, 9.65, 0.42, bg)
    for ci, cell in enumerate(row):
        clr = GREEN if cell in ["Buy"] else (RED if cell == "Avoid" else LIGHT_GRAY)
        add_text(sl, cell, col_x[ci]+0.1, 2.94+ri*0.42, col_w[ci], 0.38,
                 font_size=12, color=clr)

# weaknesses
add_text(sl, "⚠️  Weaknesses", 10.3, 2.52, 2.8, 0.35, font_size=14, bold=True, color=YELLOW)
weak = [
    "Heuristic — not a real probability",
    "×2 multiplier & 0.5 cap are arbitrary",
    "No cross-pillar disagreement check",
    "Fundamentals: only 2 signals (30% weight)",
    "FinBERT confidence score discarded",
    "No historical backtesting of confidence",
]
card(sl, 10.3, 2.9, 2.85, 4.3)
add_multiline(sl, weak, 10.45, 3.0, 2.65, 4.1,
              font_size=12, color=LIGHT_GRAY, spacing=Pt(5))


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — XGBoost Internals
# ═══════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(blank_layout)
set_bg(sl, BG_DARK)
slide_header(sl, "XGBoost — The Technical Prediction Engine",
             "Trained offline · Loaded once at startup · Runs on every /analyze call")

# Left — training
card(sl, 0.4, 1.32, 6.1, 5.9)
add_text(sl, "🏋  Training Phase  (offline, one-time)",
         0.6, 1.42, 5.7, 0.38, font_size=15, bold=True, color=ACCENT_PURPLE)
train_pts = [
    "9 stocks: AAPL MSFT GOOGL AMZN TSLA META NVDA V WMT",
    "10 years of daily OHLC price history per stock",
    "6 features: RSI · MACD · BB% · Stoch · ATR% · ROC-10",
    "Label: did price go UP after 5 days?  (1 = yes, 0 = no)",
    "200 sequential trees — each corrects the last (boosting)",
    "max_depth=4 · learning_rate=0.05 · subsample=0.8",
    "Saved as 336 KB  technical_model.joblib",
]
add_multiline(sl, train_pts, 0.6, 1.85, 5.7, 5.2,
              font_size=13, color=LIGHT_GRAY, spacing=Pt(7))

# Right — inference
card(sl, 6.85, 1.32, 6.1, 5.9)
add_text(sl, "⚡  Inference Phase  (every request)",
         7.05, 1.42, 5.7, 0.38, font_size=15, bold=True, color=ACCENT_BLUE)
inf_pts = [
    "Load 6mo price history → compute today's 6 indicators",
    "Pass one row through 200 trees",
    "predict_proba → [prob_down, prob_up]",
    "e.g.  [0.32,  0.68]  →  68 % chance price goes UP",
    "normalized = (proba_up − 0.5) × 2  →  −1 … +1",
    "Feeds 40 % weight into combine_scores()",
    "Then SHAP runs on the same input to explain WHY",
]
add_multiline(sl, inf_pts, 7.05, 1.85, 5.7, 5.2,
              font_size=13, color=LIGHT_GRAY, spacing=Pt(7))


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — FinBERT Internals
# ═══════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(blank_layout)
set_bg(sl, BG_DARK)
slide_header(sl, "FinBERT — Financial Sentiment Engine",
             "BERT fine-tuned on Reuters · WSJ · earnings call transcripts")

steps = [
    ("1️⃣  Fetch Headlines", "NewsAPI query\n20 headlines · last 7 days · cached 6 hrs\n'\"Apple\" AND (stock OR earnings OR revenue)'"),
    ("2️⃣  Tokenise", "Each headline split into sub-word tokens\n[CLS] 'Apple' 'beat' '##s' 'earn' '##ings' [SEP]\nSpecial [CLS] token carries sentence meaning"),
    ("3️⃣  12 Attention Layers", "Each token attends to every other token\n'beats' strongly attends to 'earnings'\nFull bidirectional context understanding"),
    ("4️⃣  Classify", "3-way softmax: positive / negative / neutral\nOutput: {'label':'positive', 'score':0.97}\nFinance-specific — not generic sentiment"),
    ("5️⃣  Aggregate", "positive=14  negative=4  neutral=2\nnormalized = (14−4) / 20 = +0.50\n30 % weight in combine_scores()"),
    ("⚠️  Weakness", "Confidence score (0.97 vs 0.53)\nper headline is DISCARDED — only\nthe label is counted (all-or-nothing)"),
]
positions = [(0.35,1.32),(4.6,1.32),(8.85,1.32),(0.35,3.9),(4.6,3.9),(8.85,3.9)]
for i, (t, d) in enumerate(steps):
    lx, ty = positions[i]
    bg = RGBColor(0x1F, 0x10, 0x38) if i == 5 else CARD_BG
    card(sl, lx, ty, 3.9, 2.3, bg)
    tc = YELLOW if i == 5 else ACCENT_PURPLE
    add_text(sl, t, lx+0.2, ty+0.12, 3.5, 0.38, font_size=14, bold=True, color=tc)
    add_text(sl, d, lx+0.2, ty+0.55, 3.55, 1.65, font_size=12, color=LIGHT_GRAY)

add_text(sl, "FinBERT vs Generic Sentiment:  'Shares fall short' → Generic: neutral  |  FinBERT: NEGATIVE  ✓",
         0.35, 6.52, 12.5, 0.4, font_size=13, bold=True, color=GREEN, align=PP_ALIGN.CENTER)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — Rule-Based Fundamentals
# ═══════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(blank_layout)
set_bg(sl, BG_DARK)
slide_header(sl, "Rule-Based Fundamentals Scorer",
             "Handwritten if/else expert rules — no training, 100% transparent")

# data sources
add_text(sl, "Data Sources  (fundamentals_data.py)", 0.5, 1.32, 9, 0.32,
         font_size=14, bold=True, color=ACCENT_BLUE)
card(sl, 0.5, 1.66, 12.3, 0.72)
add_text(sl,
    "Primary: Alpha Vantage API  →  Fallback: yfinance (Yahoo Finance)  →  Fallback: all None values  |  Cached 24 hours",
    0.7, 1.76, 11.9, 0.52, font_size=13, color=LIGHT_GRAY, align=PP_ALIGN.CENTER)

# Rule cards
add_text(sl, "The Two Active Scoring Rules:", 0.5, 2.55, 9, 0.32,
         font_size=14, bold=True, color=ACCENT_BLUE)
rules = [
    ("Rule 1 — P/E vs Sector Average",
     ["if pe_ratio < sector_avg_pe:   score += 1  ✅",
      "else:                          score −= 1  ❌",
      "",
      "TECHNOLOGY → avg PE = 30",
      "HEALTHCARE → avg PE = 25",
      "FINANCIAL  → avg PE = 15",
      "ENERGY     → avg PE = 12",
      "DEFAULT    → avg PE = 20"]),
    ("Rule 2 — Debt-to-Equity",
     ["if debt_to_equity < 100:   score += 1  ✅",
      "else:                      score −= 1  ❌",
      "",
      "D/E = 32.1  →  manageable  (+1)",
      "D/E = 145.0 →  high risk   (−1)",
      "D/E = None  →  max_score −= 1",
      "  (missing data, no penalty)"]),
    ("Normalization",
     ["normalized = score / max_score",
      "",
      "Both rules pass → +2/2 = +1.0  🟢",
      "Both fail       → −2/2 = −1.0  🔴",
      "One each        → 0/2  =  0.0  🟡",
      "D/E missing     → ±1/1 = ±1.0",
      "→ feeds 30 % of final score"]),
]
for i, (t, pts) in enumerate(rules):
    x = 0.5 + i * 4.3
    card(sl, x, 2.92, 4.0, 3.65)
    add_text(sl, t, x+0.2, 3.02, 3.7, 0.42, font_size=13, bold=True, color=ACCENT_PURPLE)
    add_multiline(sl, pts, x+0.2, 3.5, 3.65, 3.0, font_size=12, color=LIGHT_GRAY, spacing=Pt(4))

add_text(sl, "⚠️  10 fields fetched (EPS, PEG, Margins, Dividend…) but ONLY pe_ratio and debt_to_equity are used in scoring",
         0.5, 6.72, 12.3, 0.45, font_size=13, bold=True, color=YELLOW, align=PP_ALIGN.CENTER)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — How All Three Work Hand in Hand
# ═══════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(blank_layout)
set_bg(sl, BG_DARK)
slide_header(sl, "How All Three Work Hand in Hand",
             "Three independent pipelines — one integration point: combine_scores()")

# pipeline steps
steps = [
    ("📈 Price Data\n(2yr OHLC)", ACCENT_PURPLE, 0.4, 1.38),
    ("6 Indicators\ncomputed", CARD_BG, 2.35, 1.38),
    ("XGBoost\n200 trees", ACCENT_PURPLE, 4.3, 1.38),
    ("proba_up\nnormalized", CARD_BG, 6.25, 1.38),
    ("SHAP\nTreeExplainer", ACCENT_BLUE, 8.2, 1.38),
    ("3 Reason\nStrings", CARD_BG, 10.15, 1.38),
]
for t, bg, x, y in steps:
    add_rect(sl, x, y, 1.75, 0.9, bg)
    add_text(sl, t, x+0.08, y+0.08, 1.62, 0.78,
             font_size=11, bold=(bg != CARD_BG), color=WHITE, align=PP_ALIGN.CENTER)
    if x < 10.15:
        add_text(sl, "→", x+1.77, y+0.28, 0.4, 0.38, font_size=16, color=ACCENT_PURPLE)

# news row
news_steps = [
    ("📰 News Headlines\n(20, last 7 days)", ACCENT_BLUE, 0.4, 2.52),
    ("FinBERT\n12 attn layers", ACCENT_BLUE, 2.35, 2.52),
    ("pos / neg /\nneutral labels", CARD_BG, 4.3, 2.52),
    ("normalized\nsentiment", CARD_BG, 6.25, 2.52),
]
for t, bg, x, y in news_steps:
    add_rect(sl, x, y, 1.75, 0.9, bg)
    add_text(sl, t, x+0.08, y+0.08, 1.62, 0.78,
             font_size=11, bold=(bg != CARD_BG), color=WHITE, align=PP_ALIGN.CENTER)
    if x < 6.25:
        add_text(sl, "→", x+1.77, y+0.28, 0.4, 0.38, font_size=16, color=ACCENT_BLUE)

# fundamentals row
add_rect(sl, 0.4, 3.65, 1.75, 0.9, RGBColor(0x20, 0x60, 0x40))
add_text(sl, "📋 Fundamentals\n(PE, D/E)", 0.48, 3.73, 1.62, 0.78,
         font_size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
add_text(sl, "→", 2.18, 3.93, 0.4, 0.38, font_size=16, color=GREEN)
add_rect(sl, 2.35, 3.65, 1.75, 0.9, CARD_BG)
add_text(sl, "2 Rules\nnormalized", 2.43, 3.73, 1.62, 0.78,
         font_size=11, color=WHITE, align=PP_ALIGN.CENTER)
add_text(sl, "→", 4.13, 3.93, 0.4, 0.38, font_size=16, color=GREEN)
add_rect(sl, 4.3, 3.65, 1.75, 0.9, CARD_BG)
add_text(sl, "fund_norm\n(30% weight)", 4.38, 3.73, 1.62, 0.78,
         font_size=11, color=WHITE, align=PP_ALIGN.CENTER)

# combine arrow
add_rect(sl, 8.2, 2.4, 1.75, 2.25, RGBColor(0x25, 0x10, 0x45))
add_text(sl, "combine_scores()\n0.4×tech\n+0.3×fund\n+0.3×sent",
         8.28, 2.5, 1.62, 2.1, font_size=12, bold=True, color=ACCENT_PURPLE, align=PP_ALIGN.CENTER)
add_text(sl, "→", 10.0, 3.38, 0.4, 0.38, font_size=16, color=ACCENT_PURPLE)

# final verdict
add_rect(sl, 10.4, 2.4, 2.5, 2.25, ACCENT_PURPLE)
add_text(sl, "VERDICT\n🟢 Buy\n82 % conf.\nLow risk",
         10.5, 2.5, 2.3, 2.1, font_size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

# explanation merge arrow
add_text(sl, "Reasons from all 3 merge into unified explanation list → 'Why this verdict?' panel in UI",
         0.4, 4.75, 12.4, 0.4, font_size=13, color=LIGHT_GRAY, align=PP_ALIGN.CENTER)

# key rule
add_rect(sl, 0.4, 5.25, 12.4, 0.65, CARD_BG)
add_text(sl,
    "Key Rule:  XGBoost & SHAP always run together.  FinBERT never sees price data.  "
    "XGBoost never sees headlines.  They ONLY meet inside combine_scores().",
    0.6, 5.32, 12.1, 0.52, font_size=13, bold=True, color=YELLOW, align=PP_ALIGN.CENTER)

add_text(sl, "Most expensive component: FinBERT  ~200–500ms  |  XGBoost+SHAP: ~5ms  |  Rules: <1ms",
         0.4, 6.08, 12.4, 0.35, font_size=12, color=LIGHT_GRAY, align=PP_ALIGN.CENTER)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 9 — Black Box vs SHAP
# ═══════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(blank_layout)
set_bg(sl, BG_DARK)
slide_header(sl, "Black Box vs SHAP — The Core Difference",
             "Same model, same inputs — SHAP reveals what the black box hides")

# left — black box
card(sl, 0.4, 1.32, 5.9, 5.6)
add_text(sl, "🔒  Without SHAP  (Black Box)", 0.6, 1.42, 5.5, 0.38,
         font_size=15, bold=True, color=RED)
bb_pts = [
    "Input: RSI=67.4, MACD=0.82, BB%=0.71 …",
    "↓  200 trees — internal logic invisible",
    "↓  Thousands of if/else branches run",
    "Output:  proba_up = 0.68",
    "",
    "User sees:  'Buy  68%'",
    "",
    "You CANNOT know:",
    "  • Which indicator drove it",
    "  • Whether RSI mattered or MACD did",
    "  • If one indicator is fighting another",
    "  • Whether the confidence is trustworthy",
    "",
    "Two stocks can both show 0.68",
    "for completely opposite reasons —",
    "and you'd never know.",
]
add_multiline(sl, bb_pts, 0.6, 1.88, 5.6, 4.9,
              font_size=12, color=LIGHT_GRAY, spacing=Pt(4))

# right — SHAP
card(sl, 6.7, 1.32, 6.2, 5.6)
add_text(sl, "🔓  With SHAP  (Open Box)", 6.9, 1.42, 5.8, 0.38,
         font_size=15, bold=True, color=GREEN)
sh_pts = [
    "Same input:  RSI=67.4, MACD=0.82 …",
    "↓  TreeExplainer traverses tree structure",
    "↓  Evaluates 2^6 = 64 feature coalitions",
    "",
    "Output — one value per feature:",
    "  RSI:    +0.142  ← pushed UP  (biggest)",
    "  MACD:   +0.089  ← pushed UP",
    "  BB%:    −0.061  ← pushed DOWN",
    "  ROC:    +0.031",
    "  Stoch:  −0.018",
    "  ATR:    +0.005",
    "  Sum = 0.188 → 0.50 + 0.188 = 0.688 ✓",
    "",
    "User sees:",
    "  'RSI pushed prediction UP (0.142)'",
    "  'MACD pushed prediction UP (0.089)'",
    "  'BB% pushed prediction DOWN (−0.061)'",
]
add_multiline(sl, sh_pts, 6.9, 1.88, 5.9, 4.9,
              font_size=12, color=LIGHT_GRAY, spacing=Pt(4))

# vs badge
add_rect(sl, 6.05, 3.7, 0.65, 0.65, ACCENT_PURPLE)
add_text(sl, "VS", 6.07, 3.77, 0.62, 0.55,
         font_size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

add_text(sl,
    "SHAP Guarantee:  values always sum to exactly (prediction − baseline)  |  Mathematically proven, not approximate",
    0.4, 7.02, 12.5, 0.38, font_size=12, bold=True, color=YELLOW, align=PP_ALIGN.CENTER)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 10 — scikit-learn
# ═══════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(blank_layout)
set_bg(sl, BG_DARK)
slide_header(sl, "scikit-learn — Is It Used?",
             "Yes — but only as a measurement tool, never for prediction")

add_text(sl, "The only import:", 0.5, 1.32, 9, 0.32,
         font_size=14, bold=True, color=ACCENT_BLUE)
add_rect(sl, 0.5, 1.66, 12.3, 0.55, RGBColor(0x10, 0x14, 0x24))
add_text(sl, "from sklearn.metrics import classification_report   # backtest_technical_model.py  L3",
         0.65, 1.72, 12.0, 0.44, font_size=13, color=GREEN)

usage_cards = [
    ("Where", "backtest_technical_model.py\nWalk-forward backtesting script\nNever imported in main.py"),
    ("What it does", "Formats accuracy / precision /\nrecall / F1-score after XGBoost\nhas already made predictions"),
    ("What it does NOT do", "It makes ZERO predictions.\nXGBoost predicts.\nsklearn only measures accuracy."),
    ("Live app?", "❌  NOT part of the live pipeline.\nNever runs when a user searches\na ticker. Offline dev tool only."),
]
for i, (t, d) in enumerate(usage_cards):
    x = 0.5 + i * 3.22
    card(sl, x, 2.45, 3.0, 2.8)
    add_text(sl, t, x+0.15, 2.55, 2.75, 0.38, font_size=14, bold=True, color=ACCENT_PURPLE)
    add_text(sl, d, x+0.15, 2.98, 2.75, 2.2, font_size=13, color=LIGHT_GRAY)

# comparison table
headers2 = ["Component", "Makes Predictions?", "Part of Live App?", "Cost per Request"]
rows2 = [
    ["XGBoost",     "✅  Yes — 200 trees vote",        "✅  Runs every /analyze",     "~1 ms"],
    ["SHAP",        "❌  No — explains XGBoost",        "✅  Runs every /analyze",     "~5 ms"],
    ["FinBERT",     "✅  Yes — classifies headlines",   "✅  Runs every /analyze",     "~200–500 ms"],
    ["scikit-learn","❌  No — measures accuracy only",  "❌  Offline backtest only",   "0 ms (live)"],
]
col_w2 = [2.5, 3.5, 3.5, 2.0]
col_x2 = [0.5, 3.02, 6.54, 10.06]
add_rect(sl, 0.5, 5.5, 12.06, 0.38, ACCENT_PURPLE)
for ci, h in enumerate(headers2):
    add_text(sl, h, col_x2[ci]+0.1, 5.54, col_w2[ci], 0.32,
             font_size=13, bold=True, color=WHITE)
for ri, row in enumerate(rows2):
    bg = CARD_BG if ri % 2 == 0 else RGBColor(0x14, 0x17, 0x28)
    add_rect(sl, 0.5, 5.9+ri*0.38, 12.06, 0.38, bg)
    for ci, cell in enumerate(row):
        clr = LIGHT_GRAY
        if "✅" in cell: clr = GREEN
        if "❌" in cell: clr = RED
        add_text(sl, cell, col_x2[ci]+0.1, 5.92+ri*0.38,
                 col_w2[ci], 0.34, font_size=11, color=clr)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 11 — Market Comparison (Differences)
# ═══════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(blank_layout)
set_bg(sl, BG_DARK)
slide_header(sl, "MarketMind vs Commercial Tools",
             "Honest gap analysis — where it leads and where it lags")

areas = [
    ("Fundamentals Depth",
     "MarketMind: 2 rules (PE, D/E)",
     "Bloomberg/Seeking Alpha: 200+ metrics — FCF, ROE, ROIC, earnings surprise, guidance revisions"),
    ("Model Training",
     "9 US stocks only — used on ANY ticker",
     "Professional: sector-specific models, millions of data points across thousands of stocks"),
    ("News Sentiment",
     "20 headline titles only · confidence score discarded",
     "Professional: full article body + transcripts + SEC filings + social media at massive scale"),
    ("Data Freshness",
     "Prices: 1hr · Fundamentals: 24hr · News: 6hr",
     "Bloomberg: millisecond real-time direct market feeds"),
    ("Peer Comparison",
     "Hardcoded 16-ticker map only",
     "Professional: dynamic sector peers, hundreds of companies, full comparison"),
    ("Confidence Score",
     "Heuristic formula — not statistically calibrated",
     "Professional: Platt scaling / isotonic regression — 70% means historically ~70% correct"),
]
for i, (area, mm, pro) in enumerate(areas):
    y = 1.38 + i * 0.98
    card(sl, 0.4, y, 12.4, 0.88)
    add_text(sl, area, 0.6, y+0.06, 2.4, 0.35, font_size=12, bold=True, color=ACCENT_BLUE)
    add_rect(sl, 3.05, y+0.12, 0.04, 0.65, ACCENT_PURPLE)
    add_text(sl, "MarketMind: " + mm, 3.15, y+0.06, 4.2, 0.38, font_size=11, color=RED)
    add_text(sl, "Pro: " + pro, 3.15, y+0.46, 9.5, 0.38, font_size=11, color=GREEN)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 12 — Advantages of MarketMind
# ═══════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(blank_layout)
set_bg(sl, BG_DARK)
slide_header(sl, "MarketMind's Genuine Advantages",
             "What it does better than commercial tools — not marketing, real technical edges")

advantages = [
    ("🔍 SHAP Explainability",
     "Quant-grade, per-indicator explanation on every prediction.\n"
     "Bloomberg gives a score. MarketMind tells you EXACTLY which indicator\n"
     "moved the needle and by how much. No retail tool does this."),
    ("🤖 Three-Signal Fusion",
     "Technical (ML) + Fundamental (rules) + Sentiment (NLP)\n"
     "fused into one verdict. Most tools specialize in one.\n"
     "Multi-modal ensemble is what institutional quant funds use."),
    ("📰 FinBERT (Not Generic NLP)",
     "Finance-domain transformer — understands 'falls short of expectations'\n"
     "as negative. Generic tools miss financial language nuance entirely.\n"
     "Domain-specific NLP is rare in free retail tools."),
    ("💬 Context-Aware AI Chat",
     "Gemini assistant is injected with the LIVE analysis result on screen.\n"
     "Answers are grounded in the actual verdict, SHAP reasons, and score.\n"
     "Competitors' AI answers generically — not about your current analysis."),
    ("📊 Full Score Decomposition",
     "User sees tech=0.36, fund=1.0, sent=0.50 separately.\n"
     "Can tell if ML and sentiment agree but fundamentals are neutral.\n"
     "Most tools give one opaque number — no breakdown."),
    ("🆓 Zero Cost + Full Transparency",
     "Bloomberg: $24,000/yr. TipRanks: $600/yr. MarketMind: $0.\n"
     "Every rule, every weight, every formula is readable code.\n"
     "No black box rating — full audit trail from raw data to verdict."),
    ("📈 Risk-Adjusted Portfolio Advisor",
     "Simplified Sharpe Ratio (return/volatility) per stock.\n"
     "Best risk-adjusted performer per sector — real diversification.\n"
     "Personalized from user's own search history. Free tools don't do this."),
    ("⚡ Intelligent Tiered Caching",
     "Prices: 1hr · Fundamentals: 24hr · News: 6hr.\n"
     "Matched to how fast each data type actually changes.\n"
     "Fast + free-tier-sustainable at zero operational cost."),
]
positions2 = [
    (0.4,1.32,6.1),(6.85,1.32,6.1),
    (0.4,3.0,6.1), (6.85,3.0,6.1),
    (0.4,4.68,6.1),(6.85,4.68,6.1),
    (0.4,6.36,6.1),(6.85,6.36,6.1),
]
for i, (title, desc) in enumerate(advantages):
    lx, ty, w = positions2[i]
    card(sl, lx, ty, w, 1.55)
    add_text(sl, title, lx+0.18, ty+0.1, w-0.3, 0.38, font_size=13, bold=True, color=ACCENT_PURPLE)
    add_text(sl, desc, lx+0.18, ty+0.5, w-0.3, 0.98, font_size=11, color=LIGHT_GRAY)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 13 — Summary / Closing
# ═══════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(blank_layout)
set_bg(sl, BG_DARK)
add_rect(sl, 0, 0, 13.33, 0.08, ACCENT_PURPLE)

add_text(sl, "MarketMind — Summary", 0.5, 0.25, 12.3, 0.75,
         font_size=38, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
add_text(sl, "Institutional-grade concepts · Free · Transparent · Accessible",
         0.5, 0.95, 12.3, 0.45, font_size=18, color=ACCENT_BLUE, align=PP_ALIGN.CENTER)
add_rect(sl, 3.5, 1.45, 6.3, 0.06, ACCENT_PURPLE)

summary_items = [
    ("XGBoost", "ML model trained on 9 stocks × 10yr · Predicts price direction\n5-day horizon · 200 boosted trees · 40% of final verdict", ACCENT_PURPLE),
    ("SHAP", "Game-theory attribution per indicator · Opens the black box\nTop 3 reasons per prediction · Zero impact on score", ACCENT_BLUE),
    ("FinBERT", "Finance-domain BERT · 20 headlines · pos/neg/neutral\n12 attention layers · 30% of final verdict", RGBColor(0x3D,0xD6,0x8C)),
    ("Rules", "2 handwritten rules · PE vs sector avg · Debt/Equity\nFully auditable · 30% of final verdict", YELLOW),
    ("combine_scores()", "0.4×tech + 0.3×fund + 0.3×sent · Only meeting point\nVerdict + confidence + unified explanation", WHITE),
]
for i, (t, d, c) in enumerate(summary_items):
    y = 1.7 + i * 1.0
    add_rect(sl, 0.5, y, 0.12, 0.78, c)
    card(sl, 0.7, y, 11.9, 0.78)
    add_text(sl, t, 0.9, y+0.08, 2.5, 0.35, font_size=14, bold=True, color=c)
    add_text(sl, d, 3.5, y+0.08, 9.0, 0.62, font_size=13, color=LIGHT_GRAY)

add_rect(sl, 0.5, 6.78, 12.3, 0.6, RGBColor(0x1A, 0x0D, 0x35))
add_text(sl,
    '"MarketMind takes institutional-grade concepts — SHAP explainability, multi-signal ensemble, '
    'domain NLP — and makes them free, transparent, and understandable to any retail investor."',
    0.7, 6.83, 11.9, 0.52, font_size=13, italic=True, color=ACCENT_BLUE, align=PP_ALIGN.CENTER)

add_rect(sl, 0, 7.42, 13.33, 0.08, ACCENT_PURPLE)

# ─── Save ──────────────────────────────────────────────────────────────────────
output_path = r"c:\Users\hp\marketmind\MarketMind_Presentation.pptx"
prs.save(output_path)
print(f"Saved: {output_path}")
