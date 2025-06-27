"""Test cases for the countryflag CLI module."""

import os
import subprocess
import sys

import pytest

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


def test_help_displays_correctly():
    """Test that --help displays without error."""
    result = shell("python -m countryflag --help")
    assert result.exit_code == 0
    assert "--countries" in result.stdout
    # Help text shows mutually exclusive options with | separator in usage line
    assert "|" in result.stdout


def test_countries_flag_single_country():
    """Test CLI with --countries flag for a single country."""
    result = shell("python -m countryflag --countries France")
    assert result.exit_code == 0
    assert "🇫🇷" in result.stdout


def test_countries_flag_multiple_countries():
    """Test CLI with --countries flag for multiple countries."""
    result = shell(
        'python -m countryflag --countries France Belgium JP "United States of America"'
    )
    assert result.exit_code == 0
    expected_flags = ["🇫🇷", "🇧🇪", "🇯🇵", "🇺🇸"]
    for flag in expected_flags:
        assert flag in result.stdout


def test_countries_flag_nonexistent_country():
    """Test CLI behavior with nonexistent country."""
    result = shell("python -m countryflag --countries nonexistentcountry")
    assert "Country not found" in result.stdout


def test_countries_flag_windows_split():
    # Simulate the unwanted splitting: feed tokens one by one without quotes
    result = shell("python -m countryflag --countries United States of America")
    # The merge routine will reconstruct the full name
    assert "🇺🇸" in result.stdout


def test_mutually_exclusive_groups_valid():
    """Test valid mutually exclusive argument combinations."""
    # Test --countries alone
    result = shell("python -m countryflag --countries Germany")
    assert result.exit_code == 0

    # Test --file alone (if file exists)
    # Note: This test might need adjustment based on actual file existence
    # result = shell("python -m countryflag --file test_countries.txt")
    # We'll skip file test for now as we don't have a test file

    # Test --reverse alone
    result = shell("python -m countryflag --reverse 🇩🇪")
    assert result.exit_code == 0


def test_mutually_exclusive_groups_invalid():
    """Test invalid mutually exclusive argument combinations."""
    # Test --countries with --reverse (should fail)
    result = shell("python -m countryflag --countries Germany --reverse 🇩🇪")
    assert result.exit_code != 0
    assert "not allowed" in result.stderr.lower() or "error" in result.stderr.lower()


def test_no_arguments_provided():
    """Test CLI behavior when no arguments are provided."""
    result = shell("python -m countryflag")
    # CLI exits cleanly with no output when no args provided
    assert result.exit_code == 0
    assert norm_newlines(result.stdout) == norm_newlines("")


def test_interactive_mode():
    """Test interactive mode flag."""
    # Interactive mode is tricky to test, so we'll just test that the flag is recognized
    result = shell("python -m countryflag --interactive --help")
    assert result.exit_code == 0


def test_output_format_options():
    """Test different output format options."""
    result = shell("python -m countryflag --countries Germany --format json")
    assert result.exit_code == 0

    # Test with another valid format
    result = shell("python -m countryflag --countries Germany --format text")
    assert result.exit_code == 0


def test_region_filter():
    """Test region filtering."""
    # --region is mutually exclusive with --countries
    result = shell("python -m countryflag --region Europe")
    assert result.exit_code == 0

    # Test invalid combination
    result = shell("python -m countryflag --region Europe --countries Germany")
    assert result.exit_code != 0


def test_caching_options():
    """Test caching options."""
    result = shell("python -m countryflag --countries Germany --cache")
    assert result.exit_code == 0


def test_verbose_output():
    """Test verbose output option."""
    result = shell("python -m countryflag --countries Germany --verbose")
    assert result.exit_code == 0


def test_entrypoint_with_new_format():
    """Test that the installed entrypoint script works with new format."""
    # On Windows, probe both countryflag and countryflag.exe
    commands_to_try = ["countryflag"]
    if os.name == "nt":
        commands_to_try.append("countryflag.exe")

    success = False
    for cmd in commands_to_try:
        result = shell(f"{cmd} --countries France")
        if result.exit_code == 0 and "🇫🇷" in result.stdout:
            success = True
            break

    assert success, f"None of the commands {commands_to_try} worked successfully"


def test_entrypoint_help():
    """Test that the installed entrypoint script help works."""
    # On Windows, probe both countryflag and countryflag.exe
    commands_to_try = ["countryflag"]
    if os.name == "nt":
        commands_to_try.append("countryflag.exe")

    success = False
    for cmd in commands_to_try:
        result = shell(f"{cmd} --help")
        if result.exit_code == 0 and "--countries" in result.stdout:
            success = True
            break

    assert success, f"None of the commands {commands_to_try} worked successfully"
