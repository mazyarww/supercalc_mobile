"""
localization.rtl
-----------------
Kivy's default text renderer does NOT do Arabic/Persian letter shaping or
bidi reordering. If you just drop Persian text into a Kivy Label as-is, you
get exactly the symptoms described in the brief:
  - letters appear disconnected (each glyph rendered in isolated form)
  - text runs left-to-right instead of right-to-left
  - mixed Persian/English/number strings display in the wrong order

The fix is NOT a font swap. Correct rendering needs two separate steps:

1. Reshaping: pick the correct contextual glyph form (initial/medial/final/
   isolated) for each Arabic-script letter, using `arabic_reshaper`.
2. Bidi reordering: reorder the shaped string according to the Unicode
   Bidirectional Algorithm, using `python-bidi`.

Both must run BEFORE the string is handed to Kivy's Label/TextInput. Kivy
renders left-to-right glyph-by-glyph, so we do the layout ourselves in
Python and hand Kivy an already-correct string.

Usage:
    from localization.rtl import shape_rtl
    label.text = shape_rtl("سلام دنیا")
"""
from __future__ import annotations

import re

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    _RTL_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised when deps aren't installed
    _RTL_AVAILABLE = False

# Persian-specific reshaper configuration. The default arabic_reshaper config
# is tuned for Arabic; Persian uses a few different letterforms (ی, ک, گ, پ,
# چ, ژ) and Persian digits ۰-۹ rather than Arabic-Indic ۰-٩. This config
# block is the standard fix for "پ/چ/ژ/گ render as boxes or wrong shapes".
_PERSIAN_RESHAPER_CONFIG = {
    "delete_harakat": False,
    "support_ligatures": True,
    "language": "Persian",
}

_reshaper = None
if _RTL_AVAILABLE:
    _reshaper = arabic_reshaper.ArabicReshaper(configuration=_PERSIAN_RESHAPER_CONFIG)

# Range covering Arabic + Persian + Arabic Presentation Forms
_ARABIC_SCRIPT_RE = re.compile(
    r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]"
)


def contains_rtl(text: str) -> bool:
    """True if the string contains any Persian/Arabic-script characters."""
    return bool(_ARABIC_SCRIPT_RE.search(text))


def shape_rtl(text: str) -> str:
    """
    Reshape + bidi-reorder a string containing Persian/Arabic text so it
    renders correctly in Kivy widgets (Label, Button, TextInput, etc.).

    Latin text, numbers, and punctuation mixed into the string are left in
    their correct reading positions by the bidi algorithm; only the
    Arabic-script runs are reshaped.

    Safe to call on pure-English strings too (returned unchanged), so UI
    code can call shape_rtl() unconditionally on any user-facing string.
    """
    if not text or not contains_rtl(text):
        return text

    if not _RTL_AVAILABLE:
        # Dependencies not installed: fail loudly in dev rather than silently
        # shipping broken RTL text to a device.
        raise RuntimeError(
            "Persian/RTL text detected but 'arabic_reshaper' and 'python-bidi' "
            "are not installed. Run: pip install arabic-reshaper python-bidi"
        )

    reshaped = _reshaper.reshape(text)
    return get_display(reshaped)


def is_rtl_language(lang_code: str) -> bool:
    return lang_code in ("fa", "ar", "he", "ur")
