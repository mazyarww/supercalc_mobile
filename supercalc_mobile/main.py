"""
main
----
Entry point for the mobile app. Run with:
    python main.py
(after `pip install -r requirements.txt`)

Or build to Android with:
    buildozer android debug
"""
from __future__ import annotations

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivymd.app import MDApp
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem

from app.ui.screens.calculator_screen import CalculatorScreen
from app.ui.screens.history_screen import HistoryScreen
from app.ui.screens.settings_screen import SettingsScreen
from localization.strings import tr
from localization.rtl import shape_rtl
from ai.device_features import (
    scan_equation_from_camera,
    listen_for_expression,
    FeatureNotAvailable,
)

KV_PATH = "app/ui/kv/main.kv"


class SuperCalcMobileApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"
        self.title = tr("app_title")

        Builder.load_file(KV_PATH)

        self.calc_screen = CalculatorScreen()
        self.history_screen = HistoryScreen(history_store=self.calc_screen.history_store)
        self.settings_screen = SettingsScreen()

        nav = MDBottomNavigation()
        nav.add_widget(self._nav_item(self.calc_screen, "calculator", tr("tab_calc")))
        nav.add_widget(self._nav_item(self.history_screen, "history", tr("tab_history")))
        nav.add_widget(self._nav_item(self.settings_screen, "settings", tr("tab_settings")))
        self.nav = nav
        return nav

    def _nav_item(self, screen, icon: str, text: str) -> MDBottomNavigationItem:
        item = MDBottomNavigationItem(name=screen.name, text=shape_rtl(text), icon=icon)
        item.add_widget(screen)
        return item

    def apply_language(self) -> None:
        """Re-apply translated + RTL-shaped strings across the app after a language switch."""
        self.title = tr("app_title")
        # KivyMD bottom-nav item labels are set at construction time; a full
        # language switch is simplest handled by refreshing each screen's own
        # widgets (history/settings already do this in on_pre_enter):
        self.calc_screen._refresh_display()
        self.history_screen.refresh()
        self.settings_screen.refresh()

    # -- device feature hooks (see ai/device_features.py for real integration notes) --
    def on_scan_pressed(self) -> None:
        try:
            expr = scan_equation_from_camera()
            self.calc_screen.current_expr = expr
            self.calc_screen._refresh_display()
        except FeatureNotAvailable:
            self._toast(tr("scanner_coming_soon"))

    def on_voice_pressed(self) -> None:
        try:
            expr = listen_for_expression()
            self.calc_screen.current_expr = expr
            self.calc_screen._refresh_display()
        except FeatureNotAvailable:
            self._toast(tr("voice_coming_soon"))

    def on_copy_result(self) -> None:
        from kivy.core.clipboard import Clipboard
        Clipboard.copy(self.calc_screen.ids.result_label.text)

    def _toast(self, message: str) -> None:
        try:
            from kivymd.toast import toast
            toast(shape_rtl(message))
        except Exception:  # noqa: BLE001 - toast is a nice-to-have, never crash on it
            print(message)


if __name__ == "__main__":
    SuperCalcMobileApp().run()
