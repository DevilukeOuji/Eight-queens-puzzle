import os
from typing import List, TypeVar

T = TypeVar('T')


def get_res(name: str) -> str:
    """
    Calcula o caminho absoluto de um recurso na pasta /genetic_applet/res.

    :param name: o nome do recurso.
    :return: o caminho absoluto do recurso
    """
    filepath = os.path.abspath(__file__)
    parent_path, _ = os.path.split(filepath)
    return os.path.join(parent_path, "res", name)


def get_child(name: str) -> str:
    """
    Calcula o caminho absoluto de um arquivo na pasta /genetic_applet.

    :param name: o nome do arquivo.
    :return: o caminho absoluto do arquivo.
    """
    filepath = os.path.abspath(__file__)
    parent_path, _ = os.path.split(filepath)
    return os.path.join(parent_path, name)


class IndexedObject:
    """
    Representa um objeto indexado.
    """

    def __init__(self, index: int, value: T):
        """
        Constrói um `IndexedObject`.

        :param index: o índice desse objeto.
        :param value: o conteúdo desse objeto.
        """
        self.index = index
        self.value = value

    @staticmethod
    def wrap(values: List[T]) -> List['IndexedObject']:
        """
        Indexa os valores de uma lista.

        :param values: os valores a serem indexados.
        :return: os objetos indexados.
        """
        return [IndexedObject(i, value) for i, value in enumerate(values)]

    @staticmethod
    def unwrap_indexes(wrappers: List['IndexedObject']) -> List[int]:
        """
        Retorna os índices de uma lista de objetos indexados.

        :param wrappers: os objetos indexaos.
        :return: os índices desses objetos. Não serão retornados os índices desses objetos na lista passada como
            parâmetro, mas sim os índices do seus atributos `index`.
        """
        return [wrapper.index for wrapper in wrappers]

    @staticmethod
    def unwrap_values(wrappers: List['IndexedObject']) -> List[T]:
        """
        Retorna os conteúdos de uma lista de objetos indexados.

        :param wrappers: os objetos indexados.
        :return: os conteúdos desses objetos.
        """
        return [wrapper.value for wrapper in wrappers]
