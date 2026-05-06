"""
ثيم / نظام تصميم موحد للتطبيق
Modern Dark Theme with Emerald/Gold accents – RTL Arabic
"""

# ─── الألوان الرئيسية ──────────────────────────────────────────────────────────
BG_DARK      = "#0A0F1A"   # خلفية رئيسية
BG_CARD      = "#111827"   # خلفية البطاقات
BG_PANEL     = "#0E1624"   # خلفية الألواح الجانبية
BG_INPUT     = "#1A2540"   # خلفية حقول الإدخال
BG_HOVER     = "#1E2D4A"   # hover

ACCENT       = "#00D4AA"   # فيروزي – لون التمييز الرئيسي
ACCENT2      = "#FFB347"   # ذهبي
ACCENT3      = "#6C8EEF"   # أزرق

SUCCESS      = "#2ECC71"
DANGER       = "#E74C3C"
WARNING      = "#F39C12"
INFO         = "#6C8EEF"

TEXT_PRIMARY = "#EEF2FF"
TEXT_SECOND  = "#8FA3C8"
TEXT_MUTED   = "#3A4A6A"
TEXT_ACCENT  = "#00D4AA"

BORDER       = "#1E3050"
BORDER_FOCUS = "#00D4AA"

# ─── الخطوط – الي يمامة (Alyamama) ──────────────────────────────────────────
FONT_AR       = "Alyamama-Bold"

FONT_H1      = (FONT_AR, 20, "bold")
FONT_H2      = (FONT_AR, 15, "bold")
FONT_H3      = (FONT_AR, 13, "bold")
FONT_BODY    = (FONT_AR, 12)
FONT_SMALL   = (FONT_AR, 10)
FONT_LARGE   = (FONT_AR, 16, "bold")
FONT_MONO    = ("Consolas", 12)
FONT_LABEL   = (FONT_AR, 12)
FONT_INPUT   = (FONT_AR, 12)
FONT_BTN     = (FONT_AR, 12, "bold")
FONT_KPI_VAL = (FONT_AR, 18, "bold")
FONT_KPI_LBL = (FONT_AR, 10)

# ─── أبعاد ────────────────────────────────────────────────────────────────────
PAD          = 14
PAD_SMALL    = 7
PAD_LARGE    = 22
RADIUS       = 8
BTN_HEIGHT   = 38
SIDEBAR_W    = 220

# ─── ألوان الأزرار ────────────────────────────────────────────────────────────
BTN_PRIMARY  = {"bg": ACCENT,   "fg": "#000000", "abg": "#00BFA0"}
BTN_DANGER   = {"bg": DANGER,   "fg": "#FFFFFF",  "abg": "#C0392B"}
BTN_SECONDARY= {"bg": "#1A2540","fg": TEXT_PRIMARY,"abg": BG_HOVER}
BTN_WARNING  = {"bg": WARNING,  "fg": "#000000",  "abg": "#D68910"}
BTN_INFO     = {"bg": INFO,     "fg": "#FFFFFF",  "abg": "#5A7ADB"}

# ─── ألوان الجداول ────────────────────────────────────────────────────────────
TBL_HEAD_BG  = "#0A0F1A"
TBL_HEAD_FG  = ACCENT
TBL_ROW_ODD  = "#111827"
TBL_ROW_EVEN = "#141E30"
TBL_SEL_BG   = "#0D3B6E"
TBL_SEL_FG   = "#FFFFFF"
TBL_BORDER   = "#1E3050"

# ─── أيقونات (Unicode) ────────────────────────────────────────────────────────
ICON = {
    "products"  : "🏷",
    "supply"    : "📦",
    "sales"     : "💰",
    "expenses"  : "💸",
    "debts"     : "📋",
    "cashbox"   : "🏦",
    "inventory" : "📊",
    "add"       : "➕",
    "edit"      : "✏",
    "delete"    : "🗑",
    "save"      : "💾",
    "search"    : "🔍",
    "refresh"   : "🔄",
    "print"     : "🖨",
    "export"    : "📤",
    "calendar"  : "📅",
    "back"      : "◀",
    "check"     : "✓",
    "warning"   : "⚠",
    "money"     : "💵",
    "pay"       : "💳",
    "report"    : "📈",
}
