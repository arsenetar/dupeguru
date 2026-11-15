from typing import Tuple, List, Union, Sequence

_block = Tuple[int, int, int]

class NoBlocksError(Exception): ...  # noqa: E302, E701
class DifferentBlockCountError(Exception): ...  # noqa E701

def getblock(image: object) -> Union[_block, None]: ...  # noqa: E302
def getblocks2(image: object, block_count_per_side: int) -> Union[List[_block], None]: ...
def diff(first: _block, second: _block) -> int: ...
def avgdiff(  # noqa: E302
    first: Sequence[_block], second: Sequence[_block], limit: int = 768, min_iterations: int = 1
) -> Union[int, None]: ...
