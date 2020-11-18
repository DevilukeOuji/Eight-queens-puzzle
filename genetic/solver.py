import random
from typing import List, Tuple

from genetic.state import State
from genetic.utils import pairwise


class GeneticSolver:
    """
    Representa um solver genético para o Problema das Oito Rainhas.
    """

    class Solution:
        """
        Representa uma solução (não necessariamente válida) para o Problema das Oito Rainhas.
        """

        def __init__(self, states: List[State], has_found: bool):
            """
            Constrói uma solução.

            :param states: os estados que essa solução possui.
            :param has_found: se a solução é válida (a solução pode não ser válida caso o número de gerações do solver
            alcance o máximo).
            """
            self.states = states
            self.has_found = has_found

        def best(self):
            """
            :return: o melhor dentre os estados dessa solução.
            """
            return max(self.states, key=lambda s: s.fitness)

    def __init__(
            self,
            population_size: int,
            crossing_rate: float,
            mutation_rate: float,
            generation_size: int,
    ):
        self._population_size = population_size
        self._crossing_rate = crossing_rate
        self._mutation_rate = mutation_rate
        self._generation_size = generation_size
        self.current_generation = 0

    @staticmethod
    def _create_states(size: int) -> List[State]:
        """
        Cria uma lista de estados aleatórios.

        :param size: o tamanho da lista.
        :return: a lista de estados.
        """
        return [State.random() for _ in range(size)]

    @staticmethod
    def _select_states(states: List[State], strategy: str = 'roulette') -> List[State]:
        """
        Seleciona estados para o cruzamento.

        :param states: os estados a serem selecionados.
        :param strategy: o nome da estratégia de seleção a ser utilizada, podendo ser 'roulette' para a estratégia
        roleta ou 'tournament' para a estratégia torneio.
        :return: os estados selecionados de acordo com a estratégia.
        """
        if strategy == 'roulette':
            return GeneticSolver._roulette_selection(states)
        if strategy == 'tournament':
            return GeneticSolver._tournament_selection(states)

        raise ValueError("estratégia de seleção inválida")

    @staticmethod
    def _roulette_selection(states: List[State]):
        """
        Seleciona estados por meio da estratégia roleta.

        A probabilidade de um estado ser selecionado é proporcional ao seu valor de fitness.

        :param states: os estados a serem selecionados.
        :return: os estados selecionados.
        """
        return random.choices(states, weights=[state.fitness for state in states], k=len(states))

    @staticmethod
    def _tournament_selection(states: List[State]):
        """
        Seleciona estados por meio da estratégia torneio.

        Os estados são selecionados aleatoriamente para um ringue onde o estado com maior fitness é selecionado.

        :param states: os estados a serem selecionados.
        :return: os estados selecionados.
        """
        return [max(random.choices(states, k=2), key=lambda s: s.fitness) for _ in range(len(states))]

    def solve(self) -> Solution:
        """
        Encontra uma solução para o Problema das Oito Rainhas.

        No retorno desse método, é possível acessar o atributo `current_generation` para ver a geração de parada.
        """
        self.current_generation = 0

        # População inicial
        states: List[State] = self._create_states(self._population_size)
        solution_states: List[State] = [state for state in states if state.fitness == 28]
        while not solution_states:
            self.current_generation += 1
            if self.current_generation == self._generation_size:
                return self.Solution(states, has_found=False)

            # Seleção
            selected_states: List[State] = self._select_states(states, strategy='roulette')

            # Crossover
            parent_states: List[Tuple[State, State]] = pairwise(selected_states)
            children_states: List[State] = []
            for parent_state_0, parent_state_1 in parent_states:
                if random.random() <= self._crossing_rate:
                    # Ocorre cruzamento entre os pais
                    child_state_0, child_state_1 = \
                        parent_state_0.cross(parent_state_1, strategy='cutoff')
                    children_states.append(child_state_0)
                    children_states.append(child_state_1)
                else:
                    # Os pais se tornam filhos
                    children_states.append(parent_state_0)
                    children_states.append(parent_state_1)

            # Mutação
            for state in children_states:
                if random.random() <= self._mutation_rate:
                    # Ocorre mutação no indivíduo
                    state.mutate(strategy='bitflip')

            # Junta os filhos gerados com os pais e seleciona apenas os melhores estados
            children_states.extend(states)
            # TODO complexidade O(n * log(n))
            states = sorted(children_states, key=lambda s: s.fitness, reverse=True)
            states = states[:self._population_size]

            solution_states = [state for state in states if state.fitness == 28]

        return self.Solution(solution_states, has_found=True)
