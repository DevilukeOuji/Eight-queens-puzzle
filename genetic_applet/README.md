# GeneticSolverApplet

Esse applet permite visualizar por meio de imagens os passos executados por um algoritmo
genético para resolver o Problema das Oito Rainhas. Cada imagem contém um conjunto de
tabuleiros (a população de indivíduos) e inclui passos como seleção, mutação e cruzamento.

![](https://i.imgur.com/2iLQkan.png)

## Requerimentos

- Python (3.7+)

- [Biblioteca `Pillow`](https://pillow.readthedocs.io/en/latest/installation.html) (5.2+)

## Uso

Para utilizar o applet, basta executar o arquivo **main.py** presente nesse diretório.
No Windows, por exemplo, pode-se abrir um prompt de comando e executar os comandos

    cd C:\diretorio\do\projeto
    python -m genetic_applet.main
    
### Seeds
    
Ao abrir o applet, será pedida uma [seed](https://en.wikipedia.org/wiki/Random_seed).
Basicamente, cada algoritmo que gera números (pseudo) aleatórios baseia-se num número
inicial para a sua execução, que é a seed. Para garantir que os mesmos números aleatórios
não sejam gerados em execuções diferentes do mesmo programa, os algoritmos utilizam por
padrão a seed como sendo o tempo atual em milissegundos (assim, execuções em tempos
diferentes levam a números aleatórios diferentes). 

Como o algoritmo genético utiliza números aleatórios em grande escala (como ao escolher
um indivíduo para a mutação ou selecionar um ponto de corte para o cruzamento), definir
uma seed previamente faz com que o algoritmo sempre dê os mesmos resultados, não importa
quantas vezes o programa seja executado. Algumas seeds levam o algoritmo a encontrar uma
solução ótima em poucas gerações, em outras o algoritmo atinge o limite máximo de gerações.
Abaixo há uma tabela com algumas seeds e o número de gerações na qual o algoritmo encontra
a solução ótima para o Problema das Oito Rainhas:

| Seed 	| Nº gerações 	| Seed 	| Nº gerações 	|
|------	|-------------	|------	|-------------	|
| 62   	| 9           	| 347  	| 12          	|
| 121  	| 11          	| 348  	| 4           	|
| 165  	| 6           	| 515  	| 7           	|
| 172  	| 8           	| 585  	| 12          	|
| 206  	| 25          	| 625  	| 1           	|
| 263  	| 2           	| 687  	| 2           	|
| 267  	| 5           	| 775  	| 18          	|

**AVISO:** O applet gera cerca de 10 imagens para cada geração. A maioria das seeds atinge
o limite máximo de gerações (100). Portanto, caso uma seed atinja esse limite, levará um 
tempo até que o applet gere essas 1000 imagens.

### Passos

Quando o applet gerar as imagens correspondentes à execução do algoritmo, é possível 
visualizar o próximo passo clicando no botão "Próximo" ou ir para o passo anterior clicando
no botão "Anterior".

![](https://i.imgur.com/SF2QpqF.png)

Para cada passo, é possível visualizar o seu título e a sua descrição, além de informações sobre
o melhor, o pior e a média dos valores da função *fitness* dos indivíduos atuais.

1. O passo de seleção seleciona os melhores indivíduos e os colore de verde. Como a estratégia
de seleção utilizada é o torneio, o mesmo indivíduo pode ser selecionado mais de uma vez.

2. O passo de cruzamento separa os indivíduos em duplas, escolhe um ponto de corte aleatório e
cria indivíduos a partir desse ponto. Esse passo é dividido em duas etapas: a primeira
encontra um ponto de corte (nesse caso, uma coluna do tabuleiro) para dois indivíduos
consecutivos e colore a esquerda dessa coluna como vermelho e a direita como azul para o
primeiro indivíduo e vice-versa; a segunda mostra os indivíduos criados em vermelho para o
primeiro indivíduo e em azul para o segundo. Como há uma taxa de cruzamento (80%), alguns
indivíduos podem não ser cruzados: esses aparecem em cinza na primeira etapa.

3. O passo de mutação altera um ou mais indivíduos aleatoriamente. Caso um indivíduo seja 
escolhido para a mutação, ele é colorido como azul. Como há uma taxa de mutação (3%), alguns
indivíduos podem não ser mudados: esses aparecem em branco em ambas as etapas.

4. O passo de seleção natural junta os indivíduos da etapa 1 com os gerados da etapa 2. Os
melhores (que possuem o maior valor da função *fitness*) são selecionados para a nova 
geração.

Os passos se repetem até que uma solução ótima seja encontrada ou o número de gerações
alcance o limite.