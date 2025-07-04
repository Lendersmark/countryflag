from functools import wraps

import pytest

from src.countryflag.utils.validation import ensure, require, runtime_typechecked


# Sample functions with decorators
@require(lambda x: x > 0, "Value must be positive")
def positive_only(x):
    """Function that requires a positive input."""
    return x


@ensure(lambda result: result >= 0, "Result must be non-negative")
def subtract_positive(a, b):
    """Subtracts two numbers ensuring non-negative result."""
    return a - b


@runtime_typechecked
def add(x: int, y: int) -> int:
    """Adds two integers."""
    return x + y


# Tests
@pytest.mark.parametrize(
    "value,expect_exception",
    [
        (1, False),
        (-1, True),
    ],
)
def test_require_decorator(value, expect_exception):
    if expect_exception:
        with pytest.raises(ValueError, match="Value must be positive"):
            positive_only(value)
    else:
        assert positive_only(value) == value


@pytest.mark.parametrize(
    "a,b,expect_exception",
    [
        (3, 2, False),
        (2, 3, True),
    ],
)
def test_ensure_decorator(a, b, expect_exception):
    if expect_exception:
        with pytest.raises(ValueError, match="Result must be non-negative"):
            subtract_positive(a, b)
    else:
        assert subtract_positive(a, b) == a - b


@pytest.mark.parametrize(
    "x,y,expect_exception",
    [
        (1, 2, False),
        ("1", 2, True),
        (1, "2", True),
        (1.5, 2, True),  # float instead of int
    ],
)
def test_runtime_typechecked_decorator(x, y, expect_exception):
    if expect_exception:
        # typeguard.TypeCheckError is a subclass of TypeError
        with pytest.raises(TypeError):
            add(x, y)
    else:
        assert add(x, y) == x + y


# Additional test functions for comprehensive coverage
@require(lambda x, y: x > y, "First argument must be greater than second")
def greater_than(x, y):
    """Function that requires first argument to be greater than second."""
    return x - y


@ensure(lambda result: isinstance(result, str), "Result must be a string")
def int_to_string(x):
    """Converts integer to string."""
    return str(x)


@runtime_typechecked
def divide(x: float, y: float) -> float:
    """Divides two floats."""
    return x / y


@runtime_typechecked
def greet(name: str) -> str:
    """Greets a person by name."""
    return f"Hello, {name}!"


# Tests for multiple argument require decorator
def test_require_multiple_args():
    """Test require decorator with multiple arguments."""
    # Should work when x > y
    assert greater_than(5, 3) == 2

    # Should fail when x <= y
    with pytest.raises(
        ValueError, match="First argument must be greater than second in greater_than"
    ):
        greater_than(3, 5)

    with pytest.raises(
        ValueError, match="First argument must be greater than second in greater_than"
    ):
        greater_than(3, 3)


# Tests for ensure decorator with type checking
def test_ensure_type_checking():
    """Test ensure decorator with type checking."""
    # Should work with proper conversion
    result = int_to_string(42)
    assert result == "42"
    assert isinstance(result, str)


# Tests for runtime type checking with floats
def test_runtime_typechecked_floats():
    """Test runtime type checking with float types."""
    # Should work with floats
    assert divide(10.0, 2.0) == 5.0

    # Should work with ints (they're compatible with float)
    assert divide(10, 2) == 5.0

    # Should fail with strings
    with pytest.raises(TypeError):
        divide("10", 2.0)


# Tests for runtime type checking with strings
def test_runtime_typechecked_strings():
    """Test runtime type checking with string types."""
    # Should work with strings
    assert greet("Alice") == "Hello, Alice!"

    # Should fail with non-strings
    with pytest.raises(TypeError):
        greet(123)


# Tests for error message formatting
def test_error_message_formatting():
    """Test that error messages include function names."""
    # Test require decorator error message
    with pytest.raises(ValueError) as exc_info:
        positive_only(-5)
    assert "in positive_only" in str(exc_info.value)

    # Test ensure decorator error message
    with pytest.raises(ValueError) as exc_info:
        subtract_positive(1, 3)
    assert "in subtract_positive" in str(exc_info.value)


# Tests for edge cases
def test_edge_cases():
    """Test edge cases for validation decorators."""
    # Test with zero (boundary condition)
    assert positive_only(0.1) == 0.1
    with pytest.raises(ValueError):
        positive_only(0)

    # Test with exactly zero result
    assert subtract_positive(5, 5) == 0


# Tests for function composition
@require(lambda x: x > 0, "Input must be positive")
@ensure(lambda result: result > 0, "Result must be positive")
@runtime_typechecked
def square_root(x: float) -> float:
    """Calculate square root with all three decorators."""
    return x**0.5


def test_decorator_composition():
    """Test that multiple decorators work together."""
    # Should work with valid input
    assert square_root(4.0) == 2.0

    # Should fail precondition
    with pytest.raises(ValueError, match="Input must be positive"):
        square_root(-4.0)

    # Should fail type checking
    with pytest.raises(TypeError):
        square_root("4")


# Metadata tests
def test_metadata_preservation():
    """Test that function metadata is preserved by decorators."""
    # Test __name__ preservation
    assert positive_only.__name__ == "positive_only"
    assert subtract_positive.__name__ == "subtract_positive"
    assert add.__name__ == "add"
    assert greater_than.__name__ == "greater_than"
    assert int_to_string.__name__ == "int_to_string"
    assert divide.__name__ == "divide"
    assert greet.__name__ == "greet"
    assert square_root.__name__ == "square_root"

    # Test __doc__ preservation
    assert positive_only.__doc__ == "Function that requires a positive input."
    assert (
        subtract_positive.__doc__
        == "Subtracts two numbers ensuring non-negative result."
    )
    assert add.__doc__ == "Adds two integers."
    assert (
        greater_than.__doc__
        == "Function that requires first argument to be greater than second."
    )
    assert int_to_string.__doc__ == "Converts integer to string."
    assert divide.__doc__ == "Divides two floats."
    assert greet.__doc__ == "Greets a person by name."
    assert square_root.__doc__ == "Calculate square root with all three decorators."


# Test successful cases to ensure proper functionality
def test_successful_cases():
    """Test that decorators don't interfere with normal function operation."""
    # Test various successful cases
    assert positive_only(1) == 1
    assert positive_only(100) == 100
    assert subtract_positive(10, 5) == 5
    assert add(3, 7) == 10
    assert greater_than(10, 5) == 5
    assert int_to_string(42) == "42"
    assert divide(15.0, 3.0) == 5.0
    assert greet("World") == "Hello, World!"
    assert square_root(9.0) == 3.0
