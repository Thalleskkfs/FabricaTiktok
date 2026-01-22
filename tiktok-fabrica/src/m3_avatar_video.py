from __future__ import annotations

from pathlib import Path
from time import perf_counter
from typing import Iterable, Optional

import pyttsx3
from moviepy.editor import AudioFileClip, ColorClip, CompositeVideoClip, TextClip


def synthesize_speech(text: str, output_path: Path) -> None:
    """Converte texto em áudio usando TTS local (pyttsx3)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    engine = pyttsx3.init()
    engine.save_to_file(text, str(output_path))
    engine.runAndWait()


def _build_title_overlay(
    title: str,
    duration: float,
    video_size: tuple[int, int],
) -> Optional[TextClip]:
    """Cria um overlay de título com fallback quando TextClip não está disponível."""
    try:
        return (
            TextClip(
                title,
                fontsize=60,
                color="white",
                method="caption",
                size=(video_size[0] - 120, None),
            )
            .set_duration(duration)
            .set_position(("center", 200))
        )
    except Exception:
        return None


def create_base_video(audio_path: Path, title: str, output_path: Path) -> None:
    """Cria um vídeo simples com fundo sólido e áudio."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    audio_clip = AudioFileClip(str(audio_path))
    duration = audio_clip.duration
    video_size = (1080, 1920)

    background = ColorClip(size=video_size, color=(20, 20, 20)).set_duration(duration)
    overlays: list = [background]

    title_overlay = _build_title_overlay(title, duration, video_size)
    if title_overlay is not None:
        overlays.append(title_overlay)

    final_clip = CompositeVideoClip(overlays).set_audio(audio_clip)
    final_clip.write_videofile(
        str(output_path),
        fps=30,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None,
    )

    audio_clip.close()
    final_clip.close()


def generate_base_videos(
    scripts: Iterable[dict],
    media_root: Path,
    dry_run: bool = False,
) -> list[dict]:
    """
    Para cada roteiro, gera um áudio TTS e um vídeo base simples.
    Retorna os roteiros com o campo base_video_path.
    """
    audio_dir = media_root / "audio"
    raw_dir = media_root / "raw_videos"

    scripts_atualizados: list[dict] = []
    for script in scripts:
        inicio = perf_counter()
        roteiro_id = script["id"]
        lang = script["lang"]
        audio_path = audio_dir / f"{roteiro_id}_{lang}.wav"
        base_video_path = raw_dir / f"{roteiro_id}_{lang}.mp4"

        script_atualizado = script.copy()
        script_atualizado["base_video_path"] = str(base_video_path)

        if dry_run:
            print(f"TTS: dry-run para {roteiro_id} ({lang}).")
            script_atualizado["status"] = "ok"
            script_atualizado["m3_time_seconds"] = perf_counter() - inicio
            scripts_atualizados.append(script_atualizado)
            continue

        try:
            print(f"TTS: gerando áudio para {roteiro_id} ({lang})...")
            synthesize_speech(script["script"], audio_path)
            print(f"Vídeo base: renderizando {roteiro_id} ({lang})...")
            create_base_video(audio_path, script["titulo"], base_video_path)
            script_atualizado["status"] = "ok"
        except Exception as exc:
            print(f"Erro ao gerar vídeo base {roteiro_id} ({lang}): {exc}")
            script_atualizado["status"] = "failed"
            script_atualizado["error"] = str(exc)

        script_atualizado["m3_time_seconds"] = perf_counter() - inicio
        scripts_atualizados.append(script_atualizado)

    return scripts_atualizados
