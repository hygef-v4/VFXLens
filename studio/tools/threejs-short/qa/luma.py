# luma.py <dir>: mean luma + saturation per still (skill QA target: luma 100-130, heads brightest)
import sys, glob, os
from PIL import Image, ImageStat
for f in sorted(glob.glob(os.path.join(sys.argv[1], 'still-*.jpg')), key=lambda f: float(os.path.basename(f)[6:-4])):
    im = Image.open(f).convert('RGB'); L = ImageStat.Stat(im.convert('L')).mean[0]; s = ImageStat.Stat(im.convert('HSV')).mean[1]
    print(f"{os.path.basename(f)[6:-4]:>6}  luma {L:5.0f} {'OK' if 100 <= L <= 135 else 'LOW' if L < 100 else 'HIGH'}  sat {s:4.0f}")
