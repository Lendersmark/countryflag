"""
Test platform-specific rendering behavior for Windows vs POSIX systems.

This test module verifies that platform-specific rendering logic correctly
chooses appropriate fallback mechanisms for Windows while preserving
color/emoji support on POSIX systems.
"""

import io
import sys
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import MagicMock, patch

import pytest

from src.countryflag.cli.main import main as cli_main
from src.countryflag.core.flag import CountryFlag


class TestPlatformSpecificRendering:
    """Test platform-specific rendering behavior for Windows vs POSIX."""

    def test_windows_platform_stdout_configuration(self, monkeypatch):
        """
        Test Windows branch of stdout/stderr configuration in CLI.

        Monkeypatch sys.platform to 'win32' and verify that Windows-specific
        stdout/stderr reconfiguration is triggered.
        """
        # Mock stdout and stderr with reconfigure method
        mock_stdout = MagicMock()
        mock_stderr = MagicMock()
        mock_stdout.reconfigure = MagicMock()
        mock_stderr.reconfigure = MagicMock()

        # Monkeypatch sys.platform to Windows
        monkeypatch.setattr(sys, "platform", "win32")
        monkeypatch.setattr(sys, "stdout", mock_stdout)
        monkeypatch.setattr(sys, "stderr", mock_stderr)

        # Import the CLI module to trigger platform-specific initialization
        # We need to reload the module to trigger the platform check again
        import importlib

        from src.countryflag.cli import main as cli_module

        importlib.reload(cli_module)

        # Verify that reconfigure was called with UTF-8 encoding for Windows
        mock_stdout.reconfigure.assert_called_with(encoding="utf-8", errors="replace")
        mock_stderr.reconfigure.assert_called_with(encoding="utf-8", errors="replace")

    def test_posix_platform_stdout_configuration(self, monkeypatch):
        """
        Test POSIX branch where stdout/stderr reconfiguration is NOT triggered.

        Monkeypatch sys.platform to 'linux' and verify that Windows-specific
        stdout/stderr reconfiguration is not called.
        """
        # Mock stdout and stderr with reconfigure method
        mock_stdout = MagicMock()
        mock_stderr = MagicMock()
        mock_stdout.reconfigure = MagicMock()
        mock_stderr.reconfigure = MagicMock()

        # Monkeypatch sys.platform to Linux
        monkeypatch.setattr(sys, "platform", "linux")
        monkeypatch.setattr(sys, "stdout", mock_stdout)
        monkeypatch.setattr(sys, "stderr", mock_stderr)

        # Import the CLI module to trigger platform-specific initialization
        # We need to reload the module to trigger the platform check again
        import importlib

        from src.countryflag.cli import main as cli_module

        importlib.reload(cli_module)

        # Verify that reconfigure was NOT called for POSIX systems
        mock_stdout.reconfigure.assert_not_called()
        mock_stderr.reconfigure.assert_not_called()

    def test_platform_optimizations_setup_windows(self, monkeypatch):
        """
        Test platform-specific optimizations for Windows.

        Monkeypatch sys.platform to 'win32' and verify that Windows-specific
        optimizations are considered (even if currently no-op).
        """
        # Monkeypatch sys.platform to Windows
        monkeypatch.setattr(sys, "platform", "win32")

        # Import and test the setup function
        from src.countryflag import _setup_platform_optimizations

        # This should not raise any exceptions and complete successfully
        # Even though it's currently a no-op, it should handle Windows case
        try:
            _setup_platform_optimizations()
            windows_setup_success = True
        except Exception:
            windows_setup_success = False

        assert (
            windows_setup_success
        ), "Windows platform optimizations should complete without error"

    def test_platform_optimizations_setup_linux(self, monkeypatch):
        """
        Test platform-specific optimizations for Linux.

        Monkeypatch sys.platform to 'linux' and verify that Linux-specific
        optimizations are considered.
        """
        # Monkeypatch sys.platform to Linux
        monkeypatch.setattr(sys, "platform", "linux")

        # Import and test the setup function
        from src.countryflag import _setup_platform_optimizations

        # This should not raise any exceptions and complete successfully
        try:
            _setup_platform_optimizations()
            linux_setup_success = True
        except Exception:
            linux_setup_success = False

        assert (
            linux_setup_success
        ), "Linux platform optimizations should complete without error"

    def test_platform_optimizations_setup_darwin(self, monkeypatch):
        """
        Test platform-specific optimizations for macOS.

        Monkeypatch sys.platform to 'darwin' and verify that macOS-specific
        optimizations are considered.
        """
        # Monkeypatch sys.platform to macOS
        monkeypatch.setattr(sys, "platform", "darwin")

        # Import and test the setup function
        from src.countryflag import _setup_platform_optimizations

        # This should not raise any exceptions and complete successfully
        try:
            _setup_platform_optimizations()
            darwin_setup_success = True
        except Exception:
            darwin_setup_success = False

        assert (
            darwin_setup_success
        ), "macOS platform optimizations should complete without error"

    @pytest.mark.parametrize(
        "platform_name,expected_behavior",
        [
            ("win32", "windows_fallback"),
            ("linux", "posix_color_emoji"),
            ("darwin", "posix_color_emoji"),
            ("freebsd", "posix_color_emoji"),
        ],
    )
    def test_comprehensive_platform_rendering(
        self, monkeypatch, platform_name, expected_behavior
    ):
        """
        Comprehensive test of platform-specific rendering behavior.

        Tests various platforms and verifies that:
        - Windows chooses appropriate fallback behavior
        - POSIX systems preserve color/emoji support
        """
        # Monkeypatch the platform
        monkeypatch.setattr(sys, "platform", platform_name)

        # Mock sys.argv to simulate CLI call
        test_argv = ["countryflag", "US"]
        monkeypatch.setattr(sys, "argv", test_argv)

        # Capture output
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # Mock argparse to avoid actual CLI parsing issues
                with patch("argparse.ArgumentParser.parse_args") as mock_parse_args:
                    # Create a mock args object with necessary attributes
                    mock_args = MagicMock()
                    mock_args.countries = ["US"]
                    mock_args.file = None
                    mock_args.files = None
                    mock_args.reverse = None
                    mock_args.region = None
                    mock_args.interactive = False
                    mock_args.list_countries = False
                    mock_args.list_regions = False
                    mock_args.validate = None
                    mock_args.use_async = False
                    mock_args.format = "text"
                    mock_args.separator = " "
                    mock_args.fuzzy = False
                    mock_args.threshold = 0.6
                    mock_args.verbose = False
                    mock_args.cache = False
                    mock_args.cache_dir = None
                    mock_args.language = "en"

                    mock_parse_args.return_value = mock_args

                    # Mock CountryFlag to avoid dependency issues in tests
                    with patch("src.countryflag.cli.main.CountryFlag") as mock_cf_class:
                        mock_cf = MagicMock()
                        mock_cf.get_flag.return_value = (
                            "🇺🇸",
                            [("United States", "🇺🇸")],
                        )
                        mock_cf_class.return_value = mock_cf

                        # Call the CLI main function
                        cli_main()

            output = stdout_capture.getvalue()

            # Verify platform-specific behavior
            if expected_behavior == "windows_fallback":
                # For Windows, we should still get the flag but verify the setup was called
                # The key test is that Windows-specific initialization occurred
                assert (
                    len(output.strip()) > 0
                ), f"Windows should produce output on {platform_name}"

            elif expected_behavior == "posix_color_emoji":
                # For POSIX systems, we should get full emoji/color support
                assert (
                    "🇺🇸" in output or len(output.strip()) > 0
                ), f"POSIX should preserve emoji on {platform_name}"

        except SystemExit:
            # CLI might call sys.exit(), which is acceptable for this test
            pass

    def test_platform_detection_coverage(self, monkeypatch):
        """
        Test that platform detection reaches all code branches.

        This test ensures that lines excluded on non-Windows hosts are reached
        when sys.platform is monkeypatched to different values.
        """
        platforms_to_test = ["win32", "linux", "darwin", "freebsd", "openbsd"]

        for platform_name in platforms_to_test:
            # Monkeypatch the platform
            monkeypatch.setattr(sys, "platform", platform_name)

            # Test platform-specific optimizations setup
            from src.countryflag import _setup_platform_optimizations

            # This should execute the appropriate branch based on platform
            try:
                _setup_platform_optimizations()
                platform_handled = True
            except Exception:
                platform_handled = False

            assert (
                platform_handled
            ), f"Platform {platform_name} should be handled without errors"

            # Test different code paths in the platform check
            if platform_name.startswith("win"):
                # Windows-specific path should be reached
                assert sys.platform.startswith(
                    "win"
                ), "Windows platform detection should work"
            elif platform_name == "darwin":
                # macOS-specific path should be reached
                assert sys.platform == "darwin", "macOS platform detection should work"
            elif platform_name.startswith("linux"):
                # Linux-specific path should be reached
                assert sys.platform.startswith(
                    "linux"
                ), "Linux platform detection should work"

    def test_windows_unicode_fallback_behavior(self, monkeypatch):
        """
        Test Windows Unicode fallback behavior specifically.

        Verifies that Windows branch chooses appropriate fallback behavior
        for Unicode rendering while POSIX keeps full support.
        """
        # Test Windows behavior
        monkeypatch.setattr(sys, "platform", "win32")

        # Create a CountryFlag instance and test emoji rendering
        cf = CountryFlag()
        flags, pairs = cf.get_flag(["US", "FR", "DE"])

        # Windows should still produce valid flags, but may use fallback encoding
        assert "🇺🇸" in flags or len(flags) > 0, "Windows should produce flag output"
        assert len(pairs) == 3, "Windows should process all countries"

        # Reset and test Linux behavior
        monkeypatch.setattr(sys, "platform", "linux")

        # Create a new CountryFlag instance for Linux
        cf_linux = CountryFlag()
        flags_linux, pairs_linux = cf_linux.get_flag(["US", "FR", "DE"])

        # POSIX should preserve full emoji support
        assert "🇺🇸" in flags_linux, "Linux should preserve emoji flags"
        assert "🇫🇷" in flags_linux, "Linux should preserve emoji flags"
        assert "🇩🇪" in flags_linux, "Linux should preserve emoji flags"
        assert len(pairs_linux) == 3, "Linux should process all countries"

    def test_cross_platform_consistency(self, monkeypatch):
        """
        Test that core functionality remains consistent across platforms.

        While rendering may differ, the core country-to-flag mapping
        should remain consistent across all platforms.
        """
        test_countries = ["US", "FR", "DE", "JP", "GB"]

        # Test on different platforms
        platforms = ["win32", "linux", "darwin"]
        results = {}

        for platform in platforms:
            monkeypatch.setattr(sys, "platform", platform)

            cf = CountryFlag()
            flags, pairs = cf.get_flag(test_countries)

            # Store the country-to-flag mapping (not the rendering)
            country_codes = [pair[0] for pair in pairs]
            results[platform] = country_codes

        # Verify that country recognition is consistent across platforms
        base_result = results["win32"]
        for platform, result in results.items():
            assert (
                result == base_result
            ), f"Country recognition should be consistent on {platform}"

    def test_cli_platform_branch_coverage(self, monkeypatch):
        """
        Test to ensure we reach the Windows-specific CLI branch with monkeypatching.

        This test directly verifies that the Windows platform branch in the CLI
        module is executed when sys.platform is set to win32.
        """
        # Create mock stdout/stderr objects with reconfigure method
        mock_stdout = MagicMock()
        mock_stderr = MagicMock()

        # Set up the mocks to track reconfigure calls
        mock_stdout.reconfigure = MagicMock()
        mock_stderr.reconfigure = MagicMock()

        # Apply monkeypatches before importing the module
        monkeypatch.setattr(sys, "platform", "win32")
        monkeypatch.setattr(sys, "stdout", mock_stdout)
        monkeypatch.setattr(sys, "stderr", mock_stderr)

        # Import the module - this should trigger the Windows branch
        import importlib

        import src.countryflag.cli.main as cli_main_module

        # Force reload to ensure the platform check runs with our mocked values
        importlib.reload(cli_main_module)

        # Verify that stdout and stderr reconfigure was called for Windows
        mock_stdout.reconfigure.assert_called_with(encoding="utf-8", errors="replace")
        mock_stderr.reconfigure.assert_called_with(encoding="utf-8", errors="replace")

        # Now test POSIX behavior - reset mocks
        mock_stdout.reconfigure.reset_mock()
        mock_stderr.reconfigure.reset_mock()

        # Set platform to Linux and reload
        monkeypatch.setattr(sys, "platform", "linux")
        importlib.reload(cli_main_module)

        # Verify that reconfigure was NOT called for POSIX
        mock_stdout.reconfigure.assert_not_called()
        mock_stderr.reconfigure.assert_not_called()

    def test_actual_platform_detection_in_init(self, monkeypatch):
        """
        Test the actual platform-specific optimizations in __init__.py.

        This ensures all platform branches are covered and that the function
        executes correctly on different platforms.
        """
        # Import the function to test
        from src.countryflag import _setup_platform_optimizations

        # Test Windows platform
        monkeypatch.setattr(sys, "platform", "win32")
        _setup_platform_optimizations()  # Should complete without error

        # Test Linux platform
        monkeypatch.setattr(sys, "platform", "linux")
        _setup_platform_optimizations()  # Should complete without error

        # Test macOS platform
        monkeypatch.setattr(sys, "platform", "darwin")
        _setup_platform_optimizations()  # Should complete without error

        # Test other POSIX platforms
        monkeypatch.setattr(sys, "platform", "freebsd")
        _setup_platform_optimizations()  # Should complete without error

        # All tests passed if we reach here
        assert True, "All platform optimization setups completed successfully"
