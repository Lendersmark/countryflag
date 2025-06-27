import os
import subprocess
import sys

from src import countryflag
from src.countryflag.utils.text import norm_newlines


class ShellResult:
    """Simple result class to mimic cli_test_helpers.shell behavior."""

    def __init__(self, exit_code, stdout, stderr):
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr


def shell(command, exe=None):
    """Simple shell command runner to replace cli_test_helpers.shell.

    Args:
        command: The command string to execute
        exe: Python executable to use (defaults to sys.executable)
    """
    if exe is None:
        exe = sys.executable

    # Replace 'python' with the actual executable path
    if command.startswith("python "):
        command = exe + command[6:]  # Replace 'python' with exe
    elif command.startswith("python3 "):
        command = exe + command[7:]  # Replace 'python3' with exe

    try:
        if os.name == "nt":  # Windows
            # On Windows, explicitly use UTF-8 encoding to handle Unicode properly
            # and use cmd /c to avoid PowerShell splitting issues
            wrapped_command = f'cmd /c "chcp 65001 >nul & {command}"'
            result = subprocess.run(
                wrapped_command,
                shell=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=30,
            )
        else:  # Unix-like systems
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )
        return ShellResult(result.returncode, result.stdout, result.stderr)
    except subprocess.TimeoutExpired:
        return ShellResult(1, "", "Command timed out")
    except Exception as e:
        return ShellResult(1, "", str(e))


def test_runas_module():
    """Can this package be run as a Python module?"""
    import sys

    # Use the same Python interpreter that's running the tests
    # On Windows, python3 command often doesn't exist
    if os.name == "nt":
        # Windows: use python command or current interpreter
        result = shell("python -m countryflag --help")
    else:
        # Unix-like: try python3 first, fallback to python
        result = shell("python3 -m countryflag --help")
        if result.exit_code != 0:
            result = shell("python -m countryflag --help")
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
        if result.exit_code == 0 and norm_newlines(result.stdout) == norm_newlines(
            expected
        ):
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
        if result.exit_code == 0 and norm_newlines(result.stdout) == norm_newlines(
            expected
        ):
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
