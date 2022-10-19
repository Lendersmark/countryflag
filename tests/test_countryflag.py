from src import countryflag
from cli_test_helpers import ArgvContext, shell


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
    result = shell("countryflag --help")
    assert result.exit_code == 0


def test_example_command():
    """Is command available?"""
    result = shell("countryflag france --help")
    assert result.exit_code == 0


def test_cli_singlecountry():
    """Tests the command line output"""
    expected = "🇫🇷\n"
    result = shell("countryflag France")
    assert result.stdout == expected, "Output doesn't match with input countries!"


def test_cli_multiplecountries():
    """Tests the command line output"""
    expected = "🇫🇷 🇧🇪 🇯🇵 🇺🇸\n"
    result = shell("countryflag France Belgium JP 'United States of America'")
    assert result.stdout == expected, "Output doesn't match with input countries!"


def test_cli_notfound():
    """Tests the error message when a country is not found in regex"""
    expected = "Please use one of the supported country names classifications.\n"
    result = shell("countryflag nonexistentcountry")
    assert result.stdout == expected
