# Silent video source assets

PNG files are actual captures of the running local product or slides from the included presentation. `storyboard.json` contains the ordered captions, durations and optional source crop rectangles. Replay frames show actual sequential five-minute timeline interactions. Before/after pairs show actual measurement-button updates. The video edits and holds these captures for reading; it is not a continuous real-time screen recording.

All cases and observations are synthetic. No external patient records are present.

Rebuild from the repository root:

```sh
pip install Pillow
python tools/create_15min_overview.py
```

Install FFmpeg on PATH, or pass its executable path as the first argument. The builder maps only video and uses `-an`, producing no audio stream. It generates chapter metadata and the overview metadata JSON. Refresh MANIFEST.sha256 after changing release files. The older 20:30 narrated edition is retained separately.
