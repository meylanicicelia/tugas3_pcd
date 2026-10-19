"""Analisis histogram dan enhancement 9 citra ijazah.
Alur per citra: RGB -> grayscale (Y = 0.299R + 0.587G + 0.114B) -> histogram -> diagnosis masalah
-> pilih metode enhancement -> histogram hasil -> simpan gambar + metrik."""
import argparse, csv, glob, os
import cv2, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ---------------------------------------------------------------- metode enhancement
def contrast_stretch(g, lo=1, hi=99):
    a, b = np.percentile(g, [lo, hi])
    return np.clip((g.astype(np.float32) - a) * 255.0 / max(b - a, 1), 0, 255).astype(np.uint8)

def gamma(g, gm):
    lut = (255.0 * (np.arange(256) / 255.0) ** gm).astype(np.uint8)
    return cv2.LUT(g, lut)

def hist_eq(g):
    return cv2.equalizeHist(g)

def clahe(g):
    return cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(g)

def median_filter(g):
    return cv2.medianBlur(g, 3)

def otsu(g):
    return cv2.threshold(cv2.GaussianBlur(g, (3, 3), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

def unsharp(g, amount=1.0):
    blur = cv2.GaussianBlur(g, (0, 0), 1.5)
    return cv2.addWeighted(g, 1 + amount, blur, -amount, 0)


# ---------------------------------------------------------------- diagnosis
def diagnose(bgr, g):
    """Hitung ciri citra lalu tentukan masalah utama (aturan sederhana, ambang bisa diubah)."""
    # ukuran asli tiap citra berbeda -> ukur noise pada lebar tetap 800 px agar sebanding
    s = 800 / g.shape[1]
    g8 = cv2.resize(g, (800, int(g.shape[0] * s)), interpolation=cv2.INTER_AREA)
    f = dict(
        median=float(np.median(g)), std=float(g.std()),
        p1=float(np.percentile(g, 1)), p99=float(np.percentile(g, 99)),
        noise=float(np.abs(g8.astype(float) - cv2.medianBlur(g8, 3)).mean()),
        cast=float(np.ptp(bgr.reshape(-1, 3).mean(0))),            # selisih rata-rata kanal B,G,R
        bg_unevenness=float(np.std([np.median(g[y:y+50, x:x+50])
                                    for y in range(0, g.shape[0]-50, 50)
                                    for x in range(0, g.shape[1]-50, 50)
                                    if np.median(g[y:y+50, x:x+50]) > np.percentile(g, 50)] or [0])),
    )
    if f["median"] < 200:
        issue, method = "Terlalu gelap (underexposed) & kontras rendah", "Gamma (g<1) + contrast stretching"
    elif f["noise"] > 2.1:
        issue, method = "Terdistorsi noise", "Median filter"
    elif f["p1"] > 140 and f["std"] < 20:
        issue, method = "Kontras rendah", "Contrast stretching"
    elif f["bg_unevenness"] > 6:
        issue, method = "Pencahayaan tidak merata", "CLAHE"
    elif f["median"] > 250:
        issue, method = "Terlalu terang (overexposed)", "Gamma (g>1)"
    else:
        issue, method = "Kondisi normal / baik", "Unsharp masking"
    return issue, method, f


def apply(method, g):
    if method.startswith("Gamma (g<1)"):
        return contrast_stretch(gamma(g, 0.7))
    if method == "Median filter":
        return median_filter(g)
    if method == "Contrast stretching":
        return contrast_stretch(g)
    if method == "CLAHE":
        return clahe(g)
    if method == "Gamma (g>1)":
        return gamma(g, 1.5)
    if method == "Histogram equalization":
        return hist_eq(g)
    if method == "Otsu thresholding":
        return otsu(g)
    return unsharp(g)


def entropy(g):
    p = np.bincount(g.ravel(), minlength=256) / g.size
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data")
    ap.add_argument("--out", default="results")
    ap.add_argument("--all_methods", action="store_true", help="juga hasilkan perbandingan semua metode per citra")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    files = sorted(glob.glob(os.path.join(a.data, "ijazah-*.*")),
                   key=lambda p: int(os.path.splitext(os.path.basename(p))[0].split("-")[1]))
    rows = []
    print(f"{'File':<14}{'Masalah':<46}{'Metode':<36}{'std':>5}->{'std':<5}{'H':>6}->{'H':<6}")
    for f in files:
        name = os.path.splitext(os.path.basename(f))[0]
        bgr = cv2.imread(f)
        g = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)            # = 0.299R + 0.587G + 0.114B
        issue, method, feat = diagnose(bgr, g)
        e = apply(method, g)
        cv2.imwrite(os.path.join(a.out, f"{name}_enhanced.png"), e)

        fig, ax = plt.subplots(2, 2, figsize=(10, 8))
        ax[0, 0].imshow(g, cmap="gray", vmin=0, vmax=255); ax[0, 0].set_title(f"Citra Grayscale ({name})"); ax[0, 0].axis("off")
        ax[0, 1].hist(g.ravel(), bins=256, range=[0, 256], color="gray"); ax[0, 1].set_title("Histogram Citra Grayscale")
        ax[1, 0].imshow(e, cmap="gray", vmin=0, vmax=255); ax[1, 0].set_title(f"Hasil: {method}"); ax[1, 0].axis("off")
        ax[1, 1].hist(e.ravel(), bins=256, range=[0, 256], color="black"); ax[1, 1].set_title("Histogram Hasil Enhancement")
        for k in (ax[0, 1], ax[1, 1]):
            k.set_xlabel("Intensitas Piksel (0-255)"); k.set_ylabel("Frekuensi")
        plt.tight_layout(); fig.savefig(os.path.join(a.out, f"hasil_histogram_{name}.png"), dpi=70); plt.close(fig)

        if a.all_methods:
            ms = ["Contrast stretching", "Gamma (g<1) + contrast stretching", "Histogram equalization",
                  "CLAHE", "Median filter", "Otsu thresholding", "Unsharp masking"]
            fig, ax = plt.subplots(2, 4, figsize=(14, 6))
            ax = ax.ravel(); ax[0].imshow(g, cmap="gray", vmin=0, vmax=255); ax[0].set_title("asli", fontsize=9)
            for k, m in enumerate(ms, 1):
                ax[k].imshow(apply(m, g), cmap="gray", vmin=0, vmax=255); ax[k].set_title(m, fontsize=8)
            for k in ax: k.axis("off")
            plt.tight_layout(); fig.savefig(os.path.join(a.out, f"semua_metode_{name}.png"), dpi=60); plt.close(fig)

        row = [name, issue, method, round(feat["median"]), round(g.std(), 1), round(e.std(), 1),
               round(entropy(g), 2), round(entropy(e), 2), round(feat["noise"], 2), round(feat["bg_unevenness"], 1)]
        rows.append(row)
        print(f"{name:<14}{issue:<46}{method:<36}{row[4]:>5}->{row[5]:<5}{row[6]:>6}->{row[7]:<6}")
    with open(os.path.join(a.out, "summary.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["citra", "masalah", "metode", "median_asli", "std_asli", "std_hasil",
                    "entropi_asli", "entropi_hasil", "noise", "ketidakmerataan_latar"])
        w.writerows(rows)

if __name__ == "__main__":
    main()
