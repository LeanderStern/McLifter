import os
import re

def handle_minecraft_version_input(input_string) -> str:
    minecraft_version_pattern = re.compile(r'^(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:\.(?:0|[1-9]\d*))?$')
    while True:
        version = input(input_string)
        if minecraft_version_pattern.match(version):
            return version
        else:
            os.system("cls")
            print("please enter valid minecraft version")