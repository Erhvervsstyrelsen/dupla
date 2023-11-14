from typing import Annotated, Any, Callable, List

from pydantic import AfterValidator, BeforeValidator


def _string_num_len_n(n: int) -> Callable[[str], str]:
    """Helper function to validate the correctness
    of integer-like strings. The length of the string is checked."""

    def _inner(s: str) -> str:
        try:
            int(s)  # Verify the number is int-like
        except ValueError:
            raise ValueError(f"Number must be integer-like, got {s!r}") from None
        if len(s) != n:
            raise ValueError(f"Must of length {n}.")
        return s

    return _inner


def _stringify_int(val: Any) -> Any:
    """Integers are valid, they just need to be strings"""
    if isinstance(val, int):
        return str(val)
    return val


CVR_STR = Annotated[str, BeforeValidator(_stringify_int), AfterValidator(_string_num_len_n(8))]
SE_STR = Annotated[str, BeforeValidator(_stringify_int), AfterValidator(_string_num_len_n(8))]
CPR_STR = Annotated[str, BeforeValidator(_stringify_int), AfterValidator(_string_num_len_n(10))]

CVR_T = List[CVR_STR]
CPR_T = List[CPR_STR]
SE_T = List[SE_STR]
