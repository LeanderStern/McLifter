from enum import StrEnum

from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import Screen, ModalScreen
from textual.widgets import Label, Button

class ButtonTypeEnum(StrEnum):
    YES = "Yes"
    NO = "No"

class YesNoDialogScreen(ModalScreen):
    CSS_PATH = "style.tcss"

    _dialog_prompt: str
    _yes_button_text: str
    _no_button_text: str

    def __init__(self, dialog_prompt: str,
                 yes_button_text: str = ButtonTypeEnum.YES,
                 no_button_text: str = ButtonTypeEnum.NO) -> None:
        self._dialog_prompt = dialog_prompt
        self._yes_button_text = yes_button_text
        self._no_button_text = no_button_text
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Grid(Label(self._dialog_prompt, id="question"),
                   Button(self._yes_button_text, variant="success", id=ButtonTypeEnum.YES),
                   Button(self._no_button_text, variant="error", id=ButtonTypeEnum.NO),
                   id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == ButtonTypeEnum.YES:
            self.dismiss(True)
        else:
            self.dismiss(False)