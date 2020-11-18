from genetic.solver import GeneticSolver


def main():
    solver = GeneticSolver(
        population_size=20,
        crossing_rate=0.8,
        mutation_rate=0.03,
        generation_size=1000,
    )

    for i in range(1, 51):
        print(f'{i:02d}.', end=' ')

        result = solver.solve()
        if not result.has_found:
            print(f'Número de gerações esgotado, melhor estado: {result.best()}')
            continue
        print(f'Solução {result.states} encontrada na geração {solver.current_generation}')


if __name__ == '__main__':
    main()
