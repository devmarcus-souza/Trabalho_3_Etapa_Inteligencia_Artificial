import json
import math
from datetime import datetime
from pathlib import Path

import requests


URL = "http://localhost:11434/api/generate"
MODELO = "qwen2.5-coder:7b"
PROMPT = "Escreva um algoritmo de ordenação Bubble Sort em C bem documentado."


def ler_decimal(rotulo, minimo, maximo):
    entrada = input(f"{rotulo} ({minimo} a {maximo}): ")
    try:
        valor = float(entrada.strip().replace(",", "."))
    except ValueError:
        raise ValueError(f"{rotulo} deve ser um número.") from None
    if not math.isfinite(valor) or not minimo <= valor <= maximo:
        raise ValueError(f"{rotulo} deve estar entre {minimo} e {maximo}.")
    return valor


def ler_parametros():
    temperatura = ler_decimal("Temperatura", 0.0, 2.0)
    top_p = ler_decimal("top_p", 0.0, 1.0)
    try:
        num_predict = int(input("num_predict (inteiro positivo): "))
    except ValueError:
        raise ValueError("num_predict deve ser um inteiro positivo.") from None
    if num_predict <= 0:
        raise ValueError("num_predict deve ser um inteiro positivo.")
    return {"temperature": temperatura, "top_p": top_p, "num_predict": num_predict}


def gerar_trechos(parametros):
    dados = {"model": MODELO, "prompt": PROMPT, "stream": True, "options": parametros}
    with requests.post(URL, json=dados, stream=True, timeout=(5, 300)) as resposta:
        if resposta.status_code == 404:
            raise RuntimeError(f"Modelo {MODELO} indisponível. Execute ollama pull {MODELO}.")
        resposta.raise_for_status()

        # Cada linha contém um objeto JSON codificado em UTF-8.
        for linha in resposta.iter_lines(chunk_size=1):
            if not linha:
                continue
            try:
                evento = json.loads(linha.decode("utf-8"))
            except (UnicodeError, ValueError):
                raise RuntimeError("O Ollama enviou um trecho inválido.") from None
            if evento.get("error"):
                raise RuntimeError(evento["error"])
            trecho = evento.get("response", "")
            if trecho:
                yield trecho
            if evento.get("done") is True:
                return
        raise RuntimeError("A conexão terminou antes da confirmação de conclusão do Ollama.")


def salvar_resposta(parametros, trechos, erro):
    data_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")
    caminho = Path(__file__).resolve().with_name(f"resposta_{data_hora}.txt")
    with caminho.open("x", encoding="utf-8") as arquivo:
        arquivo.write(
            f"Modelo: {MODELO}\nPrompt: {PROMPT}\n"
            f"Temperatura: {parametros['temperature']}\n"
            f"top_p: {parametros['top_p']}\n"
            f"num_predict: {parametros['num_predict']}\n"
        )
        if erro:
            arquivo.write(f"Status: resposta parcial. {erro}\n")
        arquivo.write("\nResposta gerada:\n")
        arquivo.writelines(trechos)
        arquivo.write("\n")
    return caminho


def main():
    try:
        parametros = ler_parametros()
    except ValueError as erro:
        print(f"Entrada inválida: {erro}")
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\nEntrada cancelada.")
        return 1

    print(f"Gerando com {MODELO}...\n", flush=True)
    trechos = []
    erro = None
    try:
        for trecho in gerar_trechos(parametros):
            trechos.append(trecho)
            print(trecho, end="", flush=True)
    except KeyboardInterrupt:
        erro = "Geração interrompida pelo usuário."
    except requests.exceptions.ConnectionError:
        erro = (
            "Geração interrompida: a conexão com o Ollama caiu."
            if trechos
            else f"Ollama indisponível ou conexão interrompida em {URL}. Verifique se o serviço está aberto."
        )
    except requests.exceptions.Timeout:
        erro = "Geração interrompida: o Ollama demorou demais para responder."
    except (requests.exceptions.RequestException, RuntimeError) as falha:
        erro = f"Geração interrompida: {falha}"

    if erro:
        print(f"\n{erro}")
    if trechos or erro is None:
        try:
            caminho = salvar_resposta(parametros, trechos, erro)
        except OSError as falha:
            print(f"\nNão foi possível salvar a resposta: {falha}")
            return 1
        print(f"\nResposta {'parcial ' if erro else ''}salva em {caminho}")
    return 1 if erro else 0


if __name__ == "__main__":
    raise SystemExit(main())
