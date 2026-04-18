from pydantic import validate_call
from rich.text import Text
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal, HorizontalGroup, Right
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static, Footer, Label

from api_service.api_service import ApiService
from file_manager.file_manager import FileManager
from tui.screens.yes_no_dialog import YesNoDialogScreen


def bool_to_api_status(status: bool) -> Text:
    string = Text("Api Connection: ")
    if status:
        string.append("⏺", "bold green")
    else:
        string.append("⏺", "bold red")
    return string


class Header(Label):
    api_connection_status: reactive[Text] = reactive(bool_to_api_status(False))

    def render(self) -> Text:
        return self.api_connection_status

class McLifterTui(App):
    CSS_PATH = "style.tcss"
    BINDINGS = [("q", "request_quit", "Quit Dialog")]

    _api_service: ApiService
    _file_manager_reference: type[FileManager]
    _api_connection_status: reactive[Text] = reactive(bool_to_api_status(False))

    def __init__(self, api_service: ApiService, file_manager_reference: type[FileManager]) -> None:
        self._api_service = api_service
        self._file_manager_reference = file_manager_reference
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header().data_bind(McLifterTui._api_connection_status)
        yield Footer()

    def on_mount(self) -> None:
        self.update_api_connection_status()
        self.screen.border_title = "McLifter"
        self.screen.border_subtitle = "1.0.0"
        self.set_interval(10, self.update_api_connection_status)

    @work(exclusive=True, thread=True)
    def update_api_connection_status(self) -> None:
        self._api_connection_status = self.call_from_thread(bool_to_api_status, self._api_service.is_api_reachable())

    def handle_yes_no_dialog_result(self, result: bool | None) -> None:
        if result:
            self.exit()

    def action_request_quit(self) -> None:
        self.push_screen(YesNoDialogScreen(dialog_prompt="Do you really want to quit?"), self.handle_yes_no_dialog_result)