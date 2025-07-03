import os

from pydantic import TypeAdapter, validate_call


@validate_call
def handle_bool_input(input_string: str) -> bool:
    while True:
        print(input_string)
        try:
            result = TypeAdapter(bool).validate_python(input("[yes/no] "))
            print("")
            return result
        except ValueError:
            os.system("cls")
            print("Please enter yes/no")