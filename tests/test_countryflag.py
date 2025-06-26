import os
from cli_test_helpers import ArgvContext, shell
from src.countryflag.utils.text import norm_newlines

from src import countryflag


def test_runas_module():
    """Can this package be run as a Python module?"""
    result = shell("python3 -m countryflag --help")
    assert result.exit_code == 0


def test_module_singlecountry():
    """Tests the Python module output"""
    expected = "🇫🇷"
    result = countryflag.getflag(["France"])
    assert result == expected, "Output doesn't match with input countries!"


def test_module_multiplecountries():
    """Tests the Python module output"""
    expected = "🇫🇷 🇧🇪 🇯🇵 🇺🇸"
    result = countryflag.getflag(
        ["France", "Belgium", "JP", "United States of America"]
    )
    assert result == expected, "Output doesn't match with input countries!"


def test_entrypoint():
    """Is entrypoint script installed? (setup.py)"""
    # On Windows, probe both countryflag and countryflag.exe
    commands_to_try = ["countryflag"]
    if os.name == "nt":
        commands_to_try.append("countryflag.exe")
    
    success = False
    for cmd in commands_to_try:
        result = shell(f"{cmd} --help")
        if result.exit_code == 0:
            success = True
            break
    
    assert success, f"None of the commands {commands_to_try} worked successfully"


def test_example_command():
    """Is command available?"""
    # On Windows, probe both countryflag and countryflag.exe
    commands_to_try = ["countryflag"]
    if os.name == "nt":
        commands_to_try.append("countryflag.exe")
    
    success = False
    for cmd in commands_to_try:
        result = shell(f"{cmd} --countries france --help")
        if result.exit_code == 0:
            success = True
            break
    
    assert success, f"None of the commands {commands_to_try} worked successfully"


def test_cli_singlecountry():
    """Tests the command line output"""
    expected = "🇫🇷\n"
    # On Windows, probe both countryflag and countryflag.exe
    commands_to_try = ["countryflag"]
    if os.name == "nt":
        commands_to_try.append("countryflag.exe")
    
    success = False
    for cmd in commands_to_try:
        result = shell(f"{cmd} --countries France")
        if result.exit_code == 0 and norm_newlines(result.stdout) == norm_newlines(expected):
            success = True
            break
    
    assert success, f"None of the commands {commands_to_try} worked successfully"


def test_cli_multiplecountries():
    """Tests the command line output"""
    expected = "🇫🇷 🇧🇪 🇯🇵 🇺🇸\n"
    # On Windows, probe both countryflag and countryflag.exe
    commands_to_try = ["countryflag"]
    if os.name == "nt":
        commands_to_try.append("countryflag.exe")
    
    success = False
    for cmd in commands_to_try:
        result = shell(
            f'{cmd} --countries France Belgium JP "United States of America"'
        )
        if result.exit_code == 0 and norm_newlines(result.stdout) == norm_newlines(expected):
            success = True
            break
    
    assert success, f"None of the commands {commands_to_try} worked successfully"


def test_cli_notfound():
    """Tests the error message when a country is not found in regex"""
    expected = "Error: Country not found: nonexistentcountry\n\nUse --list-countries to see all supported country names\n"
    # On Windows, probe both countryflag and countryflag.exe
    commands_to_try = ["countryflag"]
    if os.name == "nt":
        commands_to_try.append("countryflag.exe")
    
    success = False
    for cmd in commands_to_try:
        result = shell(f"{cmd} --countries nonexistentcountry")
        if norm_newlines(result.stdout) == norm_newlines(expected):
            success = True
            break
    
    assert success, f"None of the commands {commands_to_try} worked successfully"
