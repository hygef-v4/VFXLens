# grid.py <dir> <out.jpg> [cols]: contact sheet of still-*.jpg sorted by time, labelled.
import sys, glob, os
from PIL import Image, ImageDraw
d, out = sys.argv[1], sys.argv[2]; cols = int(sys.argv[3]) if len(sys.argv) > 3 else 6
fs = sorted(glob.glob(os.path.join(d, 'still-*.jpg')), key=lambda f: float(os.path.basename(f)[6:-4]))
w, h = 300, 533; rows = (len(fs) + cols - 1) // cols; S = Image.new('RGB', (cols * w, rows * h), 'black'); D = ImageDraw.Draw(S)
for i, f in enumerate(fs):
    x, y = (i % cols) * w, (i // cols) * h; S.paste(Image.open(f).resize((w, h)), (x, y)); D.rectangle([x, y, x + 70, y + 22], fill='black'); D.text((x + 4, y + 4), os.path.basename(f)[6:-4], fill='yellow')
S.save(out, quality=85); print(out, len(fs))
