from src import countryflag


def test_countryflag():
    expected = "🇫🇷 🇧🇪 🇯🇵 🇺🇸"
    actual = countryflag.getflag(
        ["France", "Belgium", "JP", "United States of America"]
    )
    assert actual == expected, "Output doesn't match with input countries!"
