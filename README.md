# memi — night ambience edits

Three vertical edits using the supplied meme compilation and Minecraft Starry Night Wave Ambience footage. The old synthetic gameplay and captions are no longer part of the renderer.

- 1080×1920, 30 fps, H.264/AAC
- 0.6 s of background alone, followed by a 0.65 s circular-video fade
- Soft shadow, thin progress bar, no added headings
- Original meme audio with quieter background ambience

## Render locally
Install FFmpeg and Pillow, then run:

```sh
python render.py --source "ТИК ТОК МЕМЫ ЧАСТЬ 60 [get-save.com].mp4" --background "Minecraft Starry Night Wave Ambience and Music relax and sleep [get-save.com].mp4"
```

The three MP4s are exported to out/. Source media and finished binary videos are not committed to Git.

## GitHub Actions
The manual workflow accepts authorized direct MP4 links to the same two source files and exports the three clips as the night-memes artifact. Only reuse media you have permission to publish.
