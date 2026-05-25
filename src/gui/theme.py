"""
theme.py — Visual design tokens for Rolex GUI (Glassmorphism)

Single source of truth for every colour, size, font, and timing value.
"""

# ─── Window ───────────────────────────────────────────────────────────────────

WINDOW_SIZE    = 420          # Square window (420 x 420)
WINDOW_MARGIN  = 16           # Distance from screen edges
WINDOW_RADIUS  = 18           # Corner rounding

# ─── Section heights ──────────────────────────────────────────────────────────

HEADER_HEIGHT  = 44
ORB_SECTION_H  = 110          # Orb + state label area
VIZ_HEIGHT     = 48           # Mic visualizer bar area
STATUS_HEIGHT  = 36
# Chat takes the remaining space

# ─── Glassmorphism palette ────────────────────────────────────────────────────

# Window base — very dark, semi-transparent
GLASS_BG        = "rgba(8, 12, 22, 210)"        # Main background
GLASS_BORDER    = "rgba(255, 255, 255, 18)"     # Frosted border
GLASS_SECTION   = "rgba(255, 255, 255, 6)"      # Section dividers / insets
GLASS_CARD      = "rgba(255, 255, 255, 8)"      # Message bubble background
GLASS_CARD_USER = "rgba(0, 100, 180, 35)"       # User bubble tint
GLASS_HEADER    = "rgba(255, 255, 255, 10)"     # Header bar

# Glow accent — changes with orb state
GLOW_IDLE      = "#1A6FAA"
GLOW_LISTENING = "#00B4D8"
GLOW_THINKING  = "#A0AEC0"
GLOW_SPEAKING  = "#00C896"
GLOW_WEB       = "#FF8C42"
GLOW_CAMERA    = "#A855F7"
GLOW_VISION    = "#FACC15"
GLOW_ERROR     = "#EF4444"

# Text
TEXT_PRIMARY   = "#E8EDF5"
TEXT_SECONDARY = "#5A6A82"
TEXT_DIM       = "#3A4A5E"

# ─── Orb state colour pairs (primary, glow) ───────────────────────────────────

ORB_IDLE      = ("#1A4A7A", "#0D2A4A")
ORB_LISTENING = ("#00B4D8", "#005F73")
ORB_THINKING  = ("#C0C8D8", "#404858")
ORB_SPEAKING  = ("#00C896", "#006845")
ORB_WEB       = ("#FF8C42", "#7A3A10")
ORB_CAMERA    = ("#A855F7", "#4A1A7A")
ORB_VISION    = ("#FACC15", "#6A5000")
ORB_ERROR     = ("#EF4444", "#6A0000")

ORB_SIZE      = 64    # Orb diameter inside the window

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

ANIM_PULSE_MS  = 2200
ANIM_RIPPLE_MS = 1100
ANIM_SPIN_MS   = 900
VIZ_BAR_COUNT  = 16