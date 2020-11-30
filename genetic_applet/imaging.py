import glob
import math
import os
import statistics
from typing import List, Callable, Tuple, Set, Optional

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

from genetic.state import State
from genetic_applet import utils


def _is_perfect_square(x: float) -> bool:
    """
    Verifica se um número é um quadrado perfeito.

    Essa função é utilizada para verificar se o número de tabuleiros a serem inseridos em uma imagem forma um quadrado.
    Por exemplo, caso o número de tabuleiros seja 25, é possível montar uma imagem de 5x5 tabuleiros.

    :param x: o número a ser verificado.
    :return: se o número é um quadrado perfeito.
    """
    root = math.sqrt(x)
    return root == math.floor(root)


def _next_perfect_square(x: float) -> int:
    """
    Calcula o próximo quadrado perfeito depois de um número.

    Essa função é utilizada para calcular o número de tabuleiros totais na imagem tal que essa imagem forme um quadrado.
    Por exemplo, caso o número de tabuleiros seja 16, é montada uma imagem de 4x4 tabuleiros. Porém, caso o número de
    tabuleiros seja 30, deverá ser montada uma imagem de 6x6 tabuleiros (36, próximo quadrado perfeito depois de 30).

    :param x: o número base.
    :return: o próximo quadrado perfeito depois desse número.
    """
    n = int(math.sqrt(x)) + 1
    return n * n


def _copy(img: PIL.Image) -> PIL.Image:
    """
    Copia uma imagem.

    Todas as modificações feitas na cópia retornada não afetarão a imagem original.

    :param img: a imagem a ser copiada.
    :return: a cópia dessa imagem.
    """
    img_copy = PIL.Image.new("RGBA", img.size, (0x00, 0x00, 0x00, 0xFF))
    img_copy.paste(img, (0, 0), img)
    return img_copy


def _parse_color(color: int) -> Tuple[int, int, int, int]:
    """
    Interpreta uma cor no formato 0xAARRGGBB.

    :param color: a cor a ser interpretada.
    :return: uma tupla de valores no formato (RR, GG, BB, AA).
    """
    c_a = 0xFF & (color >> 24)
    c_r = 0xFF & (color >> 16)
    c_g = 0xFF & (color >> 8)
    c_b = 0xFF & (color >> 0)
    return c_r, c_g, c_b, c_a


class BoardBuilder:
    """
    Manipula a imagem de um tabuleiro.
    """

    def __init__(self, board_img: PIL.Image, queen_img: PIL.Image):
        """
        Constrói um `BoardBuilder`.

        :param board_img: a imagem contendo o tabuleiro.
        :param queen_img: a imagem contendo a rainha.
        """
        self._board_img: PIL.Image = board_img
        self._queen_img: PIL.Image = queen_img

    def _mark(self, r: int, c: int):
        """
        Cola a imagem de uma rainha em uma posição desse tabuleiro.

        :param r: a linha a ser colada.
        :param c: a coluna a ser colada.
        :raises `ValueError` se a linha e/ou a coluna forem menores que 0 ou maiores que 7.
        """
        if r < 0:
            raise ValueError("linha não pode ser negativa")
        if r > 7:
            raise ValueError("linha não pode exceder o tabuleiro")
        if c < 0:
            raise ValueError("coluna não pode ser negativa")
        if c > 7:
            raise ValueError("coluna não pode exceder o tabuleiro")

        self._board_img.paste(self._queen_img, (100 * (r + 1), 100 * (c + 1)), self._queen_img)

    def create(self, array: List[int]) -> 'BoardBuilder':
        """
        Cria um tabuleiro com rainhas.

        :param array: um vetor contendo as colunas de cada rainha.
        :return: esse objeto.
        """
        for i, value in enumerate(array):
            self._mark(i, 7 - value + 1)

        return self

    def fill(self, c0: int, c1: int, color: int = 0x80FF0000) -> 'BoardBuilder':
        """
        Pinta o intervalo de um tabuleiro de uma cor.

        :param c0: a primeira coluna do intervalo a ser pintado.
        :param c1: a segunda coluna do intervalo a ser pintado.
        :param color: a cor a ser utilizada na pintura, no formato 0xAARRGGBB.
        :return: esse objeto.
        """
        size = c1 - c0 + 1
        fill_img = PIL.Image.new("RGBA", (100 * size, 802), _parse_color(color))
        self._board_img.paste(fill_img, (100 * (c0 + 1), 100), fill_img)
        return self

    def select(self, r: int, c: int, color: int = 0x80FF0000) -> 'BoardBuilder':
        """
        Pinta uma casa do tabuleiro de uma cor.

        :param r: a linha da casa a ser pintada.
        :param c: a coluna da casa a ser pintada.
        :param color: a cor a ser utilizada na pintura, no formato 0xAARRGGBB.
        :return: esse objeto.
        """
        fill_img = PIL.Image.new("RGBA", (100, 100), _parse_color(color))
        self._board_img.paste(fill_img, (100 * (r + 1), 100 * (c + 1)), fill_img)
        return self

    def get(self) -> PIL.Image:
        """
        :return: a imagem desse tabuleiro.
        """
        return self._board_img


class BoardGroupBuilder:
    """
    Manipula a imagem de um grupo de tabuleiros.
    """

    def __init__(
            self,
            size: int,
            /,
            board_img: PIL.Image = PIL.Image.open(utils.get_res("board.png")),
            queen_img: PIL.Image = PIL.Image.open(utils.get_res("queen.png")),
            out_img_size: Tuple[int, int] = (1000, 1000),
    ):
        """
        Constrói um `BoardGroupBuilder`.

        :param size: o número de tabuleiros nesse conjunto.
        :param board_img: a imagem contendo o tabuleiro.
        :param queen_img: a imagem contendo a rainha.
        :param out_img_size: o tamanho da imagem de saída, em pixels.
        """
        if size < 1:
            raise ValueError("invalid size")

        self._size = size

        out_img_w, out_img_h = out_img_size

        sq_size = size if _is_perfect_square(size) else _next_perfect_square(size)
        self._sq_h = int(math.sqrt(sq_size))

        in_img_w, in_img_h = out_img_w // self._sq_h, out_img_h // self._sq_h

        self._in_img_size = (in_img_w, in_img_h)
        self._img = PIL.Image.new("RGBA", out_img_size, (0x00, 0x00, 0x00, 0xFF))

        self._builders = [BoardBuilder(_copy(board_img), queen_img) for _ in range(size)]

    def apply(self, index: int, action: Callable[[BoardBuilder], None]) -> 'BoardGroupBuilder':
        """
        Aplica uma operação em um tabuleiro desse grupo.

        :param index: o índice do tabuleiro nesse grupo.
        :param action: a operação a ser aplicada.
        :return: esse objeto.
        """
        action(self._builders[index])
        return self

    def get(self) -> PIL.Image:
        """
        :return: a imagem desse grupo de tabuleiros.
        """
        in_img_w, in_img_h = self._in_img_size
        for i in range(self._size):
            builder_img = self._builders[i].get()

            ii, ij = i // self._sq_h, i % self._sq_h
            copy_img = _copy(builder_img)
            copy_img.thumbnail(self._in_img_size, PIL.Image.ANTIALIAS)

            self._img.paste(copy_img, (ij * in_img_w, ii * in_img_h), copy_img)

        return self._img


class SolverListener:
    """
    Definem ações a serem realizadas para etapas do algoritmo genético.
    """

    def on_population_created(self, states: List[State]):
        """
        Define uma ação a ser realizada quando a população iniciada é criada.
        :param states: a população inicial.
        """
        pass

    def on_solution_found(self, index: int):
        """
        Define uma ação a ser realizada quando uma solução ótima é encontrada.

        :param index: o índice do melhor indivíduo.
        """
        pass

    def on_pre_population_selected(self, indexes: Set[int]):
        """
        Define uma ação a ser realizada quando a população inicial começa a ser selecionada.
        :param indexes: os índices dos indivíduos selecionados na população inicial.
        """
        pass

    def on_post_population_selected(self, selected_states: List[State]):
        """
        Define uma ação a ser realizada quando a população inicial é selecionada.
        :param selected_states: os indivíduos selecionados.
        """
        pass

    def on_hit_crossing_over(self, p0i: int, p1i: int, cutoff: int):
        """
        Define uma ação a ser realizada quando o cruzamento entre dois indivíduos ocorre.

        Quando um número aleatório entre 0-1 é menor ou igual à taxa de cruzamento definida pelo algoritmo, o cruzamento
        entre dois indivíduos ocorre. Nesse caso, dois novos indivíduos são gerados (filhos).

        :param p0i: o índice do primeiro indivíduo na lista de indivíduos.
        :param p1i: o índice do segundo indivíduo na lista de indivíduos.
        :param cutoff: o ponto de corte do cruzamento.
        """
        pass

    def on_miss_crossing_over(self, p0i: int, p1i: int):
        """
        Define uma ação a ser realizada quando o cruzamento entre dois indivíduos não ocorre.

        Quando um número aleatório entre 0-1 é maior do que taxa de cruzamento definida pelo algoritmo, o cruzamento
        entre dois indivíduos não ocorre. Nesse caso, os dois indivíduos se tornam filhos.

        :param p0i: o índice do primeiro indivíduo na lista de indivíduos.
        :param p1i: o índice do segundo indivíduo na lista de indivíduos.
        """
        pass

    def on_post_crossing_over(self, children_states: List[State]):
        """
        Define uma ação a ser realizada após o cruzamento de todos os indivíduos.

        :param children_states: os indivíduos resultantes do cruzamento.
        """
        pass

    def on_mutate(self, index: int):
        """
        Define uma ação a ser realizada quando um indivíduo sofre mutação.

        Um indivíduo sofre mutação quando um número aleatório entre 0-1 é menor ou igual à taxa de mutação definida pelo
        algoritmo.

        :param index: o índice do indivíduo mutante na lista de indivíduos.
        """
        pass

    def on_post_mutate(self, children_states: List[State]):
        """
        Define uma ação a ser realizada após a etapa de mutação.

        :param children_states: os indivíduos resultantes da mutação.
        """
        pass

    def on_merging(self, merged_states: List[State]):
        """
        Define uma ação a ser realizada antes da etapa de seleção natural.

        Nessa etapa, os pais são mesclados com os filhos e, desse grupo, apenas os melhores indivíduos sobreviverão.

        :param merged_states: os indíviduos pais e filhos.
        """
        pass

    def on_natural_selection(self, merged_states: List[State], indexes: List[int]):
        """
        Define uma ação a ser realizada na etapa de seleção natural.

        :param merged_states: os indivíduos pais e filhos.
        :param indexes: os índices dos indivíduos selecionados do grupo de indivíduos pais e filhos.
        """
        pass


class BoardBuilderListener(SolverListener):
    """
    Um `SolverListener` que cria imagens representando cada etapa.
    """

    @staticmethod
    def enable(size: int):
        """
        Inicializa o listener global desse módulo com uma instância desse objeto.

        :param size: o tamanho da população inicial.
        """
        global listener
        listener = BoardBuilderListener(size)

    @staticmethod
    def _compact():
        """
        Transforma os arquivos .png no diretório local 'imgs' em .gif.

        Caso o diretório não exista, nenhuma ação é realizada.
        """
        dir_path = utils.get_child("imgs")
        if not os.path.isdir(dir_path):
            return

        input_pattern = os.path.join(dir_path, "output_*.png")
        output_path = os.path.join(dir_path, "output.gif")
        img, *imgs = [PIL.Image.open(f) for f in sorted(glob.glob(input_pattern))]
        img.save(fp=output_path, format='GIF', append_images=imgs, save_all=True, duration=1000, loop=0)

    @staticmethod
    def _clean():
        """
        Remove os arquivos .png do diretório local 'imgs'.

        Caso o diretório não exista, nenhuma ação é realizada.
        """
        dir_path = utils.get_child("imgs")
        if not os.path.isdir(dir_path):
            return

        pattern = os.path.join(dir_path, "*.png")
        for fp in glob.glob(pattern):
            os.remove(fp)

    def __init__(self, size: int):
        """
        Constrói um `BoardBuilderListener`.

        :param size: o tamanho da população inicial.
        """
        self._size = size

        self._builder: Optional[BoardGroupBuilder] = None
        self._index: int = 0

        self._cutoffs = []

    def _save(self, title: str = "", subtitle: str = ""):
        """
        Salva uma imagem.

        :param title: o título da imagem.
        :param subtitle: o subtítulo da imagem.
        """
        img = self._builder.get()

        img_w, img_h = img.size
        new_img = PIL.Image.new("RGBA", (img_w, img_h + 200), _parse_color(0xFFFFFFFF))
        new_img.paste(img, (0, 200), img)

        draw = PIL.ImageDraw.Draw(new_img)
        for pos, text, size in (((10, 10), title, 36), ((10, 60), subtitle, 30)):
            draw.text(
                pos,
                text,
                _parse_color(0xFF000000),
                font=PIL.ImageFont.truetype(utils.get_res("arial.ttf"), size),
            )

        dir_path = utils.get_child("imgs")
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)

        filename = os.path.join(dir_path, f"output_{self._index:07d}.png")
        new_img.save(filename)
        self._index += 1

    def on_population_created(self, states: List[State]):
        self._builder = BoardGroupBuilder(self._size)
        for i, state in enumerate(states):
            self._builder.apply(i, lambda b: b.create([v + 1 for v in state.array.iterate(8)]))
        self._save(
            "Criando população inicial",
            f"Melhor fitness: {max(states, key=lambda s: s.fitness).fitness}\n"
            f"Pior fitness: {min(states, key=lambda s: s.fitness).fitness}\n"
            f"Média de fitness: {statistics.mean(s.fitness for s in states)}\n"
            f"Tamanho: {len(states)}\n"
        )
        self._cache = states

    def on_solution_found(self, index: int):
        self._builder.apply(index, lambda b: b.fill(0, 7, color=0x80FFFF00))
        self._save("Solução ótima encontrada")

    def on_pre_population_selected(self, indexes: Set[int]):
        for index in indexes:
            self._builder.apply(index, lambda b: b.fill(0, 7, color=0x5200FF00))

        # noinspection PyTypeChecker
        states: List[State] = self._cache
        self._save(
            "Selecionando melhores indivíduos",
            f"Melhor fitness: {max(states, key=lambda s: s.fitness).fitness}\n"
            f"Pior fitness: {min(states, key=lambda s: s.fitness).fitness}\n"
            f"Média de fitness: {statistics.mean(s.fitness for s in states)}\n"
            f"Método: Torneio ({len(indexes)} indivíduos distintos selecionados)\n"
        )
        self._cache = indexes

    def on_post_population_selected(self, selected_states: List[State]):
        self._builder = BoardGroupBuilder(self._size)
        for i, state in enumerate(selected_states):
            self._builder.apply(i, lambda b: b.create([v + 1 for v in state.array.iterate(8)]))

        indexes = self._cache
        self._save(
            "Selecionando melhores indivíduos",
            f"Melhor fitness: {max(selected_states, key=lambda s: s.fitness).fitness}\n"
            f"Pior fitness: {min(selected_states, key=lambda s: s.fitness).fitness}\n"
            f"Média de fitness: {statistics.mean(s.fitness for s in selected_states)}\n"
            f"Método: Torneio ({len(indexes)} indivíduos distintos selecionados)\n",
        )
        self._cache = selected_states

    def on_hit_crossing_over(self, p0i: int, p1i: int, cutoff: int):
        self._builder \
            .apply(p0i, lambda b: b.fill(0, cutoff).fill(cutoff + 1, 7, color=0x800000FF)) \
            .apply(p1i, lambda b: b.fill(0, cutoff, color=0x800000FF).fill(cutoff + 1, 7))

        self._cutoffs.append(p0i)
        self._cutoffs.append(p1i)

    def on_miss_crossing_over(self, p0i: int, p1i: int):
        self._builder \
            .apply(p0i, lambda b: b.fill(0, 8, color=0x52000000)) \
            .apply(p1i, lambda b: b.fill(0, 8, color=0x52000000))

        self._cutoffs.append(None)
        self._cutoffs.append(None)

    def on_post_crossing_over(self, children_states: List[State]):
        states = self._cache
        self._save(
            "Realizando cruzamento (1)",
            f"Melhor fitness: {max(states, key=lambda s: s.fitness).fitness}\n"
            f"Pior fitness: {min(states, key=lambda s: s.fitness).fitness}\n"
            f"Média de fitness: {statistics.mean(s.fitness for s in states)}\n"
            "Taxa de cruzamento: 80%\n",
        )

        self._builder = BoardGroupBuilder(self._size)
        for i, state in enumerate(children_states):
            cutoff = self._cutoffs[i]
            color = 0x00000000 if cutoff is None else 0x52FF0000 if i % 2 == 0 else 0x520000FF
            self._builder.apply(i, lambda b: b.create([v + 1 for v in state.array.iterate(8)]).fill(0, 7, color=color))
        self._save(
            "Realizando cruzamento (2)",
            f"Melhor fitness: {max(children_states, key=lambda s: s.fitness).fitness}\n"
            f"Pior fitness: {min(children_states, key=lambda s: s.fitness).fitness}\n"
            f"Média de fitness: {statistics.mean(s.fitness for s in children_states)}\n"
            "Taxa de cruzamento: 80%\n",
        )

        self._builder = BoardGroupBuilder(self._size)
        for i, state in enumerate(children_states):
            self._builder.apply(i, lambda b: b.create([v + 1 for v in state.array.iterate(8)]))
        self._save(
            "Realizando cruzamento (2)",
            f"Melhor fitness: {max(children_states, key=lambda s: s.fitness).fitness}\n"
            f"Pior fitness: {min(children_states, key=lambda s: s.fitness).fitness}\n"
            f"Média de fitness: {statistics.mean(s.fitness for s in children_states)}\n"
            "Taxa de cruzamento: 80%\n",
        )

        self._cutoffs = []

    def on_mutate(self, index: int):
        self._builder.apply(index, lambda b: b.fill(0, 7, color=0x520000FF))

    def on_post_mutate(self, children_states: List[State]):
        self._save(
            "Realizando mutação (1)",
            f"Melhor fitness: {max(children_states, key=lambda s: s.fitness).fitness}\n"
            f"Pior fitness: {min(children_states, key=lambda s: s.fitness).fitness}\n"
            f"Média de fitness: {statistics.mean(s.fitness for s in children_states)}\n"
            "Taxa de mutação: 3%\n",
        )

        self._builder = BoardGroupBuilder(self._size)
        for i, state in enumerate(children_states):
            self._builder.apply(i, lambda b: b.create([v + 1 for v in state.array.iterate(8)]))
        self._save(
            "Realizando mutação (2)",
            f"Melhor fitness: {max(children_states, key=lambda s: s.fitness).fitness}\n"
            f"Pior fitness: {min(children_states, key=lambda s: s.fitness).fitness}\n"
            f"Média de fitness: {statistics.mean(s.fitness for s in children_states)}\n"
            "Taxa de mutação: 3%\n"
        )

    def on_merging(self, merged_states: List[State]):
        self._builder = BoardGroupBuilder(self._size * 2)
        for i, state in enumerate(merged_states):
            self._builder.apply(i, lambda b: b.create([v + 1 for v in state.array.iterate(8)]))
        self._save(
            "Juntando indivíduos pais/filhos",
            f"Melhor fitness: {max(merged_states, key=lambda s: s.fitness).fitness}\n"
            f"Pior fitness: {min(merged_states, key=lambda s: s.fitness).fitness}\n"
            f"Média de fitness: {statistics.mean(s.fitness for s in merged_states)}\n",
        )

    def on_natural_selection(self, merged_states: List[State], indexes: List[int]):
        self._builder = BoardGroupBuilder(self._size * 2)
        for i, state in enumerate(merged_states):
            self._builder.apply(i, lambda b: b.create([v + 1 for v in state.array.iterate(8)]))
            if i in indexes:
                self._builder.apply(i, lambda b: b.fill(0, 7, color=0x5200FF00))
        self._save(
            "Selecionando melhores indíviduos",
            f"Melhor fitness: {max(merged_states, key=lambda s: s.fitness).fitness}\n"
            f"Pior fitness: {min(merged_states, key=lambda s: s.fitness).fitness}\n"
            f"Média de fitness: {statistics.mean(s.fitness for s in merged_states)}\n",
        )

        self._builder = BoardGroupBuilder(self._size)
        selected_states = [merged_states[i] for i in indexes]
        for i, state in enumerate(selected_states):
            self._builder.apply(i, lambda b: b.create([v + 1 for v in state.array.iterate(8)]))
        self._save(
            "Criando nova geração",
            f"Melhor fitness: {max(selected_states, key=lambda s: s.fitness).fitness}\n"
            f"Pior fitness: {min(selected_states, key=lambda s: s.fitness).fitness}\n"
            f"Média de fitness: {statistics.mean(s.fitness for s in selected_states)}\n",
        )


listener: SolverListener = SolverListener()
