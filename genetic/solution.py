from typing import Set

from genetic.state import State


class Solution:
    """
    Representa uma solução (não necessariamente ótima) para o Problema das Oito Rainhas.
    """

    @classmethod
    def optimal(cls, states: Set[State]):
        """
        Constrói uma solução ótima.

        :param states: os estados ótimos encontrados.
        """
        return cls(states, has_found=True)

    @classmethod
    def non_optimal(cls, states: Set[State]):
        """
        Constrói uma solução não ótima.

        Essa solução pode ser retornada pelo algoritmo caso o número de gerações máximo seja alcançado.

        :param states: os estados não ótimos encontrados.
        """
        return cls(states, has_found=False)

    def __init__(self, states: Set[State], has_found: bool):
        """
        Constrói uma solução.

        :param states: os estados que essa solução possui.
        :param has_found: se os estados desse solução são ótimos.
        """
        self.states = states
        self.has_found = has_found

    def best(self):
        """
        :return: o melhor dentre os estados dessa solução.
        """
        return max(self.states, key=lambda s: s.fitness)
