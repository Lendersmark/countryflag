def norm_newlines(s: str) -> str:
    """Normalize newlines in a string to Unix format and strip trailing whitespace.

    Converts Windows-style CRLF (\\r\\n) line endings to Unix-style LF (\\n)
    and removes trailing whitespace from the string.

    Args:
        s: The input string to normalize

    Returns:
        The normalized string with Unix-style line endings and no trailing whitespace
    """
    return s.replace("\r\n", "\n").rstrip()
