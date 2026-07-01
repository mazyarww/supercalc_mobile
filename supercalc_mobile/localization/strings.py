"""
localization.strings
---------------------
Simple string table for language switching. Add new keys here and to both
dicts; UI code should always go through tr(key) rather than hardcoding text,
so the whole app can flip language at runtime.
"""

STRINGS = {
    "en": {
        "app_title": "Ultimate AI Super Calculator",
        "tab_calc": "Calculator",
        "tab_history": "History",
        "tab_settings": "Settings",
        "equals": "=",
        "clear": "C",
        "delete": "DEL",
        "history_empty": "No calculations yet",
        "settings_theme": "Theme",
        "settings_theme_dark": "Dark",
        "settings_theme_light": "Light",
        "settings_language": "Language",
        "settings_precision": "Decimal precision",
        "settings_angle_mode": "Angle mode",
        "error_prefix": "Error: ",
        "scanner_coming_soon": "Camera equation scanner — coming soon",
        "voice_coming_soon": "Voice input — coming soon",
        "cloud_coming_soon": "Cloud backup — coming soon",
    },
    "fa": {
        "app_title": "ماشین‌حساب فوق‌پیشرفته هوش مصنوعی",
        "tab_calc": "ماشین‌حساب",
        "tab_history": "تاریخچه",
        "tab_settings": "تنظیمات",
        "equals": "=",
        "clear": "پاک کردن",
        "delete": "حذف",
        "history_empty": "هنوز محاسبه‌ای انجام نشده",
        "settings_theme": "پوسته",
        "settings_theme_dark": "تیره",
        "settings_theme_light": "روشن",
        "settings_language": "زبان",
        "settings_precision": "دقت اعشار",
        "settings_angle_mode": "واحد زاویه",
        "error_prefix": "خطا: ",
        "scanner_coming_soon": "اسکنر معادله با دوربین — به‌زودی",
        "voice_coming_soon": "ورودی صوتی — به‌زودی",
        "cloud_coming_soon": "پشتیبان‌گیری ابری — به‌زودی",
    },
}

_current_lang = "en"


def set_language(lang_code: str) -> None:
    global _current_lang
    if lang_code not in STRINGS:
        raise ValueError(f"Unsupported language: {lang_code}")
    _current_lang = lang_code


def get_language() -> str:
    return _current_lang


def tr(key: str) -> str:
    """Translate a UI string key into the current language. Falls back to English, then the key itself."""
    table = STRINGS.get(_current_lang, STRINGS["en"])
    return table.get(key, STRINGS["en"].get(key, key))
