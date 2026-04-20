from enum import StrEnum
from pathlib import Path
from typing import List

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Middle, Center, HorizontalGroup, VerticalGroup, Vertical, Container, CenterMiddle, \
    ScrollableContainer, Horizontal
from textual.screen import ModalScreen
from textual.widgets import OptionList, Label, Button

class ButtonTypeEnum(StrEnum):
    SELECT = "Select"
    CUSTOM = "Custom"

class SelectPathsDialog(ModalScreen):
    CSS_PATH = "style.tcss"

    _paths: list[Path]
    _highlighted_option_index: int #OptionList always auto-highlights the first item in a list, so this will always have a value

    def __init__(self, paths: List[Path]) -> None:
        self._paths = paths
        super().__init__()

    def compose(self) -> ComposeResult:
        with Container():
            yield Label("Previously saved paths detected! Select one or choose a custom path.")
            option_list = OptionList()
            for path in self._paths:
                option_list.add_option(str(path))
                option_list.add_option(None)
            yield option_list
            with Horizontal():
                yield Button(ButtonTypeEnum.SELECT, variant="primary", id=ButtonTypeEnum.SELECT)
                yield Button(ButtonTypeEnum.CUSTOM, variant="default", id=ButtonTypeEnum.CUSTOM)

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted):
        self._highlighted_option_index = event.option_index

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == ButtonTypeEnum.CUSTOM:
            self.dismiss()
        else:
            self.dismiss(self._paths[self._highlighted_option_index])