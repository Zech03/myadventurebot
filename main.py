import time
import random
import logging
import json
import os
from typing import List, Dict, Tuple, Optional
from datetime import datetime

# Setup logging
logging.basicConfig(
    filename='game_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# Save file configuration
SAVE_DIR = "saves"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

class Ally:
    def __init__(self, name: str, race: str, skill: str, specialty: str):
        self.name = name
        self.race = race  # beastman, naga, penyihir, pendekar, elf, dark elf
        self.skill = skill
        self.specialty = specialty
    
    def __str__(self):
        return f"{self.name} ({self.race}) - {self.skill}"

class Player:
    def __init__(self, name: str):
        self.name = name
        self.lives = 3
        self.max_lives = 3
        self.allies: List[Ally] = []
        self.max_allies = 5
        self.story_state = "awal"
    
    def recruit_ally(self, ally: Ally) -> bool:
        if len(self.allies) < self.max_allies:
            self.allies.append(ally)
            return True
        return False
    
    def lose_life(self):
        if self.lives > 0:
            self.lives -= 1
    
    def is_alive(self) -> bool:
        return self.lives > 0
    
    def __str__(self):
        return f"Pemain: {self.name} | Nyawa: {self.lives}/{self.max_lives} | Sekutu: {len(self.allies)}/{self.max_allies}"

class MysteryGame:
    def __init__(self):
        self.player = None
        self.typing_speed = 0.05  # jeda per karakter dalam detik
        self.current_chapter = 0  # 0: awal, 1: harad pink, 2: harad biru, 3: ending
        self.game_paused = False
        self.available_allies = [
            Ally("Kade", "Pendekar", "Bela Diri Tinju Dahsyat", "Ahli dalam pertempuran satu lawan satu"),
            Ally("Lyssa", "Elf", "Panahan Presisi", "Mata tajam, tak pernah meleset"),
            Ally("Grendor", "Beastman", "Kekuatan Bruto", "Kekuatan ganda lipat dari manusia normal"),
            Ally("Valdris", "Penyihir", "Sihir Gelap", "Menguasai kutukan dan sihir ilmu tersembunyi"),
            Ally("Zephyr", "Pendekar", "Seni Pedang Kilat", "Kecepatan tak tertandingi"),
            Ally("Nyx", "Dark Elf", "Pembunuh Bayangan", "Ahli stealth dan assassinasi"),
            Ally("Rinka", "Naga", "Napas Api", "Bisa mengeluarkan api yang membakar segalanya"),
            Ally("Morvain", "Penyihir", "Pemulih Kekuatan", "Menyembuhkan dan memberikan buff pada tim"),
            Ally("Torg", "Beastman", "Perisai Hidup", "Tank yang solid untuk melindungi tim"),
            Ally("Elara", "Elf", "Ketajaman Indera", "Bisa mendeteksi kelemahan musuh"),
        ]
    
    def type_text(self, text: str, speed: float = None):
        """Cetak teks dengan efek mengetik dramatis"""
        if speed is None:
            speed = self.typing_speed
        
        for char in text:
            print(char, end='', flush=True)
            time.sleep(speed)
        print()  # newline di akhir
    
    def type_line(self, text: str, speed: float = None):
        """Cetak satu baris dengan efek mengetik"""
        if speed is None:
            speed = self.typing_speed
        
        for char in text:
            print(char, end='', flush=True)
            time.sleep(speed)
        print()  # newline di akhir
    
    def print_fast(self, text: str):
        """Print normal tanpa efek mengetik"""
        print(text)
    
    def clear_screen(self):
        print("\n" * 3)
    
    def pause(self, durasi: float = 2):
        time.sleep(durasi)
    
    def save_game(self) -> bool:
        """Simpan progress game ke file"""
        if not self.player:
            return False
        
        try:
            save_data = {
                "player_name": self.player.name,
                "lives": self.player.lives,
                "max_lives": self.player.max_lives,
                "current_chapter": self.current_chapter,
                "allies": [
                    {
                        "name": ally.name,
                        "race": ally.race,
                        "skill": ally.skill,
                        "specialty": ally.specialty
                    }
                    for ally in self.player.allies
                ],
                "save_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            save_file = os.path.join(SAVE_DIR, f"{self.player.name}_save.json")
            with open(save_file, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            logging.info(f"Game disimpan: {self.player.name} - Chapter {self.current_chapter}")
            return True
        except Exception as e:
            logging.error(f"Error menyimpan game: {e}")
            return False
    
    def load_game(self, player_name: str) -> bool:
        """Muat progress game dari file"""
        try:
            save_file = os.path.join(SAVE_DIR, f"{player_name}_save.json")
            
            if not os.path.exists(save_file):
                return False
            
            with open(save_file, 'r') as f:
                save_data = json.load(f)
            
            # Recreate player
            self.player = Player(save_data["player_name"])
            self.player.lives = save_data["lives"]
            self.player.max_lives = save_data["max_lives"]
            self.current_chapter = save_data["current_chapter"]
            
            # Recreate allies
            for ally_data in save_data["allies"]:
                ally = Ally(
                    ally_data["name"],
                    ally_data["race"],
                    ally_data["skill"],
                    ally_data["specialty"]
                )
                self.player.allies.append(ally)
            
            logging.info(f"Game dimuat: {self.player.name} - Chapter {self.current_chapter}")
            return True
        except Exception as e:
            logging.error(f"Error memuat game: {e}")
            return False
    
    def get_save_files(self) -> List[str]:
        """Dapatkan daftar file save yang tersedia"""
        try:
            save_files = []
            for file in os.listdir(SAVE_DIR):
                if file.endswith("_save.json"):
                    player_name = file.replace("_save.json", "")
                    save_files.append(player_name)
            return sorted(save_files)
        except:
            return []
    
    def show_main_menu(self) -> Optional[str]:
        """Tampilkan menu utama dan return pilihan"""
        self.clear_screen()
        print("╔" + "═"*58 + "╗")
        print("║" + "PETUALANGAN BANGSAWAN MALAS".center(58) + "║")
        print("║" + "vs Kaum Harad Yang Berbahaya".center(58) + "║")
        print("╚" + "═"*58 + "╝")
        print()
        
        save_files = self.get_save_files()
        
        print("=" * 60)
        print("MENU UTAMA")
        print("=" * 60)
        print()
        
        option = 1
        
        if save_files:
            print(f"{option}. Continue Game (Status Tersimpan)")
            option += 1
        
        print(f"{option}. New Game")
        option += 1
        
        print(f"{option}. Keluar")
        print()
        
        pilihan = input("Pilih opsi: > ").strip()
        
        if pilihan == "1" and save_files:
            # Show save file options
            self.clear_screen()
            print("PILIH SAVE FILE:")
            print()
            for i, save_file in enumerate(save_files, 1):
                print(f"{i}. {save_file}")
            print()
            
            pilih_save = input("Pilih nomor: > ").strip()
            try:
                idx = int(pilih_save) - 1
                if 0 <= idx < len(save_files):
                    return f"continue:{save_files[idx]}"
            except:
                pass
            return None
        elif pilihan == str(option - 1):  # Keluar
            return "exit"
        else:
            return "new_game"
    
    def print_status(self):
        print(f"\n{'='*60}")
        print(self.player)
        if self.player.allies:
            print("Sekutu Anda:")
            for i, ally in enumerate(self.player.allies, 1):
                print(f"  {i}. {ally}")
        print(f"{'='*60}\n")
    
    def game_intro(self):
        self.clear_screen()
        print("╔" + "═"*58 + "╗")
        print("║" + " "*58 + "║")
        print("║" + "PETUALANGAN BANGSAWAN MALAS".center(58) + "║")
        print("║" + "vs Kaum Harad Yang Berbahaya".center(58) + "║")
        print("║" + " "*58 + "║")
        print("╚" + "═"*58 + "╝")
        print()
        
        nama = input("Siapa nama yang Anda gunakan? > ").strip()
        if not nama:
            nama = "Pahlawan Tanpa Nama"
        
        self.player = Player(nama)
        logging.info(f"Game dimulai: {nama}")
        
        print(f"\n--- Selamat datang, {nama}! ---\n")
        self.pause(1)
        
        # Story intro dengan typing effect
        story = """
Anda adalah seorang bangsawan muda berdarah biru. Setiap hari Anda hanya ingin bersantai,
berminum teh, membaca buku, dan menikmati kehidupan yang nyaman tanpa beban apapun.
Itulah impian Anda... hidup malas tanpa kekhawatiran.

Namun, satu malam, ketenangan itu hancur berkeping-keping.
        """
        self.type_text(story.strip(), speed=0.02)
        self.pause(2)
        
        story2 = """
Makhluk aneh menembus dunia Anda dari dimensi lain. Mereka hidup di dua muka,
dua keluarga satu kegelapan: Harad Pink dan Harad Biru.

Mereka menyerang kampung halaman Anda tanpa ampun. Penduduk menderita.
Keluarga Anda, orang-orang terkasih Anda, terluka dan nyaris kehilangan nyawa.
        """
        self.type_text(story2.strip(), speed=0.02)
        self.pause(2)
        
        story3 = """
Pada malam ketika semuanya terasa hopeless, sang Dewa Mati menampilkan diri.
Dia menawarkan perjanjian: Anda bisa melintasi dimensi lain, memburu kedua keluarga Harad,
dan menumpas mereka sampai ke akar-akarnya. Tapi ada syarat...

Anda hanya boleh membawa MAKSIMAL 5 sekutu untuk menemani perjalanan Anda.
Pilihan ini menentukan nasib semuanya.
        """
        self.type_text(story3.strip(), speed=0.02)
        self.pause(2)
        
        print(self.player)
        print()
    
    def recruitment_phase(self):
        print("\n" + "="*60)
        print("FASE REKRUTMEN SEKUTU")
        print("="*60)
        print(f"\nAnda dapat merekrut maksimal {self.player.max_allies} sekutu untuk petualangan ini.")
        print("Pilih dengan bijak! Komposisi tim Anda akan menentukan kesuksesan.\n")
        
        while len(self.player.allies) < self.player.max_allies:
            print(f"\nSecond Chance - Anda sudah merekrut {len(self.player.allies)} dari {self.player.max_allies} sekutu")
            print("\n--- Daftar Calon Sekutu Tersedia ---")
            
            available = [a for a in self.available_allies if a not in self.player.allies]
            
            for i, ally in enumerate(available, 1):
                print(f"{i}. {ally}")
            
            print(f"{len(available)+1}. Lanjutkan ke Petualangan")
            
            pilihan = input(f"\nPilih nomor (1-{len(available)+1}): > ").strip()
            
            try:
                pilihan = int(pilihan)
                if pilihan == len(available) + 1:
                    if len(self.player.allies) == 0:
                        print("\n⚠️  Anda harus merekrut MINIMAL 1 sekutu untuk bertahan!")
                        continue
                    break
                elif 1 <= pilihan <= len(available):
                    ally = available[pilihan - 1]
                    self.player.recruit_ally(ally)
                    print(f"\n✓ {ally.name} ({ally.race}) bergabung dengan tim Anda!")
                    self.pause(1)
                else:
                    print("\n❌ Pilihan tidak valid!")
            except ValueError:
                print("\n❌ Masukkan angka yang valid!")
        
        print("\n" + "="*60)
        self.print_status()
    
    def chapter_one_harad_pink(self):
        """Bab 1 - Dimensi Harad Pink (Dunia Wuxia)"""
        self.clear_screen()
        
        print("╔" + "═"*58 + "╗")
        print("║" + "⚔ BAB 1: DIMENSI HARAD PINK ⚔".center(58) + "║")
        print("║" + "Dunia Pendekar Bela Diri".center(58) + "║")
        print("╚" + "═"*58 + "╝")
        
        story = """
Anda melintasi portal gelap menuju dunia baru yang dipenuhi gunung-gunung megah 
dan pagoda-pagoda kuno. Ini adalah Harad Pink, dimensi yang diisi oleh pendekar-pendekar
bela diri yang handal.

Keluarga Harad Pink adalah keluarga bangsawan terlarang yang ditakuti dan dibenci
oleh semua fraksi di dunia ini. Mereka mencari keajaiban terlarang dan kekuatan gelap.

Untuk mengalahkan mereka, Anda membutuhkan ALIANSI dengan berbagai fraksi:
  • SEKTE TERANG - Penjaga keseimbangan (tersedia jika ada Pendekar di tim)
  • ORGANISASI PEMBUNUH - Pengkhianat kelas tinggi Harad Pink (tersedia jika ada Assassin)
  • BIARA TIMUR - Penyembuh dan diplomat (tersedia jika ada Penyihir)
        """
        self.type_text(story.strip(), speed=0.015)
        self.pause(2)
        
        # Check available alliances
        alliances_available = []
        team_races = [ally.race for ally in self.player.allies]
        
        if any(race in team_races for race in ["Pendekar"]):
            alliances_available.append("Sekte Terang")
        if any(race in team_races for race in ["Dark Elf"]):
            alliances_available.append("Organisasi Pembunuh")
        if any(race in team_races for race in ["Penyihir"]):
            alliances_available.append("Biara Timur")
        
        if not alliances_available:
            logging.warning(f"{self.player.name} - Aliansi Harad Pink gagal dibentuk")
            print("\n\n⚠️  ENDING GELAP ⚠️")
            print("\nTim Anda tidak memiliki cukup tipe karakter untuk membentuk aliansi!")
            print("Tanpa dukungan fraksi lokal, Anda terhimpit dari segala arah.")
            print("Pasukan Harad Pink menghancurkan Anda.")
            print("\n❌ ANDA KALAH DAN DUNIA ANDA AKAN KEMBALI DALAM KEGELAPAN")
            self.player.lose_life()
            return False
        
        print(f"\n✓ Aliansi tersedia: {', '.join(alliances_available)}")
        print("Anda telah membentuk aliansi strategis!")
        self.pause(1)
        
        # Battle scenario
        print("\n" + "="*60)
        print("⚔ PERTEMPURAN TERAKHIR HARAD PINK ⚔")
        print("="*60)
        
        print(f"\nDengan dukungan aliansi lokal, tim Anda ({len(self.player.allies)} anggota) bersiap menghadapi")
        print("pasukan Harad Pink yang dipimpin oleh SANG PANGERAN MERAH.\n")
        self.pause(1)
        
        # PILIHAN UTAMA (Level 1)
        print("\n┌─ STRATEGI PERTAMA ─────────────────────────────────────┐")
        print("│ Ada tiga strategi besar yang bisa Anda persiapkan:      │")
        print("└────────────────────────────────────────────────────────┘\n")
        
        print("1. ⚔️  SERANGAN LANGSUNG - Serang markas Harad Pink dengan penuh kekuatan")
        print("   └─ Cepat, berisiko tinggi pada sekutu\n")
        
        print("2. 🕵️  SABOTASE INTERNAL - Gunakan spion untuk menghancurkan dari dalam")
        print("   └─ Aman, memerlukan strategi kompleks\n")
        
        print("3. ⚡ MAGIK GELAP - Gunakan artefak kuno untuk sealing kekuatan mereka")
        print("   └─ Powerful, tidak semua orang bisa menguasainya\n")
        
        pilihan_utama = input("Pilih strategi utama (1-3): > ").strip()
        logging.info(f"{self.player.name} - Harad Pink strategi utama: {pilihan_utama}")
        
        if pilihan_utama == "1":
            return self._harad_pink_serangan_langsung(alliances_available)
        elif pilihan_utama == "2":
            return self._harad_pink_sabotase(alliances_available)
        elif pilihan_utama == "3":
            return self._harad_pink_magik_gelap(alliances_available)
        else:
            print("\n❌ Pilihan tidak valid! Anda ragu dan pertempuran dimulai dengan sembarangan...")
            print("Harad Pink mengambil kesempatan emas untuk menyerang!")
            self.player.lose_life()
            return False
    
    def _harad_pink_serangan_langsung(self, alliances):
        """Cabang 1: Serangan Langsung"""
        print("\n" + "="*60)
        print("⚔️ PERSIAPAN SERANGAN LANGSUNG ⚔️")
        print("="*60)
        
        story = """
Anda mengarahkan semua pasukan untuk menyerang frontal markas Harad Pink.
Aliansi Anda berkumpul di perbatasan, bersiap untuk menyerbu.

Namun saat akan menyerang, Anda menemukan TIGA PILIHAN TAKTIK:
        """
        self.type_text(story.strip(), speed=0.015)
        self.pause(1)
        
        print("\n1. SERBU SIANG HARI - Serang ketika mereka tidak siap")
        print("   └─ Keuntungan: Elemen kejutan penuh\n")
        
        print("2. SERBU MALAM HARI - Tunggu sampai darkness untuk hidden attack")
        print("   └─ Keuntungan: Aliansi bisa bergerak lebih stealth\n")
        
        print("3. SERBU SERENTAK - Serang dari tiga sisi berbeda bersamaan")
        print("   └─ Keuntungan: Tidak ada jalan keluar untuk musuh\n")
        
        pilihan_taktik = input("Pilih taktik serangan (1-3): > ").strip()
        logging.info(f"{self.player.name} - Serangan Langsung taktik: {pilihan_taktik}")
        
        # PERCABANGAN LEVEL 3 untuk Serangan Langsung
        if pilihan_taktik == "1":
            self.type_text("\nSerangan siang hari dimulai dengan cahaya matahari menembus pagoda merah...", speed=0.02)
            self.pause(1)
            # Sub-pilihan untuk siang hari
            return self._serangan_langsung_siang()
        elif pilihan_taktik == "2":
            self.type_text("\nMalam gelap menyelimuti dunia Harad Pink, menjadi penutup sempurna untuk penyerangu...", speed=0.02)
            self.pause(1)
            return self._serangan_langsung_malam()
        elif pilihan_taktik == "3":
            self.type_text("\nTiga pasukan bergerak dari tiga penjuru dengan koordinasi sempurna...", speed=0.02)
            self.pause(1)
            return self._serangan_langsung_serentak()
        else:
            print("\n❌ Taktik tidak jelas, pertempuran menjadi kacau!")
            self.player.lose_life()
            return False
    
    def _serangan_langsung_siang(self):
        """Level 3: Serangan Siang Hari"""
        print("\nPangeran Merah terkejut melihat serangan di siang bolong!")
        
        print("\nNamun dia memiliki TIGA KARTU AS yang bisa dimainkan:")
        print("1. BALA BANTUAN - Memanggil pendekar-pendekar terpencar untuk bertahan")
        print("2. LEDAKAN MAGIK - Menggunakan sihir terlarang untuk counterattack")
        print("3. NEGOSIASI - Menawarkan perdamaian dengan syarat sulit\n")
        
        sub_pilihan = input("Apa yang Anda lakukan? (1-3): > ").strip()
        logging.info(f"{self.player.name} - Siang hari respon: {sub_pilihan}")
        
        if sub_pilihan == "1":
            print("\nAnda menghadang bala bantuan sebelum mereka tiba!")
            print("Pertempuran sengit, tapi aliansi Anda lebih disiplin dan terkoordinasi.")
            print("\n✓ HARAD PINK BERHASIL DIHANCURKAN SECARA TOTAL!")
            return True
        elif sub_pilihan == "2":
            print("\nLedakan magik dahsyat meledak di mana-mana!")
            print("Ada korban di kedua belah pihak. Namun...")
            print("Pangeran Merah terlalu terpaksa menghabiskan semua energinya.")
            print("Anda menangkap kesempatan emas untuk mengalahkannya!")
            print("\n✓ HARAD PINK DIHANCURKAN - Dengan beberapa korban")
            self.player.lose_life()  # Berkurang 1
            return True
        else:
            print("\nAnda mendengarkan tawarannya... tapi ini hanya trik!")
            print("Pangeran Merah menyerang saat Anda lengah!")
            print("\n❌ ANDA TERJEBAK DAN KALAH!")
            self.player.lose_life()
            return False
    
    def _serangan_langsung_malam(self):
        """Level 3: Serangan Malam Hari"""
        print("\nKegelapan malam membuat Harad Pink tidak melihat serangan Anda!")
        
        print("\nAnda memiliki TIGA FASE PERHITUNGAN TAKTIK:")
        print("1. TEMBAK DULU - Serang langsung tanpa memberikan kesempatan")
        print("2. TANGKAP PEMIMPIN - Fokus mengejar Pangeran Merah dulu")
        print("3. AMANKAN POSISI - Kuatkan pertahanan sebelum serangan balik\n")
        
        sub_pilihan = input("Fase apa yang Anda prioritaskan? (1-3): > ").strip()
        logging.info(f"{self.player.name} - Malam hari fase: {sub_pilihan}")
        
        if sub_pilihan == "1":
            print("\nSerangan membabi buta di kegelapan!")
            print("Harad Pink tidak punya waktu untuk bersiap...")
            print("Mereka diculik dari lingkaran keamanan mereka sendiri!")
            print("\n✓ HARAD PINK DIHANCURKAN - Dengan casualty minimal!")
            return True
        elif sub_pilihan == "2":
            print("\nAnda hunt Pangeran Merah melalui lorong-lorong gelap pagoda!")
            print("Akhirnya Anda pun bertemu dia... dalam pertempuran 1v1 yang legendary!")
            print("Eksklusif - single combat, tim Anda tidak bisa membantu...")
            print("\nTapi Anda berhasil! Pangeran Merah jatuh!")
            print("\n✓ HARAD PINK DIHANCURKAN - SANG PAHLAWAN TERUNGKAP!")
            return True
        else:
            print("\nAnda membangun pertahanan, tapi ini kesalahan fatal!")
            print("Pangeran Merah dengan teman-temannya counter-attack Anda!")
            print("Pertempuran kali ini berbalik menjadi defensif...")
            print("\n⚠️ Anda berhasil bertahan, namun dengan KERUGIAN BESAR")
            self.player.lose_life()
            return True
    
    def _serangan_langsung_serentak(self):
        """Level 3: Serangan Serentak 3 Sisi"""
        print("\nTiga pasukan menyerang dari timur, barat, dan utara!")
        print("Pangeran Merah yang licik menyadari strategi Anda...")
        
        print("\nDia memecah pertahanan menjadi TIGA BLOK PERTAHANAN:")
        print("1. BLOK UTARA - Bela diri dengan beastmaster")
        print("2. BLOK TIMUR - Pertahanan dengan penjaga istana")
        print("3. BLOK BARAT - Serangan balasan dengan elit warrior\n")
        
        sub_pilihan = input("Blok mana yang paling RENTAAN untuk Anda targetkan? (1-3): > ").strip()
        logging.info(f"{self.player.name} - 3 sisi blok target: {sub_pilihan}")
        
        if sub_pilihan == "1":
            print("\nBlok Utara mudah ditembus oleh strategi Anda!")
            print("Setelah bobol di utara, Anda bisa mengejar Pangeran Merah ke arah pusat!")
            print("\n✓ HARAD PINK DIHANCURKAN - STRATEGI 3 SISI BERHASIL SEMPURNA!")
            return True
        elif sub_pilihan == "2":
            print("\nBlok Timur adalah jantung pertahanan mereka...")
            print("Pertempuran brutal berlangsung di sini selama berjam-jam!")
            print("Akhirnya... Anda tembus juga!")
            print("\n✓ HARAD PINK DIHANCURKAN - KEMENANGAN PENUH DARAH!")
            self.player.lose_life()
            return True
        else:
            print("\nAnda fokus ke blok barat... TAPI INI JEBAKAN!")
            print("Blok barat malah balik menyerang tim Anda!")
            print("Anda harus retreat dengan kerugian besar!")
            print("\n❌ PERTEMPURAN GAGAL - ANDA KALAH!")
            self.player.lose_life()
            self.player.lose_life()
            return False
    
    def _harad_pink_sabotase(self, alliances):
        """Cabang 2: Sabotase Internal"""
        print("\n" + "="*60)
        print("🕵️ PERSIAPAN SABOTASE INTERNAL 🕵️")
        print("="*60)
        
        story = """
Anda memilih rute yang lebih halus - menghancurkan Harad Pink dari dalam.
Spion-spion Anda sudah tersebar di berbagai lokasi penting.

Anda merencanakan TIGA TARGET SABOTASE strategis:
        """
        self.type_text(story.strip(), speed=0.015)
        self.pause(1)
        
        print("\n1. SABOASE GUDANG SENJATA - Ledakkan senjata mereka, buat mereka lemah")
        print("   └─ Efek: Pasukan tanpa senjata kuat\n")
        
        print("2. SABOTASE MARKAS KOMANDO - Bunuh para jenderal, hancurkan koordinasi")
        print("   └─ Efek: Pasukan tidak terkoordinasi\n")
        
        print("3. SABOTASE RUMAH PANGERAN - Bunuh Pangeran Merah langsung")
        print("   └─ Efek: Kepemimpinan hilang, chaos total\n")
        
        pilihan_target = input("Target sabotase utama (1-3)? > ").strip()
        logging.info(f"{self.player.name} - Sabotase target: {pilihan_target}")
        
        if pilihan_target == "1":
            return self._sabotase_gudang()
        elif pilihan_target == "2":
            return self._sabotase_markas()
        elif pilihan_target == "3":
            return self._sabotase_pangeran()
        else:
            print("\n❌ Target tidak jelas, rencana Anda kebacaan!")
            print("Harad Pink siap dan menghancurkan tim Anda!")
            self.player.lose_life()
            return False
    
    def _sabotase_gudang(self):
        """Level 3: Sabotase Gudang Senjata"""
        print("\nSpion Anda berhasil masuk ke gudang senjata Harad Pink!")
        print("Namun mereka menemukan SISTEM PENGAMANAN BERLAPIS:\n")
        
        print("1. DEFUSALKAN BOM PERANGKAP - Disarm sistem keamanan tiga layer")
        print("2. LEDAKKAN SEKARANG - Serang manual tanpa menghindari perangkap")
        print("3. LEPAS DARI SINI - Retreat untuk rencana lain\n")
        
        sub_pilihan = input("Aksi spion (1-3)? > ").strip()
        logging.info(f"{self.player.name} - Gudang sabotase aksi: {sub_pilihan}")
        
        if sub_pilihan == "1":
            print("\nDengan kesabaran dan keahlian, spion Anda berhasil disarm sistem!")
            print("Gudang ledak meledak dengan sempurna, menghancurkan semua senjata!")
            print("\n✓ HARAD PINK BERHASIL DILEMAHKAN - TAHAP KEDUA DIMULAI!")
            print("Tanpa senjata, mereka mudah dikalahkan oleh pasukan aliansi Anda!")
            print("\n✓ HARAD PINK TELAH DIHANCURKAN!")
            return True
        elif sub_pilihan == "2":
            print("\nLedakan besar meruntuhkan gudang!")
            print("Tapi alarm aktivasi - Harad Pink siap-siap!")
            print("Pertempuran jadi lebih sulit dan banyak korban di pihak Anda...")
            print("\n⚠️ HARAD PINK DIHANCURKAN - TAPI DENGAN HARGA MAHAL!")
            self.player.lose_life()
            return True
        else:
            print("\nSpion Anda mundur... tapi mereka ketahuan!")
            print("Keamanan Harad Pink meningkat dua kali lipat!")
            print("\n❌ SABOTASE GAGAL - ANDA KALAH!")
            self.player.lose_life()
            return False
    
    def _sabotase_markas(self):
        """Level 3: Sabotase Markas Komando"""
        print("\nMarkas komando Harad Pink terletak di puncak pagoda tertinggi!")
        print("Spion Anda mengidentifikasi TIGA JALAN MASUK:\n")
        
        print("1. JALAN DEPAN - Langsung masuk melalui gerbang utama")
        print("2. JALAN ATAP - Naik lewat atap dengan akrobatik berbahaya")
        print("3. JALAN BAWAH - Terobos dari catacomb bawah pagoda\n")
        
        sub_pilihan = input("Jalan masuk yang dipilih (1-3)? > ").strip()
        logging.info(f"{self.player.name} - Markas sabotase jalan: {sub_pilihan}")
        
        if sub_pilihan == "1":
            print("\nMasuk dari depan - action direct!")
            print("Spion Anda berhasil menembus penjaga...")
            print("Para jenderal Harad Pink jatuh satu per satu...")
            print("\n✓ MARKAS KOMANDO BERHASIL DIHANCURKAN!")
            print("Tanpa koordinasi, Harad Pink ambruk!")
            print("\n✓ HARAD PINK TELAH DIHANCURKAN!")
            return True
        elif sub_pilihan == "2":
            print("\nAkrobatik di atap berbahaya...")
            print("Spion Anda sempat, tapi sulit - ada pertempuran atap yang epik!")
            print("Akhirnya, semua jenderal jatuh!")
            print("\n⚠️ MARKAS KOMANDO DIHANCURKAN - DENGAN KORBAN SPION!")
            self.player.lose_life()
            return True
        else:
            print("\nJalan catacomb gelap dan berbahaya...")
            print("Ada monster terperangkap di bawah!")
            print("\n❌ SPION ANDA HILANG - SABOTASE GAGAL!")
            self.player.lose_life()
            return False
    
    def _sabotase_pangeran(self):
        """Level 3: Sabotase Langsung ke Pangeran Merah"""
        print("\nMembunuh Pangeran Merah adalah target tertinggi!")
        print("Spion elite Anda harus menembus TIGA LAPISAN PERLINDUNGAN:\n")
        
        print("1. LAPISAN FISIK - Bunuh langsung malam hari di kamarnya")
        print("2. LAPISAN MAGIK - Gunakan kutukan untuk melemahkannya dulu")
        print("3. LAPISAN SOSIAL - Manfaatkan gundik atau sekutu untuk akses\n")
        
        sub_pilihan = input("Metode penetrasi (1-3)? > ").strip()
        logging.info(f"{self.player.name} - Pangeran sabotase metode: {sub_pilihan}")
        
        if sub_pilihan == "1":
            print("\nAssassinasi langsung! Spion Anda masuk ke kamar Pangeran Merah...")
            print("Pertarungan sepi di malam gelap...")
            print("Pangeran Merah terbunuh! Tanpa pemimpin, Harad Pink runtuh!")
            print("\n✓ PANGERAN MERAH TERBUNUH - HARAD PINK KEHILANGAN KEPEMIMPINAN!")
            print("\n✓ HARAD PINK TELAH DIHANCURKAN!")
            return True
        elif sub_pilihan == "2":
            print("\nKutukan dikirim ke Pangeran Merah, dia jatuh sakit parah!")
            print("Namun dia masih hidup dan bisa counterattack dengan lemah...")
            print("Anda manfaatkan kesempatan ini!")
            print("\n⚠️ PANGERAN MERAH DIKALAHKAN - STRATEGY BERHASIL!")
            return True
        else:
            print("\nSpion Anda bermain cinta dengan gundik Pangeran...")
            print("Tapi ini adalah JEBAKAN! Gundik itu mata-mata Harad Pink!")
            print("\n❌ SPION ANDA TERTANGKAP - SABOTASE GAGAL TOTAL!")
            self.player.lose_life()
            self.player.lose_life()
            return False
    
    def _harad_pink_magik_gelap(self, alliances):
        """Cabang 3: Magik Gelap"""
        print("\n" + "="*60)
        print("⚡ PERSIAPAN RITUAL MAGIK GELAP ⚡")
        print("="*60)
        
        # Check if player has wizard
        has_wizard = any(ally.race == "Penyihir" for ally in self.player.allies)
        
        if not has_wizard:
            print("\n⚠️ MASALAH FATAL!")
            print("Untuk ritual magik gelap, Anda HARUS memiliki Penyihir di tim!")
            print("Tim Anda tidak memiliki Penyihir yang cakap!")
            print("\nRitual gagal, tenaga gelap membalik ke Anda!")
            print("\n❌ ANDA KEWALAHAN OLEH ENERGI MAGIK SENDIRI!")
            self.player.lose_life()
            self.player.lose_life()
            return False
        
        wizard_ally = [a.name for a in self.player.allies if a.race == "Penyihir"][0]
        
        story = f"""
{wizard_ally} sang Penyihir mempersiapkan ritual magik gelap yang sangat powerful!
Dia mengumpulkan artefak-artefak kuno dan melakukan ceremony mistis.

Ritual ini memiliki TIGA VARIAN BERBEDA dengan risiko/reward berbeda:
        """
        self.type_text(story.strip(), speed=0.015)
        self.pause(1)
        
        print("\n1. SEALING KESELURUHAN - Seal semua kekuatan Harad Pink sekaligus")
        print("   └─ Risiko: SANGAT TINGGI, nyawa penyihir terancam\n")
        
        print("2. BINDING GELAP - Ikat Pangeran Merah dengan rantai magik")
        print("   └─ Risiko: Tinggi, tapi terkontrol\n")
        
        print("3. CURSE KETURUNAN - Kutukan yang melemahkan garis keturunan mereka")
        print("   └─ Risiko: Sedang, efek jangka panjang\n")
        
        pilihan_ritual = input("Varian ritual magik (1-3)? > ").strip()
        logging.info(f"{self.player.name} - Magik gelap varian: {pilihan_ritual}")
        
        if pilihan_ritual == "1":
            return self._magik_sealing_keseluruhan(wizard_ally)
        elif pilihan_ritual == "2":
            return self._magik_binding_gelap(wizard_ally)
        elif pilihan_ritual == "3":
            return self._magik_curse_keturunan(wizard_ally)
        else:
            print("\n❌ Varian ritual tidak jelas, energi rogue!")
            print(f"{wizard_ally} jatuh karena ledakan magik!")
            self.player.lose_life()
            return False
    
    def _magik_sealing_keseluruhan(self, wizard):
        """Level 3: Sealing Keseluruhan"""
        print(f"\n{wizard} memulai ritual SEALING KESELURUHAN!")
        print("Energi gelap bergabung dari semua arah...\n")
        
        print("TEST KEKUATAN PENYIHIR:")
        print("1. KUAT - Ritual berhasil penuh, semua kekuatan Harad Pink di-seal!")
        print("2. SEDANG - Ritual berhasil sebagian, mereka lemah tapi tidak fully sealed")
        print("3. LEMAH - Ritual gagal, energi counter-attack balik\n")
        
        sub_pilihan = input("Berapa kuat penyihir Anda (1-3)? > ").strip()
        logging.info(f"{self.player.name} - Sealing kekuatan ritual: {sub_pilihan}")
        
        if sub_pilihan == "1":
            print(f"\n{wizard} mencurahkan semua kekuatan nyawanya...")
            print("Ritual SUKSES! Semua kekuatan Harad Pink ter-seal dalam dimensi lain!")
            print("Mereka tidak bisa bertarung lagi!")
            print("\n✓ HARAD PINK DIHANCURKAN - SEALING SEMPURNA!")
            return True
        elif sub_pilihan == "2":
            print(f"\n{wizard} melakukan ritual dengan effort penuh...")
            print("Ritual berhasil 60% - Harad Pink jauh lebih lemah!")
            print("Pertempuran masih bisa dimenangkan dengan upaya ekstra!")
            print("\n⚠️ HARAD PINK DILEMAHKAN - PERTEMPURAN LANJUT!")
            print("Aliansi Anda menyelesaikan pekerjaan dengan serangan konvensional!")
            print("\n✓ HARAD PINK AKHIRNYA DIHANCURKAN!")
            self.player.lose_life()
            return True
        else:
            print(f"\n{wizard} kehilangan kendali atas ritual!")
            print("Energi counter-attack balik dengan ganas!")
            print(f"Yah sayangnya {wizard} tidak survive dari ledakan ini...")
            print("Tapi before that, dia berhasil melukai Pangeran Merah parah!")
            print("Tim Anda mengejar dan mengalahkannya!")
            print("\n⚠️ HARAD PINK DIHANCURKAN - DENGAN PENGORBANAN BESAR!")
            self.player.lose_life()
            return True
    
    def _magik_binding_gelap(self, wizard):
        """Level 3: Binding Gelap"""
        print(f"\n{wizard} melempar rantai magik gelap menuju Pangeran Merah!")
        print("Rantai mistis membungkus badannya...\n")
        
        print("PERTANYAAN KRITIS:")
        print("1. SERANG SEKARANG - Manfaatkan dia dalam binding state")
        print("2. NEGOSIASI - Coba buat deal dengan Pangeran yang terikat")
        print("3. TUNGGU PENUH - Binding akan semakin kuat seiring waktu\n")
        
        sub_pilihan = input("Tindakan Anda (1-3)? > ").strip()
        logging.info(f"{self.player.name} - Binding gelap tindakan: {sub_pilihan}")
        
        if sub_pilihan == "1":
            print(f"\n{wizard} mempertahankan binding, Anda langsung serang!")
            print("Pangeran Merah terikat dan tidak bisa counter!")
            print("Dia jatuh dalam pertempuran yang tidak adil ini...")
            print("\n✓ HARAD PINK DIHANCURKAN - BINDING STRATEGY BERHASIL!")
            return True
        elif sub_pilihan == "2":
            print(f"\nPangeran Merah terikat, Anda tawarkan dia mercy...")
            print("Dia bahkan mundur dan menarik pasukannya!")
            print("Mereka meninggalkan dimensi ini selamanya!")
            print("\n✓ HARAD PINK DIKALAHKAN TANPA PERTEMPURAN LEBIH LANJUT!")
            return True
        else:
            print(f"\n{wizard} mempertahankan binding yang semakin kuat...")
            print("Pangeran Merah semakin lemah...")
            print("Namun binding tersebut juga menyerap energi {wizard} sendiri!")
            print(f"Saat binding sempurna, {wizard} jatuh pingsan...")
            print("Tim Anda harus selesaikan sendiri - tapi dengan mudah karena dia lemah!")
            print("\n⚠️ HARAD PINK DIHANCURKAN - DENGAN HARGA ENERGI PENYIHIR!")
            return True
    
    def _magik_curse_keturunan(self, wizard):
        """Level 3: Curse Keturunan"""
        print(f"\n{wizard} mengucapkan mantram kuno yang mengerikan!")
        print("Kutukan merah terbang menuju garis keturunan Harad Pink...\n")
        
        print("DAMPAK KUTUKAN:")
        print("1. IMMEDIATE - Semua Harad Pink terkena langsung, mereka ambruk")
        print("2. SCOUTED - Hanya Pangeran Merah saja yang terkena kuat")
        print("3. DELAYED - Pertama terasa lemah, terus berkurang tiap hari\n")
        
        sub_pilihan = input("Bagaimana kutukan bekerja (1-3)? > ").strip()
        logging.info(f"{self.player.name} - Curse keturunan efek: {sub_pilihan}")
        
        if sub_pilihan == "1":
            print(f"\n{wizard} curse dengan power penuh - MASSIVE!")
            print("Seluruh garis keturunan Harad Pink terkena sekaligus!")
            print("Mereka collapse seperti domino!")
            print("Tidak ada satu pun yang bisa bertahan!")
            print("\n✓ HARAD PINK DIHANCURKAN SECARA TOTAL - CURSE MELAMPAUI HARAPAN!")
            return True
        elif sub_pilihan == "2":
            print(f"\nKutukan fokus ke Pangeran Merah saja...")
            print("Dia melemah drastis, pasukan Harad Pink jadi chaos tanpa komando!")
            print("Anda serang dan akhiri dengan nyaman!")
            print("\n✓ HARAD PINK DIHANCURKAN - CURSE STRATEGY BERHASIL!")
            return True
        else:
            print(f"\n{wizard} curse dengan efek jangka panjang...")
            print("Harad Pink masih bisa bertarung hari ini, tapi besok jadi lemah...")
            print("Anda bisa tarik mundur hari ini dan kembali esok untuk finishing blow!")
            print("Atau langsung serang dengan keuntungan kecil?")
            
            final_choice = input("Retreat hari ini (y) atau Serang sekarang (n)? > ").strip().lower()
            
            if final_choice == 'y':
                print("\nAnda retreat dan kembali esok hari...")
                print("Harad Pink sudah sangat lemah akibat kutukan!")
                print("Mereka mudah dikalahkan!")
                print("\n✓ HARAD PINK DIHANCURKAN - STRATEGI BERTAHAP BERHASIL!")
                return True
            else:
                print("\nAnda serang sekarang walaupun tidak optimal...")
                print("Pertempuran sengit, tapi Anda menang juga!")
                print("\n⚠️ HARAD PINK DIHANCURKAN - DENGAN KESULITAN LEBIH TINGGI!")
                self.player.lose_life()
                return True
        
        self.pause(2)
        return True
    
    def chapter_two_harad_biru(self):
        """Bab 2 - Dimensi Harad Biru (Dunia Naga)"""
        self.clear_screen()
        
        print("╔" + "═"*58 + "╗")
        print("║" + "🐉 BAB 2: DIMENSI HARAD BIRU 🐉".center(58) + "║")
        print("║" + "Dunia Didominasi Naga".center(58) + "║")
        print("╚" + "═"*58 + "╝")
        
        story = """
Setelah menumpas Harad Pink, Anda melintasi portal ke dimensi kedua.
Harad Biru adalah dunia yang sangat berbeda - dunia Naga.

Mereka bukan mayoritas dalam hal jumlah, namun mereka adalah PENGUASA MUTLAK.
Setiap langkah di dunia ini didominasi oleh kekuatan dan hierarki naga yang ketat.

Keluarga Harad Biru dipimpin oleh RAJA NAGA BIRU yang telah memerintah selama ribuan tahun.
Dia dan anak-anaknya telah menindas makhluk lain dan mencuri kekuatan dari berbagai dimensi.
        """
        self.type_text(story.strip(), speed=0.015)
        self.pause(2)
        
        # Check if player has ally from dragon race
        has_dragon_ally = any(ally.race == "Naga" for ally in self.player.allies)
        
        if not has_dragon_ally:
            logging.warning(f"{self.player.name} - Tidak ada Naga di tim untuk chapter 2")
            print("\n⚠️  Tim Anda tidak memiliki Naga!")
            print("Tanpa perspektif insider tentang struktur sosial Naga, Anda tersesat.")
            print("\nAnda tanpa sadar memicu perangkap Raja Naga Biru...")
            self.player.lose_life()
            return False
        
        naga_ally = [a.name for a in self.player.allies if a.race == "Naga"][0]
        print(f"\n✓ {naga_ally} (Naga) memberikan informasi berharga!")
        print("Dia menjelaskan kelemahan dalam struktur kerajaan Naga.")
        self.pause(1)
        
        # PILIHAN STRATEGI UTAMA (Level 1)
        print("\n" + "="*60)
        print("🐉 STRATEGI MELAWAN HARAD BIRU 🐉")
        print("="*60)
        
        strategy_text = """
Berkat pengetahuan {0}, Anda memiliki TIGA RUTE STRATEGIS berbeda:
        """.format(naga_ally)
        self.type_text(strategy_text.strip(), speed=0.015)
        self.pause(1)
        
        print("\n1. 🤝 DIPLOMASI PACIFIK - Persatuan melalui negosiasi damai")
        print("   └─ Sulit tapi ada jalan tanpa pertumpahan darah\n")
        
        print("2. 🔥 PEMBERONTAKAN INTERNAL - Picu rebellion dari kalangan naga sendiri")
        print("   └─ Risiko tinggi tapi bisa hancurkan dari dalam\n")
        
        print("3. ⚔️  PERTEMPURAN LANGSUNG - Serang langsung dengan kekuatan penuh")
        print("   └─ Berisiko tapi cepat selesai\n")
        
        pilihan_strategi = input("Pilih strategi Harad Biru (1-3): > ").strip()
        logging.info(f"{self.player.name} - Harad Biru strategi: {pilihan_strategi}")
        
        if pilihan_strategi == "1":
            return self._diplomasi_naga_pacifik(naga_ally)
        elif pilihan_strategi == "2":
            return self._pemberontakan_naga_internal(naga_ally)
        elif pilihan_strategi == "3":
            return self._pertempuran_naga_langsung(naga_ally)
        else:
            print("\n❌ Strategi tidak jelas, Raja Naga Biru malah bergerak duluan!")
            print("Anda terjebak dan tertumpas!")
            self.player.lose_life()
            return False
    
    def _diplomasi_naga_pacifik(self, naga_ally):
        """Cabang 1: Diplomasi Pacifik"""
        print("\n" + "="*60)
        print("🤝 MISI DIPLOMASI PACIFIK 🤝")
        print("="*60)
        
        story = """
Anda memulai misi diplomatik untuk mempersatukan tiga faksi Naga yang tertindas:
  • NAGA PERAK - Kelas bangsawan yang diabaikan
  • PEKERJA NAGA - Kelas bawah yang tereksploitasi
  • NAGA BIADAB - Yang menolak tunduk pada hierarki

Anda harus memilih TIGA LOKASI MEETING untuk membicarakan perlawanan bersama.
        """
        self.type_text(story.strip(), speed=0.015)
        self.pause(1)
        
        print("\nUrutakn meeting diplomasi:")
        print("1. TEMUI NAGA PERAK DULU - Mulai dari yang paling berpengaruh")
        print("   └─ Mereka bisa membantu mengajak faksi lain\n")
        
        print("2. TEMUI PEKERJA NAGA DULU - Mulai dari yang paling tertindas")
        print("   └─ Mereka punya ketergantungan pada struktur yang akan dijatuhkan\n")
        
        print("3. TEMUI NAGA BIADAB DULU - Mulai dari yang paling berani")
        print("   └─ Mereka punya keberanian untuk memulai")
        
        urutan = input("\nUrutkan jadwal meeting (1-3): > ").strip()
        logging.info(f"{self.player.name} - Diplomasi urutan: {urutan}")
        
        if urutan == "1":
            return self._diplomasi_mulai_naga_perak(naga_ally)
        elif urutan == "2":
            return self._diplomasi_mulai_pekerja_naga(naga_ally)
        elif urutan == "3":
            return self._diplomasi_mulai_naga_biadab(naga_ally)
        else:
            print("\n❌ Anda tidak tahu urutan yang tepat!")
            print("Pertemuan menjadi kacau dan Raja Naga Biru tahu!")
            self.player.lose_life()
            return False
    
    def _diplomasi_mulai_naga_perak(self, naga_ally):
        """Level 3: Diplomasi - Mulai dari Naga Perak"""
        print(f"\n{naga_ally} membawa Anda ke toreh tersembunyi Naga Perak...")
        print("Raja Naga Perak duduk di atas batu mulia yang indah.\n")
        
        print("PERCAKAPAN DIPLOMASI:")
        print("1. BUJUK MEREKA - 'Raja Biru telah menindas Anda terlalu lama!'")
        print("2. TAWARKAN KEKUATAN - 'Bergabunglah dan ambil alih kerajaan!'")
        print("3. TUNJUKKAN ALIANSI - 'Faksi lain sudah siap bergabung!'\n")
        
        pendekatan = input("Pendekatan diplomasi (1-3): > ").strip()
        logging.info(f"{self.player.name} - Perak pendekatan: {pendekatan}")
        
        if pendekatan == "1":
            print("\nRaja Perak mendengarkan dengan penuh minat...")
            print("'Ya... kami memang tertekan...' dia berkata dengan sedih.")
            print("Raja Perak setuju untuk bergabung!")
            print("\n✓ Naga Perak menjadi Aliansi Level 1\n")
            
            # Continue to next faction
            print("Sekarang Anda harus meyakinkan DUA faksi lain...")
            print("Anda berhasil tanpa masalah, karena Naga Perak membantu membujuk mereka!")
            print("Semua faksi bersatu melawan Raja Naga Biru!")
            print("\n✓ HARAD BIRU DIHANCURKAN - DIPLOMASI SUKSES!")
            return True
        elif pendekatan == "2":
            print("\nRaja Perak tergoda dengan janji kekuatan...")
            print("'Menarik... tapi bagaimana caranya?'")
            print("Dia meminta bukti nyata dari Anda.")
            print("\nAnda harus menunjukkan tindakan nyata untuk meyakinkan mereka.")
            print("Pertempuran jadi lebih kompleks, tapi akhirnya berhasil!")
            print("\n⚠️ HARAD BIRU DIHANCURKAN - DIPLOMASI DENGAN KERUMITAN TAMBAHAN!")
            self.player.lose_life()
            return True
        else:
            print("\nRaja Perak tertawa keras!")
            print("'Aliansi? Tidak ada yang berani melawan Raja Biru!'")
            print("Dia langsung melaporkan Anda ke Raja Naga Biru!")
            print("\n❌ JEBAKAN DIPLOMASI - RAJA PERAK PENGKHIANAT!")
            self.player.lose_life()
            return False
    
    def _diplomasi_mulai_pekerja_naga(self, naga_ally):
        """Level 3: Diplomasi - Mulai dari Pekerja Naga"""
        print(f"\n{naga_ally} membawa Anda ke gua-gua dalam bumi tempat Pekerja Naga bekerja keras...")
        print("Mereka terlihat sangat lelah dari kerja paksa.\n")
        
        print("STRATEGI PENYAMPAIAN PESAN:")
        print("1. KAMPANYE BURUH - 'Bergabunglah, kita akan bebas dari pajak kerjanya!'")
        print("2. RENCANA PEMBERONTAKAN - 'Mari mogok kerja bersama-sama!'")
        print("3. TAWARKAN HADIAH - 'Jika menang, kalian dapat emas dan kebebasan!'\n")
        
        strategi = input("Strategi persuasi (1-3): > ").strip()
        logging.info(f"{self.player.name} - Pekerja strategi: {strategi}")
        
        if strategi == "1":
            print("\nPekerja Naga bersemangat mendengarkan!")
            print("'Kami SANGAT ingin bebas dari pajak ini!'")
            print("Mereka langsung bergabung dengan antusias!")
            print("\n✓ Pekerja Naga menjadi Aliansi Level 1\n")
            
            print("Dengan dukungan mereka, faksi-faksi lain juga mengikuti...")
            print("Hal ini karena mereka tahu Pekerja Naga adalah mayoritas!")
            print("Satu per satu faksi bergabung!")
            print("\n✓ HARAD BIRU DIHANCURKAN - REVOLUSI BURUH BERHASIL!")
            return True
        elif strategi == "2":
            print("\nPekerja Naga sangat tertarik dengan mogok kerja!")
            print("'Iya, kami BISA mogok! Mereka butuh kita!'")
            print("Mereka setuju untuk mogok, tapi diperlukan koordinasi ekstra...")
            print("\nPertempuran jadi lebih mudah karena raja kekurangan sumber daya!")
            print("\n⚠️ HARAD BIRU DIHANCURKAN - MOGOK KERJA TERBUKTI EFEKTIF!")
            return True
        else:
            print("\nPekerja Naga tertarik dengan hadiah...")
            print("'Emas? Kebebasan? Ini terdengar bagus... TAPI...'")
            print("Mereka ragu-ragu dan pada akhirnya takut untuk bergabung!")
            print("\nTanpa mayoritas, perlawanan Anda lemah dan tertinggal!")
            print("\n❌ HARAD BIRU BERHASIL MEMPERTAHANKAN KEKUASAAN!")
            self.player.lose_life()
            return False
    
    def _diplomasi_mulai_naga_biadab(self, naga_ally):
        """Level 3: Diplomasi - Mulai dari Naga Biadab"""
        print(f"\n{naga_ally} menemani Anda ke tengah hutan belantara untuk bertemu Naga Biadab...")
        print("Mereka adalah naga liar yang tidak menginginkan tata krama kerajaan.\n")
        
        print("PENDEKATAN KOMUNIKASI:")
        print("1. SEJAJARKAN MOMENTUM - 'Mari kita ubah sistem bersama!'")
        print("2. TANTANG LANGSUNG - 'Kalian takut dengan Raja Biru?'")
        print("3. AJAK MEREKA MENJADI PEMIMPIN - 'Kalian akan memimpin revolusi!'\n")
        
        pendekatan = input("Pendekatan negosiasi (1-3): > ").strip()
        logging.info(f"{self.player.name} - Biadab pendekatan: {pendekatan}")
        
        if pendekatan == "1":
            print("\nNaga Biadab mengangguk dengan puas!")
            print("'Mengubah sistem? YA! Kami ingin itu!'")
            print("Dengan antusiasme mereka, mereka membawa Anda ke faksi lain!")
            print("\n✓ Naga Biadab menjadi Aliansi Level 1 dan PEMANDU\n")
            
            print("Mereka membawa Anda ke pertemuan dengan faksi lain...")
            print("Energi pemberontakan mereka menular!")
            print("Semua faksi bergabung dalam gerakan revolusi!")
            print("\n✓ HARAD BIRU DIHANCURKAN - REVOLUSI RAKYAT UNGGUL!")
            return True
        elif pendekatan == "2":
            print("\nNaga Biadab berbaris menghadapi tantangan Anda!")
            print("'TAKUT?! TIDAK! KITA AKAN TUNJUKKAN PADA MEREKA!'")
            print("Mereka setuju tapi dengan cara yang lebih... eksplosif!")
            print("\nPertempuran berubah menjadi lebih kasar tapi efektif!")
            print("\n⚠️ HARAD BIRU DIHANCURKAN - DENGAN KEKERASAN TINGGI!")
            self.player.lose_life()
            return True
        else:
            print("\nNaga Biadab terlihat tertarik dengan peran pemimpin...")
            print("'PEMIMPIN?! KAMI BISA?!'")
            print("Mereka bersemangat, tapi pertanyaannya... sanggupkah mereka?")
            print("\nHasil akhirnya mereka terlalu kasar dan kurang strategis!")
            print("Revolusi jadi kacau dan Raja Naga Biru memanfaatkan hal ini!")
            print("\n❌ HARAD BIRU MENANG - REVOLUSI GAGAL KARENA DISORGANISIR!")
            self.player.lose_life()
            self.player.lose_life()
            return False
    
    def _pemberontakan_naga_internal(self, naga_ally):
        """Cabang 2: Pemberontakan Internal"""
        print("\n" + "="*60)
        print("🔥 MISI PEMBERONTAKAN INTERNAL 🔥")
        print("="*60)
        
        story = """
Anda memutuskan untuk memicu pemberontakan dari dalam kerajaan Naga Biru.
Dengan bantuan {0}, Anda menemukan celah-celah dalam struktur kerajaan.

Anda harus memilih THREE TARGET SABOTASE + PEMBERONTAKAN:
        """.format(naga_ally)
        self.type_text(story.strip(), speed=0.015)
        self.pause(1)
        
        print("\n1. PUNCAK-PUNCAK KEKUATAN RAJA - Target putra/putri Raja yang paling kuat")
        print("   └─ Dengan mereka jatuh, Raja kehilangan tungkat utama\n")
        
        print("2. PUSAT KOMANDO MILITER - Target markas kerajaan")
        print("   └─ Jika komando kalah, pasukan menjadi chaos\n")
        
        print("3. ASET EKONOMI RAJA - Target gudang harta karun kerajaan")
        print("   └─ Tanpa finansial, kerajaan tidak bisa bayar tentara\n")
        
        target = input("Target pemberontakan utama (1-3): > ").strip()
        logging.info(f"{self.player.name} - Pemberontakan target: {target}")
        
        if target == "1":
            return self._pemberontakan_target_keluarga(naga_ally)
        elif target == "2":
            return self._pemberontakan_target_militer(naga_ally)
        elif target == "3":
            return self._pemberontakan_target_ekonomi(naga_ally)
        else:
            print("\n❌ Target tidak jelas, pemberontakan berkoar tetapi gagal!")
            print("Raja Naga Biru menahan dengan mudah!")
            self.player.lose_life()
            return False
    
    def _pemberontakan_target_keluarga(self, naga_ally):
        """Level 3: Pemberontakan - Target Keluarga Raja"""
        print(f"\n{naga_ally} memandu Anda untuk mengidentifikasi keluarga Raja...")
        print("Ada TIGA ANAK UTAMA RAJA yang dapat dijatuhkan secara berurutan.\n")
        
        print("STRATEGI PENGHILANGAN:")
        print("1. BUNUH SATU SATU (Diplomatic Pressure) - Setiap kebunuhan, apostate yang lain takut")
        print("2. BUNUH SEKALIGUS (Mass Assassination) - Serang mereka secara simultan")
        print("3. BALIK MEREKA (Corruption) - Bujuk anak Raja untuk melawan ayahnya\n")
        
        metode = input("Metode pemberontakan (1-3): > ").strip()
        logging.info(f"{self.player.name} - Keluarga Raja metode: {metode}")
        
        if metode == "1":
            print(f"\n{naga_ally} mulai membunuh satu anak Raja...")
            print("Setiap kematian menciptakan kepanikan di istana!")
            print("Satu per satu anak Raja jatuh tanpa tahu siapa pembunuhnya!")
            print("Akhirnya Raja Biru sendiri yang menjadi target!")
            print("\n✓ HARAD BIRU RUNTUH - STRATEGI ONE BY ONE SUKSES!")
            return True
        elif metode == "2":
            print(f"\n{naga_ally} dan tim Anda bergerak serentak ke istana kerajaan!")
            print("PERTEMPURAN BESAR terjadi di dalam istana!")
            print("Semua anak Raja bertarung tapi kalah dari kombinasi seranganmu!")
            print("Raja Biru yatim piatu dan kerajaan runtuh!")
            print("\n⚠️ HARAD BIRU DIHANCURKAN - DENGAN PERTEMPURAN SARKIS!")
            self.player.lose_life()
            return True
        else:
            print(f"\nAnda mencoba membujuk anak Raja untuk memberontak...")
            print("NAMUN... Raja Biru menyadari rencanamu!")
            print("Anak-anak Raja malah jadi pemburgul untuk menjebak Anda!")
            print("\n❌ PEMBERONTAKAN GAGAL - ANDA JEBAKAN SENDIRI!")
            self.player.lose_life()
            return False
    
    def _pemberontakan_target_militer(self, naga_ally):
        """Level 3: Pemberontakan - Target Markas Militer"""
        print(f"\n{naga_ally} membawa Anda ke belakang garis markas militer Raja...")
        print("Tentara Raja Biru sangat disiplin dan terorganisir.\n")
        
        print("STRATEGI KERUNTUHAN MILITER:")
        print("1. BAKAR GUDANG SENJATA - Tanpa senjata, tentara jadi lemah")
        print("2. BUNUH JENDERALNYA - Jenderal adalah jantung strategi militer")
        print("3. PICU MUTINY - Bujuk tentara untuk memberontak dari dalam\n")
        
        strategi = input("Strategi keruntuhan (1-3): > ").strip()
        logging.info(f"{self.player.name} - Militer strategi: {strategi}")
        
        if strategi == "1":
            print(f"\n{naga_ally} mengatur kebakaran di gudang senjata!")
            print("Ledakan besar menghancurkan semua persediaan!")
            print("Tentara Raja Biru jadi lemah dan tidak bisa berperang!")
            print("Dengan keuntungan ini, Anda mudah mengalahkan mereka!")
            print("\n✓ HARAD BIRU DIHANCURKAN - GUDANG SENJATA HABIS!")
            return True
        elif strategi == "2":
            print(f"\nAnda mengidentifikasi 5 jenderal utama Raja Biru...")
            print("Satu per satu mereka dibunuh oleh assassin profesional!")
            print("Tanpa jenderal terampil, tentara menjadi lesu dan tidak terkoordinasi!")
            print("Mereka mudah dikalahkan oleh aliansi Anda!")
            print("\n⚠️ HARAD BIRU DIHANCURKAN - JENDERAL SEMUA GUGUR!")
            return True
        else:
            print(f"\nAnda mencoba membujuk tentara untuk memberontak...")
            print("Berhasil! 1000 tentara bersikap netral dan tidak berjuang!")
            print("Tapi ini tidak cukup untuk mengalahkan Raja Biru secara instant!")
            print("Pertempuran masih harus dilakukan dengan intensitas tinggi!")
            print("\n⚠️ HARAD BIRU DIHANCURKAN - TAPI DENGAN UPAYA EKSTRA!")
            self.player.lose_life()
            return True
    
    def _pemberontakan_target_ekonomi(self, naga_ally):
        """Level 3: Pemberontakan - Target Ekonomi Raja"""
        print(f"\n{naga_ally} membawa Anda ke gudang harta karun Raja Biru...")
        print("Emas, batu mulia, dan artefak kuno tersimpan di sini.\n")
        
        print("STRATEGI EKONOMI KERUNTUHAN:")
        print("1. CURI DAN DISTRIBUSIKAN - Ambil harta untuk membeli dukungan faksi")
        print("2. HANCURKAN SEMUANYA - Burn it all untuk membuat Raja marah dan kacau")
        print("3. TRANSFER HARTA - Pindahkan ke pihak yang mau memberontak\n")
        
        metode = input("Metode sabotase ekonomi (1-3): > ").strip()
        logging.info(f"{self.player.name} - Ekonomi metode: {metode}")
        
        if metode == "1":
            print(f"\nAnda mengambil harta besar-besaran...")
            print("Kemudian mendistribusikannya ke faksi-faksi Naga yang tertindas!")
            print("Mereka sangat senang dan langsung bergabung dengan pemberontakan!")
            print("Dengan dukungan luas, Raja Biru tidak tahan!")
            print("\n✓ HARAD BIRU DIHANCURKAN - STRATEGI REDISTRIBUSI SUKSES!")
            return True
        elif metode == "2":
            print(f"\nAnda dan {naga_ally} membakar seluruh gudang!")
            print("Ledakan besar-besaran! Raja Biru sangat marah dan panik!")
            print("Dalam kepanikan, dia membuat kesalahan strategis!")
            print("Anda manfaatkan kesempatan itu untuk menyerang!")
            print("\n⚠️ HARAD BIRU DIHANCURKAN - DENGAN CHAOS YANG DIREKAYASA!")
            return True
        else:
            print(f"\nAnda secara diam-diam memindahkan harta...")
            print("Tapi ini proses yang SANGAT lambat!")
            print("Raja Biru menyadari ada yang mencuri sebelum Anda selesai!")
            print("Dia memindahkan harta yang tersisa dan keamanan meningkat!")
            print("\nPemberontakan jadi lebih sulit tanpa dukungan harta!")
            print("\n⚠️ HARAD BIRU DIHANCURKAN - TAPI PERTEMPURAN LEBIH SULIT!")
            self.player.lose_life()
            return True
    
    def _pertempuran_naga_langsung(self, naga_ally):
        """Cabang 3: Pertempuran Langsung"""
        print("\n" + "="*60)
        print("⚔️ PERSIAPAN PERTEMPURAN LANGSUNG ⚔️")
        print("="*60)
        
        story = """
Anda memilih strategi paling langsung - pertempuran frontal melawan Raja Naga Biru.
Dengan {0} memandu, Anda bersiap untuk pertempuran terbesar Anda.

Sebelum pertempuran, Anda harus memilih POSITIONING dan TIMING yang tepat.
        """.format(naga_ally)
        self.type_text(story.strip(), speed=0.015)
        self.pause(1)
        
        print("\nPILIHAN TIMING SERANGAN:")
        print("1. SERBU SIANG HARI - Ketika Raja sedang menerima tamu")
        print("   └─ Keuntungan: Raja tidak sepenuhnya siap\n")
        
        print("2. SERBU MALAM HARI - Ketika Raja sedang istirahat")
        print("   └─ Keuntungan: Pasukan terancang kurang kuat di malam hari\n")
        
        print("3. SERBU SAAT PERAYAAN - Ketika Raja mengadakan pesta besar")
        print("   └─ Keuntungan: Semua sedang santai dan tidak waspada\n")
        
        timing = input("Pilih timing serangan (1-3): > ").strip()
        logging.info(f"{self.player.name} - Pertempuran timing: {timing}")
        
        if timing == "1":
            return self._pertempuran_siang_hari(naga_ally)
        elif timing == "2":
            return self._pertempuran_malam_hari(naga_ally)
        elif timing == "3":
            return self._pertempuran_saat_pesta(naga_ally)
        else:
            print("\n❌ Timing tidak jelas, Raja Biru sudah siap menyambut Anda!")
            print("Anda kalah dalam pertempuran yang sangat tidak adil!")
            self.player.lose_life()
            self.player.lose_life()
            return False
    
    def _pertempuran_siang_hari(self, naga_ally):
        """Level 3: Pertempuran siang hari"""
        print(f"\n{naga_ally} memimpin Anda ke istana Raja di siang terik...")
        print("Raja sedang menerima delegasi dari berbagai daerah.\n")
        
        print("MOMENTUM DI SIANG HARI:")
        print("1. SERANG LANGSUNG - Terjang ke tengah pesta tamu Raja")
        print("2. ISOLASI DULU - Pisahkan Raja dari tamu sambil mereka bingung")
        print("3. TARIK KELUAR RAJA - Ciptakan provokasi agar Raja keluar dari istana\n")
        
        taktik = input("Taktik pertempuran (1-3): > ").strip()
        logging.info(f"{self.player.name} - Siang taktik: {taktik}")
        
        if taktik == "1":
            print(f"\nSerangan frontal dimulai!")
            print("Kaos terjadi di tengah pesta tamu!")
            print("Tamu-tamu berlarian ketakutan, memberi Anda akses ke Raja!")
            print("Pertempuran 1v1 dimulai - Anda vs Raja Naga Biru!")
            print("\n✓ HARAD BIRU DIHANCURKAN - RAJA NAGA BIRU TERBUNUH!")
            return True
        elif taktik == "2":
            print(f"\n{naga_ally} secara strategis mengisolasi Raja...")
            print("Sementara tamu-tamu masih bingung, Anda menyerang Raja!")
            print("Tanpa bodyguard yang cukup, Raja Biru kewalahan!")
            print("\n⚠️ HARAD BIRU DIHANCURKAN - STRATEGI ISOLASI BERHASIL!")
            return True
        else:
            print(f"\nAnda membuat provokasi besar di pesta...")
            print("Raja Biru marah besar dan keluar dari istana!")
            print("Pertempuran terjadi di luar, arena terbuka!")
            print("Raja Biru lebih lemah di arena terbuka tanpa fortifikasi!")
            print("\n⚠️ HARAD BIRU DIHANCURKAN - PERTEMPURAN DI MEDAN TERBUKA!")
            return True
    
    def _pertempuran_malam_hari(self, naga_ally):
        """Level 3: Pertempuran malam hari"""
        print(f"\n{naga_ally} membimbing Anda menembus kegelapan menuju gua Raja...")
        print("Raja Naga Biru sedang tidur di chamber pribadinya.\n")
        
        print("STRATEGI SERANGAN MALAM:")
        print("1. SILENT ASSASSINATION - Bunuh Raja saat tidur tanpa alarm")
        print("2. AWAKENING ATTACK - Bangunkan Raja dan langsung serang")
        print("3. SEAL CHAMBER - Kunci chamber sebelum pertempuran dimulai\n")
        
        strategi = input("Strategi malam (1-3): > ").strip()
        logging.info(f"{self.player.name} - Malam strategi: {strategi}")
        
        if strategi == "1":
            print(f"\n{naga_ally} membawa Anda ke chamber Raja...")
            print("Dengan gerakan silent, Anda mendekat ke Raja yang lagi tidur...")
            print("Serangan final! Raja Naga Biru tidak sempat bangun!")
            print("\n✓ HARAD BIRU DIHANCURKAN - SILENT ASSASSINATION BERHASIL!")
            return True
        elif strategi == "2":
            print(f"\nAnda membuat alarm besar di istana!")
            print("Raja Biru terbangun dengan kaget dan marah!")
            print("Pertempuran dimulai dalam keadaan kacau!")
            print("Meskipun Raja kacau, dia masih kuat dan pertempuran sengit!")
            print("\n⚠️ HARAD BIRU DIHANCURKAN - PERTEMPURAN SENGIT DI MALAM HARI!")
            self.player.lose_life()
            return True
        else:
            print(f"\nAnda seal chamber Raja dan menghadang semua exit!")
            print("Raja terperangkap dan harus melawan kepada Anda!")
            print("Pertempuran 1v1 yang spektakuler dalam chamber tertutup!")
            print("Akhirnya Raja jatuh, kingdom jatuh bersamanya!")
            print("\n⚠️ HARAD BIRU DIHANCURKAN - CHAMBER MENJADI GLADIATOR ARENA!")
            return True
    
    def _pertempuran_saat_pesta(self, naga_ally):
        """Level 3: Pertempuran saat pesta"""
        print(f"\n{naga_ally} mengidentifikasi pesta besar Raja Naga Biru...")
        print("Festival perayaan kemenangan atas berbagai dimensi sedang berlangsung.\n")
        
        print("EKSEKUSI SAAT PESTA:")
        print("1. BUAT KERUMUNAN CHAOS - Serang dan ciptakan kepanikan panik publik")
        print("2. TARGET RAJA LANGSUNG - Abaikan kerumunan, serang Raja saja")
        print("3. BUNUH KOMANDAN TERLEBIH DULU - Matikan kepala keamanan Raja\n")
        
        metode = input("Metode serangan pesta (1-3): > ").strip()
        logging.info(f"{self.player.name} - Pesta metode: {metode}")
        
        if metode == "1":
            print(f"\nKerumunan pesta menciptakan chaos yang luar biasa!")
            print("Orang-orang berlarian dalam kepanikan!")
            print("Dalam chaos ini, Anda mendekati Raja yang dilindungi security yang kurang!")
            print("Anda berhasil terbunuh... Raja! Harad Biru runtuh!")
            print("\n✓ HARAD BIRU DIHANCURKAN - CHAOS STRATEGY ULTIMATE SUCCESS!")
            return True
        elif metode == "2":
            print(f"\nAnda membuat jalan langsung menuju Raja melalui kerumunan!")
            print("{0} membuka jalan dengan kekuatan bruto!".format(naga_ally))
            print("Pertempuran dimulai langsung di tengah pesta!")
            print("Guests berlarian sambil Raja dan Anda bertarung!")
            print("\n⚠️ HARAD BIRU DIHANCURKAN - PERTEMPURAN DI TENGAH PESTA!")
            return True
        else:
            print(f"\nAnda target komandan keamanan Raja terlebih dulu...")
            print("Komandan jatuh dalam pertempuran brutal!")
            print("Tapi dengan jatuhnya komandan, security jadi lebih kacau dan berontak!")
            print("Alih-alih membantu Raja, mereka justru mulai menjaga diri sendiri!")
            print("Raja Biru terpaksa bertempur sendiri dan jatuh!")
            print("\n⚠️ HARAD BIRU DIHANCURKAN - EFEK DOMINO KEAMANAN!")
            return True
        
        self.pause(2)
        return True
    
    def final_chapter(self):
        """Bab Akhir - Konsekuensi dan Ending"""
        self.clear_screen()
        
        if self.player.lives <= 0:
            self.bad_ending()
        else:
            self.good_ending()
    
    def good_ending(self):
        print("╔" + "═"*58 + "╗")
        print("║" + "✨ ENDING: KEBANGKITAN KAMPUNG HALAMAN ✨".center(58) + "║")
        print("╚" + "═"*58 + "╝")
        
        story = """
Kedua keluarga Harad akhirnya dihancurkan. Anda pulang ke kampung halaman dengan para sekutu.

Penduduk berkumpul untuk menyambut Anda. Keluarga Anda merangkul Anda dengan erat,
mata mereka berbinar dengan kebahagiaan dan apresiasi.

Kehidupan malas yang Anda impikan kini bisa Anda nikmati lagi, namun kali ini
DENGAN MAKNA. Anda telah memahami bahwa hidup tidak hanya tentang diri sendiri,
tapi juga tentang melindungi yang Anda cintai.

Para sekutu Anda memutuskan untuk tinggal bersama di kampung halaman, membantu
membangun kembali apa yang telah hancur. Mereka adalah keluarga baru Anda.
        """
        self.type_text(story.strip(), speed=0.02)
        self.pause(2)
        
        logging.info(f"{self.player.name} - GOOD ENDING dengan sisa {self.player.lives} nyawa")
        print(f"\n✓ SELAMAT! Anda telah menyelesaikan petualangan dengan sisa {self.player.lives} nyawa!")
        
        # Custom ending message dengan nama pemain
        self.pause(1)
        print()
        ending_message = f"""
╔{'═'*58}╗
║{' '*58}║
║ {f'{self.player.name} akhirnya dengan tenang hidup malas bersama'.ljust(56)} ║
║ {f'sekutunya, menjalani hari-hari penuh makna setelah perang'.ljust(56)} ║
║ {f'besar melawan Harad. Kehidupan yang mereka impikan kini'.ljust(56)} ║
║ {f'menjadi kenyataan berkat kebersamaan dan kepercayaan.'.ljust(56)} ║
║{' '*58}║
║ {f'Kedamaian telah datang ke {self.player.name} dan keluarganya.'.ljust(56)} ║
║ {f'Cerita heroik Anda akan dikenang selamanya.'.ljust(56)} ║
║{' '*58}║
╚{'═'*58}╝
        """
        self.type_text(ending_message, speed=0.01)
        self.pause(2)
        
        print("\nKREDIT:")
        print("─" * 60)
        for i, ally in enumerate(self.player.allies, 1):
            print(f"  • {ally.name} ({ally.race}) - {ally.specialty}")
        print("─" * 60)
    
    def bad_ending(self):
        print("╔" + "═"*58 + "╗")
        print("║" + "ENDING: KEGELAPAN YANG ABADI".center(58) + "║")
        print("╚" + "═"*58 + "╝")
        
        story = """
Anda kehabisan nyawa dalam misi melawan Harad.

Portal menutup rapat, memisahkan Anda dari kampung halaman selamanya.
Keluarga Anda tidak pernah tahu apa yang terjadi padanya.
Mereka menunggu kedatangan Anda yang tidak akan pernah tiba.

Malam demi malam, ibukota kembali diserang oleh sisa-sisa Harad yang belum terbunuh.
Tanpa kehadiran Anda, tidak ada lagi harapan bagi kampung halaman.

Kehidupan malas yang Anda impikan berubah menjadi mimpi buruk yang tak terlupakan.
        """
        self.type_text(story.strip(), speed=0.02)
        self.pause(2)
        
        logging.info(f"{self.player.name} - BAD ENDING - Kehabisan nyawa")
        print("\n❌ GAME OVER - Anda telah kehilangan semua nyawa")
        print("\nTips untuk lain kali:")
        print("  • Pilih komposisi tim yang BERAGAM")
        print("  • Perhatikan syarat untuk membentuk aliansi")
        print("  • Fokus pada KERJASAMA antar sekutu")
    
    def run(self):
        try:
            while True:
                # Show main menu
                menu_choice = self.show_main_menu()
                
                if menu_choice == "exit":
                    print("\nTerima kasih telah bermain!")
                    logging.info("Game keluar dari main menu")
                    break
                elif menu_choice and menu_choice.startswith("continue:"):
                    # Load saved game
                    player_name = menu_choice.replace("continue:", "")
                    if self.load_game(player_name):
                        print(f"\n✓ Game dimuat: {player_name}")
                        print(f"Chapter terakhir: {self.current_chapter}")
                        self.pause(1)
                        # Continue dari chapter yang sesuai
                        if self.current_chapter == 0:
                            self.recruitment_phase()
                            if not self.chapter_one_harad_pink():
                                self.final_chapter()
                                if not self.ask_play_again():
                                    break
                                continue
                            self.current_chapter = 1
                            self.save_game()
                        
                        if self.current_chapter == 1:
                            self.pause(1)
                            print("\nMelanjutkan ke portal menuju Harad Biru...")
                            self.pause(1)
                            if not self.chapter_two_harad_biru():
                                self.final_chapter()
                                if not self.ask_play_again():
                                    break
                                continue
                            self.current_chapter = 2
                            self.save_game()
                        
                        self.pause(2)
                        self.final_chapter()
                        if not self.ask_play_again():
                            break
                    else:
                        print("\n✗ Gagal memuat game")
                        self.pause(1)
                    continue
                
                # New game
                self.game_intro()
                self.current_chapter = 0
                self.recruitment_phase()
                self.current_chapter = 1
                self.save_game()
                
                self.print_status()
                print("\nBersiaplah memasuki dimensi lain...")
                self.pause(1)
                
                # Chapter 1
                if not self.chapter_one_harad_pink():
                    self.final_chapter()
                    self.current_chapter = 0
                    if not self.ask_play_again():
                        break
                    continue
                
                self.pause(1)
                print("\nMelanjutkan ke portal menuju Harad Biru...")
                self.pause(1)
                
                # Chapter 2
                self.current_chapter = 2
                self.save_game()
                if not self.chapter_two_harad_biru():
                    self.final_chapter()
                    self.current_chapter = 0
                    if not self.ask_play_again():
                        break
                    continue
                
                self.pause(2)
                
                # Final
                self.final_chapter()
                self.current_chapter = 0
                
                # Delete save file setelah menyelesaikan game
                try:
                    save_file = os.path.join(SAVE_DIR, f"{self.player.name}_save.json")
                    if os.path.exists(save_file):
                        os.remove(save_file)
                except:
                    pass
                
                if not self.ask_play_again():
                    break
                
        except KeyboardInterrupt:
            print("\n\nGame dihentikan. Terima kasih telah bermain!")
            logging.info("Game dihentikan oleh user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logging.error(f"Error: {e}")
    
    def ask_play_again(self) -> bool:
        """Tanyakan apakah pemain ingin main lagi"""
        print("\n" + "="*60)
        
        while True:
            pilihan = input("Ingin main lagi? (y/n): > ").strip().lower()
            
            if pilihan in ['y', 'yes', 'ya']:
                logging.info("Player memilih untuk main lagi")
                self.clear_screen()
                return True
            elif pilihan in ['n', 'no', 'tidak']:
                print("\nTerima kasih telah bermain! Sampai jumpa lagi!")
                logging.info("Game berakhir - Player tidak ingin main lagi")
                return False
            else:
                print("Masukan tidak valid. Ketik 'y' atau 'n': ")

if __name__ == "__main__":
    game = MysteryGame()
    game.run()