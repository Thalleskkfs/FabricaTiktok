from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from src.pipeline_semana import carregar_config, run_pipeline


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Executa o pipeline semanal da FabricaTikTok.")
    parser.add_argument(
        "--config",
        default="config/config.yaml",
        help="Caminho para o arquivo de configuração.",
    )
    parser.add_argument("--niche", help="Override para o nicho (nicho).")
    parser.add_argument(
        "--videos",
        type=int,
        help="Override para videos_por_lote.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Força dry_run = true.",
    )
    return parser.parse_args()


def _apply_overrides(config: dict, args: argparse.Namespace) -> dict:
    config_atualizado = dict(config)
    if args.niche:
        config_atualizado["nicho"] = args.niche
    if args.videos is not None:
        config_atualizado["videos_por_lote"] = args.videos
    if args.dry_run:
        config_atualizado["dry_run"] = True
    return config_atualizado


def _print_config_header(config: dict[str, Any]) -> None:
    print("\n=== FabricaTikTok | Configuração efetiva ===")
    print(f"Nicho: {config.get('nicho')}")
    print(f"Idiomas: {config.get('idiomas')}")
    print(f"Vídeos por lote: {config.get('videos_por_lote')}")
    print(f"Dry run: {config.get('dry_run')}")
    print("===========================================\n")


def main() -> None:
    args = _parse_args()
    try:
        config_path = Path(args.config)
        config = carregar_config(config_path)
        config = _apply_overrides(config, args)
        _print_config_header(config)
        run_pipeline(config, base_dir=config_path.resolve().parents[1])
    except Exception as exc:
        print(f"Erro ao executar o pipeline: {exc}")


if __name__ == "__main__":
    main()
