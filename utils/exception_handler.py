from typing import Callable

from pydantic import validate_call


@validate_call
def exception_handler(func: Callable) -> Callable:
    def wrapper():
        try:
            func()
        except Exception as E:
            print(E)
            input("Press Enter to close.")
    return wrapper