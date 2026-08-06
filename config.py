import os

# Base Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "database")
IMAGES_DIR = os.path.join(BASE_DIR, "images", "citizen_photos")
ICONS_DIR = os.path.join(BASE_DIR, "icons")

# Ensure required directories exist
os.makedirs(DATABASE_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(ICONS_DIR, exist_ok=True)

# Database File Path
DB_PATH = os.path.join(DATABASE_DIR, "citizens.db")

# GUI Configuration
APP_TITLE = "National People Database & Face Recognition System"
WINDOW_SIZE = "1200x700"
IS_RESIZABLE = False

# Colors - Modern Slate & Blue Palette
COLOR_PRIMARY = "#2563EB"       # Vibrant Royal Blue
COLOR_PRIMARY_HOVER = "#1D4ED8" # Darker Blue
COLOR_SECONDARY = "#F8FAFC"     # Off-white / Light Grey
COLOR_BACKGROUND = "#F1F5F9"    # Soft Light Blue-Grey
COLOR_CARD_BG = "#FFFFFF"       # White
COLOR_DARK_TEXT = "#0F172A"     # Dark Slate Text
COLOR_MUTED_TEXT = "#64748B"    # Muted Slate Text
COLOR_BORDER = "#E2E8F0"        # Subtle Border Grey
COLOR_ACCENT = "#3B82F6"        # Light Blue Accent
COLOR_SUCCESS = "#10B981"       # Emerald Green
COLOR_WARNING = "#F59E0B"       # Amber Warning
COLOR_DANGER = "#EF4444"        # Coral Red
COLOR_SIDEBAR = "#1E293B"       # Deep Navy Sidebar
COLOR_SIDEBAR_TEXT = "#F8FAFC"  # Sidebar White Text
COLOR_SIDEBAR_HOVER = "#334155" # Sidebar Hover Navy

# Typography
FONT_FAMILY = "Segoe UI"
FONT_TITLE = (FONT_FAMILY, 18, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 14, "bold")
FONT_HEADING = (FONT_FAMILY, 12, "bold")
FONT_BODY = (FONT_FAMILY, 10)
FONT_BODY_BOLD = (FONT_FAMILY, 10, "bold")
FONT_SMALL = (FONT_FAMILY, 9)

# Recognition Parameters
FACE_MATCH_THRESHOLD = 0.6  # Maximum distance threshold for face match (lower = stricter)
CONFIDENCE_PASS_PERCENT = 60.0 # Min percentage to declare match

# Admin Default Credentials
DEFAULT_ADMIN_USER = "admin"
DEFAULT_ADMIN_PASS = "admin123"
