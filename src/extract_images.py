"""Ekstrak 9 citra dari IJAZAH_PCD.pdf -> data/ijazah-1.png ... ijazah-9.png
(urutan = urutan halaman PDF, diputar tegak). Jika punya file asli ijazah-1.jpg dst,
taruh langsung di folder data/ dan lewati langkah ini."""
import os, sys
import cv2, numpy as np
from pypdf import PdfReader

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

def main(pdf):
    os.makedirs(OUT, exist_ok=True)
    for i, page in enumerate(PdfReader(pdf).pages, 1):
        img = cv2.cvtColor(np.array(page.images[0].image.convert("RGB")), cv2.COLOR_RGB2BGR)
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        cv2.imwrite(os.path.join(OUT, f"ijazah-{i}.png"), img)
        print("tersimpan: ijazah-%d.png" % i)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "IJAZAH_PCD.pdf")
