import random
from typing import Tuple

from genetic.utils import BitArray


class State:
    """
    Representa uma solução candidata para o Problema das Oito Rainhas.
    """

    _MAX_FITNESS = 28
    """
    Representa o valor da função fitness ótimo para esse estado.
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
        # random.sample(range(8), 8) == (values = list(range(8)); random.shuffle(values))
        return cls(BitArray.from_list(random.sample(range(8), 8), 3))

    @property
    def is_optimal(self) -> bool:
        """
        :return: se esse estado é ótimo.
        """
        return self.fitness == self._MAX_FITNESS

    @property
    def fitness(self) -> int:
        """
        Calcula a função fitness para esse estado no contexto do Problema das Oito Rainhas.

        :return: o número de pares únicos de rainhas que não se atacam entre si.
        """
        total = self._MAX_FITNESS
        array = list(self.array.iterate(8))

        # Remove as rainhas da mesma coluna do total
        unique_values = len(set(array))
        total -= 8 - unique_values

        for i, v0 in enumerate(array):
            # Monitora as direções que uma rainha atacada foi encontrada. Se 'topleft' for
            # `True`, por exemplo, uma rainha foi atacada na diagonal superior esquerda.
            directions = {
                'topleft': False,
                'bottomleft': False,
                'topright': False,
                'bottomright': False,
            }

            # Itera sobre os elementos à direita de v0 no vetor
            for j, v1 in enumerate(array[i + 1:], start=i + 1):
                dx = j - i
                dy = v1 - v0

                direction = ''
                direction += 'top' if dy < 0 else 'bottom'
                direction += 'left' if dx < 0 else 'right'

                # Verifica se existe alguma rainha na mesma diagonal apenas
                # se ainda não tiver ocorrido nenhum conflito nessa direção.
                if not directions[direction] and abs(dx) == abs(dy):
                    directions[direction] = True
                    total -= 1

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
        cutoff = random.choice(range(1, 7))
        array_0 = BitArray.from_list([self.array[i] if i <= cutoff else other.array[i] for i in range(8)], 3)
        array_1 = BitArray.from_list([self.array[i] if i > cutoff else other.array[i] for i in range(8)], 3)
        return State(array_0), State(array_1)

    def _uniform_cross(self, other) -> Tuple['State', 'State']:
        """
        Troca material genético com outro estado por meio de um vetor binário.

        :param other: o outro estado.
        :return: o resultado do cruzamento entre esses dois estados.
        """
        # random.getrandbits(1) == random.randint(0, 1)
        split_0 = [random.getrandbits(1) for _ in range(8)]
        array_0 = BitArray.from_list([self.array[i] if v == 0 else other.array[i] for i, v in enumerate(split_0)], 3)

        split_1 = [random.getrandbits(1) for _ in range(8)]
        array_1 = BitArray.from_list([self.array[i] if v == 0 else other.array[i] for i, v in enumerate(split_1)], 3)
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
        i0, i1 = random.sample(range(8), 2)
        self.array[i0], self.array[i1] = self.array[i1], self.array[i0]

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
