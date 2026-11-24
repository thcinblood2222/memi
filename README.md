# memi — clean circular reaction edits

1080×1920, 30 fps, H.264/AAC. Actual parkour footage fills the screen. The source video is center-cropped into a 780 px circle in the upper-middle of the frame. No titles, text, frames, progress bars, or artificial gameplay. Original source audio is retained; optional licensed background music is mixed quietly.

## Sources
- Background reference: https://www.youtube.com/watch?v=u7kdVe8q5zs
- Main source reference: https://www.youtube.com/watch?v=HdVirZO_860
- Music reference: 09:03 in the main source. Track not yet identified; supply a licensed music file.
- Editorial selection pending review of the source. No fabricated timestamps.

Use only media you are authorized to download and reuse. If the video host blocks CI downloads, use authorized direct media URLs or local files.

## GitHub Actions
Open Actions → Render source clips → Run workflow.
1. Select transcribe mode. The workflow exports timestamped speech in transcript.txt and transcript.json for editorial selection.
2. Review the actual moments. Select three nonoverlapping intervals, expressed in seconds.
3. Run render mode, set clips to the three chosen intervals, and optionally provide a licensed music URL. Download the resulting MP4 files from Artifacts.

## Local
With Python and FFmpeg installed:
```sh
pip install faster-whisper
python render.py transcribe --source source.mp4
python render.py render --source source.mp4 --background parkour.mp4 --music music.wav --clips "START1-END1,START2-END2,START3-END3"
```
Replace the placeholders with reviewed numerical timestamps. Omit --music if no licensed track is available.
