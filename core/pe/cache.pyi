from typing import Union, Tuple, List

_block = Tuple[int, int, int]

def colors_to_bytes(colors: List[_block]) -> bytes: ...  # noqa: E302
def bytes_to_colors(s: bytes) -> Union[List[_block], None]: ...
