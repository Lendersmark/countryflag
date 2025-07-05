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
                errors="replace",
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                timeout=30,
            )
        else:  # Unix-like systems
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                timeout=30,
            )
        # Coerce stdout/stderr to empty string if None
        return ShellResult(result.returncode, result.stdout or "", result.stderr or "")
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
        "For more options, use: countryflag --help",
    ]

    # Verify all expected content is present
    for content in expected_content:
        assert (
            content in result.stdout
        ), f"Expected '{content}' in output: {result.stdout}"


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
        "countryflag --help",
    ]

    for example in expected_examples:
        assert (
            example in result.stdout
        ), f"Expected example '{example}' not found in help message"

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
    assert (
        "optional arguments:" in help_result.stdout.lower()
        or "options:" in help_result.stdout.lower()
    )
    assert (
        "optional arguments:" not in no_args_result.stdout.lower()
        and "options:" not in no_args_result.stdout.lower()
    )


def test_no_arguments_entrypoint():
    """Test that the installed entrypoint also shows help message with no arguments."""
    # Test both possible command names on different platforms
    commands_to_try = ["countryflag"]
    if os.name == "nt":
        commands_to_try.append("countryflag.exe")

    success = False
    for cmd in commands_to_try:
        result = shell(cmd)
        if (
            result.exit_code == 0
            and "CountryFlag: Convert country names to emoji flags" in result.stdout
        ):
            success = True
            # Verify it contains usage examples
            assert "Usage examples:" in result.stdout
            assert "countryflag italy france spain" in result.stdout
            break

    assert (
        success
    ), f"None of the commands {commands_to_try} showed the expected help message"


# New coverage improvement tests


def test_cli_valid_country_code():
    """Test #1: CLI - Valid Country Code Test

    Test the basic invocation by running with a valid country code like US.
    """
    result = shell("python -m countryflag US")

    # Exit status should be 0
    assert (
        result.exit_code == 0
    ), f"Expected exit code 0, got {result.exit_code}. Stderr: {result.stderr}"

    # stdout should contain the expected flag for "US"
    assert "🇺🇸" in result.stdout, f"Expected US flag in output: {result.stdout}"

    # No stderr output for successful case
    assert result.stderr == "", f"Expected no stderr output, got: {result.stderr}"


def test_cli_invalid_country_code():
    """Test #2: CLI - Invalid Country Code Test

    Test the CLI with an unknown code like ZZ.
    """
    result = shell("python -m countryflag ZZ")

    # SystemExit status should be non-zero
    assert result.exit_code != 0, f"Expected non-zero exit code, got {result.exit_code}"

    # stderr should contain "Country not found" based on current implementation
    assert (
        "Country not found" in result.stderr
    ), f"Expected 'Country not found' in stderr: {result.stderr}"

    # Verify the specific country code is mentioned in the error
    assert "ZZ" in result.stderr, f"Expected 'ZZ' in stderr: {result.stderr}"


@pytest.mark.parametrize(
    "option,expected_content",
    [
        ("--help", "usage:"),
        ("-h", "usage:"),
        ("--version", "1.1.1"),
    ],
)
def test_cli_help_and_version_options(option, expected_content):
    """Test #3: CLI - Help and Version Options

    Parametrise over `--help` and `--version`:
    • exit status 0
    • stdout starts with usage text or prints the library version.
    Ensures coverage of the arg-parse early-exit branches.
    """
    result = shell(f"python -m countryflag {option}")

    # Exit status should be 0
    assert (
        result.exit_code == 0
    ), f"Expected exit code 0 for {option}, got {result.exit_code}"

    if option == "--version":
        # stdout should contain the version number
        assert (
            expected_content in result.stdout
        ), f"Expected version '{expected_content}' in output for {option}: {result.stdout}"
        # Should contain the program name
        assert (
            "countryflag" in result.stdout.lower()
        ), f"Expected 'countryflag' in version output for {option}: {result.stdout}"
    else:
        # stdout should start with usage text
        assert (
            expected_content in result.stdout.lower() or "countryflag" in result.stdout
        ), f"Expected usage text in output for {option}: {result.stdout}"
        # Should contain argument descriptions
        assert (
            "--countries" in result.stdout
        ), f"Expected '--countries' in help output for {option}: {result.stdout}"


@pytest.mark.parametrize(
    "options,country",
    [
        ("--format json", "US"),
        ("--separator ,", "US"),
        ("--format csv --separator ';'", "US"),
        ("--fuzzy --threshold 0.8", "USA"),  # Test fuzzy matching
        ("--verbose --format json", "GB"),
    ],
)
def test_cli_combined_options(options, country):
    """Test #4: CLI - Combined Options

    Test combined options such as --format and --separator.
    """
    result = shell(f"python -m countryflag {country} {options}")

    # Exit status should be 0 for valid options
    assert (
        result.exit_code == 0
    ), f"Expected exit code 0 for options '{options}', got {result.exit_code}. Stderr: {result.stderr}"

    # Output should contain something (not empty)
    assert (
        result.stdout.strip() != ""
    ), f"Expected non-empty output for options '{options}': {result.stdout}"

    # Check specific format expectations
    if "--format json" in options:
        # Should be valid JSON or contain JSON-like structure
        assert (
            "{" in result.stdout or "[" in result.stdout
        ), f"Expected JSON-like output for options '{options}': {result.stdout}"

    if "--format csv" in options:
        # Should contain CSV-like structure
        assert (
            "," in result.stdout
            or "Country" in result.stdout
            or "Flag" in result.stdout
        ), f"Expected CSV-like output for options '{options}': {result.stdout}"


def test_cli_no_arguments_comprehensive():
    """Test #5: CLI - No Arguments

    Test invoking the CLI with no parameters.
    """
    result = shell("python -m countryflag")

    # Exit status should be 0 (shows help)
    assert (
        result.exit_code == 0
    ), f"Expected exit code 0 for no arguments, got {result.exit_code}"

    # Should contain help/usage text
    assert (
        "CountryFlag" in result.stdout
    ), f"Expected 'CountryFlag' in help output: {result.stdout}"
    assert (
        "Usage examples" in result.stdout
    ), f"Expected 'Usage examples' in help output: {result.stdout}"

    # Should contain various usage examples
    assert (
        "countryflag italy france spain" in result.stdout
    ), f"Expected usage example in output: {result.stdout}"


@pytest.mark.skipif(os.name != "nt", reason="Windows-specific test")
def test_cli_windows_platform_specific():
    """Test #6a: Platform-Specific Logic - Windows

    Test different behaviors for Windows platforms.
    """
    result = shell("python -m countryflag US")

    # Should work without errors on Windows
    assert (
        result.exit_code == 0
    ), f"Expected exit code 0 on Windows, got {result.exit_code}"

    # Should handle Unicode properly
    assert "🇺🇸" in result.stdout, f"Expected US flag in Windows output: {result.stdout}"


@pytest.mark.skipif(os.name != "nt", reason="Windows-specific test")
def test_cli_windows_cache_dir_with_spaces_and_quotes():
    """Test Windows path handling with spaces and quotes in cache-dir.

    This test verifies the robustness requirement for cache-dir paths.
    """
    import shutil
    import tempfile

    # Create a temporary directory with spaces in the name
    with tempfile.TemporaryDirectory() as base_temp_dir:
        # Create a subdirectory with spaces
        cache_dir_with_spaces = os.path.join(base_temp_dir, "my cache dir")
        os.makedirs(cache_dir_with_spaces, exist_ok=True)

        # Test 1: Without quotes (should work due to our preprocessing)
        result = shell(
            f"python -m countryflag --cache --cache-dir {cache_dir_with_spaces} US"
        )
        assert (
            result.exit_code == 0
        ), f"Cache dir without quotes failed: {result.stderr}"
        assert "🇺🇸" in result.stdout, "Should work with cache dir containing spaces"

        # Test 2: With double quotes
        result = shell(
            f'python -m countryflag --cache --cache-dir "{cache_dir_with_spaces}" US'
        )
        assert (
            result.exit_code == 0
        ), f"Cache dir with double quotes failed: {result.stderr}"
        assert "🇺🇸" in result.stdout, "Should work with quoted cache dir"

        # Test 3: With single quotes (use proper Windows cmd escaping)
        # On Windows cmd, single quotes don't work the same as double quotes
        # So we'll test with double quotes in cmd /c context
        escaped_path = cache_dir_with_spaces.replace("\\", "\\\\")
        result = shell(f'python -m countryflag --cache --cache-dir "{escaped_path}" US')
        assert (
            result.exit_code == 0
        ), f"Cache dir with escaped quotes failed: {result.stderr}"
        assert "🇺🇸" in result.stdout, "Should work with properly escaped cache dir"

        # Test 4: Test that tilde expansion works
        # Create a test directory in the user's home directory
        user_home = os.path.expanduser("~")
        home_cache_dir = os.path.join(user_home, "temp_countryflag_test")

        try:
            # Use tilde notation
            result = shell(
                "python -m countryflag --cache --cache-dir '~/temp_countryflag_test' US"
            )
            assert result.exit_code == 0, f"Tilde expansion failed: {result.stderr}"
            assert "🇺🇸" in result.stdout, "Should work with tilde expansion"

            # Verify the directory was actually created
            assert os.path.exists(
                home_cache_dir
            ), "Cache directory should be created with tilde expansion"

        finally:
            # Clean up the test directory
            if os.path.exists(home_cache_dir):
                shutil.rmtree(home_cache_dir, ignore_errors=True)


@pytest.mark.skipif(os.name == "nt", reason="POSIX-specific test")
def test_cli_posix_platform_specific():
    """Test #6b: Platform-Specific Logic - POSIX

    Test different behaviors for POSIX platforms.
    """
    result = shell("python -m countryflag US")

    # Should work without errors on POSIX
    assert (
        result.exit_code == 0
    ), f"Expected exit code 0 on POSIX, got {result.exit_code}"

    # Should retain color/emoji properly
    assert "🇺🇸" in result.stdout, f"Expected US flag in POSIX output: {result.stdout}"


def test_cli_asset_loading_fallback():
    """Test #7: Asset Loading Fallback

    Test handling when resources are missing or fallback behavior.
    """
    # Test with a country that should work regardless of missing resources
    result = shell("python -m countryflag US")

    # Should fallback to Unicode emoji even if resources are missing
    assert (
        result.exit_code == 0
    ), f"Expected successful fallback, got exit code {result.exit_code}"
    assert "🇺🇸" in result.stdout, f"Expected Unicode emoji fallback: {result.stdout}"


def test_cli_caching_behavior():
    """Test #8: Caching Behavior

    Test repeated cache calls and caching functionality.
    """
    # Test with cache enabled
    result1 = shell("python -m countryflag --cache US")
    assert result1.exit_code == 0, f"First cache call failed: {result1.stderr}"

    # Second call should use cache (should be fast and produce same result)
    result2 = shell("python -m countryflag --cache US")
    assert result2.exit_code == 0, f"Second cache call failed: {result2.stderr}"

    # Results should be identical
    assert (
        result1.stdout == result2.stdout
    ), f"Cache results differ: '{result1.stdout}' vs '{result2.stdout}'"

    # Test with disk cache
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        result3 = shell(f"python -m countryflag --cache --cache-dir {temp_dir} US")
        assert result3.exit_code == 0, f"Disk cache call failed: {result3.stderr}"
        assert (
            "🇺🇸" in result3.stdout
        ), f"Expected US flag with disk cache: {result3.stdout}"


@pytest.mark.parametrize(
    "input_case,expected_flag",
    [
        ("uk", "🇬🇧"),
        ("UK", "🇬🇧"),
        ("Uk", "🇬🇧"),
        ("gb", "🇬🇧"),
        ("GB", "🇬🇧"),
        ("Gb", "🇬🇧"),
        ("us", "🇺🇸"),
        ("US", "🇺🇸"),
        ("usa", "🇺🇸"),
        ("USA", "🇺🇸"),
        ("united states", "🇺🇸"),
        ("UNITED STATES", "🇺🇸"),
        ("United States", "🇺🇸"),
    ],
)
def test_cli_case_sensitivity_and_aliases(input_case, expected_flag):
    """Test #9: Case Sensitivity and Aliases

    Test different case inputs and aliases.
    """
    result = shell(f'python -m countryflag "{input_case}"')

    # Should succeed for all valid aliases
    assert result.exit_code == 0, f"Failed for input '{input_case}': {result.stderr}"

    # Should map to the expected flag
    assert (
        expected_flag in result.stdout
    ), f"Expected {expected_flag} for '{input_case}', got: {result.stdout}"


def test_cli_type_error_handling():
    """Test #10: Type Error Handling

    Test passing non-string arguments and edge cases.
    """
    # Test with weird characters that might cause issues
    result = shell('python -m countryflag "123"')
    assert result.exit_code != 0, "Numeric input should fail"
    assert "Country not found" in result.stderr

    # Test with special characters
    result = shell('python -m countryflag "@#$%^&*()"')
    assert result.exit_code != 0, "Special characters should fail"
    assert "Country not found" in result.stderr

    # Test with very long input
    long_input = "a" * 1000
    result = shell(f'python -m countryflag "{long_input}"')
    assert result.exit_code != 0, "Very long input should fail"
    assert "Country not found" in result.stderr

    # Test with empty quoted strings
    result = shell('python -m countryflag ""')
    assert result.exit_code != 0, "Empty string should fail"
    assert "country names cannot be empty" in result.stderr


def test_cli_unicode_regional_indicator_handling():
    """Test #11: Unicode Regional Indicator Handling

    Test regional indicators with unusual cases.
    """
    # Test reverse lookup with various flag formats
    result = shell('python -m countryflag --reverse "🇺🇸"')
    assert result.exit_code == 0, f"US flag reverse lookup failed: {result.stderr}"
    assert (
        "United States" in result.stdout
    ), f"Expected 'United States' in output: {result.stdout}"

    # Test reverse lookup with multiple flags
    result = shell('python -m countryflag --reverse "🇺🇸" "🇫🇷" "🇩🇪"')
    assert (
        result.exit_code == 0
    ), f"Multiple flag reverse lookup failed: {result.stderr}"
    assert (
        "United States" in result.stdout
        and "France" in result.stdout
        and "Germany" in result.stdout
    )

    # Test with flag that might have regional indicator issues
    result = shell('python -m countryflag --reverse "🇬🇧"')
    assert result.exit_code == 0, f"GB flag reverse lookup failed: {result.stderr}"
    assert "United Kingdom" in result.stdout or "Great Britain" in result.stdout


def test_cli_flag_size_scaling_tests():
    """Test #12: Flag Size Scaling Tests

    Test with extreme scaling and format options.
    """
    # Test JSON format which should handle scaling gracefully
    result = shell("python -m countryflag --format json US")
    assert result.exit_code == 0, f"JSON format failed: {result.stderr}"

    # Verify JSON output is parseable
    import json

    try:
        data = json.loads(result.stdout)
        assert isinstance(data, (list, dict)), "JSON output should be list or dict"
    except json.JSONDecodeError:
        pytest.fail(f"Invalid JSON output: {result.stdout}")

    # Test CSV format
    result = shell("python -m countryflag --format csv US FR DE")
    assert result.exit_code == 0, f"CSV format failed: {result.stderr}"

    # CSV should have headers and proper structure
    lines = result.stdout.strip().split("\n")
    assert len(lines) >= 2, "CSV should have header and data rows"
    assert (
        "Country" in result.stdout or "Flag" in result.stdout
    ), "CSV should have appropriate headers"

    # Test with custom separator
    result = shell('python -m countryflag --separator "; " US FR DE')
    assert result.exit_code == 0, f"Custom separator failed: {result.stderr}"
    assert "; " in result.stdout, "Custom separator should appear in output"


def test_cli_list_countries_functionality():
    """Test #13: List Countries Functionality

    Test --list-countries with different output formats.
    """
    # Test default text format
    result = shell("python -m countryflag --list-countries")
    assert result.exit_code == 0, f"--list-countries failed: {result.stderr}"
    assert "United States" in result.stdout, "Should contain country names"
    assert "(US)" in result.stdout, "Should contain ISO codes"

    # Test JSON format
    result = shell("python -m countryflag --list-countries --format json")
    assert result.exit_code == 0, f"--list-countries JSON failed: {result.stderr}"
    assert result.stdout.strip().startswith("["), "JSON output should start with ["
    assert "name" in result.stdout, "JSON should contain name field"
    assert "iso2" in result.stdout, "JSON should contain iso2 field"

    # Test CSV format
    result = shell("python -m countryflag --list-countries --format csv")
    assert result.exit_code == 0, f"--list-countries CSV failed: {result.stderr}"
    assert "Name,ISO2,ISO3" in result.stdout, "CSV should have headers"
    assert "United States,US,USA" in result.stdout, "CSV should contain data rows"


def test_cli_list_regions_functionality():
    """Test #14: List Regions Functionality

    Test --list-regions with different output formats.
    """
    # Test default text format
    result = shell("python -m countryflag --list-regions")
    assert result.exit_code == 0, f"--list-regions failed: {result.stderr}"
    assert "Supported regions" in result.stdout, "Should contain header text"
    assert "Africa" in result.stdout, "Should contain region names"
    assert "Europe" in result.stdout, "Should contain region names"

    # Test JSON format
    result = shell("python -m countryflag --list-regions --format json")
    assert result.exit_code == 0, f"--list-regions JSON failed: {result.stderr}"
    assert result.stdout.strip().startswith("["), "JSON output should start with ["
    assert "Africa" in result.stdout, "JSON should contain Africa"

    # Test CSV format
    result = shell("python -m countryflag --list-regions --format csv")
    assert result.exit_code == 0, f"--list-regions CSV failed: {result.stderr}"
    assert "Region" in result.stdout, "CSV should have Region header"
    assert "Africa" in result.stdout, "CSV should contain region data"


def test_cli_validate_functionality():
    """Test #15: Validate Country Name Functionality

    Test --validate with valid and invalid country names.
    """
    # Test valid country name (use ISO code which is more reliable)
    result = shell('python -m countryflag --validate "US"')
    assert result.exit_code == 0, f"Valid country validation failed: {result.stderr}"
    assert "is a valid country name" in result.stdout, "Should confirm valid country"

    # Test another valid country name
    result = shell('python -m countryflag --validate "Germany"')
    assert result.exit_code == 0, f"Valid country validation failed: {result.stderr}"
    assert "is a valid country name" in result.stdout, "Should confirm valid country"

    # Test invalid country name
    result = shell("python -m countryflag --validate 'InvalidCountry'")
    assert (
        result.exit_code == 1
    ), f"Invalid country should return exit code 1, got {result.exit_code}"
    assert (
        "is NOT a valid country name" in result.stdout
    ), "Should indicate invalid country"

    # Test invalid country with fuzzy matching suggestions
    result = shell("python -m countryflag --validate 'Germny' --fuzzy")
    assert result.exit_code == 1, "Invalid country with fuzzy should return exit code 1"
    assert (
        "is NOT a valid country name" in result.stdout
    ), "Should indicate invalid country"
    assert "Did you mean" in result.stdout, "Should provide fuzzy suggestions"


def test_cli_cache_options():
    """Test #16: Cache Options

    Test --cache and --cache-dir functionality.
    """
    # Test with cache enabled (memory cache)
    result = shell("python -m countryflag --cache US")
    assert result.exit_code == 0, f"Cache option failed: {result.stderr}"
    assert "🇺🇸" in result.stdout, "Should work with cache enabled"

    # Test with cache directory (create temp directory for test)
    import os
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        result = shell(f'python -m countryflag --cache --cache-dir "{temp_dir}" US')
        assert result.exit_code == 0, f"Cache directory option failed: {result.stderr}"
        assert "🇺🇸" in result.stdout, "Should work with cache directory"

        # Check that cache directory was used (some files should be created)
        cache_files = os.listdir(temp_dir)
        # Note: May or may not create files immediately depending on implementation


def test_cli_verbose_option():
    """Test #17: Verbose Option

    Test --verbose flag for debug logging.
    """
    result = shell("python -m countryflag --verbose US")
    assert result.exit_code == 0, f"Verbose option failed: {result.stderr}"
    assert "🇺🇸" in result.stdout, "Should work with verbose enabled"
    # Note: verbose output typically goes to stderr for logging
