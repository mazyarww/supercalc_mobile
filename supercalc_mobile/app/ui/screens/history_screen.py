from __future__ import annotations

from kivy.uix.screenmanager import Screen
from kivymd.uix.list import TwoLineListItem

from database.history import HistoryStore
from localization.strings import tr
from localization.rtl import shape_rtl


class HistoryScreen(Screen):
    def __init__(self, history_store: HistoryStore | None = None, **kwargs):
        super().__init__(**kwargs)
        self.history_store = history_store or HistoryStore()

    def on_pre_enter(self, *args) -> None:
        self.refresh()

    def refresh(self) -> None:
        self.ids.history_bar.title = shape_rtl(tr("tab_history"))
        entries = self.history_store.recent(limit=200)
        listview = self.ids.history_list
        listview.clear_widgets()
        if not entries:
            listview.add_widget(TwoLineListItem(text=shape_rtl(tr("history_empty")), secondary_text=""))
            return
        for entry in entries:
            listview.add_widget(
                TwoLineListItem(
                    text=shape_rtl(entry.expression),
                    secondary_text=shape_rtl(f"= {entry.result}"),
                )
            )

    def clear_history(self) -> None:
        self.history_store.clear()
        self.refresh()
