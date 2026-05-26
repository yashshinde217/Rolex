"""
theme.py — Visual design tokens for Rolex GUI (Glassmorphism)
Single source of truth for every colour, size, font, and timing value.
"""

# ─── Window ───────────────────────────────────────────────────────────────────

WINDOW_SIZE    = 420
WINDOW_MARGIN  = 16
WINDOW_RADIUS  = 18

# ─── Section heights ──────────────────────────────────────────────────────────

HEADER_HEIGHT  = 44
ORB_SECTION_H  = 110
VIZ_HEIGHT     = 48
STATUS_HEIGHT  = 36

# ─── Glassmorphism palette ────────────────────────────────────────────────────

GLASS_BG        = "rgba(8, 12, 22, 220)"
GLASS_BORDER    = "rgba(255, 255, 255, 18)"
GLASS_SECTION   = "rgba(255, 255, 255, 6)"
GLASS_CARD      = "rgba(255, 255, 255, 8)"
GLASS_CARD_USER = "rgba(0, 100, 180, 35)"
GLASS_HEADER    = "rgba(255, 255, 255, 10)"
GLASS_HOVER     = "rgba(255, 255, 255, 14)"
GLASS_SETTINGS  = "rgba(6, 10, 20, 240)"

TEXT_PRIMARY   = "#E8EDF5"
TEXT_SECONDARY = "#5A6A82"
TEXT_DIM       = "#3A4A5E"
TEXT_ACCENT    = "#4A90D9"

# ─── Orb state colour pairs (primary, glow) ───────────────────────────────────

ORB_IDLE      = ("#1A4A7A", "#0D2A4A")
ORB_LISTENING = ("#00B4D8", "#005F73")
ORB_THINKING  = ("#C0C8D8", "#404858")
ORB_SPEAKING  = ("#00C896", "#006845")
ORB_WEB       = ("#FF8C42", "#7A3A10")
ORB_CAMERA    = ("#A855F7", "#4A1A7A")
ORB_VISION    = ("#FACC15", "#6A5000")
ORB_ERROR     = ("#EF4444", "#6A0000")

ORB_SIZE = 64

# ─── Mode tag colours ─────────────────────────────────────────────────────────

TAG_BRAIN   = ("rgba(30,58,95,180)",  "#4A90D9")
TAG_WEB     = ("rgba(61,32,0,180)",   "#FF8C42")
TAG_CAMERA  = ("rgba(45,10,74,180)",  "#A855F7")
TAG_VISION  = ("rgba(61,48,0,180)",   "#FACC15")
TAG_OCR     = ("rgba(20,48,0,180)",   "#6BCB77")

# ─── Typography ───────────────────────────────────────────────────────────────

FONT_TITLE  = "Segoe UI"
FONT_BODY   = "Segoe UI"
FONT_MONO   = "Consolas"
SIZE_SM     = 10
SIZE_MD     = 12
SIZE_LG     = 14
SIZE_XL     = 16

# ─── Animation ────────────────────────────────────────────────────────────────

ANIM_PULSE_MS   = 2200
ANIM_RIPPLE_MS  = 1100
ANIM_MORPH_MS   = 320      # Minimize/restore morph duration
VIZ_BAR_COUNT   = 16

# ─── Tray ─────────────────────────────────────────────────────────────────────

TRAY_TOOLTIP = "Rolex — Personal AI"