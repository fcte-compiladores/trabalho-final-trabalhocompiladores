# Compilador de Expressões Regulares para Autômatos Finitos

## Integrantes

* Igor Justino — Matrícula: 211061897 — Turma: 01

## Introdução

Este projeto acadêmico implementa um compilador que traduz expressões regulares em autômatos finitos não-determinísticos (AFND) e determinísticos (AFD), seguindo as etapas clássicas da construção de compiladores e os princípios da teoria de linguagens formais.

### Estratégias e Algoritmos

* **Algoritmo de Thompson**: Para gerar AFNDs a partir de árvores sintáticas abstratas (AST), construindo componentes para cada operação regular (união, concatenação, fecho de Kleene) e os combinando de maneira estruturada.
* **Algoritmo de Subconjuntos**: Para determinizar o AFND em um AFD, calculando fechos epsilon e criando novos estados determinísticos.

### Sintaxe Suportada

A linguagem aceita expressões com os seguintes operadores:

* Concatenação: `ab` — reconhece a sequência “ab”
* União: `a|b` — reconhece “a” ou “b”
* Fecho de Kleene: `a*` — reconhece zero ou mais “a”
* Agrupamento: `(a|b)*` — aplica fecho sobre a união

Exemplos de uso:

| Expressão | Aceita           |                                  |
| --------- | ---------------- | -------------------------------- |
| `a`       | “a”              |                                  |
| \`a       | b\`              | “a”, “b”                         |
| `a*`      | “”, “a”, “aa”, … |                                  |
| \`(a      | b)\*\`           | qualquer combinação de “a” e “b” |

## Instalação

### Requisitos

* Python 3.6 ou superior

### Passos

```bash
# Clone o projeto
git clone <URL_DO_REPOSITORIO>
cd Trabalho-Compiladores1

# Verifique a versão do Python
python3 --version

# Execute ajuda do compilador
python3 src/main.py --help
```

### Execução

```bash
# Compilar expressão simples
python3 src/main.py "a*"

# Compilar com geração do AFD
printf3 src/main.py "(a|b)*" --dfa

# Testar strings
python3 src/main.py "a*" --test "" "a" "aa"

# Executar testes unitários
python3 -m unittest discover tests/
```

## Exemplos de Uso

O compilador suporta diversos tipos de expressões regulares:

```bash
# Exemplos básicos
python3 src/main.py "a" --test "a" "b"
python3 src/main.py "a|b" --test "a" "b" "c"
python3 src/main.py "ab" --test "ab" "ba" "a"
python3 src/main.py "a*" --test "" "a" "aa" "b"
python3 src/main.py "(a|b)*" --test "ab" "ba" "aabb" ""

# Exemplos avançados
python3 src/main.py "((a|b)*c(d|e)*)*" --dfa
python3 src/main.py "a*b*c*d*e*" --dfa --test "" "abcde" "aaabbcccdddeee"
```

## Referências

* **Aho et al., Compilers: Principles, Techniques, and Tools** — Base para os conceitos de compilação e determinização.
* **Hopcroft et al., Introduction to Automata Theory** — Fundamentação sobre linguagens formais, AFND, AFD.
* **Thompson, 1968** — Artigo original do algoritmo de Thompson.

As contribuições originais incluem integração dos algoritmos em um pipeline modular, interface de linha de comando e visualização textual.

## Estrutura do Código

O código segue uma arquitetura modular com as etapas clássicas:

* `lexer.py` — análise léxica
* `parser.py` — análise sintática
* `nfa.py` — construção do AFND
* `dfa.py` — construção do AFD
* `compiler.py` — orquestração do processo
* `visualizer.py` — geração de representações textuais/DOT
* `main.py` — interface CLI

## Bugs, Limitações e Melhorias

### Limitações

* Alfabeto restrito a caracteres alfanuméricos.
* Não implementa operadores `+` e `?`.
* Geração gráfica requer ferramentas externas como Graphviz.

### Melhorias possíveis

* Suporte a mais operadores e alfabeto ampliado.
* Minimização de AFD.
* Parser não recursivo para maior profundidade.

## Código

O código fonte está neste repositório e as dependências são especificadas em `requirements.txt`. Execute os testes com:

```bash
python3 -m unittest discover tests/
```

