# 🎮 Petualangan Bangsawan Malas - Mystery Adventure Game

Game petualangan interaktif berbasis CLI dengan cerita yang dinamis dan sistem pilihan yang mempengaruhi outcome.

## 📖 Cerita

Anda adalah seorang bangsawan muda yang ingin hidup malas tanpa beban. Namun, makhluk berbahaya dari dimensi lain (Harad Pink & Harad Biru) menyerang kampung halaman Anda dan melukai keluarga Anda.

Dengan perjanjian dari Dewa Mati, Anda dapat melintasi dua dimensi untuk menumpas kedua keluarga Harad sekaligus. Anda boleh membawa maksimal **5 sekutu** untuk membantu misi Anda.

### Dua Dimensi untuk Ditaklukkan:

1. **⚔ Harad Pink** - Dunia Wuxia penuh pendekar bela diri
   - Kunci: Membentuk aliansi dengan berbagai fraksi
   - Diperlukan: Pendekar, Dark Elf, atau Penyihir di tim

2. **🐉 Harad Biru** - Dunia didominasi Naga
   - Kunci: Diplomasi dan kerjasama dengan faksi Naga
   - Wajib: Harus punya 1 Naga di tim

## 🎮 Cara Bermain

```bash
python main.py
```

### Menu Utama:
1. **Continue Game** - Lanjutkan game yang sudah disimpan (jika ada)
2. **New Game** - Mulai permainan baru
3. **Keluar** - Tutup aplikasi

### Langkah-Langkah Bermain:

1. **Masukkan Nama** - Nama Anda akan tercatat di log game
2. **Rekrut Sekutu (Max 5)** - Pilih anggota tim dari 10 karakter berbeda:
   - Pendekar (Kade, Zephyr)
   - Elf (Lyssa, Elara)
   - Dark Elf (Nyx)
   - Beastman (Grendor, Torg)
   - Penyihir (Valdris, Morvain)
   - Naga (Rinka)

3. **Jelajahi Dimensi** - Hadapi tantangan di Harad Pink dan Harad Biru
4. **Buat Keputusan Strategis** - Pilihan Anda menentukan jalannya cerita
5. **Sampai di Ending** - Ada Good Ending atau Bad Ending tergantung performa Anda

### Auto-Save:
- Game otomatis disimpan setelah menyelesaikan setiap chapter
- Anda bisa melanjutkan dari menu utama kapan saja
- Save file hilang setelah mencapai ending (good atau bad)

## ⚙️ Fitur Game

- ✨ **Efek Mengetik Dramatis** - Teks keluar dengan jeda 0.05 detik per karakter
- 📍 **Icon Dimensi** - ⚔ untuk Harad Pink, 🐉 untuk Harad Biru
- 📊 **Sistem Logging** - Setiap pilihan dicatat di `game_log.txt`
- � **Save/Load System** - Simpan progress otomatis, lanjutkan kapan saja dari menu utama
- 🔄 **Play Again** - Setelah selesai, bisa langsung bermain lagi
- ❤️ **Sistem Nyawa (3)** - Tiap ending yang salah mengurangi 1 nyawa
- 🎯 **Multiple Endings** - Good atau Bad tergantung pilihan tim & diplomasi
- 🌟 **Custom Ending** - Ending yang dipersonalisasi dengan nama pemain Anda

## � Sistem Save/Load

Game secara otomatis menyimpan progress Anda setelah menyelesaikan setiap chapter:

- **Auto-Save** - Progress tersimpan di folder `saves/` sebagai JSON file
- **Continue Game** - Dari menu utama, pilih pemain untuk melanjutkan game
- **Load Chapter** - Game melanjutkan dari chapter terakhir yang dimainkan
- **Auto Delete** - Save file otomatis dihapus setelah mencapai ending (win atau lose)
- **Multiple Saves** - Bisa menyimpan progress dari berbagai karakter berbeda

## 📊 Sistem Logging

## ❤️ Sistem Nyawa

Anda memulai dengan **3 nyawa**:
- Jika keputusan strategis salah → Nyawa berkurang 1
- Jika nyawa habis sebelum menyelesaikan 2 dimensi → Bad Ending
- Jika menyelesaikan keduanya → Good Ending dengan sisa nyawa

## 🎯 Tips Bermain

1. **Komposisi Tim yang Beragam** - Pikiran yang berbeda menghasilkan solusi lebih baik
2. **Perhatikan Persyaratan Aliansi** - Setiap dimensi butuh tipe karakter tertentu
3. **Fokus pada Kerjasama** - Berbagai ras berbeda membuat diplomasi lebih mudah
4. **Diversitas > Jumlah** - Lebih baik 3 karakter beragam daripada 5 karakter sama

## 📝 Logging System

Semua aktivitas game dicatat di `game_log.txt`:
- Waktu game dimulai
- Nama pemain
- Pilihan strategi
- Outcome setiap chapter
- Ending yang dicapai

Berguna untuk tracking progress dan analytics!

## 🛠️ Requirements

- Python 3.6+
- Tidak ada dependency eksternal

## 📦 File Struktur

```
myadventurebot/
├── main.py           # Game utama
├── game_log.txt      # Log file (dibuat otomatis saat bermain)
├── saves/            # Folder untuk save files
└── README.md         # Dokumentasi ini
```

---

**Selamat menikmati petualangan! Bisakah Anda menumpas kedua keluarga Harad?** 🎮
