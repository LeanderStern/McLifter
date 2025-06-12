import os

from pydantic import TypeAdapter


def handle_bool_input(input_string: str) -> bool:
    while True:
        print(input_string)
        try:
            return TypeAdapter(bool).validate_python(input("[yes/no]"))
        except ValueError:
            os.system("cls")
            print("Please enter yes/no")