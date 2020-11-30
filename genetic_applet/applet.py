import os
import random
import shutil
import threading
import tkinter as tk
import tkinter.ttk as ttk
from typing import Optional

from PIL import Image
from PIL import ImageTk

from genetic.solver import GeneticSolver
from genetic_applet import utils
from genetic_applet.solver import AppletGeneticSolver, GeneticSolverListener


def run():
    """
    Executa o applet.
    """
    root = tk.Tk()
    Applet(root)
    root.mainloop()


def _get_generations():
    """
    :return: o número de gerações que o algoritmo genético encontra uma solução ótima.
    """
    solver: GeneticSolver = GeneticSolver(
        population_size=20,
        crossing_rate=0.8,
        mutation_rate=0.03,
        generation_size=100,
    )
    solver.solve()
    return solver.current_generation


class Applet(tk.Frame, GeneticSolverListener):
    """
    Interface gráfica do applet do algoritmo genético.
    """

    def __init__(self, root, **kwargs):
        super().__init__(**kwargs)
        self.grid()

        self._img_number: Optional[int] = None
        self._img_max_number: Optional[int] = None

        self._root = root
        self._root.title("Genetic Solver Applet")
        tk.Label(self._root, text="Insira uma seed:").grid(row=0, column=0)

        self._w_txt_seed = tk.Text(self._root, width=20, height=1)
        self._w_txt_seed.grid(row=0, column=1, columnspan=1)

        self._w_btn_create = tk.Button(self._root, text="Criar", command=self._on_create_seed)
        self._w_btn_create.grid(row=0, column=2)

        self._w_lbl_img = tk.Label(self._root)

        self._w_btn_previous = tk.Button(self._root, text="Anterior", command=self.on_previous)
        self._w_btn_next = tk.Button(self._root, text="Próximo", command=self.on_next)

    def _solve(self):
        """
        Remove imagens já existentes e cria novas imagens para serem mostradas pelo applet.

        Esse método é rodado em uma thread diferente da thread de interface gráfica.
        """
        dir_path = utils.get_child("imgs")
        if os.path.isdir(dir_path):
            shutil.rmtree(dir_path)

        solver = AppletGeneticSolver(
            population_size=20,
            crossing_rate=0.8,
            mutation_rate=0.03,
            generation_size=100,
            generate_images=True,
            listener=self,
        )

        solver.solve()

    def _on_create_seed(self):
        """
        Define uma ação a ser realizada quando o usuário insere uma seed.
        """
        self._root.focus()
        self._w_lbl_img.grid_forget()

        seed = self._w_txt_seed.get("1.0", tk.END)
        try:
            seed = int(seed)
        except ValueError:
            seed = hash(seed)

        random.seed(seed)
        gens = _get_generations()

        random.seed(seed)
        self._var_gen = tk.IntVar()
        self._w_pbr_gens = ttk.Progressbar(
            self._root,
            orient=tk.HORIZONTAL,
            maximum=gens + 1,
            variable=self._var_gen,
            mode="determinate",
        )
        self._w_pbr_gens.grid(row=2, column=0, columnspan=3)

        threading.Thread(target=self._solve).start()

    def on_new_generation(self, number: int):
        """
        Atualiza a barra de progresso com o valor da geração atual do algoritmo.
        :param number: o valor da geração atual.
        """
        super().on_new_generation(number)
        self._var_gen.set(number)

    def _get_img_tk(self):
        """
        :return: a imagem a ser mostrada pelo applet.
        """
        dir_path = utils.get_child("imgs")
        filepath = os.path.join(dir_path, f"output_{self._img_number:07d}.png")
        img = Image.open(filepath)
        img = img.resize((600, 600), Image.ANTIALIAS)
        return ImageTk.PhotoImage(img)

    def _fetch_image(self):
        """
        Atualiza a imagem mostrada pelo applet.
        """
        img_tk = self._get_img_tk()
        self._w_lbl_img.configure(image=img_tk)
        self._w_lbl_img.image = img_tk

    def on_previous(self):
        """
        Define uma ação a ser realizada quando o usuário pressiona o botão de passo anterior.
        """
        if self._img_number == 1:
            self._w_btn_previous.grid_forget()
        if self._img_number == self._img_max_number:
            self._w_btn_next.grid(row=2, column=2)

        self._img_number -= 1
        self._fetch_image()

    def on_next(self):
        """
        Define uma ação a ser realizada quando o usuário pressiona o botão de próximo passo.
        """
        if self._img_number == 0:
            self._w_btn_previous.grid(row=2, column=0)
        if self._img_number == self._img_max_number - 1:
            self._w_btn_next.grid_forget()

        self._img_number += 1
        self._fetch_image()

    def on_finish(self):
        """
        Mostra as imagens geradas pelo algoritmo.
        """
        super().on_finish()
        dir_path = utils.get_child("imgs")
        self._img_max_number = len(os.listdir(dir_path)) - 1

        self._w_pbr_gens.grid_forget()
        self._w_btn_next.grid(row=2, column=2)
        self._w_btn_previous.grid_forget()

        self._w_lbl_img.grid(row=1, column=0, columnspan=3)
        self._img_number = 0
        self._fetch_image()
