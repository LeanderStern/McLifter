import os

from packaging.version import Version
from pydantic import TypeAdapter

from constraints import MinecraftVersion


def handle_semantic_version_input(input_string) -> Version:
    while True:
        try:
            version = input(input_string)
            verified_version = TypeAdapter(MinecraftVersion).validate_python(version)
            return Version(verified_version)
        except ValueError:
            os.system("cls")
            print("please enter valid minecraft version")