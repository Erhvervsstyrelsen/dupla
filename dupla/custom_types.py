from typing import Annotated, List

from pydantic import AfterValidator


def _string_num_len_n(n: int) -> str:
    """Helper function to validate the correctness
    of integer-like strings. The length of the string is checked."""

    def _inner(s: str):
        try:
            int(s)  # Verify the number is int-like
        except ValueError:
            raise ValueError(f"Number must be integer-like, got {s!r}") from None
        if len(s) != n:
            raise ValueError(f"Must of length {n}.")
        return s

    return _inner


CVR_STR = Annotated[str, AfterValidator(_string_num_len_n(8))]
SE_STR = Annotated[str, AfterValidator(_string_num_len_n(8))]
CPR_STR = Annotated[str, AfterValidator(_string_num_len_n(10))]

CVR_T = List[CVR_STR]
CPR_T = List[CPR_STR]
SE_T = List[SE_STR]
