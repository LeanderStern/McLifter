import os

from pydantic import validate_call
from semantic_version import Version, validate


@validate_call
def handle_minecraft_version_input(input_string: str) -> Version:
    while True:
        version = input(input_string + " ")
        if validate(version):
            return Version(version)
        os.system("cls")
        print("please enter valid minecraft version")