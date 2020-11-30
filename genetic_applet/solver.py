import heapq
import random
from typing import List, Tuple, Optional

from genetic.solution import Solution
from genetic.solver import GeneticSolver
from genetic.state import State
from genetic.utils import pairwise
from genetic_applet import imaging
from genetic_applet.state import AppletState
from genetic_applet.utils import IndexedObject


class GeneticSolverListener:
    """
    Escuta ações de um algoritmo genético.
    """

    def on_new_generation(self, number: int):
        """
        Define uma ação a ser realizada quando um algoritmo genético passa para a próxima geração.
        :param number: o número da geração atual do algoritmo.
        """
        pass

    def on_finish(self):
        """
        Define uma ação a ser realizada quando o algoritmo genético termina.

        O algoritmo genético termina ou quando é encontrada uma solução ótima ou quando o limite de gerações é atingido.
        """
        pass


class AppletGeneticSolver(GeneticSolver):
    """
    Modificação de um algoritmo genético para funcionar de acordo com o applet.
    """

    def __init__(
            self,
            population_size: int,
            crossing_rate: float,
            mutation_rate: float,
            generation_size: int,
            generate_images: bool,
            listener: Optional[GeneticSolverListener] = None,
    ):
        """
        Constrói um `AppletGeneticSolver`.

        :param generate_images: se imagens devem ser geradas quando esse algoritmo estiver executando.
        :param listener: o listener a ser notificado quando esse algoritmo estiver executando.
        """
        super().__init__(population_size, crossing_rate, mutation_rate, generation_size)
        self._generate_images = generate_images
        self._listener = listener

    @staticmethod
    def _create_states(size: int) -> List[State]:
        return [AppletState.random() for _ in range(size)]

    @staticmethod
    def _tournament_selection(states: List[State]) -> List[State]:
        selected_states = []
        indexes = set()
        for _ in states:
            state = max(random.choices(states, k=2), key=lambda s: s.fitness)
            indexes.add(states.index(state))
            selected_states.append(state)

        imaging.listener.on_pre_population_selected(indexes)
        return selected_states

    def solve(self) -> Solution:
        if not self._generate_images:
            return super().solve()

        self.current_generation = 0
        imaging.BoardBuilderListener.enable(self._population_size)

        states: List[State] = self._create_states(self._population_size)
        imaging.listener.on_population_created(states)

        optimal_states: List[State] = [state for state in states if state.is_optimal]
        while not optimal_states:
            selected_states: List[State] = AppletGeneticSolver._tournament_selection(states)
            imaging.listener.on_post_population_selected(selected_states)

            parent_states: List[Tuple[State, State]] = pairwise(selected_states)
            children_states: List[State] = []
            for i, (parent_state_0, parent_state_1) in enumerate(parent_states):
                p0i, p1i = i * 2, i * 2 + 1
                if random.random() <= self._crossing_rate:
                    child_state_0, child_state_1, cutoff = parent_state_0.cross(parent_state_1, strategy='cutoff')
                    imaging.listener.on_hit_crossing_over(p0i, p1i, cutoff)
                    children_states.append(child_state_0)
                    children_states.append(child_state_1)
                else:
                    imaging.listener.on_miss_crossing_over(p0i, p1i)
                    children_states.append(parent_state_0)
                    children_states.append(parent_state_1)
            imaging.listener.on_post_crossing_over(children_states)

            for i, state in enumerate(children_states):
                if random.random() <= self._mutation_rate:
                    imaging.listener.on_mutate(i)
                    state.mutate(strategy='bitflip')
            imaging.listener.on_post_mutate(children_states)

            children_states.extend(states)
            imaging.listener.on_merging(children_states)

            wrappers = heapq.nlargest(
                self._population_size,
                IndexedObject.wrap(children_states),
                key=lambda s: s.value.fitness
            )

            states = IndexedObject.unwrap_values(wrappers)
            imaging.listener.on_natural_selection(children_states, IndexedObject.unwrap_indexes(wrappers))

            optimal_states = [state for state in states if state.is_optimal]
            if optimal_states:
                break

            self.current_generation += 1
            if self._listener is not None:
                self._listener.on_new_generation(self.current_generation)
            if self.current_generation == self._generation_size:
                if self._listener is not None:
                    self._listener.on_finish()
                return Solution.non_optimal(set(states))

        imaging.listener.on_solution_found(max(enumerate(states), key=lambda t: t[1].fitness)[0])
        if self._listener is not None:
            self._listener.on_finish()
        return Solution.optimal(set(optimal_states))
