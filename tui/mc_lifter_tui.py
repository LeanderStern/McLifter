from enum import Enum, IntEnum, StrEnum
from pathlib import Path
from typing import List, Tuple

from pydantic import validate_call
from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Footer, Label, DirectoryTree, TabbedContent, TabPane
from textual.widgets._option_list import Option

from api_service.api_service import ApiService
from constraints import DirectoryPath
from file_manager.file_manager import FileManager
from tui.dialogs.select_paths_dialog.select_paths_dialog import SelectOptionDialog
from tui.dialogs.yes_no_dialog.yes_no_dialog import YesNoDialog
from tui.theme import darkorchid_theme
from utils.shorten_path import shorten_path


def bool_to_api_status(status: bool) -> Text:
    string = Text("Api Connection: ")
    if status:
        string.append("⏺", "bold green")
    else:
        string.append("⏺", "bold red")
    return string

class ActionBindingEnum(StrEnum):
    REQUEST_QUIT = "request_quit"
    PREVIOUS = "previous"
    NEXT = "next"
    SELECT_STANDARD_PATH = "select_standard_path"

class Header(Label):
    _api_connection_status: reactive[Text] = reactive(bool_to_api_status(False))

    def render(self) -> Text:
        return self._api_connection_status

class McLifterTui(App):
    CSS_PATH = "style.tcss"
    BINDINGS = [
        ("q", ActionBindingEnum.REQUEST_QUIT, "Quit McLifter"),
        ("a", ActionBindingEnum.PREVIOUS, "Previous tab"),
        ("d", ActionBindingEnum.NEXT, "Next tab"),
        ("f", ActionBindingEnum.SELECT_STANDARD_PATH, "Select standard minecraft path"),
    ]

    _api_service: ApiService
    _file_manager_reference: type[FileManager]
    _api_connection_status: reactive[Text] = reactive(bool_to_api_status(False))
    _tabbed_content = TabbedContent()
    _directory_tree: DirectoryTree = DirectoryTree("")
    _tabs: List[TabPane] = []

    def __init__(self, api_service: ApiService, file_manager_reference: type[FileManager]) -> None:
        self._api_service = api_service
        self._file_manager_reference = file_manager_reference
        super().__init__()

    def compose(self) -> ComposeResult:
        with Container(id="app-container") as container:
            container.border_title = "McLifter"
            container.border_subtitle = "1.0.0"
            yield Header().data_bind(McLifterTui._api_connection_status)
            with self._tabbed_content:
                with TabPane(title="Mod Folder") as mod_folder_tab:
                    self._tabs.append(mod_folder_tab)
                    with VerticalScroll():
                        yield self._directory_tree
                with TabPane(title="Select Mods", disabled=True) as select_mods_tab:
                    self._tabs.append(select_mods_tab)
                with TabPane(title="Overview", disabled=True) as overview_tab:
                    self._tabs.append(overview_tab)
            yield Footer()

    def on_mount(self) -> None:
        self.register_theme(darkorchid_theme)
        self.theme = "darkorchid"
        self.update_api_connection_status()
        self.set_interval(10, self.update_api_connection_status)
        self.prompt_for_prefill_path()

    @work(exclusive=True, thread=True)
    def update_api_connection_status(self) -> None:
        self._api_connection_status = self.call_from_thread(bool_to_api_status, self._api_service.is_api_reachable())

    def on_yes_no_dialog_result(self, result: bool | None) -> None:
        if result:
            self.exit()

    def on_select_paths_dialog_result(self, result: Option | None):
        if result and result.id is not None:
            self._directory_tree.path = Path(result.id)

    def action_request_quit(self) -> None:
        self.push_screen(YesNoDialog(dialog_prompt="Do you really want to quit?"), self.on_yes_no_dialog_result)

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        match action:
            case ActionBindingEnum.SELECT_STANDARD_PATH:
                if self._tabbed_content.active == self._tabs[0].id:
                    return False
            case _:
                return True
        return True

    def action_next(self) -> None:
        self.step_tabs(1)

    def action_previous(self) -> None:
        self.step_tabs(-1)

    @validate_call()
    def step_tabs(self, steps: int) -> None:
        active_tab_index = self.find_active_tab_index()
        if active_tab_index is None:
            raise ValueError("No active tab found")
        next_tab_index = (active_tab_index + steps) % self._tabbed_content.tab_count
        next_tab = self._tabs[next_tab_index]
        if next_tab.disabled:
            return
        next_tab_id = next_tab.id
        if next_tab_id is None:
            # should not happen because tabs should always have an id
            raise ValueError("Tab Pane doesnt have id")
        self._tabbed_content.active = next_tab_id

    def prompt_for_prefill_path(self) -> None:
        backup_paths = FileManager.get_source_paths_from_backups()
        if backup_paths is None:
            return
        unique_paths: set[Path] = set(backup_paths)
        styled_unique_options = []
        for path in unique_paths:
            styled_option = self.get_styled_option_from_mod_folder_path(path)
            if styled_option:
                styled_unique_options.append(styled_option)
        if len(styled_unique_options) > 0:
            self.push_screen(SelectOptionDialog(styled_unique_options, True), self.on_select_paths_dialog_result)

    def find_active_tab_index(self) -> int | None:
        for i, tab in enumerate(self._tabs):
            if tab.id == self._tabbed_content.active:
                return i
        return None

    @validate_call
    def get_styled_option_from_mod_folder_path(self, path: DirectoryPath, max_jars: int = 2) -> Option | None:
        entries: List[Path] = list(path.iterdir())
        jars: List[Path] = [file for file in entries if file.suffix == ".jar"]
        if len(jars) <= 0:
            return None
        remaining = len(jars) - max_jars

        tree = Tree(f"📁[dim]{path.name}[/]", guide_style=darkorchid_theme.background)
        for i, jar in enumerate(jars):
            if i + 1 <= max_jars or remaining <= 1:
                row = Table.grid()
                row.add_column(vertical="middle")
                row.add_column(vertical="middle")
                row.add_row("☕\ufe0f", Text(jar.name))

                tree.add(row)
            else:
                tree.add(f"[dim italic]… +{len(jars) - i} more mods[/]")
                break

        abs_path: Path = path.resolve()
        short_abs_path: str = shorten_path(path.resolve())

        panel = Panel(
            tree,
            title=f"[bold]{short_abs_path}[/]",
            title_align="center",
            subtitle_align="center",
            border_style="white",
        )
        return Option(prompt=panel, id=str(abs_path))