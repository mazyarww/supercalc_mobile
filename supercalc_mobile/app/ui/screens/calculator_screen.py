"""
app.ui.screens.calculator_screen
----------------------------------
The main calculator screen. Keypad is built programmatically (not in KV) so
we can swap between "basic" and "scientific" key sets without duplicating
markup, and so RTL-shaped labels can be applied uniformly via shape_rtl().

Evaluation runs on a background thread via Kivy's Clock + threading, so a
slow symbolic simplification never freezes the touch UI - this addresses
the "slow calculations = janky UI" failure mode called out in the brief.
"""
from __future__ import annotations

import threading

from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDRaisedButton

from core.math_engine.engine import Engine, EngineError
from database.history import HistoryStore
from localization.strings import tr
from localization.rtl import shape_rtl

BASIC_KEYS = [
    "7", "8", "9", "/",
    "4", "5", "6", "*",
    "1", "2", "3", "-",
    "0", ".", "=", "+",
    "C", "DEL", "(", ")",
]

SCIENTIFIC_KEYS = [
    "sin(", "cos(", "tan(", "^",
    "sqrt(", "log(", "ln(", "!",
    "pi", "e", "i", "%",
]


class CalculatorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.engine = Engine(precision_digits=15)
        self.history_store = HistoryStore()
        self.current_expr = ""
        self.mode = "basic"  # or "scientific"
        # Keypad is populated once the KV rule has attached self.ids
        Clock.schedule_once(lambda dt: self.build_keypad(), 0)

    # -- keypad construction --------------------------------------------------
    def build_keypad(self) -> None:
        grid = self.ids.keypad
        grid.clear_widgets()
        keys = BASIC_KEYS if self.mode == "basic" else SCIENTIFIC_KEYS
        for key in keys:
            btn = MDRaisedButton(
                text=shape_rtl(key),
                size_hint_y=None,
                height="56dp",
                on_release=lambda inst, k=key: self.on_key(k),
            )
            grid.add_widget(btn)

    def toggle_mode(self) -> None:
        self.mode = "scientific" if self.mode == "basic" else "basic"
        self.build_keypad()

    # -- key handling -----------------------------------------------------------
    def on_key(self, key: str) -> None:
        if key == "C":
            self.current_expr = ""
            self._refresh_display()
        elif key == "DEL":
            self.current_expr = self.current_expr[:-1]
            self._refresh_display()
        elif key == "=":
            self.evaluate_async()
        else:
            self.current_expr += key
            self._refresh_display()

    def _refresh_display(self) -> None:
        self.ids.expr_label.text = shape_rtl(self.current_expr or " ")

    # -- evaluation (background thread) ------------------------------------------
    def evaluate_async(self) -> None:
        expr = self.current_expr.strip()
        if not expr:
            return

        def worker():
            try:
                result = self.engine.evaluate(expr)
                display = str(result.exact)
                Clock.schedule_once(lambda dt: self._on_eval_success(expr, display), 0)
            except EngineError as exc:
                Clock.schedule_once(lambda dt: self._on_eval_error(str(exc)), 0)
            except Exception as exc:  # noqa: BLE001 - never crash the UI thread on bad input
                Clock.schedule_once(lambda dt: self._on_eval_error(str(exc)), 0)

        threading.Thread(target=worker, daemon=True).start()

    def _on_eval_success(self, expr: str, display: str) -> None:
        self.ids.result_label.text = shape_rtl(display)
        self.history_store.add(expr, display)
        self.current_expr = display

    def _on_eval_error(self, message: str) -> None:
        self.ids.result_label.text = shape_rtl(tr("error_prefix") + message)
