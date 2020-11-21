import random
from typing import Tuple

from genetic.utils import BitArray


class State:
    """
    Representa uma solução candidata para o Problema das Oito Rainhas.
    """

    def __init__(self, array: BitArray):
        """
        Constrói um estado.

        :param array: um vetor binário onde cada posição representa uma coluna do tabuleiro e cada valor representa a
        linha da coluna onde a rainha está posicionada nesse tabuleiro.
        """
        valid_range = range(8)
        # Itera sobre as 8 primeiros grupos de bits (elementos) desse vetor
        if any(value not in valid_range for value in array.iterate(8)):
            raise ValueError(f"todos os valores do vetor devem estar entre {valid_range.start}-{valid_range.stop}")

        self.array = array

    @classmethod
    def random(cls):
        """
        Cria um estado aleatório.
        :return: o estado criado.
        """
        values = list(range(8))
        random.shuffle(values)
        return cls(BitArray.from_list(values, 3))

    @property
    def fitness(self):
        """
        Calcula a função fitness para esse estado no contexto do Problema das Oito Rainhas.
        :return: o número de pares únicos de rainhas que não se atacam entre si.
        """
        total = 28

        # Remove as rainhas da mesma coluna do total
        unique_values = len(set(self.array.iterate(8)))
        total -= 8 - unique_values

        diagonal_occurrences = 0
        for i, v0 in enumerate(self.array.iterate(8)):
            # Monitora as direções que uma rainha atacada foi encontrada. Se 'topleft' for
            # `True`, por exemplo, uma rainha foi atacada na diagonal superior esquerda.
            directions = {
                'topleft': False,
                'bottomleft': False,
                'topright': False,
                'bottomright': False,
            }

            # Itera sobre os elementos à direita de v0 no vetor
            for j, v1 in enumerate(self.array.iterate_from(i + 1, 8), start=i + 1):
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

    def cross(self, other, strategy='cutoff') -> Tuple['State', 'State']:
        """
        Troca material genético com outro estado.

        :param other: o outro estado.
        :param strategy: o nome da estratégia de cruzamento a ser utilizada, podendo ser 'cutoff' (utiliza um ponto de
        corte) ou  'uniform' (utiliza um vetor binário).
        :return: o resultado do cruzamento entre esses dois estados.
        """
        if strategy == 'cutoff':
            return self._cutoff_cross(other)
        if strategy == 'uniform':
            return self._uniform_cross(other)

        raise ValueError("estratégia de cruzamento inválida")

    def _cutoff_cross(self, other: 'State') -> Tuple['State', 'State']:
        """
        Troca material genético com outro estado por meio de um ponto de corte.

        :param other: o outro estado.
        :return: o resultado do cruzamento entre esses dois estados.
        """
        i_slots = range(8)
        cutoff = random.choice(i_slots)
        array_0 = BitArray.from_list([self.array[i] if i <= cutoff else other.array[i] for i in i_slots], 3)
        array_1 = BitArray.from_list([self.array[i] if i > cutoff else other.array[i] for i in i_slots], 3)
        return State(array_0), State(array_1)

    def _uniform_cross(self, other) -> Tuple['State', 'State']:
        """
        Troca material genético com outro estado por meio de um vetor binário.

        :param other: o outro estado.
        :return: o resultado do cruzamento entre esses dois estados.
        """
        i_slots = range(8)
        split_0 = [random.randint(0, 1) for _ in i_slots]
        split_1 = [random.randint(0, 1) for _ in i_slots]
        array_0 = BitArray.from_list([self.array[i] if v == 0 else other.array[i] for i, v in zip(i_slots, split_0)], 3)
        array_1 = BitArray.from_list([self.array[i] if v == 0 else other.array[i] for i, v in zip(i_slots, split_1)], 3)
        return State(array_0), State(array_1)

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
        arr_index = random.choice(range(8))
        bit_index = random.choice(range(3))
        self.array[arr_index] ^= 1 << bit_index

    def _permutation_mutation(self):
        """
        Sofre uma mutação por meio da estratégia permutação.

        Escolhem-se aleatoriamente duas posições do vetor e a permutam.
        """
        i0 = random.choice(range(8))
        while True:
            i1 = random.choice(range(8))
            if i0 != i1:
                self.array[i0], self.array[i1] = self.array[i1], self.array[i0]
                return

    def __hash__(self) -> int:
        return hash(self.array)

    def __eq__(self, other: 'State') -> bool:
        return self.array == other.array

    def __repr__(self):
        array_repr = repr(self.array)
        # A representação do vetor binário apenas será menor que 31 (8 elementos no vetor * 3 bits para cada elemento +
        # 7 espaços entre cada elemento) caso o seu primeiro elemento seja '000'. Nesse caso, teremos que inserí-lo.
        if len(array_repr) < 31:
            array_repr = '000 ' + array_repr
        return f'{array_repr}'
