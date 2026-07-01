[app]
title = Ultimate AI Super Calculator
package.name = supercalcmobile
package.domain = org.supercalc
source.dir = .
source.include_exts = py,kv,png,jpg,ttf,json
version = 0.1.0

requirements = python3,kivy==2.3.0,kivymd==1.2.0,sympy,mpmath,arabic-reshaper,python-bidi

orientation = portrait
fullscreen = 0

# Android
android.permissions = CAMERA,RECORD_AUDIO,INTERNET
android.api = 34
android.minapi = 24
android.archs = arm64-v8a,armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
