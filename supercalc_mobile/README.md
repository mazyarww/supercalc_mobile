# Ultimate AI Super Calculator — Mobile

A KivyMD mobile front end for the calculator engine, with real Persian/RTL
support. Read this before assuming everything on the original wishlist is
here — it isn't, and pretending otherwise would just move the disappointment
to later.

## What's actually implemented and verified

- **Calculation engine** (`core/math_engine/engine.py`) — arbitrary precision
  (mpmath), complex numbers, constants library, percentages, variables,
  user-defined functions, degree/radian modes. Tested directly in this
  sandbox (sympy/mpmath/numpy are installed here) — see the test commands in
  the build transcript; results like `2^10=1024`, `(3+4i)(1-2i)=11-2i`,
  `100!`, `e^(iπ)+1=0` all check out.
- **RTL/Persian text rendering** (`localization/rtl.py`) — uses
  `arabic_reshaper` + `python-bidi`, the actual standard fix for
  disconnected-letter Persian rendering in Kivy (a font swap alone does
  *not* fix this — Kivy's renderer needs pre-shaped, pre-reordered strings).
  Logic verified in this sandbox for the parts that don't require the
  reshaper library itself (pass-through on non-RTL text, RTL detection).
- **History store** (`database/history.py`) — SQLite, tested here (add,
  recent, favorite, clear all work).
- **Language switching** EN/FA (`localization/strings.py`) — tested here.
- **Mobile UI structure** — bottom nav (Calculator / History / Settings),
  touch-sized buttons, dark/light theme toggle, async evaluation (keypad
  presses never block on the calculation thread).

## What's real code but UNTESTED (no network/Kivy in this sandbox)

I don't have internet access or Kivy/KivyMD installed in the environment I
built this in, so the `.kv` layout and the screen classes that depend on
Kivy widgets (`app/ui/*`, `main.py`) are written carefully against the real
KivyMD 1.2 API but **not executed**. Before you trust this:

```bash
pip install -r requirements.txt
python main.py
```

and fix whatever surfaces — I'd expect minor issues (a widget id typo, a
KV binding that needs adjusting) rather than structural problems, but I
can't promise it runs first try without having run it myself.

## What's a deliberate stub, not a fake feature

`ai/device_features.py` — camera OCR, voice input/output, and cloud backup
all raise `FeatureNotAvailable` with a note on exactly what real integration
each needs (Mathpix API for math OCR, platform speech APIs for voice, a real
backend for cloud sync). I did this on purpose instead of writing something
that *looks* functional but returns canned/wrong answers — a fake OCR stub
that "recognizes" the same equation every time is worse than an honest
"coming soon" toast.

## What's not here at all yet

The original desktop spec's CAS (symbolic solve/simplify/integrate),
graphing, matrix tools, and unit conversion were never built on the desktop
side either — only the numeric engine was. This mobile scaffold carries over
what exists (the engine) and is structured so those modules can drop into
`core/` later without touching the UI layer, but they still need to be
written.

## Project structure

```
/app/ui/screens   - Kivy Screen subclasses (Calculator, History, Settings)
/app/ui/kv        - KV layout files
/core/math_engine - the real calculation engine
/ai               - device-feature integration points (OCR/voice/cloud stubs)
/database         - SQLite history
/localization     - EN/FA strings + RTL shaping
buildozer.spec    - Android build config
```

## Building the APK

```bash
buildozer android debug
```
This requires the Android SDK/NDK, which buildozer will fetch on first run —
expect that step to take a while and to need a real network connection and
several GB of disk.
