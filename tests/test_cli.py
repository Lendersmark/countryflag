"""Test cases for the countryflag CLI module."""

import os
import subprocess
import sys

import pytest

from src.countryflag.core.flag import CountryFlag
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
    assert "Country not found" in result.stderr


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


def test_precedence_rules_positional_ignored_when_flags_provided():
    """Regression test: positional args must be ignored if any mutually-exclusive flag is provided."""
    # Test with --countries flag and positional args - positional should be ignored
    result = shell(
        'python -c "from src.countryflag.cli.main import main; main()" Germany --countries France'
    )
    assert result.exit_code == 0
    assert "🇫🇷" in result.stdout  # Only France should be processed
    assert "🇩🇪" not in result.stdout  # Germany (positional) should be ignored

    # Test with --reverse flag and positional args - positional should be ignored
    result = shell(
        'python -c "from src.countryflag.cli.main import main; main()" Germany --reverse 🇫🇷'
    )
    assert result.exit_code == 0
    assert "France" in result.stdout  # Reverse lookup should work
    assert "🇩🇪" not in result.stdout  # Germany (positional) should be ignored

    # Test with --region flag and positional args - positional should be ignored
    # Note: Testing that positional args are ignored, not the region functionality itself
    # Use Japan (not in Europe) to avoid false positive matches
    result = shell(
        'python -c "from src.countryflag.cli.main import main; main()" Japan --region Europe'
    )
    assert result.exit_code == 0
    # The key test is that Japan (positional) is ignored, not what region outputs
    assert "🇯🇵" not in result.stdout  # Japan (positional) should be ignored

    # Test with --file flag and positional args - positional should be ignored
    # Note: We'll create a temporary file for this test
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("France\n")
        temp_file = f.name

    try:
        result = shell(
            f'python -c "from src.countryflag.cli.main import main; main()" Germany --file {temp_file}'
        )
        assert result.exit_code == 0
        assert "🇫🇷" in result.stdout  # File content should be processed
        assert "🇩🇪" not in result.stdout  # Germany (positional) should be ignored
    finally:
        os.unlink(temp_file)


def test_precedence_rules_positional_used_when_no_flags():
    """Test that positional args are used when no mutually-exclusive flags are provided."""
    # Test with only positional args - should be processed
    result = shell(
        'python -c "from src.countryflag.cli.main import main; main()" Germany France'
    )
    assert result.exit_code == 0
    assert "🇩🇪" in result.stdout
    assert "🇫🇷" in result.stdout

    # Test with positional args and non-mutually-exclusive flags - should work
    result = shell(
        'python -c "from src.countryflag.cli.main import main; main()" Germany --format json'
    )
    assert result.exit_code == 0
    assert (
        "🇩🇪" in result.stdout or '"flag"' in result.stdout
    )  # JSON format or flag present


def test_no_arguments_provided():
    """Test CLI behavior when no arguments are provided."""
    result = shell("python -m countryflag")
    # CLI exits cleanly and shows helpful usage message when no args provided
    assert result.exit_code == 0
    
    # Check that the help message is displayed
    expected_content = [
        "CountryFlag: Convert country names to emoji flags",
        "Usage examples:",
        "countryflag italy france spain",
        "countryflag --countries italy france spain",
        "countryflag --reverse",
        "countryflag --region Europe",
        "countryflag --interactive",
        "countryflag --list-countries",
        "countryflag --help",
        "For more options, use: countryflag --help"
    ]
    
    # Verify all expected content is present
    for content in expected_content:
        assert content in result.stdout, f"Expected '{content}' in output: {result.stdout}"


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


# Parametrized tests for positional arguments
@pytest.mark.parametrize(
    "invocation_style,countries,expected_flags",
    [
        # Single country success cases
        ("positional", ["Germany"], ["🇩🇪"]),
        ("named", ["Germany"], ["🇩🇪"]),
        ("positional", ["France"], ["🇫🇷"]),
        ("named", ["France"], ["🇫🇷"]),
        ("positional", ["JP"], ["🇯🇵"]),  # ISO code
        ("named", ["JP"], ["🇯🇵"]),  # ISO code
        # Multiple countries success cases
        ("positional", ["Germany", "France"], ["🇩🇪", "🇫🇷"]),
        ("named", ["Germany", "France"], ["🇩🇪", "🇫🇷"]),
        ("positional", ["Italy", "Spain", "Portugal"], ["🇮🇹", "🇪🇸", "🇵🇹"]),
        ("named", ["Italy", "Spain", "Portugal"], ["🇮🇹", "🇪🇸", "🇵🇹"]),
        # Multi-word country names
        ("positional", ["United States of America"], ["🇺🇸"]),
        ("named", ["United States of America"], ["🇺🇸"]),
        ("positional", ["United Kingdom"], ["🇬🇧"]),
        ("named", ["United Kingdom"], ["🇬🇧"]),
        # Mixed cases
        ("positional", ["germany"], ["🇩🇪"]),  # lowercase
        ("named", ["germany"], ["🇩🇪"]),  # lowercase
        ("positional", ["FRANCE"], ["🇫🇷"]),  # uppercase
        ("named", ["FRANCE"], ["🇫🇷"]),  # uppercase
    ],
)
def test_positional_args_success_cases(invocation_style, countries, expected_flags):
    """Test successful positional argument handling with both invocation styles."""
    if invocation_style == "positional":
        # Use positional arguments (direct CLI call)
        countries_str = " ".join(
            f'"{country}"' if " " in country else country for country in countries
        )
        command = f"python -m countryflag {countries_str}"
    else:  # named
        # Use --countries flag
        countries_str = " ".join(
            f'"{country}"' if " " in country else country for country in countries
        )
        command = f"python -m countryflag --countries {countries_str}"

    result = shell(command)
    assert result.exit_code == 0, f"Command failed: {command}\nStderr: {result.stderr}"

    # Check that all expected flags are present in output
    for flag in expected_flags:
        assert (
            flag in result.stdout
        ), f"Expected flag {flag} not found in output: {result.stdout}"


@pytest.mark.parametrize(
    "invocation_style,countries,expected_error_text,should_exit_non_zero",
    [
        # Single invalid country - these should exit with non-zero
        ("positional", ["nonexistentcountry"], "Country not found", True),
        ("named", ["nonexistentcountry"], "Country not found", True),
        ("positional", ["fakecountry"], "Country not found", True),
        ("named", ["fakecountry"], "Country not found", True),
        # Mixed valid and invalid countries - these continue processing and exit with 0
        ("positional", ["Germany", "nonexistentcountry"], "Country not found", False),
        ("named", ["Germany", "nonexistentcountry"], "Country not found", False),
        ("positional", ["invalidcountry", "France"], "Country not found", False),
        ("named", ["invalidcountry", "France"], "Country not found", False),
        # Empty string - should now raise an error
        ("positional", ["''"], "country names cannot be empty", True),
        ("named", ["''"], "country names cannot be empty", True),
        # Invalid characters/symbols
        ("positional", ["@#$%"], "Country not found", True),
        ("named", ["@#$%"], "Country not found", True),
    ],
)
def test_positional_args_error_cases(
    invocation_style, countries, expected_error_text, should_exit_non_zero
):
    """Test error handling for invalid positional arguments with both invocation styles."""
    if invocation_style == "positional":
        # Use positional arguments (direct CLI call)
        countries_str = " ".join(countries)
        command = f"python -m countryflag {countries_str}"
    else:  # named
        # Use --countries flag
        countries_str = " ".join(countries)
        command = f"python -m countryflag --countries {countries_str}"

    result = shell(command)

    # Check exit code based on expected behavior
    if should_exit_non_zero:
        assert (
            result.exit_code != 0
        ), f"Command should have failed but didn't: {command}"
    else:
        # For mixed cases, CLI continues processing and exits with 0
        assert (
            result.exit_code == 0
        ), f"Command failed unexpectedly: {command}\nStderr: {result.stderr}"

    # Check that error message is present in output (either stdout or stderr)
    error_output = result.stdout + result.stderr
    assert (
        expected_error_text in error_output
    ), f"Expected error text '{expected_error_text}' not found in output: {error_output}"


@pytest.mark.parametrize(
    "invocation_style,format_type,countries,expected_format",
    [
        # JSON output format
        ("positional", "json", ["Germany"], "json"),
        ("named", "json", ["Germany"], "json"),
        ("positional", "json", ["France", "Italy"], "json"),
        ("named", "json", ["France", "Italy"], "json"),
        # CSV output format
        ("positional", "csv", ["Germany"], "csv"),
        ("named", "csv", ["Germany"], "csv"),
        ("positional", "csv", ["Spain", "Portugal"], "csv"),
        ("named", "csv", ["Spain", "Portugal"], "csv"),
        # Text output format (default)
        ("positional", "text", ["Japan"], "text"),
        ("named", "text", ["Japan"], "text"),
        ("positional", "text", ["China", "India"], "text"),
        ("named", "text", ["China", "India"], "text"),
    ],
)
def test_positional_args_output_formats(
    invocation_style, format_type, countries, expected_format
):
    """Test positional arguments with different output formats."""
    if invocation_style == "positional":
        # Use positional arguments
        countries_str = " ".join(
            f'"{country}"' if " " in country else country for country in countries
        )
        command = f"python -m countryflag {countries_str} --format {format_type}"
    else:  # named
        # Use --countries flag
        countries_str = " ".join(
            f'"{country}"' if " " in country else country for country in countries
        )
        command = (
            f"python -m countryflag --countries {countries_str} --format {format_type}"
        )

    result = shell(command)
    assert result.exit_code == 0, f"Command failed: {command}\nStderr: {result.stderr}"

    if expected_format == "json":
        # Should be valid JSON
        try:
            import json

            json.loads(result.stdout)
        except json.JSONDecodeError:
            pytest.fail(f"Output is not valid JSON: {result.stdout}")
    elif expected_format == "csv":
        # Should contain CSV headers
        assert (
            "Country,Flag" in result.stdout or "Flag,Country" in result.stdout
        ), f"CSV headers not found: {result.stdout}"
    elif expected_format == "text":
        # Should contain flag emojis (default text format)
        flag_pattern = r"[🇦-🇿]{2}"  # Unicode flag pattern
        import re

        assert re.search(
            flag_pattern, result.stdout
        ), f"No flag emojis found in text output: {result.stdout}"


@pytest.mark.parametrize(
    "mutually_exclusive_flag,flag_args,positional_args",
    [
        # Test with --countries flag
        ("--countries", ["Belgium"], ["Germany"]),
        ("--countries", ["Netherlands", "Austria"], ["France", "Italy"]),
        # Test with --reverse flag
        ("--reverse", ["🇩🇪"], ["France"]),
        ("--reverse", ["🇫🇷", "🇮🇹"], ["Germany", "Spain"]),
        # Test with --region flag
        ("--region", ["Europe"], ["Japan"]),
        ("--region", ["Asia"], ["Germany", "France"]),
    ],
)
def test_positional_args_precedence_with_flags(
    mutually_exclusive_flag, flag_args, positional_args
):
    """Test that positional arguments are correctly ignored when mutually exclusive flags are present."""
    # Build command with both positional args and mutually exclusive flag
    positional_str = " ".join(positional_args)
    flag_args_str = " ".join(flag_args)

    command = f'python -c "from src.countryflag.cli.main import main; main()" {positional_str} {mutually_exclusive_flag} {flag_args_str}'

    result = shell(command)
    assert result.exit_code == 0, f"Command failed: {command}\nStderr: {result.stderr}"

    # Positional arguments should be ignored, so their flags should NOT appear in output
    if mutually_exclusive_flag == "--countries":
        # For --countries, check that flag args produce output but positional don't
        country_flag = CountryFlag()
        for country in flag_args:
            flag, _ = country_flag.get_flag([country])
            assert flag in result.stdout, f"Expected flag for {country} not found"

        # Positional args should be ignored
        for country in positional_args:
            flag, _ = country_flag.get_flag([country])
            assert (
                flag not in result.stdout
            ), f"Positional arg {country} flag should be ignored but found in output"

    elif mutually_exclusive_flag == "--reverse":
        # For --reverse, check that reverse lookup works
        for country in flag_args:
            # flag_args contains flag emojis, output should contain country names
            assert (
                len(result.stdout.strip()) > 0
            ), "Reverse lookup should produce output"

        # Positional country names should not appear as flags
        country_flag = CountryFlag()
        for country in positional_args:
            flag, _ = country_flag.get_flag([country])
            assert (
                flag not in result.stdout
            ), f"Positional arg {country} flag should be ignored"

    elif mutually_exclusive_flag == "--region":
        # For --region, the key test is that positional args are ignored
        # (the region functionality itself may not work, but that's not what we're testing)
        # The important thing is that positional flags don't appear in the output
        country_flag = CountryFlag()
        for country in positional_args:
            flag, _ = country_flag.get_flag([country])
            assert (
                flag not in result.stdout
            ), f"Positional arg {country} flag should be ignored but found in output"


def test_empty_positional_args():
    """Test behavior with empty positional arguments."""
    # Test with no arguments at all - should show help message
    result = shell("python -m countryflag")
    assert result.exit_code == 0
    assert "CountryFlag: Convert country names to emoji flags" in result.stdout
    assert "Usage examples:" in result.stdout

    # Test with only whitespace (empty string)
    result = shell("python -m countryflag ''")
    # Empty string should now produce an error and exit with 1
    assert result.exit_code == 1
    assert "country names cannot be empty" in result.stderr


def test_no_arguments_help_message_content():
    """Test that the no-arguments help message contains all expected examples."""
    result = shell("python -m countryflag")
    assert result.exit_code == 0
    
    # Check specific examples are included
    expected_examples = [
        "countryflag italy france spain",
        "countryflag --countries italy france spain", 
        "countryflag --reverse",
        "countryflag --region Europe",
        "countryflag --interactive",
        "countryflag --list-countries",
        "countryflag --help"
    ]
    
    for example in expected_examples:
        assert example in result.stdout, f"Expected example '{example}' not found in help message"
        
    # Ensure the help message ends with the "For more options" line
    assert "For more options, use: countryflag --help" in result.stdout


def test_no_arguments_vs_help_flag():
    """Test that no-arguments help is different from --help flag."""
    # Get output from no arguments
    no_args_result = shell("python -m countryflag")
    assert no_args_result.exit_code == 0
    
    # Get output from --help flag
    help_result = shell("python -m countryflag --help")
    assert help_result.exit_code == 0
    
    # The outputs should be different - help should be more comprehensive
    assert no_args_result.stdout != help_result.stdout
    
    # No-args should be shorter and more focused
    assert len(no_args_result.stdout) < len(help_result.stdout)
    
    # Help should contain argparse-generated content that no-args doesn't
    assert "optional arguments:" in help_result.stdout.lower() or "options:" in help_result.stdout.lower()
    assert "optional arguments:" not in no_args_result.stdout.lower() and "options:" not in no_args_result.stdout.lower()


def test_no_arguments_entrypoint():
    """Test that the installed entrypoint also shows help message with no arguments."""
    # Test both possible command names on different platforms
    commands_to_try = ["countryflag"]
    if os.name == "nt":
        commands_to_try.append("countryflag.exe")
    
    success = False
    for cmd in commands_to_try:
        result = shell(cmd)
        if result.exit_code == 0 and "CountryFlag: Convert country names to emoji flags" in result.stdout:
            success = True
            # Verify it contains usage examples
            assert "Usage examples:" in result.stdout
            assert "countryflag italy france spain" in result.stdout
            break
    
    assert success, f"None of the commands {commands_to_try} showed the expected help message"
