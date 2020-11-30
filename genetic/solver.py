import heapq
import random
from typing import List, Tuple

from genetic.solution import Solution
from genetic.state import State
from genetic.utils import pairwise


class GeneticSolver:
    """
    Representa um algoritmo genético para o Problema das Oito Rainhas.
    """

    def __init__(
            self,
            population_size: int,
            crossing_rate: float,
            mutation_rate: float,
            generation_size: int,
    ):
        """
        Constrói um `GeneticSolver`.

        :param population_size: tamanho da população inicial.
        :param crossing_rate: a taxa de cruzamento dos indivíduos.
        :param mutation_rate: a taxa de mutação dos indivíduos.
        :param generation_size: o número máximo de gerações desse algoritmo.
        """
        if population_size < 2:
            raise ValueError("devem existir pelo menos dois indivíduos iniciais")
        self._population_size = population_size

        if crossing_rate < 0 or crossing_rate > 1:
            raise ValueError("a taxa de cruzamento dos indivíduos deve estar entre 0 e 1")
        self._crossing_rate = crossing_rate

        if mutation_rate < 0 or mutation_rate > 1:
            raise ValueError("a taxa de mutação dos indivíduos deve estar entre 0 e 1")
        self._mutation_rate = mutation_rate

        if generation_size < 1:
            raise ValueError(" o algoritmo deve ter pelo menos uma geração")
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
        return [max(random.choices(states, k=2), key=lambda s: s.fitness) for _ in states]

    def solve(self) -> Solution:
        """
        Encontra uma solução para o Problema das Oito Rainhas.

        No retorno desse método, é possível acessar o atributo `current_generation` para ver a geração de parada.
        """
        self.current_generation = 0

        # População inicial
        states: List[State] = self._create_states(self._population_size)
        optimal_states: List[State] = [state for state in states if state.is_optimal]
        while not optimal_states:
            # Seleção
            selected_states: List[State] = self._select_states(states, strategy='tournament')

            # Crossover
            parent_states: List[Tuple[State, State]] = pairwise(selected_states)
            children_states: List[State] = []
            for parent_state_0, parent_state_1 in parent_states:
                if random.random() <= self._crossing_rate:
                    # Ocorre cruzamento entre os pais
                    child_state_0, child_state_1 = parent_state_0.cross(parent_state_1, strategy='cutoff')
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

            # Junta os filhos gerados com os pais
            children_states.extend(states)

            # Utiliza um heap máximo para selecionar apenas os melhores estados
            states = heapq.nlargest(self._population_size, children_states, key=lambda s: s.fitness)

            optimal_states = [state for state in states if state.is_optimal]
            if optimal_states:
                break

            self.current_generation += 1
            if self.current_generation == self._generation_size:
                return Solution.non_optimal(set(states))

        return Solution.optimal(set(optimal_states))
