#!/usr/bin/env python3
"""Minimal vertical editor for authorized source clips."""
import argparse
import json
import math
import subprocess
from pathlib import Path

W, H, FPS = 1080, 1920, 30
CIRCLE = 780
OUT = Path("out")

def run(*args):
    subprocess.run([str(a) for a in args], check=True)

def probe(path):
    return json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_streams", "-show_format",
        "-of", "json", str(path)], text=True))

def length(info):
    return float(info["format"]["duration"])

def clock(seconds):
    return f"{int(seconds//60):02d}:{seconds%60:06.3f}"

def transcribe(source):
    from faster_whisper import WhisperModel
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, info = model.transcribe(str(source), beam_size=5,
                                      vad_filter=True, word_timestamps=True)
    results = []
    with (OUT / "transcript.txt").open("w", encoding="utf-8") as f:
        for s in segments:
            row = dict(start=round(s.start, 3), end=round(s.end, 3),
                       text=s.text.strip())
            results.append(row)
            line = f"[{clock(s.start)} - {clock(s.end)}] {s.text.strip()}"
            print(line, flush=True)
            f.write(line + "\n")
    (OUT / "transcript.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

def intervals(value, duration):
    try:
        result = [tuple(map(float, x.strip().split("-"))) for x in value.split(",")]
    except ValueError:
        raise SystemExit("Use three start-end intervals in seconds.")
    if len(result) != 3 or any(len(x)!=2 for x in result):
        raise SystemExit("Exactly three start-end intervals are required.")
    if any(not math.isfinite(a) or not math.isfinite(b) or a < 0 or
           b <= a or b > duration+.05 or b-a > 90 for a,b in result):
        raise SystemExit("Invalid interval: check source duration and use clips of at most 90 seconds.")
    if any(max(a,c)<min(b,d) for i,(a,b) in enumerate(result)
           for c,d in result[i+1:]):
        raise SystemExit("Selected moments must not overlap.")
    return result

def render(source, background, music, clip_list):
    source_info = probe(source)
    bg_duration = length(probe(background))
    source_audio = any(s["codec_type"] == "audio" for s in source_info["streams"])
    if not source_audio:
        raise SystemExit("Source has no audio. Provide the original video with sound.")
    if music and not any(s["codec_type"]=="audio" for s in probe(music)["streams"]):
        raise SystemExit("Music input has no audio.")
    for index, (start, end) in enumerate(intervals(clip_list, length(source_info)), 1):
        duration = end-start
        bg_offset = (13+(index-1)*37) % max(1, bg_duration)
        target = OUT / f"meme-{index:02d}.mp4"
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "warning", "-y",
               "-ss", str(start), "-i", str(source),
               "-stream_loop", "-1", "-ss", str(bg_offset), "-i", str(background)]
        if music:
            cmd += ["-stream_loop", "-1", "-i", str(music)]
        # Real footage fills the entire portrait frame. No UI, borders or captions.
        # The one-pixel soft alpha boundary prevents jagged edges on the circle.
        alpha = "255*clip(390.0-hypot(X-389.5,Y-389.5),0,1)"
        filters = [
            f"[1:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={FPS},setpts=PTS-STARTPTS[bg]",
            f"[0:v]scale={CIRCLE}:{CIRCLE}:force_original_aspect_ratio=increase,crop={CIRCLE}:{CIRCLE},setsar=1,fps={FPS},format=yuva444p,geq=lum='lum(X,Y)':cb='cb(X,Y)':cr='cr(X,Y)':a='{alpha}',setpts=PTS-STARTPTS[fg]",
            "[bg][fg]overlay=x=(W-w)/2:y=470:shortest=1:format=auto,format=yuv420p[v]",
            "[0:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS,volume=0.95[voice]"
        ]
        if music:
            fade = min(.25, duration/4)
            filters += [
                f"[2:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS,atrim=duration={duration},volume=0.12,afade=t=in:st=0:d={fade},afade=t=out:st={duration-fade}:d={fade}[music]",
                "[voice][music]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]"
            ]
        else:
            filters += ["[voice]alimiter=limit=0.95[a]"]
        cmd += ["-filter_complex_threads", "2", "-filter_complex", ";".join(filters),
                "-map", "[v]", "-map", "[a]", "-t", str(duration),
                "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                "-movflags", "+faststart", str(target)]
        run(*cmd)
        print(f"Exported {target}: {clock(start)} to {clock(end)}", flush=True)

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest="mode", required=True)
    t=sub.add_parser("transcribe")
    t.add_argument("--source", type=Path, required=True)
    r=sub.add_parser("render")
    r.add_argument("--source", type=Path, required=True)
    r.add_argument("--background", type=Path, required=True)
    r.add_argument("--music", type=Path)
    r.add_argument("--clips", required=True)
    args=parser.parse_args()
    if args.mode=="transcribe":
        transcribe(args.source)
    else:
        render(args.source,args.background,args.music,args.clips)
