from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import shutil
from typing import Iterable


def organize_batch(
    scripts_with_final_video: Iterable[dict],
    batch_root: Path,
    dry_run: bool = False,
) -> None:
    """
    Organiza vídeos finais e legendas em um lote por idioma.
    """
    lote_dir = batch_root / f"lote_{datetime.now().strftime('%Y-%m-%d')}"
    lote_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "created_at": datetime.now().isoformat(),
        "items": [],
    }

    for script in scripts_with_final_video:
        idioma_dir = lote_dir / script["lang"]
        idioma_dir.mkdir(parents=True, exist_ok=True)

        origem = Path(script["final_video_path"])
        destino_video = idioma_dir / origem.name
        caption_path = idioma_dir / f"{script['id']}_{script['lang']}.txt"

        status = script.get("status", "ok")
        if status == "ok":
            if dry_run:
                print(f"Batch: dry-run para {script['id']} ({script['lang']}).")
            else:
                print(
                    "Batch: copiando vídeo final para "
                    f"{lote_dir.name}/{script['lang']}..."
                )
                shutil.copy2(origem, destino_video)
                caption_path.write_text(script["caption"], encoding="utf-8")
        else:
            print(f"Batch: pulando {script['id']} ({script['lang']}) por falha.")

        manifest["items"].append(
            {
                "id": script["id"],
                "lang": script["lang"],
                "video": str(destino_video),
                "caption": str(caption_path),
                "nicho": script["nicho"],
                "status": status,
                "error": script.get("error"),
            }
        )

    manifest_path = lote_dir / "batch_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
