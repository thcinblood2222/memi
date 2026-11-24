#!/usr/bin/env python3
"""Render the three selected memes over the supplied night ambience."""
import argparse, subprocess as sp, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

W,H,S=1080,1920,720
X,Y=(W-S)//2,492
INTRO=.6
CLIPS=[
    ('01-monkeys',.7,18.30,360,360,140,0,64),
    ('02-meme',269.03,277.97,256,360,192,0,191),
    ('03-cat',972.80,992.70,360,360,140,0,317),
]

def render(source,bg,out,root,c):
    name,a,b,cw,ch,cx,cy,offset=c
    dur=b-a
    total=round((INTRO+dur)*30)/30
    if cw==ch:
        f=[f'[0:v]crop={cw}:{ch}:{cx}:{cy},scale={S}:{S},setsar=1,fps=30,format=yuv444p,tpad=start_duration={INTRO}:start_mode=clone,setpts=PTS-STARTPTS[fg]']
    else:
        f=[f'[0:v]crop={cw}:{ch}:{cx}:{cy},setsar=1,fps=30,split[fill][main]',
           f'[fill]scale={S}:{S}:force_original_aspect_ratio=increase,crop={S}:{S},gblur=sigma=24,eq=brightness=-.10[blur]',
           f'[main]scale={S}:{S}:force_original_aspect_ratio=decrease[fit]',
           f'[blur][fit]overlay=(W-w)/2:(H-h)/2,format=yuv444p,tpad=start_duration={INTRO}:start_mode=clone,setpts=PTS-STARTPTS[fg]']
    f+=['[2:v]format=gray[mask]',
        '[fg][mask]alphamerge,format=rgba,fade=t=in:st=0.6:d=0.65:alpha=1[circle]',
        '[3:v]format=rgba,fade=t=in:st=0.6:d=0.65:alpha=1[shadow]',
        f'[1:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps=30,setpts=PTS-STARTPTS[bg]',
        f'[bg][shadow]overlay=x={X-120}:y={Y-120}:format=auto[base]',
        f'[base][circle]overlay=x={X}:y={Y}:format=auto[comp]',
        f"[comp]drawbox=x=95:y=1685:w=890:h=5:color=white@0.25:t=fill:enable='gte(t,{INTRO})'[track]",
        f"color=c=white:s=890x6:r=30:d={total},format=rgba,geq=r=245:g=245:b=245:a='if(lt(T,{INTRO}),0,if(lte(X,890*(T-{INTRO})/{dur}),220,0))'[progress]",
        '[track][progress]overlay=x=95:y=1685:format=auto,format=yuv420p[v]',
        '[0:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS,adelay=600:all=1,volume=0.92[voice]',
        '[1:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS,volume=0.15[amb]',
        '[amb][voice]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]']
    sp.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(a),'-t',str(dur),'-i',str(source),
            '-ss',str(offset),'-i',str(bg),'-loop','1','-framerate','30','-i',str(root/'mask.png'),
            '-loop','1','-framerate','30','-i',str(root/'shadow.png'),'-filter_complex_threads','2',
            '-filter_complex',';'.join(f),'-map','[v]','-map','[a]','-t',str(total),'-c:v','libx264',
            '-threads','3','-preset','ultrafast','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k',
            '-movflags','+faststart',str(out/(name+'.mp4'))],check=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',required=True,type=Path)
    p.add_argument('--background',required=True,type=Path)
    p.add_argument('--out',default=Path('out'),type=Path)
    args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)
        mask=Image.new('L',(S*2,S*2))
        ImageDraw.Draw(mask).ellipse((1,1,S*2-2,S*2-2),fill=255)
        mask.resize((S,S),Image.Resampling.LANCZOS).save(root/'mask.png')
        shadow=Image.new('L',(S+240,S+240))
        ImageDraw.Draw(shadow).ellipse((120,139,120+S,139+S),fill=155)
        shadow=shadow.filter(ImageFilter.GaussianBlur(35))
        black=Image.new('RGBA',shadow.size,(0,0,0,0))
        black.putalpha(shadow)
        black.save(root/'shadow.png')
        for c in CLIPS: render(args.source,args.background,args.out,root,c)

if __name__=='__main__': main()
