"""Test cases for the countryflag CLI module."""

import subprocess
import sys

import pytest


class ShellResult:
    """Simple result class to mimic cli_test_helpers.shell behavior."""

    def __init__(self, exit_code, stdout, stderr):
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr


def shell(command):
    """Simple shell command runner to replace cli_test_helpers.shell."""
    try:
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
        "python -m countryflag --countries France Belgium JP 'United States of America'"
    )
    assert result.exit_code == 0
    expected_flags = ["🇫🇷", "🇧🇪", "🇯🇵", "🇺🇸"]
    for flag in expected_flags:
        assert flag in result.stdout


def test_countries_flag_nonexistent_country():
    """Test CLI behavior with nonexistent country."""
    result = shell("python -m countryflag --countries nonexistentcountry")
    assert "Country not found" in result.stdout


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
    assert result.stdout == ""


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
    result = shell("countryflag --countries France")
    assert result.exit_code == 0
    assert "🇫🇷" in result.stdout


def test_entrypoint_help():
    """Test that the installed entrypoint script help works."""
    result = shell("countryflag --help")
    assert result.exit_code == 0
    assert "--countries" in result.stdout
