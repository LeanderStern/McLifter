import copy
from enum import StrEnum
from pathlib import Path
from typing import List

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Middle, Center, HorizontalGroup, VerticalGroup, Vertical, Container, CenterMiddle, \
    ScrollableContainer, Horizontal, Grid
from textual.screen import ModalScreen
from textual.widgets import OptionList, Label, Button
from textual.widgets._option_list import Option


class ButtonTypeEnum(StrEnum):
    SELECT = "Select"
    CUSTOM = "Custom"

class SelectOptionDialog(ModalScreen):
    CSS_PATH = "style.tcss"

    _option_list: OptionList = OptionList()

    def __init__(self, options: List[Option], separators: bool = False) -> None:
        super().__init__()
        for i, option in enumerate(options):
            self._option_list.add_option(option)
            if separators and i < len(options) -1:
                self._option_list.add_option(None)

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("[bold]Previously saved paths detected! Select one or choose a custom path.")
            yield self._option_list
            with Center():
                with Horizontal():
                    yield Button(ButtonTypeEnum.SELECT, variant="primary", id=ButtonTypeEnum.SELECT)
                    yield Button(ButtonTypeEnum.CUSTOM, variant="default", id=ButtonTypeEnum.CUSTOM)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == ButtonTypeEnum.CUSTOM:
            self.dismiss()
        else:
            self.dismiss(self._option_list.highlighted_option)