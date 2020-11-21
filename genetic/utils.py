import math
import re
from typing import TypeVar, List, Tuple, Generator

T = TypeVar('T')


class BitArray:
    """
    Representa um vetor binário suportado por um número inteiro.

    O número inteiro 10957079, por exemplo, possui como representação em base 2 o valor 101001110011000100010111. Caso
    o número de bits de agrupamento (passado como argumento no construtor dessa classe) seja 3, esse número representa
    o vetor binário [111, 010, 100, 000, 011, 110, 001, 101] (o índice 0 se refere ao grupo de bits mais significante).

    Todas as operações de busca por índice, inserção e remoção são feitas por meio de operadores bit-a-bit.
    """

    def __init__(self, group_size: int, /):
        """
        Constrói um vetor binário.
        :param group_size: o número de bits que serão agrupados em cada índice do vetor.
        """
        self._array = 0
        self._group_size = group_size
        self._mask = (1 << self._group_size) - 1

    @classmethod
    def from_list(cls, list_: List[int], /, group_size: int):
        """
        Constrói um vetor binário a partir de uma lista de inteiros.

        >>> BitArray.from_list([3, 2, 4, 1])    # 001 100 010 011

        :param list_: a lista a ser transformada em vetor binário.
        :param group_size: o número de bits a ser armazenado para cada elemento da lista.
        """
        array = cls(group_size)
        for i, value in enumerate(list_):
            array[i] = value
        return array

    def __setitem__(self, index: int, value: int):
        """
        Insere um elemento nesse vetor binário.

        >>> array = BitArray(3)
        >>> array    # 000
        >>> array[1] = 0b101
        >>> array    # 101 000

        :param index: o índice do vetor a ser inserido.
        :param value: o valor a ser inserido. Caso o número de bits desse valor seja maior que o número de bits de
        agrupamento `n`, serão inseridos apenas os `n` bits mais significantes desse número.
        """
        value &= self._mask
        del self[index]
        self._array |= value << (self._group_size * index)

    def __getitem__(self, index: int) -> int:
        """
        Retorna um elemento desse vetor binário.

        >>> array = BitArray(3)
        >>> array[0] = 0b001
        >>> array[1] = 0b101
        >>> array[0]    # 1
        >>> array[1]    # 5

        :param index: o índice do elemento a ser retornado. Esse valor não pode ser negativo.
        :return: o elemento no índice especificado.
        """
        if index < 0:
            raise ValueError("esse valor não pode ser negativo")

        return self._array >> (self._group_size * index) & self._mask

    def __delitem__(self, index: int):
        """
        Define como 0 os bits em dado índice do vetor.

        >>> array = BitArray(3)
        >>> array[0] = 0b010
        >>> array[1] = 0b110
        >>> array    # 110 010
        >>> del array[0]
        >>> array    # 110 000

        :param index: o índice do vetor a ser limpo.
        """
        self._array &= ~(self._mask << (self._group_size * index))

    def iterate(self, length: int) -> Generator[int, None, None]:
        """
        Itera sobre os grupos de bits mais significantes desse vetor.
        :param length: o número de grupos de bits a serem iterados.
        :return: um gerador com os grupos de bits desse vetor.
        """
        return self.iterate_from(0, length)

    def iterate_from(self, start: int, stop: int, step: int = 1) -> Generator[int, None, None]:
        """
        Itera sobre um intervalo de elementos desse vetor.
        :param start: o índice do vetor cuja iteração começará.
        :param stop: o índice do vetor cuja iteração terminará.
        :param step: o passo da iteração.
        :return: um gerador com os grupos de bits do intervalo especificado desse vetor.
        """
        for i in range(start, stop, step):
            yield self[i]

    def __hash__(self):
        return self._array

    def __repr__(self) -> str:
        """
        :return: uma representação dos bits definidos nesse vetor.
        """
        # Exemplo para `self._array == 87` e `self._group_size == 3`

        # `int_repr == 1010111`
        int_repr = f'{self._array:b}'

        # Transforma '1010111' em '001010111'
        if len(int_repr) % self._group_size != 0:
            new_len = math.ceil(len(int_repr) / self._group_size) * self._group_size
            int_repr = int_repr.zfill(new_len)

        # Transforma '001010111' em '001 010 111'
        return re.sub(rf'(?<!^)(?=(\d{{{self._group_size}}})+$)', r' ', int_repr)


def pairwise(array: List[T]) -> List[Tuple[T, T]]:
    """
    Agrupa elementos consecutivos de um vetor em pares.

    Caso o número dos elementos do vetor seja ímpar, o último elemento será agrupado com o primeiro.

    >>> pairwise([1, 2, 3, 4, 5, 6])    # [(1, 2), (3, 4), (5, 6)]
    >>> pairwise([7, 8, 9, 10, 11])     # [(7, 8), (9, 10), (11, 7)]

    :param array: o vetor a ser agrupado.
    :return: os pares de elementos consecutivos desse vetor.
    """
    pairs = [(v0, v1) for v0, v1 in zip(array[::2], array[1::2])]
    if len(array) % 2 == 1:
        pairs.append((array[-1], array[0]))
    return pairs
