from typing import Tuple, List, Union
from PyQt5.QtGui import QImage

_block = Tuple[int, int, int]

def getblock(image: QImage) -> _block: ...  # noqa: E302
def getblocks(image: QImage, block_count_per_side: int) -> Union[List[_block], None]: ...
