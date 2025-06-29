import io
import warnings
from contextlib import contextmanager, redirect_stderr, redirect_stdout


@contextmanager
def silence_coco_warnings():
    """Context manager to suppress country_converter warnings and noise.

    This suppresses warnings from the country_converter module,
    direct stderr output from coco during the conversion process,
    and stdout noise that might leak through.
    It does not suppress our own error messages.
    """
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", module="country_converter")
        warnings.filterwarnings("ignore", message=".*country_converter.*")
        warnings.filterwarnings("ignore", message=".*coco.*")
        warnings.filterwarnings("ignore", message=".*not found in regex.*")
        warnings.filterwarnings("ignore", message=".*regex.*")

        # Capture stderr and stdout to prevent noise from leaking
        stderr_buffer = io.StringIO()
        stdout_buffer = io.StringIO()

        with redirect_stderr(stderr_buffer), redirect_stdout(stdout_buffer):
            yield
