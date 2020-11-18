import math
import random
from typing import List, Tuple


class State:
    """
    Representa uma solução candidata para o Problema das Oito Rainhas.
    """
    _VALID_VALUES = (0, 1, 2, 3, 4, 5, 6, 7)

    def __init__(self, array: List[int]):
        """
        Constrói um estado.

        :param array: um vetor onde cada posição representa uma coluna do tabuleiro e cada valor representa a linha da
        coluna onde a rainha está posicionada nesse tabuleiro.
        """
        if any(value not in self._VALID_VALUES for value in array):
            raise ValueError("todos os valores do vetor devem estar entre 0-7")

        self.array = array

    @classmethod
    def random(cls):
        """
        Cria um estado aleatório.

        :return: o estado criado.
        """
        values = [0, 1, 2, 3, 4, 5, 6, 7]
        random.shuffle(values)
        return cls(values)

    @property
    def fitness(self):
        """
        Calcula a função fitness para esse estado no contexto do Problema das Oito Rainhas.

        :return: o número de pares únicos de rainhas que não se atacam entre si.
        """
        total = 28

        # Remove as rainhas da mesma coluna do total
        unique_values = len(set(self.array))
        total -= len(self.array) - unique_values

        diagonal_occurrences = 0
        for i, v0 in enumerate(self.array):
            # Monitora as direções que uma rainha atacada foi encontrada. Se 'topleft' for
            # `True`, por exemplo, uma rainha foi atacada na diagonal superior esquerda.
            directions = {
                'topleft': False,
                'bottomleft': False,
                'topright': False,
                'bottomright': False,
            }

            # Itera sobre os elementos à direita de v0 no vetor
            for j, v1 in enumerate(self.array[i + 1:], start=i + 1):
                dx = j - i
                dy = v1 - v0

                direction = ''
                direction += 'top' if dy < 0 else 'bottom'
                direction += 'left' if dx < 0 else 'right'

                # Verifica se existe alguma rainha na mesma diagonal apenas
                # se ainda não tiver ocorrido nenhum conflito nessa direção.
                if not directions[direction] and abs(dx) == abs(dy):
                    directions[direction] = True
                    diagonal_occurrences += 1

        total -= diagonal_occurrences
        return total

    @property
    def slots(self):
        """
        :return: o número de elementos no vetor desse estado.
        """
        return len(self.array)

    def cross(self, other, strategy='cutoff') -> Tuple['State', 'State']:
        """
        Troca material genético com outro estado.

        :param other: o outro estado.
        :param strategy: o nome da estratégia de cruzamento a ser utilizada, podendo ser 'cutoff' (utiliza um ponto de
        corte) ou  'uniform' (utiliza um vetor binário).
        :return: o resultado do cruzamento entre esses dois estados.
        """
        if len(self.array) != len(other.array):
            raise ValueError("os vetores devem possuir tamanhos iguais")

        if strategy == 'cutoff':
            return self._cutoff_cross(other)
        if strategy == 'uniform':
            return self._uniform_cross(other)

        raise ValueError("estratégia de cruzamento inválida")

    def _cutoff_cross(self, other) -> Tuple['State', 'State']:
        """
        Troca material genético com outro estado por meio de um ponto de corte.

        :param other: o outro estado.
        :return: o resultado do cruzamento entre esses dois estados.
        """
        i_slots = range(self.slots)
        cutoff = random.choice(i_slots)
        child_0 = State([self.array[i] if i <= cutoff else other.array[i] for i in i_slots])
        child_1 = State([self.array[i] if i > cutoff else other.array[i] for i in i_slots])
        return child_0, child_1

    def _uniform_cross(self, other) -> Tuple['State', 'State']:
        """
        Troca material genético com outro estado por meio de um vetor binário.

        :param other: o outro estado.
        :return: o resultado do cruzamento entre esses dois estados.
        """
        i_slots = range(self.slots)
        split_array_0 = [random.randint(0, 1) for _ in i_slots]
        child_0 = State([self.array[i] if v == 0 else other.array[i] for i, v in zip(i_slots, split_array_0)])
        split_array_1 = [random.randint(0, 1) for _ in i_slots]
        child_1 = State([self.array[i] if v == 0 else other.array[i] for i, v in zip(i_slots, split_array_1)])
        return child_0, child_1

    def mutate(self, strategy='bitflip'):
        """
        Sofre uma mutação.

        :param strategy: o nome da estratégia de mutação a ser utilizada, podendo ser 'bitflip' para a estratégia
        bitflip ou 'permutation' para a estratégia de permutação.
        """
        if strategy == 'bitflip':
            return self._bitflip_mutation()
        if strategy == 'permutation':
            return self._permutation_mutation()

        raise ValueError("estratégia de mutação inválida")

    def _bitflip_mutation(self):
        """
        Sofre uma mutação por meio da estratégia bitflip.

        Escolhem-se aleatoriamente um elemento e uma posição para modificar o bit.
        """
        # Nesse contexto, bits_size == 3
        bits_size = int(math.log2(max(self._VALID_VALUES)))
        arr_index = random.choice(range(self.slots))
        bit_index = random.choice(range(bits_size))
        self.array[arr_index] ^= 1 << bit_index

    def _permutation_mutation(self):
        """
        Sofre uma mutação por meio da estratégia permutação.

        Escolhem-se aleatoriamente duas posições do vetor e a permutam.
        """
        i0 = random.choice(range(self.slots))
        while True:
            i1 = random.choice(range(self.slots))
            if i0 != i1:
                self.array[i0], self.array[i1] = self.array[i1], self.array[i0]
                return

    def __hash__(self):
        return hash(tuple(self.array))

    def __eq__(self, other):
        return isinstance(other, State) and self.array == other.array

    def __repr__(self):
        return f'State({self.array})'
