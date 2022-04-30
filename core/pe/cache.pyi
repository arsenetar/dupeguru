from typing import Union, Tuple, List

_block = Tuple[int, int, int]

def colors_to_string(colors: List[_block]) -> str: ...  # noqa: E302
def string_to_colors(s: str) -> Union[List[_block], None]: ...
