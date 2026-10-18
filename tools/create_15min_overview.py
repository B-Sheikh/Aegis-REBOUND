"""Build the silent 15-minute product demo: pip install Pillow; install FFmpeg.
Run: python tools/create_15min_overview.py [path/to/ffmpeg]
Editable captions and actual UI captures: submission/demo_assets.
"""
from pathlib import Path
import json, shutil, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageOps
ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'submission/demo_assets'
def font(size):
    for name in ['C:/Windows/Fonts/segoeui.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default(size=size)
def frame(card, position):
    image = Image.new('RGB', (1600, 1000), '#102f29')
    draw = ImageDraw.Draw(image)
    draw.text((40, 18), 'AEGIS REBOUND / ' + card['chapter'], font=font(22), fill='#edf4e9')
    draw.text((1320, 25), f'{position//60:02d}:{position%60:02d} / 15:00', font=font(21), fill='#d1dcbd')
    source = Image.open(ASSETS / card['source']).convert('RGB')
    if card.get('crop'):
        source = source.crop(tuple(card['crop']))
    source = ImageOps.contain(source, (1560, 740), Image.Resampling.LANCZOS)
    image.paste(source, ((1600-source.width)//2, 70+(740-source.height)//2))
    draw.rectangle((20, 830, 1580, 956), fill='#edf3e8')
    lines, line = [], ''
    for word in card['caption'].split():
        test = (line+' '+word).strip()
        if draw.textlength(test, font=font(29)) > 1490:
            lines.append(line)
            line = word
        else:
            line = test
    lines.append(line)
    if len(lines)>3:
        raise ValueError('Caption too long: '+card['caption'])
    for i, line in enumerate(lines):
        draw.text((48, 843+i*35), line, font=font(29), fill='#163d32')
    draw.text((30, 969), 'SILENT EDIT | Recorded UI interactions paced for reading | Synthetic research prototype; not clinically validated', font=font(19), fill='#d1dcbd')
    return image

def main():
    ffmpeg = sys.argv[1] if len(sys.argv)>1 else shutil.which('ffmpeg')
    if not ffmpeg:
        raise SystemExit('Install FFmpeg or provide its executable path.')
    cards = json.loads((ASSETS/'storyboard.json').read_text(encoding='utf-8'))
    assert sum(c['seconds'] for c in cards)==900
    chapters, position = [], 0
    for card in cards:
        if not chapters or chapters[-1]['title']!=card['chapter']:
            chapters.append({'start_seconds':position,'title':card['chapter']})
        position+=card['seconds']
    output = ROOT/'submission/Aegis_REBOUND_15min_Overview.mp4'
    with tempfile.TemporaryDirectory(prefix='rebound-silent-') as directory:
        temp=Path(directory)
        entries, position=[],0
        for i, card in enumerate(cards):
            path=temp/f'frame-{i:03d}.jpg'
            frame(card,position).save(path,quality=92,subsampling=0)
            entries += [f"file '{path.as_posix()}'",f"duration {card['seconds']}"]
            position+=card['seconds']
        entries.append(f"file '{path.as_posix()}'")
        (temp/'frames.txt').write_text('\n'.join(entries),encoding='utf-8')
        meta=[';FFMETADATA1','title=Aegis REBOUND - Silent product demonstrations','artist=Team Aegis']
        for i, chapter in enumerate(chapters):
            end=chapters[i+1]['start_seconds'] if i+1<len(chapters) else 900
            meta += ['[CHAPTER]','TIMEBASE=1/1000',f"START={chapter['start_seconds']*1000}",f'END={end*1000}',f"title={chapter['title']}"]
        (temp/'chapters.txt').write_text('\n'.join(meta),encoding='utf-8')
        subprocess.run([ffmpeg,'-hide_banner','-y','-f','concat','-safe','0','-i',str(temp/'frames.txt'),'-f','ffmetadata','-i',str(temp/'chapters.txt'),'-map','0:v:0','-map_metadata','1','-map_chapters','1','-vf','fps=5,format=yuv420p','-t','900','-an','-c:v','libx264','-preset','veryfast','-tune','stillimage','-crf','23','-movflags','+faststart',str(output)],check=True)
    metadata={'edition':'Silent overview with recorded product demonstrations','verified_duration_seconds':900,'audio_streams':0,'resolution':[1600,1000],'fps':5,'storyboard_cards':len(cards),'production':'Actual application captures after UI interactions, edited and paced for reading; not continuous real-time footage.','chapters':chapters}
    (ROOT/'submission/OVERVIEW_15MIN_METADATA.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    print(output)
if __name__=='__main__':
    main()
