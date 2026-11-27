# Trabalho de Inteligência Artificial — 3ª etapa

Trabalho de Ciência da Computação da UNIPAC Barbacena. A parte teórica aborda RNNs, Transformers, o mecanismo de atenção e as etapas de construção de um modelo de linguagem. Na parte prática, um script Python consulta o Ollama local para gerar um Bubble Sort em C e comparar respostas obtidas com três temperaturas.

## Arquivos

- [Relatório em PDF](Relatorio_IA_3_Etapa.pdf) com a fundamentação teórica, a análise dos resultados e as imagens dos registros.
- [Script Python](trabalho_ia.py) que solicita os parâmetros, exibe a resposta em streaming e salva o resultado em UTF-8 na pasta do script.

## Como executar no Windows

Abra o terminal do VS Code na pasta que contém o script. Com o Python 3.13 instalado e o Ollama aberto, instale o `requests` e baixe o modelo:

```powershell
py -3.13 -m pip install requests
ollama pull qwen2.5-coder:7b
```

Se o terminal não reconhecer `ollama` e o aplicativo estiver instalado no caminho padrão, use:

```powershell
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" pull qwen2.5-coder:7b
```

Execute o script uma vez por rodada. O script usa a API local em `http://localhost:11434/api/generate`.

```powershell
py -3.13 trabalho_ia.py
```

## Experimento

O prompt foi o mesmo nas três rodadas: “Escreva um algoritmo de ordenação Bubble Sort em C bem documentado.”

| Rodada | Temperatura | `top_p` | `num_predict` | Resposta original |
| --- | ---: | ---: | ---: | --- |
| A | 0.0 | 0.9 | 1000 | [TXT da rodada A](resposta_2026-11-26_19-47-16_522445.txt) |
| B | 0.9 | 0.9 | 1000 | [TXT da rodada B](resposta_2026-11-26_21-42-21_711422.txt) |
| C | 1.5 | 0.9 | 1000 | [TXT da rodada C](resposta_2026-11-26_21-34-56_446308.txt) |

Na rodada B, o código encerra a ordenação quando uma passagem termina sem trocas. Na rodada A, a explicação indica melhor caso O(n), embora os laços do código realizem O(n²) comparações mesmo para um vetor já ordenado. Na rodada C, a troca foi implementada em uma função separada que recebe ponteiros.
