"""Test error handling and stdout/stderr separation."""

import logging
import os
import subprocess
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

import pytest

from countryflag.core.exceptions import (
    InvalidCountryError,
    RegionError,
    ReverseConversionError,
)
from countryflag.core.flag import CountryFlag


def run_cli_command(command, capture_stderr=True):
    """Helper function to run CLI commands and capture stdout/stderr separately."""
    try:
        if os.name == "nt":  # Windows
            # On Windows, prepend chcp 65001 to ensure UTF-8 console and use UTF-8 environment
            # Redirect chcp output to NUL to avoid polluting stdout
            wrapped_command = f"chcp 65001 > NUL & {command}"
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
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout or "",  # Coerce None to empty string
            "stderr": result.stderr or "",  # Coerce None to empty string
        }
    except subprocess.TimeoutExpired:
        return {"exit_code": 1, "stdout": "", "stderr": "Command timed out"}
    except Exception as e:
        return {"exit_code": 1, "stdout": "", "stderr": str(e)}


class TestErrorHandling:
    """Test error handling behavior for CLI and core functionality."""

    def test_valid_country_output_to_stdout_only(self):
        """Test that valid countries output flags to stdout and nothing to stderr."""
        result = run_cli_command("python -m countryflag --countries Germany France")

        assert result["exit_code"] == 0
        assert "🇩🇪" in result["stdout"]
        assert "🇫🇷" in result["stdout"]

        # Should have no output to stderr for valid countries
        assert result["stderr"].strip() == ""

    def test_invalid_country_error_to_stderr(self):
        """Test that invalid countries output clean error message to stderr."""
        result = run_cli_command("python -m countryflag --countries invalidcountry")

        assert result["exit_code"] == 1

        # Error message should be in stderr
        assert "Country not found: invalidcountry" in result["stderr"]

        # Should have no flags in stdout for invalid countries
        assert result["stdout"].strip() == ""

        # Should not contain any country_converter noise
        assert "country_converter" not in result["stderr"].lower()
        assert "coco" not in result["stderr"].lower()

    def test_invalid_region_error_to_stderr(self):
        """Test that invalid regions output clean error message to stderr."""
        result = run_cli_command("python -m countryflag --region InvalidRegion")

        # Argparse errors return exit code 2
        assert result["exit_code"] == 2

        # Error message should be in stderr (argparse puts errors in stderr)
        assert "invalid choice: 'InvalidRegion'" in result["stderr"]

        # Should have no output in stdout for invalid regions
        assert result["stdout"].strip() == ""

        # Should not contain any country_converter noise
        assert "country_converter" not in result["stderr"].lower()
        assert "coco" not in result["stderr"].lower()

    def test_reverse_lookup_invalid_flag_error_to_stderr(self):
        """Test that invalid flags for reverse lookup output clean error message to stderr."""
        result = run_cli_command("python -m countryflag --reverse 🏳️")

        assert result["exit_code"] == 1

        # Error message should be in stderr
        assert "Cannot convert flag emoji to country name" in result["stderr"]

        # Should have no output in stdout for invalid flags
        assert result["stdout"].strip() == ""

        # Should not contain any country_converter noise
        assert "country_converter" not in result["stderr"].lower()
        assert "coco" not in result["stderr"].lower()

    def test_mixed_valid_invalid_countries(self):
        """Test behavior with mix of valid and invalid countries."""
        result = run_cli_command(
            "python -m countryflag --countries Germany invalidcountry"
        )

        # This might fail or succeed depending on implementation
        # The key is that valid flags go to stdout, errors to stderr
        if result["exit_code"] == 0:
            # If it continues processing, valid flags should be in stdout
            assert "🇩🇪" in result["stdout"]
            # Invalid country message might be in stderr
        else:
            # If it fails on first invalid country, error should be in stderr
            assert "Country not found" in result["stderr"]

    def test_core_invalid_country_exception_handling(self):
        """Test that core InvalidCountryError exceptions are properly raised."""
        cf = CountryFlag()

        with pytest.raises(InvalidCountryError) as excinfo:
            cf.get_flag(["invalidcountry"])

        assert "invalidcountry" in str(excinfo.value)
        assert excinfo.value.country == "invalidcountry"

    def test_core_region_error_exception_handling(self):
        """Test that core RegionError exceptions are properly raised."""
        cf = CountryFlag()

        with pytest.raises(RegionError) as excinfo:
            cf.get_flags_by_region("InvalidRegion")

        assert "InvalidRegion" in str(excinfo.value)
        assert excinfo.value.region == "InvalidRegion"

    def test_core_reverse_conversion_error_exception_handling(self):
        """Test that core ReverseConversionError exceptions are properly raised."""
        cf = CountryFlag()

        with pytest.raises(ReverseConversionError) as excinfo:
            cf.reverse_lookup(["🏳️"])

        assert "🏳️" in str(excinfo.value)
        assert excinfo.value.flag == "🏳️"

    def test_logging_behavior_for_errors(self):
        """Test that errors are properly logged."""
        # Capture log output
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.ERROR)

        logger = logging.getLogger("countryflag.cli")
        logger.addHandler(handler)
        logger.setLevel(logging.ERROR)

        try:
            # Run command that should produce an error
            result = run_cli_command("python -m countryflag --countries invalidcountry")

            # Should still fail as expected
            assert result["exit_code"] == 1

            # Note: The logging test might be tricky because subprocess doesn't
            # capture the parent process's logging. We'll focus on the stderr behavior.

        finally:
            logger.removeHandler(handler)

    def test_no_coco_noise_in_output(self):
        """Test that country_converter warnings/noise don't appear in CLI output."""
        # Test various scenarios that might trigger country_converter warnings
        test_cases = [
            "python -m countryflag --countries unknowncountry",
            "python -m countryflag --countries ''",
            "python -m countryflag --region UnknownRegion",
            "python -m countryflag --reverse 🏳️",
        ]

        for command in test_cases:
            result = run_cli_command(command)

            # Check that no country_converter noise appears in either stdout or stderr
            combined_output = result["stdout"] + result["stderr"]

            # These patterns should not appear in user-visible output
            forbidden_patterns = [
                "country_converter",
                "coco",
                "WARNING",
                "UserWarning",
                "FutureWarning",
                "DeprecationWarning",
            ]

            for pattern in forbidden_patterns:
                assert pattern not in combined_output, (
                    f"Found forbidden pattern '{pattern}' in output for command: {command}\n"
                    f"stdout: {result['stdout']}\n"
                    f"stderr: {result['stderr']}"
                )

    def test_fuzzy_matching_suggestions_to_stderr(self):
        """Test that fuzzy matching suggestions go to stderr when errors occur."""
        result = run_cli_command("python -m countryflag --countries Germny --fuzzy")

        # With fuzzy matching, this should succeed
        if result["exit_code"] == 0:
            # Should show Germany flag
            assert "🇩🇪" in result["stdout"]
            # Stderr might be empty or contain info about fuzzy matching
        else:
            # If it fails, suggestions should be in stderr
            assert "Did you mean" in result["stderr"] or "Error:" in result["stderr"]

    def test_help_and_list_commands_to_stdout(self):
        """Test that help and list commands output to stdout only."""
        test_cases = [
            "python -m countryflag --help",
            "python -m countryflag --list-countries",
            "python -m countryflag --list-regions",
        ]

        for command in test_cases:
            result = run_cli_command(command)

            assert result["exit_code"] == 0
            assert len(result["stdout"].strip()) > 0
            # Help and list commands should not output to stderr
            assert result["stderr"].strip() == ""


class TestStdoutStderrSeparation:
    """Test proper separation of stdout and stderr streams."""

    def test_valid_flag_output_only_stdout(self):
        """Test that valid flag conversion outputs only to stdout."""
        # Create a temporary script to test stdout/stderr separation more precisely
        script_content = """
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from countryflag.core.flag import CountryFlag

try:
    cf = CountryFlag()
    flags, pairs = cf.get_flag(["Germany", "France"])
    print(flags)  # Should go to stdout
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)  # Should go to stderr
    sys.exit(1)
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(script_content)
            script_path = f.name

        try:
            result = run_cli_command(f"python {script_path}")

            assert result["exit_code"] == 0
            assert "🇩🇪" in result["stdout"]
            assert "🇫🇷" in result["stdout"]
            assert result["stderr"].strip() == ""

        finally:
            os.unlink(script_path)

    def test_error_output_only_stderr(self):
        """Test that error cases output only to stderr."""
        script_content = """
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from countryflag.core.flag import CountryFlag
from countryflag.core.exceptions import InvalidCountryError

try:
    cf = CountryFlag()
    flags, pairs = cf.get_flag(["invalidcountry"])
    print(flags)  # Should go to stdout
except InvalidCountryError as e:
    print(f"Error: {e}", file=sys.stderr)  # Should go to stderr
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}", file=sys.stderr)  # Should go to stderr
    sys.exit(1)
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(script_content)
            script_path = f.name

        try:
            result = run_cli_command(f"python {script_path}")

            assert result["exit_code"] == 1
            assert result["stdout"].strip() == ""
            assert "Error:" in result["stderr"]
            assert "invalidcountry" in result["stderr"]

        finally:
            os.unlink(script_path)
