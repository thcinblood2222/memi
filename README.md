# memi

Three Russian-language reaction memes, 1080×1920 H.264 MP4, 30 fps.
Real CC0 reaction footage in Telegram-style circular crops over original animated voxel parkour backgrounds (not captured Minecraft gameplay).

## Render
On Ubuntu: install ffmpeg, python3, python3-pil, fonts-dejavu-core, then run `python3 render.py`.
The GitHub Actions workflow renders all three and uploads them as an artifact.
Outputs: `out/01-online.mp4`, `out/02-discord.mp4`, `out/03-sleep.mp4`.

## Source footage
All reaction clips are marked CC0 on their respective Wikimedia Commons pages. Cropped, trimmed, and combined with original captions and graphics.
- [Cat Jumpscare](https://commons.wikimedia.org/wiki/File:Cat_Jumpscare.webm), Panini!
- [Howling Husky Dog](https://commons.wikimedia.org/wiki/File:Howling_Husky_Dog.webm), Klaudya Teodora
- [Sophy the Cat is Really High On A Ledge](https://commons.wikimedia.org/wiki/File:Sophy_the_Cat_is_Really_High_On_A_Ledge.webm), PseudoSkull

Backgrounds and captions are generated locally. No music or external API keys required.
