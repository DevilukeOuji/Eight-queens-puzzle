from typing import TypeVar, List, Tuple

T = TypeVar('T')


def pairwise(array: List[T]) -> List[Tuple[T, T]]:
    """
    Agrupa elementos consecutivos de um vetor em pares.

    Caso o número dos elementos do vetor seja ímpar, o último elemento será agrupado com o primeiro.

    >>> pairwise([1, 2, 3, 4, 5, 6])
    [(1, 2), (3, 4), (5, 6)]
    >>> pairwise([7, 8, 9, 10, 11])
    [(7, 8), (9, 10), (11, 7)]

    :param array: o vetor a ser agrupado.
    :return: os pares de elementos consecutivos desse vetor.
    """
    pairs = [(v0, v1) for v0, v1 in zip(array[::2], array[1::2])]
    if len(array) % 2 == 1:
        pairs.append((array[-1], array[0]))
    return pairs
