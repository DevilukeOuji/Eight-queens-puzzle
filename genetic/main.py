import random
import time

from genetic.solver import GeneticSolver


def main():
    random.seed(0)

    solver = GeneticSolver(
        population_size=20,
        crossing_rate=0.8,
        mutation_rate=0.03,
        generation_size=1000,
    )

    with open('output.csv', 'w+') as f:
        print('ITER;BEST;FITNESS;TIME;GEN', file=f)
        for i in range(1, 51):
            print(f'{i}', end=';', file=f)

            start_time = time.time()
            result = solver.solve()
            end_time = time.time()
            time_repr = f'{int((end_time - start_time) * 1000)}'

            best = result.best()
            print(f'{best}', end=';', file=f)
            print(f'{best.fitness}', end=';', file=f)
            print(time_repr, end=';', file=f)
            print(f'{solver.current_generation}', file=f)


if __name__ == '__main__':
    main()
