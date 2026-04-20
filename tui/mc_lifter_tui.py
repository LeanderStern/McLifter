from pathlib import Path

from rich.text import Text
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Footer, Label, DirectoryTree

from api_service.api_service import ApiService
from file_manager.file_manager import FileManager
from tui.dialogs.select_paths_dialog.select_paths_dialog import SelectPathsDialog
from tui.dialogs.yes_no_dialog.yes_no_dialog import YesNoDialogScreen
from tui.theme import darkorchid_theme


def bool_to_api_status(status: bool) -> Text:
    string = Text("Api Connection: ")
    if status:
        string.append("⏺", "bold green")
    else:
        string.append("⏺", "bold red")
    return string


class Header(Label):
    _api_connection_status: reactive[Text] = reactive(bool_to_api_status(False))

    def render(self) -> Text:
        return self._api_connection_status

class McLifterTui(App):
    CSS_PATH = "style.tcss"
    BINDINGS = [("Q", "request_quit", "Quit McLifter")]

    _api_service: ApiService
    _file_manager_reference: type[FileManager]
    _api_connection_status: reactive[Text] = reactive(bool_to_api_status(False))
    _pre_selected_path: Path | None = None

    def __init__(self, api_service: ApiService, file_manager_reference: type[FileManager]) -> None:
        self._api_service = api_service
        self._file_manager_reference = file_manager_reference
        super().__init__()

    def compose(self) -> ComposeResult:
        with Container(id="app-container") as container:
            container.border_title = "McLifter"
            container.border_subtitle = "1.0.0"
            yield Header().data_bind(McLifterTui._api_connection_status)
            yield DirectoryTree("")
            yield Footer()

    def on_mount(self) -> None:
        self.register_theme(darkorchid_theme)
        self.theme = "darkorchid"
        self.update_api_connection_status()
        self.set_interval(10, self.update_api_connection_status)
        backup_paths = FileManager.get_source_paths_from_backups()
        if backup_paths:
            self.push_screen(SelectPathsDialog(backup_paths), self.on_select_paths_dialog_result)

    @work(exclusive=True, thread=True)
    def update_api_connection_status(self) -> None:
        self._api_connection_status = self.call_from_thread(bool_to_api_status, self._api_service.is_api_reachable())

    def on_yes_no_dialog_result(self, result: bool | None) -> None:
        if result:
            self.exit()

    def on_select_paths_dialog_result(self, result: Path | None):
        self._pre_selected_path = result

    def action_request_quit(self) -> None:
        self.push_screen(YesNoDialogScreen(dialog_prompt="Do you really want to quit?"), self.on_yes_no_dialog_result)