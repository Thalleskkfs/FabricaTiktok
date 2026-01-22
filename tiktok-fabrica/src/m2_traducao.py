from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request


def montar_prompt_traducao(texto: str, origem: str, destino: str) -> str:
    """Cria o prompt de tradução/adaptação com tom de fala."""
    return (
        f"Traduza e adapte o texto abaixo do idioma {origem} para {destino}. "
        "Mantenha o tom psicológico e a fala natural para vídeo curto. "
        "Retorne apenas o texto traduzido.\n\n"
        f"Texto:\n{texto}"
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


def traduzir_texto(texto: str, origem: str, destino: str, model: str) -> str:
    """Traduz e adapta um texto único para o idioma destino."""
    prompt = montar_prompt_traducao(texto, origem, destino)
    return chamar_modelo(prompt, model=model, temperature=0.3).strip()


def traduzir_roteiros(roteiros_br: list[dict], idiomas_destino: list[str]) -> list[dict]:
    """Gera roteiros traduzidos mantendo o tom do original."""
    model = os.getenv("OPENAI_MODEL_TRADUCAO", "gpt-4o-mini")
    tentativas = int(os.getenv("TENTATIVAS_TRADUCAO", "3"))
    roteiros_finais = list(roteiros_br)

    for roteiro in roteiros_br:
        for idioma in idiomas_destino:
            roteiro_id = f"{roteiro['id']}_{idioma}"
            for tentativa in range(1, tentativas + 1):
                try:
                    titulo_traduzido = traduzir_texto(
                        roteiro["titulo"], "pt-BR", idioma, model=model
                    )
                    script_traduzido = traduzir_texto(
                        roteiro["script"], "pt-BR", idioma, model=model
                    )
                    roteiros_finais.append(
                        {
                            "id": roteiro_id,
                            "lang": idioma,
                            "titulo": titulo_traduzido,
                            "script": script_traduzido,
                            "duracao_target": roteiro["duracao_target"],
                            "nicho": roteiro["nicho"],
                        }
                    )
                    break
                except (RuntimeError, urllib.error.URLError) as exc:
                    if tentativa == tentativas:
                        print(f"Falha ao traduzir roteiro {roteiro_id}: {exc}")
                        break
                    time.sleep(1.5 * tentativa)

    return roteiros_finais


def translate_scripts(roteiros_br: list[dict], idiomas_destino: list[str]) -> list[dict]:
    """Alias para traduzir_roteiros, mantendo compatibilidade com o pipeline."""
    return traduzir_roteiros(roteiros_br, idiomas_destino)

