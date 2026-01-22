from __future__ import annotations

from datetime import datetime
import json
import os
import time
import urllib.error
import urllib.request


def montar_prompt_roteiro(nicho: str, duracao_target: int) -> str:
    """Gera o prompt base para criação de um roteiro em PT-BR."""
    return (
        "Você é um roteirista de vídeos curtos. Gere um roteiro em PT-BR para um "
        f"vídeo de aproximadamente {duracao_target} segundos no nicho '{nicho}'. "
        "Retorne apenas um JSON com as chaves: titulo, script, duracao_target. "
        "O script deve estar em formato de fala para avatar, com tom direto e envolvente."
    )


def chamar_modelo(prompt: str, model: str, temperature: float) -> str:
    """Encapsula a chamada ao provedor de IA (OpenAI)."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY não está configurada.")

    payload = json.dumps(
        {
            "model": model,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        data = json.loads(response.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]


def parsear_resposta_para_titulo_script(resposta: str) -> tuple[str, str, int]:
    """Converte a resposta JSON do modelo em campos estruturados."""
    dados = json.loads(resposta)
    titulo = dados["titulo"].strip()
    script = dados["script"].strip()
    duracao_target = int(dados.get("duracao_target", 40))
    return titulo, script, duracao_target


def gerar_roteiros(config: dict) -> list[dict]:
    """Gera roteiros em PT-BR usando IA, com retries básicos."""
    nicho = config["nicho"]
    quantidade = config["videos_por_lote"]
    duracao_target = int(config.get("duracao_target", 40))
    model = config.get("modelo_roteiro", "gpt-4o-mini")
    tentativas = int(config.get("tentativas_roteiro", 3))

    data_ref = datetime.now().strftime("%Y%m%d")
    roteiros: list[dict] = []

    for indice in range(1, quantidade + 1):
        prompt = montar_prompt_roteiro(nicho, duracao_target)
        roteiro_id = f"{nicho}_{data_ref}_{indice:03d}".lower()

        for tentativa in range(1, tentativas + 1):
            try:
                resposta = chamar_modelo(prompt, model=model, temperature=0.7)
                titulo, script, duracao = parsear_resposta_para_titulo_script(resposta)
                roteiros.append(
                    {
                        "id": roteiro_id,
                        "lang": "br",
                        "titulo": titulo,
                        "script": script,
                        "duracao_target": duracao,
                        "nicho": nicho,
                    }
                )
                break
            except (
                json.JSONDecodeError,
                KeyError,
                ValueError,
                RuntimeError,
                urllib.error.URLError,
            ) as exc:
                if tentativa == tentativas:
                    print(f"Falha ao gerar roteiro {roteiro_id}: {exc}")
                    break
                time.sleep(1.5 * tentativa)

    return roteiros


def generate_scripts(config: dict) -> list[dict]:
    """Alias para gerar_roteiros, mantendo compatibilidade com o pipeline."""
    return gerar_roteiros(config)

