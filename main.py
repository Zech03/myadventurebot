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
        
        print(f"\nDengan dukungan aliansi lokal, tim Anda ({len(self.player.allies)} anggota) bersiap berhada-hadapan")
        print("dengan pasukan Harad Pink yang dipimpin oleh SANG PANGERAN MERAH.\n")
        self.pause(1)
        
        # Multiple choice for final decision
        print("\nAda dua strategi yang dapat Anda lakukan:\n")
        print("1. SERANGAN LANGSUNG - Serang markas Harad Pink dengan kekuatan penuh")
        print("   ├─ Risiko: Tinggi, banyak korban di kalangan sekutu")
        print("   └─ Reward: Cepat selesai, Harad Pink hancur total\n")
        
        print("2. SABOTASE - Gunakan spion untuk melemahkan mereka terlebih dahulu")
        print("   ├─ Risiko: Rendah, tidak ada korban")
        print("   └─ Reward: Lebih aman, mereka terpecah belah")
        
        pilihan = input("\nPilih strategi (1 atau 2): > ").strip()
        logging.info(f"{self.player.name} - Harad Pink dipilih strategi: {pilihan}")
        
        # Variasi respons berdasarkan pilihan
        response_direct = [
            "Anda menggerakkan serangan frontal yang menghancurkan semua dalam jalurnya...",
            "Semua pasukan bergerak menyerang sekaligus dengan kekuatan penuh...",
            "Ledakan dahsyat dimulai dari semua arah secara bersamaan...",
        ]
        
        response_sabotage = [
            "Agen-agen Anda bekerja dalam bayang-bayang dengan presisi sempurna...",
            "Rencana sabotase Anda berjalan lancar melampaui ekspektasi...",
            "Dari dalam, Harad Pink mulai terpecah belah dengan sendirinya...",
        ]
        
        if pilihan == "1":
            self.type_text(random.choice(response_direct), speed=0.02)
            self.pause(1.5)
            print("\nLedakan dahsyat meruntuhkan markas Harad Pink!")
            print("Sang Pangeran Merah gugur bersama pengikut setianya.")
            print("\n✓ HARAD PINK TELAH DIHANCURKAN!")
        else:
            self.type_text(random.choice(response_sabotage), speed=0.02)
            self.pause(1.5)
            print("\nHarad Pink terpecah dari dalam, saling membunuh, hancur dengan sendirinya.")
            print("\n✓ HARAD PINK TELAH DIHANCURKAN!")
        
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
        
        # Key to winning: cooperation
        print("\n" + "="*60)
        print("🐉 DIPLOMASI RAHASIA NAGA 🐉")
        print("="*60)
        
        diplomacy_text = """
Berkat pengetahuan Naga Anda, Anda membunuh diri sendiri ke istana tersembunyi
dan melakukan negosiasi kompleks dengan berbagai faksi Naga yang tertindas:

  • NAGA PERAK (korban oppression Raja Naga Biru)
  • PEKERJA NAGA (kelas rendah yang ingin kebebasan)
  • NAGA BIADAB (yang tidak menunduk pada hierarki kerajaan)

Jika Anda bisa menyatukan mereka semua, peluang untuk mengalahkan Raja akan terbuka.
        """
        self.type_text(diplomacy_text.strip(), speed=0.015)
        self.pause(1)
        
        # Check team composition for cooperation
        team_diversity = len(set(ally.race for ally in self.player.allies))
        communication_score = 0
        
        # Diplomacy check
        if any(ally.race in ["Penyihir", "Elf"] for ally in self.player.allies):
            communication_score += 1  # Penyihir/Elf dianggap diplomat baik
        
        if any(ally.race == "Beastman" for ally in self.player.allies):
            communication_score += 1  # Beastman punya empati
        
        if team_diversity >= 3:
            communication_score += 1  # Tim diverse lebih mudah berempati
        
        logging.info(f"{self.player.name} - Diplomasi score: {communication_score}, Diversity: {team_diversity}")
        
        print("\nAnda memulai misi diplomasi...")
        self.pause(1)
        
        if communication_score >= 2:
            logging.info(f"{self.player.name} - Diplomasi Harad Biru BERHASIL")
            success_responses = [
                "Dari percakapan demi percakapan, Anda berhasil meyakinkan mereka...",
                "Dengan kata-kata yang tepat, satu per satu faksi Naga bergabung...",
                "Keberagaman tim Anda membuat Naga lain percaya pada visi Anda...",
            ]
            self.type_text(random.choice(success_responses), speed=0.02)
            self.pause(1)
            print("\n✓ KESUKSESAN DIPLOMASI!")
            print("Semua faksi Naga setuju untuk bergabung melawan Raja Naga Biru!")
            print("Dalam pertempuran besar, mereka mengkhianati Raja dari dalam.")
            print("Kerajaan Naga Biru runtuh dalam chaos internal.")
            print("\n✓ HARAD BIRU TELAH DIHANCURKAN!")
            return True
        else:
            logging.info(f"{self.player.name} - Diplomasi Harad Biru GAGAL")
            failure_responses = [
                "Namun, tim Anda terlalu homogen untuk membangun kepercayaan...",
                "Faksi Naga ragu-ragu dengan proposal yang Anda buat...",
                "Kurangnya pemahaman mendalam membuat negosiasi hancur berantakan...",
            ]
            self.type_text(random.choice(failure_responses), speed=0.02)
            self.pause(1)
            print("\n✗ DIPLOMASI GAGAL")
            print("Anda tidak bisa meyakinkan faksi-faksi Naga untuk bergabung.")
            print("Raja Naga Biru menemukan rencana Anda.")
            print("Pasukan Naga yang luar biasa kuat menghancurkan tim Anda.")
            print("\n❌ ANDA KALAH - Ditumpas oleh Naga yang lebih kuat")
            self.player.lose_life()
            return False
    
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