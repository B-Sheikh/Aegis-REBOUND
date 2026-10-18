"""Recreate the complete 15-minute edition using FFmpeg available on PATH.

Run from any directory: python tools/create_15min_overview.py
Requires the bundled original 20:30 video and VIDEO_METADATA.json.
All narration is retained. Pitch-preserving tempo adjustment gives ~150 words/min.
"""
from pathlib import Path
import json
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("Install FFmpeg and put it on PATH before recreating the video.")
    original = ROOT / "submission/Aegis_REBOUND_Demo.mp4"
    output = ROOT / "submission/Aegis_REBOUND_15min_Overview.mp4"
    metadata = json.loads((ROOT / "submission/VIDEO_METADATA.json").read_text(encoding="utf-8"))
    factor = metadata["verified_duration_seconds"] / 900
    lines = [";FFMETADATA1", "title=Aegis REBOUND - 15-minute project overview", "artist=Team Aegis"]
    chapters = metadata["chapters"]
    for i, chapter in enumerate(chapters):
        start = round(chapter["start_seconds"] / factor * 1000)
        end = round(chapters[i + 1]["start_seconds"] / factor * 1000) if i + 1 < len(chapters) else 900000
        title = chapter["title"].replace("=", "-").replace("\n", " ")
        lines += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={start}", f"END={end}", f"title={title}"]
    with tempfile.TemporaryDirectory(prefix="rebound-video-") as directory:
        chapter_file = Path(directory) / "chapters.ffmetadata"
        chapter_file.write_text("\n".join(lines), encoding="utf-8")
        subprocess.run([
            ffmpeg, "-hide_banner", "-y", "-i", str(original), "-f", "ffmetadata", "-i", str(chapter_file),
            "-map", "0:v:0", "-map", "0:a:0", "-map_metadata", "1", "-map_chapters", "1",
            "-vf", f"setpts=PTS/{factor:.12f},fps=5", "-af", f"atempo={factor:.12f}",
            "-t", "900", "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage",
            "-crf", "23", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k",
            "-movflags", "+faststart", str(output),
        ], check=True)
    print(output)
    print("If regenerating release files, refresh MANIFEST.sha256 afterwards.")


if __name__ == "__main__":
    main()
