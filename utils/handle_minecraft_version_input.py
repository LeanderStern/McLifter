import os

from packaging.version import Version
from pydantic import TypeAdapter, validate_call

from constraints import MinecraftVersion

@validate_call
def handle_minecraft_version_input(input_string: str) -> Version:
    while True:
        try:
            version = input(input_string)
            verified_version = TypeAdapter(MinecraftVersion).validate_python(version)
            return Version(verified_version)
        except ValueError:
            os.system("cls")
            print("please enter valid minecraft version")