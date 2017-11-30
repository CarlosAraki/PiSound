# PiSound
Desenvolvido para a disciplina de Introdução ao Projeto de Sistemas Embarcados no segundo semestre de 2017 por:
 
+ Carlos Vinicius Araki Oliveira
+ Dener Stassun Christinele
+ Iago Agrella Fancio
+ Paulo Victor da Silva Lage
+ Raul de Oliveira Santos Pereira


## Resumo do Projeto
O trabalho consistiu em projetar e construir um instrumento musical tocado a partir do movimento de objetos (um objeto azul e um verde) em frente a uma webcam. Para alcançar nosso objetivo, separamos o projeto em três módulos:

__Processamento de Imagem:__ Escrito em python utilizando a biblioteca OpenCV, é responsável por captar uma imagem da webcam, realizar a filtragem na frame capturada para obter o centróide dos pixels azuis e o centróide dos pixels verdes da frame e enviar estes dados para a aplicação central. Para cumprir os requisitos temporais de execução, este módulo faz uso de multithreading para acelerar o processamento das frames.

__Processamento de Som:__ Responsável por sintetizar sons em tempo real de frequência e amplitude determinadas por um input externo. Foi escrito na linguagem de programação de som CSound, escolhida por ter uma extensa documentação (existe desde 1985), por prover grande liberdade e potencial na síntese de som e por permitir saída de audio em tempo real.

__Aplicação Central:__ Escrita em C, é responsável por inicializar os outros módulos e fazer a ponte entre o módulo de imagem e o módulo de som, criando os devidos canais de comunicação para obter os dados do processamento de imagem e para enviar dados para o processamento de som. Além disto, converte as coordenadas recebidas do processamento de imagem em devidos valores de frequência e amplitude. As faixas de frequência e amplitude que serão passadas para o processamento de som, além da ativação e volume dos "instrumentos" podem ser configuradas e impressos na tela em tempo real a partir de uma linha de comando interativa gerenciado pela aplicação central.


## Compilando
Dependências:

+ OpenCV 3.3
+ CSound
+ Flex, Bison
+ Python 2.7

Primeiro, na pasta _src/_ edite o Makefile para especificar o caminho da shared library do CSound (Alterar flag -L). Após isto, execute:  
```
make
```

## Executando
Em _src/_, execute:  
```
./main instrumentos.csd
```


## Limitações, trabalhos futuros
__Latência na saída de som:__ A saída do som em relação ao movimento das mãos tem uma latência que apesar de não ser muito notável para o observador, é perceptível para quem está tocando o instrumento. Algumas possíveis soluções seriam uma maior otimização do processamento de imagem e o uso de um driver/servidor dedicado de audio como o Jackd2 ao invés do que foi utilizado (portaudio)

__Sofisticação da aplicação central__ O resultado final do projeto resulta em um instrumento de som contínuo, tanto no sentido de que não há maneira de sintetizar instrumentos com ataque (como violão, piano) como no sentido em que a alteração das frequências se dá de forma contínua e não de forma discreta (como aumentar de meio-tom em meio-tom). A aplicação central poderia ser trabalhada para permitir que estas possibilidades fossem configuráveis em tempo real.

__Síntese de som:__ Não consiguimos dar o enfoque desejado na síntese de som e assim, ao fim do projeto, as únicas opções de síntese eram ondas senoidais, ondas triangulares e ondas quadradas. Um aprofundamento maior no uso do CSound e na teoria de síntese poderia trazer a síntese de ondas de som rico e completo.