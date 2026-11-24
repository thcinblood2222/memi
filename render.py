#!/usr/bin/env python3
import hashlib, math, os, random, subprocess, wave, struct, urllib.request, urllib.parse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W,H,FPS = 720,1280,30
S=470
BASE=Path(__file__).resolve().parent
OUT=BASE/'out'; ASSETS=BASE/'assets'
OUT.mkdir(exist_ok=True); ASSETS.mkdir(exist_ok=True)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
MEMES=[
 dict(id='01-online', file='Cat_Jumpscare.webm', seconds=9.5, start=0, theme=0,
      hook=['КОГДА ДРУГ ПИШЕТ:','«ТЫ В СЕТИ?»'],
      beats=[(0,3.1,['я, который обещал','сегодня лечь пораньше']),
             (3.1,6.4,['ну вообще-то','я уже сплю']),
             (6.4,9.5,['ЗАЛЕТАЙ В ДИСКОРД'])]),
 dict(id='02-discord', file='Howling_Husky_Dog.webm', seconds=12, start=4, theme=1,
      hook=['ТИММЕЙТ ПОСЛЕ','ОДНОГО ПОРАЖЕНИЯ'],
      beats=[(0,3.3,['«да нормально,','ещё одну»']),
             (3.3,7.4,['через 30 секунд:']),
             (7.4,12,['МИКРОФОН НА 200%'])]),
 dict(id='03-sleep', file='Sophy_the_Cat_is_Really_High_On_A_Ledge.webm', seconds=6, start=0, theme=2,
      hook=['МОЙ МОЗГ В 03:47'],
      beats=[(0,2.5,['а что если','переехать в другую страну']),
             (2.5,6,['купить остров','И НАЧАТЬ НОВУЮ ЖИЗНЬ'])]),
]
THEMES=[
 dict(sky=(104,181,238), haze=(203,228,238), water=(48,132,183), grass=(99,174,53), dirt=(126,86,51), side=(79,104,38)),
 dict(sky=(96,61,151), haze=(239,155,150), water=(119,55,96), grass=(249,160,61), dirt=(123,68,112), side=(131,69,126)),
 dict(sky=(59,141,158), haze=(197,239,218), water=(34,100,117), grass=(65,195,141), dirt=(66,105,96), side=(44,129,99))
]
def run(*args):
    subprocess.run([str(a) for a in args],check=True)
def get_clip(name):
    dest=ASSETS/name
    if dest.exists() and dest.stat().st_size>1000: return dest
    h=hashlib.md5(name.encode()).hexdigest()
    url='https://upload.wikimedia.org/wikipedia/commons/'+h[0]+'/'+h[:2]+'/'+urllib.parse.quote(name)
    tmp=dest.with_suffix('.part')
    run('curl','--fail','--location','--retry','4','--retry-all-errors','--connect-timeout','20','--max-time','180','-A','memi-reaction-video-render/1.0 (https://github.com/thcinblood2222/memi)','-o',tmp,url)
    tmp.replace(dest)
    return dest
def font(sz): return ImageFont.truetype(FONT,sz)
def mix(a,b,v): return tuple(round(x+(y-x)*v) for x,y in zip(a,b))
def shade(c,k): return tuple(max(0,min(255,int(x*k))) for x in c)
def gradient(theme):
    im=Image.new('RGB',(W,H)); d=ImageDraw.Draw(im)
    for y in range(H):
        if y<680: c=mix(theme['sky'],theme['haze'],y/680)
        else: c=mix(theme['water'],shade(theme['water'],.70),(y-680)/(H-680))
        d.line((0,y,W,y),fill=c)
    return im
def lane(n): return 1.6*math.sin(n*.57)+.42*math.sin(n*1.9)
def level(n): return .19*math.sin(n*.72)
def bg(t,theme_id,base):
    theme=THEMES[theme_id]; im=base.copy(); d=ImageDraw.Draw(im)
    speed=5.4; zcam=t*speed; n0=math.floor(zcam/3.3); phase=(zcam/3.3)%1
    xcam=lane(zcam/3.3); ycam=2.0+.85*math.sin(math.pi*phase)+level(n0)
    focal=620; horizon=545+20*math.sin(math.pi*phase)
    def p(x,y,z):
        zz=max(.24,z-zcam)
        return (round(W/2+(x-xcam)*focal/zz),round(horizon+(ycam-y)*focal/zz))
    # Pixel clouds drift, distant islands and water grid.
    for i in range(7):
        cx=int((i*173+theme_id*43-t*11)%(W+220))-110
        cy=85+(i*83)%290
        c=mix(theme['haze'],(255,255,255),.45)
        for dx,dy,ww,hh in [(0,0,90,18),(18,-18,54,18),(40,18,77,12)]:
            d.rectangle((cx+dx,cy+dy,cx+dx+ww,cy+dy+hh),fill=c)
    for k in range(24,0,-1):
        z=zcam+.8+k*2.1
        a=p(-24,-1.4,z); b=p(24,-1.4,z)
        if 680<a[1]<H: d.line((a,b),fill=mix(theme['water'],theme['haze'],.22),width=2)
    for k in range(-9,10):
        d.line((p(k*3.1,-1.4,zcam+52),p(k*3.1,-1.4,zcam+.8)),fill=mix(theme['water'],theme['haze'],.17),width=2)
    # Draw far to near. Each jump is a solid, textured grass block.
    for n in range(n0+20,n0-1,-1):
        z=n*3.3; z1=z+1.65
        if z1-zcam<.5 or z-zcam<.28: continue
        x=lane(n); y=level(n); x0=x-.83; x1=x+.83
        a,b,c,e=p(x0,y,z),p(x1,y,z),p(x1,y,z1),p(x0,y,z1)
        d.polygon([a,b,p(x1,y-.85,z),p(x0,y-.85,z)],fill=theme['dirt'])
        if xcam<x: d.polygon([a,e,p(x0,y-.85,z1),p(x0,y-.85,z)],fill=theme['side'])
        else: d.polygon([b,c,p(x1,y-.85,z1),p(x1,y-.85,z)],fill=shade(theme['dirt'],.76))
        d.polygon([a,b,c,e],fill=theme['grass'])
        rng=random.Random(n+theme_id*5000)
        for j in range(8):
            for k in range(8):
                xx=x0+j*1.66/8; zz=z+k*1.65/8
                col=shade(theme['grass'],rng.uniform(.83,1.16))
                d.polygon([p(xx,y,zz),p(xx+1.66/8,y,zz),p(xx+1.66/8,y,zz+1.65/8),p(xx,y,zz+1.65/8)],fill=col)
        for j in range(8):
            for k in range(4):
                xx=x0+j*1.66/8; yy=y-k*.85/4
                col=shade(theme['dirt'],rng.uniform(.75,1.22))
                d.polygon([p(xx,yy,z),p(xx+1.66/8,yy,z),p(xx+1.66/8,yy-.85/4,z),p(xx,yy-.85/4,z)],fill=col)
        d.line([a,b,c,e,a],fill=shade(theme['grass'],.67),width=2)
    # First-person blocky hand, kept low enough not to obscure the reaction.
    handx=584+int(10*math.sin(t*10)); handy=1110+int(17*math.sin(t*9))
    d.polygon([(handx,handy),(W,handy-45),(W,H),(handx-48,H)],fill=(46,102,137))
    d.polygon([(handx,handy),(handx+86,handy-29),(handx+110,handy+27),(handx+15,handy+57)],fill=(205,155,111))
    return im
def line_text(d, text, y, maxsize, color='white'):
    size=maxsize
    while size>20 and d.textlength(text,font=font(size))>W-54: size-=1
    f=font(size)
    d.text((W//2,y+4),text,font=f,anchor='mm',fill=(0,0,0),stroke_width=5,stroke_fill=(0,0,0))
    d.text((W//2,y),text,font=f,anchor='mm',fill=color,stroke_width=3,stroke_fill=(18,18,20))
mask=Image.new('L',(S*2,S*2)); ImageDraw.Draw(mask).ellipse((1,1,S*2-2,S*2-2),fill=255)
mask=mask.resize((S,S),Image.Resampling.LANCZOS)
shadow=Image.new('RGBA',(W,H),(0,0,0,0)); sd=ImageDraw.Draw(shadow)
sd.ellipse((W//2-S//2-12,332-12,W//2+S//2+12,332+S+12),fill=(0,0,0,175))
shadow=shadow.filter(ImageFilter.GaussianBlur(15))
def frame(m,t,clip,base):
    im=bg(t,m['theme'],base).convert('RGBA')
    im.alpha_composite(shadow)
    # Telegram-like circle, full-motion video, restrained white rim.
    x=W//2-S//2; y=332
    d=ImageDraw.Draw(im); d.ellipse((x-6,y-6,x+S+6,y+S+6),fill=(249,249,249,255))
    im.paste(clip,(x,y),mask)
    d=ImageDraw.Draw(im)
    for i,line in enumerate(m['hook']): line_text(d,line,160+i*65,56)
    beat=next((b for b in m['beats'] if b[0]<=t<b[1]),m['beats'][-1])
    for i,line in enumerate(beat[2]):
        line_text(d,line,892+i*61,51,'#ffdf4d' if beat==m['beats'][-1] and i==len(beat[2])-1 else 'white')
    # Discreet playback arc and bottom progress.
    d.arc((x-6,y-6,x+S+6,y+S+6),-90,-90+360*t/m['seconds'],fill=(114,232,140),width=6)
    d.rounded_rectangle((36,1224,W-36,1231),radius=3,fill=(42,45,47))
    d.rounded_rectangle((36,1224,max(43,36+int((W-72)*t/m['seconds'])),1231),radius=3,fill=(245,245,245))
    return im.convert('RGB')
def make_sfx(path,m):
    rate=44100; n=int(m['seconds']*rate)
    events=[(0,.055,600),(.15,.055,880)]+[(b[0],.12,350 if i<2 else 145) for i,b in enumerate(m['beats']) if b[0]>0]
    data=bytearray()
    for i in range(n):
        t=i/rate; v=0
        for at,dur,hz in events:
            dt=t-at
            if 0<=dt<dur:
                v+=.19*math.sin(2*math.pi*(hz*dt-100*dt*dt))*math.sin(math.pi*dt/dur)**2
        data.extend(struct.pack('<h',int(max(-1,min(1,v))*32767)))
    with wave.open(str(path),'wb') as f:
        f.setparams((1,2,rate,0,'NONE','not compressed')); f.writeframes(data)
def render(m):
    src=get_clip(m['file']); sfx=ASSETS/(m['id']+'.wav'); make_sfx(sfx,m)
    total=round(m['seconds']*FPS); dur=total/FPS; out=OUT/(m['id']+'.mp4')
    dec=subprocess.Popen(['ffmpeg','-v','error','-stream_loop','-1','-ss',str(m['start']),'-i',str(src),'-an','-vf',f'fps={FPS},scale={S}:{S}:force_original_aspect_ratio=increase,crop={S}:{S},setsar=1','-frames:v',str(total),'-f','rawvideo','-pix_fmt','rgb24','-threads','1','pipe:1'],stdout=subprocess.PIPE)
    probe=subprocess.check_output(['ffprobe','-v','error','-select_streams','a:0','-show_entries','stream=index','-of','csv=p=0',str(src)]).strip()
    cmd=['ffmpeg','-hide_banner','-loglevel','warning','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','pipe:0','-i',str(sfx)]
    if probe:
        cmd+=['-stream_loop','-1','-ss',str(m['start']),'-i',str(src),'-filter_complex','[2:a]aresample=44100,volume=0.75[a];[1:a]volume=0.9[b];[a][b]amix=inputs=2:duration=shortest:normalize=0,alimiter=limit=0.9[mix]','-map','0:v:0','-map','[mix]']
    else: cmd+=['-map','0:v:0','-map','1:a:0']
    cmd+=['-t',str(dur),'-vf','scale=1080:1920:flags=lanczos,setsar=1','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)]
    enc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    base=gradient(THEMES[m['theme']])
    try:
        for i in range(total):
            raw=dec.stdout.read(S*S*3)
            if len(raw)!=S*S*3: raise RuntimeError('Unexpected end of source clip: '+str(src))
            clip=Image.frombytes('RGB',(S,S),raw)
            enc.stdin.write(frame(m,i/FPS,clip,base).tobytes())
    finally:
        enc.stdin.close(); dec.stdout.close()
        dr=dec.wait(); er=enc.wait()
    if dr or er: raise RuntimeError(f'ffmpeg failed: decoder={dr}, encoder={er}')
    print('Rendered',out,flush=True)
if __name__=='__main__':
    import sys
    selection=sys.argv[1:]
    for m in MEMES:
        if not selection or m['id'] in selection: render(m)
