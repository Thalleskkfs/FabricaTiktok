from __future__ import annotations

from pathlib import Path
from time import perf_counter
from typing import Iterable

from moviepy.editor import ColorClip, CompositeVideoClip, TextClip, VideoFileClip


def _split_text(text: str, max_words: int) -> list[str]:
    words = text.split()
    return [" ".join(words[i : i + max_words]) for i in range(0, len(words), max_words)]


def generate_subtitle_clips(text: str, duration: float, video_size: tuple[int, int]) -> list:
    """Cria clipes de legenda simples distribuídos ao longo do vídeo."""
    chunks = _split_text(text, max_words=7)
    if not chunks:
        return []

    chunk_duration = max(duration / len(chunks), 0.1)
    clips = []
    for index, chunk in enumerate(chunks):
        start_time = index * chunk_duration
        try:
            subtitle = (
                TextClip(
                    chunk,
                    fontsize=48,
                    color="white",
                    method="caption",
                    size=(video_size[0] - 160, None),
                )
                .set_position(("center", video_size[1] - 380))
                .set_start(start_time)
                .set_duration(chunk_duration)
            )
            clips.append(subtitle)
        except Exception:
            return []

    return clips


def generate_caption(titulo: str, nicho: str) -> str:
    hashtags = [f"#{nicho}", "#shorts", "#tiktok"]
    return f"{titulo}\n\n" + " ".join(hashtags)


def apply_template(
    scripts_with_video: Iterable[dict],
    media_root: Path,
    dry_run: bool = False,
) -> list[dict]:
    """
    Aplica um template simples com legendas e proporção vertical.
    Retorna roteiros com final_video_path e caption.
    """
    final_dir = media_root / "final_videos"
    final_dir.mkdir(parents=True, exist_ok=True)

    scripts_finalizados: list[dict] = []
    for script in scripts_with_video:
        inicio = perf_counter()
        base_video_path = Path(script["base_video_path"])
        output_path = final_dir / f"{script['id']}_{script['lang']}.mp4"
        caption = generate_caption(script["titulo"], script["nicho"])
        script_final = script.copy()
        script_final["final_video_path"] = str(output_path)
        script_final["caption"] = caption
        if script.get("status") == "failed":
            script_final["status"] = "failed"
            script_final["m4_time_seconds"] = perf_counter() - inicio
            scripts_finalizados.append(script_final)
            continue

        if dry_run:
            print(f"Template: dry-run para {script['id']} ({script['lang']}).")
            script_final["status"] = "ok"
            script_final["m4_time_seconds"] = perf_counter() - inicio
            scripts_finalizados.append(script_final)
            continue

        video_clip = None
        final_clip = None
        try:
            print(f"Template: aplicando legendas em {script['id']} ({script['lang']})...")
            video_clip = VideoFileClip(str(base_video_path))
            duration = video_clip.duration
            vertical_size = (1080, 1920)
            background = ColorClip(size=vertical_size, color=(12, 12, 12)).set_duration(
                duration
            )

            resized_video = video_clip.resize(width=vertical_size[0] - 120).set_position(
                "center"
            )
            overlays = [background, resized_video]

            subtitle_clips = generate_subtitle_clips(script["script"], duration, vertical_size)
            overlays.extend(subtitle_clips)

            try:
                watermark = (
                    TextClip(
                        "FabricaTiktok",
                        fontsize=32,
                        color="white",
                        method="caption",
                    )
                    .set_duration(duration)
                    .set_position(("center", 60))
                )
                overlays.append(watermark)
            except Exception:
                pass

            final_clip = CompositeVideoClip(overlays).set_audio(video_clip.audio)
            final_clip.write_videofile(
                str(output_path),
                fps=30,
                codec="libx264",
                audio_codec="aac",
                verbose=False,
                logger=None,
            )
            script_final["status"] = "ok"
        except Exception as exc:
            print(f"Erro ao aplicar template {script['id']} ({script['lang']}): {exc}")
            script_final["status"] = "failed"
            script_final["error"] = str(exc)
        finally:
            if video_clip is not None:
                video_clip.close()
            if final_clip is not None:
                final_clip.close()

        script_final["m4_time_seconds"] = perf_counter() - inicio
        scripts_finalizados.append(script_final)

    return scripts_finalizados
