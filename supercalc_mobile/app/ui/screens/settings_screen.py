from __future__ import annotations

from kivy.uix.screenmanager import Screen
from kivymd.uix.list import OneLineAvatarIconListItem, IRightBodyTouch
from kivymd.uix.selectioncontrol import MDSwitch

from localization.strings import tr, set_language, get_language
from localization.rtl import shape_rtl


class RightSwitch(IRightBodyTouch, MDSwitch):
    """An MDSwitch that can be placed as the trailing control on a list item."""


class SettingsScreen(Screen):
    def on_pre_enter(self, *args) -> None:
        self.refresh()

    def refresh(self) -> None:
        self.ids.settings_bar.title = shape_rtl(tr("tab_settings"))
        listview = self.ids.settings_list
        listview.clear_widgets()

        # Theme toggle (dark / light)
        theme_item = OneLineAvatarIconListItem(text=shape_rtl(tr("settings_theme")))
        theme_switch = RightSwitch(active=self._app().theme_cls.theme_style == "Dark")
        theme_switch.bind(active=self._on_theme_toggle)
        theme_item.add_widget(theme_switch)
        listview.add_widget(theme_item)

        # Language toggle (EN / FA) - triggers a full RTL relayout on change
        lang_item = OneLineAvatarIconListItem(text=shape_rtl(tr("settings_language")))
        lang_switch = RightSwitch(active=(get_language() == "fa"))
        lang_switch.bind(active=self._on_language_toggle)
        lang_item.add_widget(lang_switch)
        listview.add_widget(lang_item)

    def _app(self):
        from kivy.app import App
        return App.get_running_app()

    def _on_theme_toggle(self, switch, active) -> None:
        self._app().theme_cls.theme_style = "Dark" if active else "Light"

    def _on_language_toggle(self, switch, active) -> None:
        set_language("fa" if active else "en")
        self._app().apply_language()
        self.refresh()
