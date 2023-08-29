from .color import Color, ResetColor
from typing import Callable

def eprint(message):
    """
    Print an error without traceback (For input verification)
    :param message: The error message to print
    :return: None
    """
    print(f"{Color(203)}{message}{ResetColor()}")
    quit(-1)

def enum_input(message: str, error_message: str, choices: dict) -> str:
    """

    :param message: The message to show to ask the input of the user.
    :param error_message: The message to show when the user didn't answer correctly the question.
    :param choices: A dictionary containing the choices -> Key: short description, value: what user should type
    :return: The value written by the user.
    """
    choices_format = "[" + ", ".join([f"{key}: {Color(34)}{value}{ResetColor()}" for key, value in choices.items()]) + "]"
    ans = input(f"{message} (Write the keyword corresponding to the task you want to execute) "
                f"{choices_format}\n> ")
    while ans not in choices.values():
        ans = input(f"{Color(203)}{error_message}{ResetColor()}\nWrite a valid keyword {choices_format}\n> ")

    return ans

def std_in(message: str, error_message: str, condition: Callable) -> str:
    """
    This function will verify that the input text satisfy the condition of verificator
    :param message: The message to display
    :param error_message: The error message to display.  (It will be followed by the message)
    :param condition: A callback that takes one string as input and returns a bool: True if ok, False otherwise.
    :return: The text entered by the user
    """
    name = input(f"{message}\n> ")
    while not condition(name):
        name = input(f"{Color(203)}{error_message}{ResetColor()}\n"
                     f"{message}\n> ")

    return name

def bool_input(message: str, default: bool = True) -> bool:
    """
    This function will verify the user input text and convert it to a boolean.
    :param message: The message to display to ask the user.
    :param default: If no entry is provided, the default is used
    :return: Whether the user entered true or false
    """
    ans = input(f"{message} [True-T-Yes-Y, False-f-No-N]>  ")
    if ans == "":
        return default
    else:
        while ans.upper() not in ["TRUE", "T", "FALSE", "F", "YES", "Y", "NO", "N"]:
            ans = input(f"{Color(203)}Wrong input!{ResetColor()}\n"
                         f"{message} [True-T-Yes-Y, False-f-No-N]>  ")

        return ans.upper().startswith("T") or ans.upper().startswith("Y")