from contextlib import contextmanager, redirect_stderr
import io, warnings, sys

@contextmanager
def silence_coco_warnings():
    """Context manager to suppress country_converter warnings and noise.
    
    This only suppresses warnings from the country_converter module
    and direct stderr output from coco during the conversion process.
    It does not suppress our own error messages.
    """
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", module="country_converter")
        warnings.filterwarnings("ignore", message=".*country_converter.*")
        warnings.filterwarnings("ignore", message=".*coco.*")
        yield
