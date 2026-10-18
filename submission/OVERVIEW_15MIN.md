# Aegis REBOUND - Silent 15-minute product overview

No narration, music, or audio track. On-screen captions explain the product and demonstrations. Actual UI captures show replay changes and before/after interactions; sequences are edited and paced for reading, not a continuous real-time screen recording. All cases are synthetic.

## Chapters

- 00:00 - The product question
- 01:30 - Inside the algorithm
- 03:00 - Demo 1 - Replay the day
- 05:00 - Demo 2 - Peak-flow update
- 07:00 - Demo 3 - Independent respiratory rate
- 08:00 - Demo 4 - Ambiguous evidence
- 09:30 - Demo 5 - Retrospective forecast check
- 10:30 - Demo 6 - Sensor-gap abstention
- 11:30 - Demo 7 - Experiments and results
- 13:30 - Limitations and originality
- 14:30 - Run and review the project

## Editing and rebuilding

`demo_assets/storyboard.json` contains every on-screen explanation, source capture, crop and duration. See [source asset instructions](demo_assets/README.md). Rebuild with `python tools/create_15min_overview.py` after installing Pillow and FFmpeg. The export is exactly 900 seconds, 1600 x 1000, five frames per second, with no audio stream.

`DEMO_SCRIPT.md` remains the narration guide for the separate original 20:30 edition. It is not the transcript of this silent edit. The longer original is retained for the supplied challenge brief's stricter minimum-duration wording.
