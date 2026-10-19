# Analisis Teoritis Distribusi Histogram

**Pertanyaan: apakah citra dengan histogram yang lebih tersebar selalu berkualitas lebih baik?**
**Jawab: tidak selalu.**

1. Histogram yang lebih tersebar menandakan rentang intensitas lebih luas, tetapi itu belum berarti kualitasnya lebih baik. Pada ijazah, tujuannya adalah membuat tulisan mudah dibedakan dari latar.
2. Peregangan histogram juga memperkuat noise dan tekstur kertas. Pada `ijazah-6`, histogram equalization menghasilkan sebaran paling lebar, tetapi artefak kotak-kotak kompresi di latar ikut menonjol dan teks tampak lebih kotor dibanding contrast stretching (lihat `results/semua_metode_ijazah-6.png`).
3. Median filter pada `ijazah-4` justru **menurunkan** std (28,7 → 23,3) dan entropi (4,45 → 4,00) karena noise dibuang, tetapi citranya lebih bersih.
4. Kualitas dinilai dari pemisahan karakter dan latar, pencahayaan yang sesuai, dan noise yang rendah, bukan dari lebar histogram saja. Metode dipilih sesuai masalah tiap citra.
