import os

def handle_bool_input(input_string: str) -> bool:
    while True:
        print(input_string)
        match input("yes/no").lower():
            case "yes":
                return True

            case "no":
                return False

            case _:
                os.system("cls")
                print("please enter either 'yes' or 'no'")