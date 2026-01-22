from __future__ import annotations

from datetime import datetime
from pathlib import Path
from time import perf_counter

import yaml

from src import m1_roteiros, m2_traducao, m3_avatar_video, m4_template_editor, m5_organizador


def carregar_config(caminho_config: Path) -> dict:
    config = yaml.safe_load(caminho_config.read_text(encoding="utf-8")) or {}

    idiomas = config.get("idiomas", ["br"])
    nicho = config.get("nicho", "nicho_nao_definido")
    quantidade = config.get(
        "videos_por_lote",
        config.get("quantidade_videos_por_lote", config.get("quantidade", 1)),
    )

    return {
        "idiomas": idiomas,
        "nicho": nicho,
        "videos_por_lote": quantidade,
        "base_dir": str(caminho_config.parents[1]),
        "dry_run": config.get("dry_run", False),
    }


def criar_diretorio_lote(base_dir: Path) -> Path:
    data_lote = datetime.now().strftime("%Y-%m-%d")
    lote_dir = base_dir / "batches" / f"lote_{data_lote}"
    lote_dir.mkdir(parents=True, exist_ok=True)
    return lote_dir


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    config_path = base_dir / "config" / "config.yaml"

    print("🔧 Carregando configurações...")
    config = carregar_config(config_path)

    print("🗂️ Criando diretório do lote...")
    lote_dir = criar_diretorio_lote(base_dir)
    media_root = base_dir / "media"

    dry_run = bool(config.get("dry_run", False))

    total_inicio = perf_counter()

    print("1️⃣ Gerando roteiros em PT-BR...")
    inicio_m1 = perf_counter()
    scripts_br = m1_roteiros.generate_scripts(config)
    tempo_m1 = perf_counter() - inicio_m1

    print("2️⃣ Traduzindo roteiros para outros idiomas...")
    inicio_m2 = perf_counter()
    idiomas_destino = [idioma for idioma in config["idiomas"] if idioma != "br"]
    scripts_traduzidos = m2_traducao.translate_scripts(scripts_br, idiomas_destino)
    tempo_m2 = perf_counter() - inicio_m2

    print("3️⃣ Gerando vídeos base...")
    inicio_m3 = perf_counter()
    scripts_com_video = m3_avatar_video.generate_base_videos(
        scripts_traduzidos,
        media_root,
        dry_run=dry_run,
    )
    tempo_m3 = perf_counter() - inicio_m3

    print("4️⃣ Aplicando template...")
    inicio_m4 = perf_counter()
    scripts_finalizados = m4_template_editor.apply_template(
        scripts_com_video,
        media_root,
        dry_run=dry_run,
    )
    tempo_m4 = perf_counter() - inicio_m4

    print("5️⃣ Organizando lote final...")
    inicio_m5 = perf_counter()
    m5_organizador.organize_batch(
        scripts_finalizados,
        base_dir / "batches",
        dry_run=dry_run,
    )
    tempo_m5 = perf_counter() - inicio_m5

    total_tempo = perf_counter() - total_inicio
    m3_times = [s.get("m3_time_seconds", 0.0) for s in scripts_com_video if s.get("status") == "ok"]
    m4_times = [s.get("m4_time_seconds", 0.0) for s in scripts_finalizados if s.get("status") == "ok"]
    m3_avg = sum(m3_times) / len(m3_times) if m3_times else 0.0
    m4_avg = sum(m4_times) / len(m4_times) if m4_times else 0.0

    print("\nPipeline Summary:")
    print(f"  - M1 (scripts): {tempo_m1:.1f}s")
    print(f"  - M2 (translation): {tempo_m2:.1f}s")
    print(f"  - M3 (base video): {tempo_m3:.1f}s (avg {m3_avg:.1f}s per video)")
    print(f"  - M4 (template): {tempo_m4:.1f}s (avg {m4_avg:.1f}s per video)")
    print(f"  - M5 (organize): {tempo_m5:.1f}s")
    print(f"  - TOTAL: {total_tempo:.1f}s")

    print(f"✅ Lote gerado com sucesso em {lote_dir}!")


if __name__ == "__main__":
    main()
