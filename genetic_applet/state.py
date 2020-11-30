import random
from typing import Tuple

from genetic.state import State
from genetic.utils import BitArray


class AppletState(State):
    """
    Modificação de um estado para funcionar de acordo com o applet.
    """

    def _cutoff_cross(self, other: 'AppletState') -> Tuple['AppletState', 'AppletState', int]:
        cutoff = random.choice(range(1, 7))
        array_0 = BitArray.from_list([self.array[i] if i <= cutoff else other.array[i] for i in range(8)], 3)
        array_1 = BitArray.from_list([self.array[i] if i > cutoff else other.array[i] for i in range(8)], 3)
        return AppletState(array_0), AppletState(array_1), cutoff
