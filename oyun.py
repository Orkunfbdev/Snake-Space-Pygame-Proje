import math
import random
import time

import pygame

from assetler import Assetler, GUI
from ayarlar import *

BOLGELER = {
    1: ("Başlangıç Sistemi", "Temel eğitim bölgesi. Kontroller ve tempo burada öğrenilir."),
    2: ("Dış Halkalar", "İklim değişir, engeller artar ve rota biraz daralır."),
    3: ("Çorak Sektör", "Kayalık alanlar daha çoktur, manevra yapmak zorlaşır."),
    4: ("Yabancı Bölge", "Zehirli ve renkli gezegenler, daha hızlı seviye akışı."),
    5: ("Kaos Çekirdeği", "Son bölge. Hedef sayısı ve hız en yüksek seviyededir."),
}

LEVEL_ADLARI = {
    1: "Dünya", 2: "Yeni Dünya", 3: "Tropik", 4: "Su Gaz Devi",
    5: "Çöl", 6: "Kum Fırtınası", 7: "Buz", 8: "Buzul Göktaşı",
    9: "Çorak Kayalık", 10: "Paslı Kaya", 11: "Dikenli", 12: "Mor Okyanus",
    13: "Zümrüt", 14: "Turuncu Gaz Devi", 15: "Aurora", 16: "Pembe Krater",
    17: "Ametist", 18: "Yakut Kristali", 19: "Radyoaktif Çatlak", 20: "Magma Çatlak",
}


class Oyun:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 256)
        pygame.init()
        pygame.display.set_caption("Snake Space")
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION])
        self.ekran = pygame.display.set_mode((W, H), pygame.DOUBLEBUF)
        self.saat = pygame.time.Clock()
        self.a = Assetler()
        self.fontlari_kur()
        self.menu_muzik = GUI / "Audio" / "game_menu.mp3"
        self.game_over_muzik = GUI / "Audio" / "game_over.wav"
        self.level_gecis_muzik = GUI / "Audio" / "level_gecis.wav"
        self.game_over_sesi = None
        self.level_gecis_sesi = None
        self.gecis_suresi = 2200
        self.ses_hazir = False
        self.menu_caliyor = False
        self.menu_durus_zamani = 0
        self.menu_fade_suresi = 2000
        self.durum = "menu"
        self.oyun_modu = "normal"
        self.region = 1
        self.level = 1
        self.acik_level = 1
        self.puan = 0
        self.level_puan_baslangic = 0
        self.rekor = 0
        self.sonuc_suresi = 0
        self.ses_acik = True
        self.efekt_acik = True
        self.muzik_ses = 0.70
        self.kazandi = False
        self.ayarlar_donus = "menu"
        self.pause_zamani = 0
        self.gecis_basla = 0
        self.gecis_level = 1
        self.gecis_puan = None
        self.son_sure = -1
        self.sesleri_hazirla()
        self.level_kur()
        self.menu_muzigi_baslat()

    def font_yukle(self, dosya, boyut, sistem="arial", bold=False):
        if dosya.exists():
            return pygame.font.Font(str(dosya), boyut)
        return pygame.font.SysFont(sistem, boyut, bold=bold)

    def fontlari_kur(self):
        font_klasor = GUI / "Fonts"
        rubik = font_klasor / "Rubik-SemiBold.ttf"
        digital = font_klasor / "Digitalt.ttf"
        self.font = self.font_yukle(rubik, 22)
        self.kucuk = self.font_yukle(rubik, 16)
        self.mini = self.font_yukle(rubik, 12)
        self.level_ad_font = self.font_yukle(rubik, 14)
        self.bolge_font = self.font_yukle(rubik, 22)
        self.yardim_font = self.font_yukle(rubik, 12)
        self.buyuk = self.font_yukle(digital, 42, "arialblack", True)
        self.baslik_font = self.font_yukle(digital, 24, "arialblack", True)
        self.menu_buton_font = self.font_yukle(digital, 46, "arialblack")
        self.mode_buton_font = self.font_yukle(digital, 32, "arialblack", True)
        self.mode_rozet_font = self.font_yukle(rubik, 15)
        self.buton_font = self.font_yukle(digital, 20, "arialblack", True)
        self.buton_kucuk = self.font_yukle(digital, 13, "arialblack", True)
        self.level_baslik_font = self.font_yukle(digital, 23, "arialblack", True)
        self.dijital_mini = self.font_yukle(digital, 13, "arialblack", True)
        self.ayarlar_baslik_font = self.font_yukle(digital, 34, "arialblack")
        self.ayarlar_label_font = self.font_yukle(rubik, 26)
        self.ayarlar_buton_font = self.font_yukle(digital, 28, "arialblack", True)
        self.mode_popup_title_font = self.font_yukle(digital, 38, "arialblack")
        self.mode_popup_buton_font = self.font_yukle(digital, 26, "arialblack", True)
        self.mode_popup_label_font = self.font_yukle(rubik, 18)
        self.hud_label_font = self.font_yukle(rubik, 13)
        self.hud_value_font = self.font_yukle(rubik, 20)
        self.sonuc_baslik_font = self.font_yukle(digital, 36, "arialblack")
        self.sonuc_skor_font = self.font_yukle(rubik, 36)
        self.sonuc_buton_font = self.font_yukle(digital, 22, "arialblack")
        self.sonuc_stat_val_font = self.font_yukle(rubik, 24)

    def sesleri_hazirla(self):
        try:
            pygame.mixer.init()
            self.game_over_sesi = pygame.mixer.Sound(str(self.game_over_muzik))
            self.level_gecis_sesi = pygame.mixer.Sound(str(self.level_gecis_muzik))
            self.gecis_suresi = max(1500, min(2300, int(self.level_gecis_sesi.get_length() * 1000)))
            self.ses_hazir = True
        except (pygame.error, OSError):
            self.ses_hazir = False

    def menu_muzigi_baslat(self):
        if not self.ses_acik or not self.ses_hazir:
            return
        try:
            if self.game_over_sesi:
                self.game_over_sesi.stop()
            if self.menu_caliyor:
                self.menu_durus_zamani = 0
                pygame.mixer.music.set_volume(self.muzik_ses)
                return
            pygame.mixer.music.load(str(self.menu_muzik))
            pygame.mixer.music.set_volume(self.muzik_ses)
            pygame.mixer.music.play(-1)
            self.menu_caliyor = True
            self.menu_durus_zamani = 0
        except (pygame.error, OSError):
            self.ses_hazir = False

    def menu_muzigi_durdur(self):
        if self.ses_hazir:
            pygame.mixer.music.stop()
        self.menu_caliyor = False
        self.menu_durus_zamani = 0

    def menu_muzigi_oyunda_kapat(self):
        if self.menu_caliyor:
            self.menu_durus_zamani = pygame.time.get_ticks() + 10000

    def sesleri_guncelle(self):
        if self.menu_durus_zamani and pygame.time.get_ticks() >= self.menu_durus_zamani:
            if self.ses_hazir:
                pygame.mixer.music.fadeout(self.menu_fade_suresi)
            self.menu_caliyor = False
            self.menu_durus_zamani = 0

    def kaybetme_sesi_cal(self):
        self.menu_muzigi_durdur()
        if self.efekt_acik and self.ses_hazir and self.game_over_sesi:
            self.game_over_sesi.play()

    def level_gecis_sesi_cal(self):
        if self.efekt_acik and self.ses_hazir and self.level_gecis_sesi:
            self.level_gecis_sesi.stop()
            self.level_gecis_sesi.set_volume(1)
            if self.menu_caliyor:
                pygame.mixer.music.set_volume(self.muzik_ses * 0.35)
            self.level_gecis_sesi.play()

    def pause_baslat(self):
        if self.durum == "oyun":
            self.pause_zamani = time.time()
            self.durum = "pause"

    def pause_bitir(self):
        if self.pause_zamani:
            gecen = time.time() - self.pause_zamani
            self.baslama += gecen
            if self.elma_yeri:
                self.elma_zamani += gecen
        self.pause_zamani = 0
        self.durum = "oyun"

    def muzik_sesi_degistir(self, miktar):
        self.muzik_ses = max(0, min(1, round(self.muzik_ses + miktar, 2)))
        if self.ses_hazir:
            pygame.mixer.music.set_volume(self.muzik_ses)

    def level_kur(self):
        self.yilan = [(7, 8), (6, 8), (5, 8)]
        self.yon = self.sonraki = (1, 0)
        self.toplanan = 0
        self.kapi_acik = False
        self.kapi_yeri = None
        self.son_hareket = pygame.time.get_ticks()
        self.baslama = time.time()
        self.sonuc_suresi = 0
        self.engeller = self.engel_uret()
        self.elma_yeri = None
        self.elma_uret()
        self.tahta = self.tahta_hazirla()

    def tahta_hazirla(self):
        acik = self.a.level(self.level, "checkers_light.png", (KARE, KARE))
        koyu = self.a.level(self.level, "checkers_dark.png", (KARE, KARE))
        s = pygame.Surface(ALAN.size, pygame.SRCALPHA)
        for y in range(SATIR):
            for x in range(SUTUN):
                s.blit(acik if (x + y) % 2 == 0 else koyu, (x * KARE, y * KARE))
        return s

    def hedef(self):
        return 3 if self.level == 1 else 5 + (self.level - 2) * 3

    def hiz(self):
        taban = 142 - (self.level - 1) * 2
        if self.oyun_modu == "zor":
            taban -= 10
        return max(90, taban)

    def engel_uret(self):
        rnd = random.Random(self.level * 77)
        engel = set()
        guvenli_baslangic = {(x, y) for x in range(3, 12) for y in range(6, 11)}
        yasak = set(self.yilan) | guvenli_baslangic
        adet = 4 + self.level * 2
        if self.oyun_modu == "zor":
            adet += 3 + self.level // 2
        while len(engel) < adet:
            yer = (rnd.randrange(2, SUTUN - 2), rnd.randrange(2, SATIR - 2))
            if yer not in yasak:
                engel.add(yer)
        if self.level >= 6:
            bos = rnd.randrange(7, SUTUN - 7)
            engel |= {(x, 5) for x in range(4, SUTUN - 4) if abs(x - bos) > 1 and (x, 5) not in yasak}
        return engel

    def kapi_uret(self):
        dolu = set(self.yilan) | self.engeller
        if self.elma_yeri:
            dolu.add(self.elma_yeri)
        bos = [(x, y) for x in range(1, SUTUN - 1) for y in range(1, SATIR - 1)
               if (x, y) not in dolu]
        return random.choice(bos) if bos else (SUTUN - 3, SATIR - 3)

    def elma_uret(self):
        if self.toplanan >= self.hedef():
            self.elma_yeri = None
            self.kapi_yeri = self.kapi_uret()
            self.kapi_acik = True
            return
        dolu = set(self.yilan) | self.engeller
        if self.kapi_yeri:
            dolu.add(self.kapi_yeri)
        bos = [(x, y) for x in range(SUTUN) for y in range(SATIR) if (x, y) not in dolu]
        self.elma_yeri = random.choice(bos)
        self.elma_zamani = time.time()

    def bolge_no(self, level=None):
        return ((level or self.level) - 1) // 4 + 1

    def gezegen_yolu(self, level, kilitli=False):
        bolge = self.bolge_no(level)
        durum = "locked" if kilitli else "color"
        return ("Level Menus", f"Region {bolge}", f"level_{level:02d}_planet_{durum}.png")

    def gecis_baslat(self, level, puan=None):
        self.gecis_level = level
        self.gecis_puan = puan
        self.region = self.bolge_no(level)
        self.level_gecis_sesi_cal()
        self.gecis_basla = pygame.time.get_ticks()
        self.durum = "gecis"

    def level_baslat(self, level, puan=None):
        if self.game_over_sesi:
            self.game_over_sesi.stop()
        if self.level_gecis_sesi:
            self.level_gecis_sesi.stop()
        if self.ses_hazir and self.menu_caliyor:
            pygame.mixer.music.set_volume(self.muzik_ses)
        self.level = level
        if puan is not None:
            self.puan = puan
        elif level == 1:
            self.puan = 0
        self.level_puan_baslangic = self.puan
        self.level_kur()
        self.menu_muzigi_oyunda_kapat()
        self.durum = "oyun"

    def mod_baslat(self, mod):
        self.oyun_modu = mod
        self.region = 1
        self.level = 1
        self.acik_level = 1
        self.puan = 0
        self.level_puan_baslangic = 0
        self.kazandi = False
        self.level_kur()
        self.durum = "level_menu"
        self.menu_muzigi_baslat()

    def zor_mod_sifirla(self):
        self.region = 1
        self.level = 1
        self.acik_level = 1
        self.puan = 0
        self.level_puan_baslangic = 0
        self.kazandi = False
        self.level_kur()

    def olaylar(self):
        degisti = False
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if e.type == pygame.KEYDOWN:
                degisti = self.tus(e.key) or degisti
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                degisti = self.tikla(e.pos) or degisti
            if e.type == pygame.MOUSEMOTION:
                if self.durum in ("menu", "mod_menu", "level_menu", "ayarlar", "pause", "cikis", "kazandin", "kaybettin"):
                    degisti = True
        return degisti

    def tus(self, tus):
        if self.durum == "menu":
            if tus in (pygame.K_RETURN, pygame.K_SPACE):
                self.durum = "mod_menu"
                self.menu_muzigi_baslat()
                return True
        if self.durum == "mod_menu":
            if tus == pygame.K_1:
                self.mod_baslat("zor")
                return True
            if tus in (pygame.K_2, pygame.K_RETURN, pygame.K_SPACE):
                self.mod_baslat("normal")
                return True
            if tus == pygame.K_ESCAPE:
                self.durum = "menu"
                self.menu_muzigi_baslat()
                return True
        if self.durum == "level_menu":
            if tus in (pygame.K_RIGHT, pygame.K_d):
                if self.region < 5:
                    self.region += 1
                    return True
                return False
            if tus in (pygame.K_LEFT, pygame.K_a):
                if self.region > 1:
                    self.region -= 1
                    return True
                return False
            if tus == pygame.K_ESCAPE:
                self.durum = "menu"
                self.menu_muzigi_baslat()
                return True
        if self.durum == "oyun":
            yonler = {pygame.K_w: (0, -1), pygame.K_UP: (0, -1), pygame.K_s: (0, 1),
                      pygame.K_DOWN: (0, 1), pygame.K_a: (-1, 0), pygame.K_LEFT: (-1, 0),
                      pygame.K_d: (1, 0), pygame.K_RIGHT: (1, 0)}
            if tus in yonler and yonler[tus] != (-self.yon[0], -self.yon[1]):
                self.sonraki = yonler[tus]
                return True
            if tus == pygame.K_ESCAPE:
                self.pause_baslat()
                return True
            if tus == pygame.K_r:
                self.level_baslat(self.level, self.level_puan_baslangic)
                return True
        if self.durum == "pause":
            if tus in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                self.pause_bitir()
                return True
            if tus == pygame.K_a:
                self.ayarlar_donus = "pause"
                self.durum = "ayarlar"
                return True
            if tus == pygame.K_l:
                self.durum = "level_menu"
                self.menu_muzigi_baslat()
                return True
        if self.durum in ("kazandin", "kaybettin") and tus in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_r):
            self.sonuc_devam()
            return True
        if tus == pygame.K_ESCAPE and self.durum in ("ayarlar", "cikis"):
            self.durum = self.ayarlar_donus if self.durum == "ayarlar" else "menu"
            if self.durum == "menu":
                self.menu_muzigi_baslat()
            return True
        return False

    def tikla(self, pos):
        if self.durum == "menu":
            if self.play_rect.collidepoint(pos):
                self.durum = "mod_menu"
                self.menu_muzigi_baslat()
            elif self.settings_rect.collidepoint(pos):
                self.ayarlar_donus = "menu"
                self.durum = "ayarlar"
            elif self.exit_rect.collidepoint(pos):
                self.durum = "cikis"
            return True
        if self.durum == "mod_menu":
            if self.hard_mode_rect.collidepoint(pos):
                self.mod_baslat("zor")
                return True
            if self.normal_mode_rect.collidepoint(pos):
                self.mod_baslat("normal")
                return True
            if self.mode_close.collidepoint(pos):
                self.durum = "menu"
                self.menu_muzigi_baslat()
                return True
        if self.durum == "level_menu":
            if self.region > 1 and self.prev_region_rect.collidepoint(pos):
                self.region -= 1
                return True
            if self.region < 5 and self.next_region_rect.collidepoint(pos):
                self.region += 1
                return True
            for level, rect in self.level_rects:
                if rect.collidepoint(pos) and level <= self.acik_level:
                    puan = self.level_puan_baslangic if level == self.level else 0
                    self.gecis_baslat(level, puan)
                    return True
        if self.durum == "ayarlar":
            if self.music_toggle.collidepoint(pos):
                self.ses_acik = not self.ses_acik
                if self.ses_acik:
                    self.menu_muzigi_baslat()
                else:
                    self.menu_muzigi_durdur()
                return True
            if self.effects_toggle.collidepoint(pos):
                self.efekt_acik = not self.efekt_acik
                if not self.efekt_acik:
                    if self.game_over_sesi:
                        self.game_over_sesi.stop()
                    if self.level_gecis_sesi:
                        self.level_gecis_sesi.stop()
                return True
            if self.settings_close.collidepoint(pos):
                self.durum = self.ayarlar_donus
                if self.durum == "menu":
                    self.menu_muzigi_baslat()
                return True
        if self.durum == "pause":
            if self.pause_close_rect.collidepoint(pos):
                self.pause_bitir()
                return True
            if self.pause_resume_rect.collidepoint(pos):
                self.pause_bitir()
                return True
            if self.pause_settings_rect.collidepoint(pos):
                self.ayarlar_donus = "pause"
                self.durum = "ayarlar"
                return True
            if self.pause_lobby_rect.collidepoint(pos):
                self.durum = "level_menu"
                self.menu_muzigi_baslat()
                return True
        if self.durum == "cikis":
            if self.quit_yes.collidepoint(pos):
                pygame.quit()
                raise SystemExit
            if self.quit_no.collidepoint(pos):
                self.durum = "menu"
                self.menu_muzigi_baslat()
                return True
        if self.durum in ("kazandin", "kaybettin"):
            if self.result_main.inflate(26, 22).collidepoint(pos):
                if self.oyun_modu == "zor":
                    self.zor_mod_sifirla()
                self.durum = "level_menu"
                self.menu_muzigi_baslat()
                return True
            if self.result_action.inflate(26, 22).collidepoint(pos):
                self.sonuc_devam()
                return True
        return False

    def sonuc_devam(self):
        if self.durum == "kaybettin":
            if self.oyun_modu == "zor":
                self.zor_mod_sifirla()
                self.gecis_baslat(1, 0)
            else:
                self.level_baslat(self.level, self.level_puan_baslangic)
        elif self.level < SON_LEVEL:
            self.gecis_baslat(self.level + 1, self.puan)
        else:
            self.durum = "level_menu"
            self.menu_muzigi_baslat()

    def guncelle(self):
        self.sesleri_guncelle()
        if self.durum == "gecis":
            if pygame.time.get_ticks() - self.gecis_basla > self.gecis_suresi:
                self.level_baslat(self.gecis_level, self.gecis_puan)
                return True
            return True
        if self.durum != "oyun" or pygame.time.get_ticks() - self.son_hareket < self.hiz():
            return False
        self.son_hareket = pygame.time.get_ticks()
        self.yon = self.sonraki
        x, y = self.yilan[0]
        bas = (x + self.yon[0], y + self.yon[1])
        if self.carpti(bas):
            self.rekor = max(self.rekor, self.puan)
            self.kazandi = False
            self.sonuc_suresi = time.time() - self.baslama
            self.kaybetme_sesi_cal()
            self.durum = "kaybettin"
            return True
        self.yilan.insert(0, bas)
        if bas == self.elma_yeri:
            self.elma_topla()
        else:
            self.yilan.pop()
        if self.kapi_acik and bas == self.kapi_yeri:
            self.acik_level = min(SON_LEVEL, max(self.acik_level, self.level + 1))
            self.rekor = max(self.rekor, self.puan)
            self.kazandi = True
            self.sonuc_suresi = time.time() - self.baslama
            self.durum = "kazandin"
        return True

    def carpti(self, yer):
        x, y = yer
        return x < 0 or y < 0 or x >= SUTUN or y >= SATIR or yer in self.engeller or yer in self.yilan[:-1]

    def elma_topla(self):
        gecen = time.time() - self.elma_zamani
        self.puan += max(10, int(120 + self.level * 12 - gecen * (7 + self.level)))
        self.toplanan += 1
        self.elma_uret()

    def kare(self, yer):
        return pygame.Rect(ALAN.x + yer[0] * KARE, ALAN.y + yer[1] * KARE, KARE, KARE)

    def ciz(self):
        if self.durum == "menu":
            self.menu_ciz()
        elif self.durum == "mod_menu":
            self.mod_menu_ciz()
        elif self.durum == "level_menu":
            self.level_menu_ciz()
        elif self.durum == "gecis":
            self.gecis_ciz()
        elif self.durum == "oyun":
            self.oyun_ciz()
        elif self.durum == "pause":
            self.oyun_ciz()
            self.pause_ciz()
        elif self.durum == "ayarlar":
            if self.ayarlar_donus == "pause":
                self.oyun_ciz()
            else:
                self.menu_ciz()
            self.ayarlar_ciz()
        elif self.durum == "cikis":
            self.menu_ciz()
            self.cikis_ciz()
        else:
            self.oyun_ciz()
            self.sonuc_ciz()

    def menu_ciz(self):
        self.ekran.fill((0, 0, 0))
        self.ekran.blit(self.a.al("Main Menu", "bg_main_menu.png", boyut=(W, H)), (0, 0))
        btn_y = int(H * 0.82)
        btn_h = 82
        gap_between = 40
        play_w = 260
        settings_w = 300
        exit_w = 260
        total_w = play_w + settings_w + exit_w + gap_between * 2
        start_x = W // 2 - total_w // 2
        self.play_rect = pygame.Rect(start_x, btn_y, play_w, btn_h)
        self.settings_rect = pygame.Rect(start_x + play_w + gap_between, btn_y, settings_w, btn_h)
        self.exit_rect = pygame.Rect(start_x + play_w + settings_w + gap_between * 2, btn_y, exit_w, btn_h)
        self.ana_menu_buton_ciz(self.play_rect, "btn_bg_pink.png", "icon_play.png", "BAŞLA")
        self.ana_menu_buton_ciz(self.settings_rect, "btn_bg_gray.png", "icon_settings.png", "AYARLAR")
        self.ana_menu_buton_ciz(self.exit_rect, "btn_bg_red.png", "icon_exit.png", "ÇIKIŞ")

    def mod_menu_ciz(self):
        self.menu_ciz()
        self.kutu((0, 0, W, H), 130)
        
        modal = self.a.al("Level Mod Menu", "ui_modal_bg.png", boyut=(630, 270))
        r = modal.get_rect(center=(W // 2, H // 2))
        self.ekran.blit(modal, r)
        
        self.yazi("OYUN MODU", self.mode_popup_title_font, BEYAZ, (r.centerx, r.y + 35))
        
        self.mode_close = pygame.Rect(r.right - 58, r.y + 12, 42, 42)
        pos = pygame.mouse.get_pos()
        close_hover = self.mode_close.collidepoint(pos)
        close_rect = self.mode_close.copy()
        if close_hover:
            close_rect = close_rect.inflate(6, 6)
        self.ekran.blit(self.a.al("Settings", "btn_bg_red_round.png", boyut=close_rect.size), close_rect)
        self.yazi("X", self.buton_font, BEYAZ, close_rect.center)
        
        self.hard_mode_rect = pygame.Rect(r.centerx - 225, r.y + 110, 210, 68)
        self.normal_mode_rect = pygame.Rect(r.centerx + 15, r.y + 110, 210, 68)
        
        self.mod_buton_ciz(self.hard_mode_rect, "btn_bg_red.png", "ZORLAYIIC MOD", self.mode_popup_buton_font)
        self.mod_buton_ciz(self.normal_mode_rect, "btn_bg_gray.png", "NORMAL MOD", self.mode_popup_buton_font)
        
        self.yazi("Ölünce Başa Döner", self.mode_popup_label_font, (64, 66, 74), (self.hard_mode_rect.centerx, r.y + 207))
        self.yazi("Checkpoint Açık", self.mode_popup_label_font, (64, 66, 74), (self.normal_mode_rect.centerx, r.y + 207))

    def level_menu_ciz(self):
        self.ekran.fill((0, 0, 0))
        self.ekran.blit(self.a.region(self.region, f"bg_level_menu_region_{self.region}.png", (W, H)), (0, 0))
        baslik = BOLGELER[self.region][0]
        self.ekran.blit(self.a.fixed("logo_main.png", (185, 82)), (W - 235, 24))
        basla = (self.region - 1) * 4 + 1
        self.level_yolu_ciz(basla)
        self.level_rects = []
        konumlar = [(195, 232), (486, 535), (808, 232), (1067, 595)]
        etiketler = [(195, 80), (486, 375), (808, 80), (1067, 450)]
        boylar = [230, 245, 230, 215]
        for i in range(4):
            level = basla + i
            x, y = konumlar[i]
            kilitli = level > self.acik_level
            boy = boylar[i]
            halka = self.a.fixed("fx_ring.png", (boy + 48, boy + 48)).copy()
            halka.set_alpha(125 if kilitli else 170)
            self.ekran.blit(halka, halka.get_rect(center=(x, y)))
            if level == self.acik_level and not kilitli:
                glow = self.a.fixed("fx_glow_ring.png", (boy + 58, boy + 58)).copy()
                glow.set_alpha(115)
                self.ekran.blit(glow, glow.get_rect(center=(x, y)))
            gezegen = self.a.al(*self.gezegen_yolu(level, kilitli), boyut=(boy, boy))
            rect = gezegen.get_rect(center=(x, 390))
            rect.center = (x, y)
            self.ekran.blit(gezegen, rect)
            etiket_rect = self.level_etiket_ciz(level, LEVEL_ADLARI[level],
                                                etiketler[i],
                                                level == self.acik_level, not kilitli)
            self.level_rects.append((level, rect.inflate(30, 30).union(etiket_rect)))
        panel = self.a.region(self.region, f"ui_panel_region_{self.region}_info.png", (345, 65))
        panel_rect = panel.get_rect(bottomleft=(22, H - 20))
        self.ekran.blit(panel, panel_rect)
        self.yazi_sol(f"Bölge {self.region}: {baslik}", self.bolge_font, (52, 58, 66),
                      (panel_rect.x + 18, panel_rect.centery + 1))
        self.prev_region_rect = pygame.Rect(30, H // 2 - 27, 54, 54)
        self.next_region_rect = pygame.Rect(W - 84, H // 2 - 27, 54, 54)
        ok_bg = self.a.fixed("btn_bg_round_gray.png", (54, 54))
        ok = self.a.fixed("icon_arrow_right.png", (26, 23))
        if self.region > 1:
            self.ekran.blit(ok_bg, self.prev_region_rect)
            self.ekran.blit(pygame.transform.flip(ok, True, False), (44, H // 2 - 11))
        else:
            self.prev_region_rect = pygame.Rect(0, 0, 0, 0)
        if self.region < 5:
            self.ekran.blit(ok_bg, self.next_region_rect)
            self.ekran.blit(ok, (W - 70, H // 2 - 11))
        else:
            self.next_region_rect = pygame.Rect(0, 0, 0, 0)

    def level_yolu_ciz(self, basla):
        if self.acik_level < basla:
            acik_parca = 0
        elif self.acik_level >= basla + 3:
            acik_parca = 4
        else:
            acik_parca = self.acik_level - basla + 1

        cizgiler = [
            [(152, 360), (145, 485), (348, 522)],
            [(504, 350), (519, 255), (670, 212)],
            [(796, 419), (776, 533), (915, 609)],
            [(1073, 383), (1140, 264), (1375, 244)],
        ]
        for i, noktalar in enumerate(cizgiler):
            alfa = 245 if i < acik_parca else 115
            renk = (245, 245, 245) if i < acik_parca else (150, 158, 166)
            self.kesik_egri_ciz(noktalar, renk, alfa)

    def kesik_egri_ciz(self, noktalar, renk, alfa):
        katman = pygame.Surface((W, H), pygame.SRCALPHA)
        ornekler = []
        for i in range(80):
            t = i / 79
            x = (1 - t) ** 2 * noktalar[0][0] + 2 * (1 - t) * t * noktalar[1][0] + t ** 2 * noktalar[2][0]
            y = (1 - t) ** 2 * noktalar[0][1] + 2 * (1 - t) * t * noktalar[1][1] + t ** 2 * noktalar[2][1]
            ornekler.append((x, y))
        uzakliklar = [0]
        for a, b in zip(ornekler, ornekler[1:]):
            uzakliklar.append(uzakliklar[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))

        def nokta_al(hedef):
            for i in range(1, len(uzakliklar)):
                if uzakliklar[i] >= hedef:
                    oran = (hedef - uzakliklar[i - 1]) / max(1, uzakliklar[i] - uzakliklar[i - 1])
                    ax, ay = ornekler[i - 1]
                    bx, by = ornekler[i]
                    return ax + (bx - ax) * oran, ay + (by - ay) * oran
            return ornekler[-1]

        toplam = uzakliklar[-1]
        mesafe = 0
        while mesafe < toplam:
            bas = nokta_al(mesafe)
            bit = nokta_al(min(toplam, mesafe + 10))
            pygame.draw.line(katman, (*renk, alfa), bas, bit, 7)
            pygame.draw.circle(katman, (*renk, alfa), (int(bas[0]), int(bas[1])), 3)
            pygame.draw.circle(katman, (*renk, alfa), (int(bit[0]), int(bit[1])), 3)
            mesafe += 22
        self.ekran.blit(katman, (0, 0))

    def level_etiket_ciz(self, level, ad, merkez, aktif, acik):
        dosya = "ui_label_bg_active.png" if aktif else "ui_label_bg.png"
        etiket = self.a.fixed(dosya, (154, 56))
        r = etiket.get_rect(center=merkez)
        self.ekran.blit(etiket, r)
        renk = BEYAZ if aktif else ((42, 42, 52) if acik else (78, 78, 88))
        self.yazi(f"LEVEL {level}", self.level_baslik_font, renk, (r.centerx, r.y + 20))
        self.yazi(ad, self.level_ad_font, renk, (r.centerx, r.y + 39))
        return r

    def gecis_ciz(self):
        self.level_menu_ciz()
        t = min(1, (pygame.time.get_ticks() - self.gecis_basla) / self.gecis_suresi)
        self.kutu((0, 0, W, H), int(170 * t))
        boy = int(120 + 210 * math.sin(t * math.pi / 2))
        gezegen = self.a.al(*self.gezegen_yolu(self.gecis_level), boyut=(boy, boy))
        self.ekran.blit(gezegen, gezegen.get_rect(center=(W // 2, H // 2)))
        self.yazi(f"Level {self.gecis_level}", self.buyuk, BEYAZ, (W // 2, H // 2 + boy // 2 + 45))
        self.yazi("Hazırlanıyor...", self.font, BEYAZ, (W // 2, H // 2 + boy // 2 + 82))

    def oyun_ciz(self):
        self.ekran.fill((0, 0, 0))
        self.ekran.blit(self.a.level(self.level, "bg_world.png", (W, H)), (0, 0))
        self.hud_ciz()
        self.ekran.blit(self.tahta, ALAN)
        kenar = pygame.Surface(ALAN.size, pygame.SRCALPHA)
        pygame.draw.rect(kenar, (0, 0, 0, 85), kenar.get_rect(), 3)
        self.ekran.blit(kenar, ALAN.topleft)
        duvar = self.a.level(self.level, "wall_block.png", (KARE, KARE))
        for e in self.engeller:
            self.ekran.blit(duvar, self.kare(e))
        if self.kapi_acik:
            r = self.kare(self.kapi_yeri)
            portal = self.a.level(self.level, "fx_portal.png", (KARE + 14, KARE + 14))
            self.ekran.blit(portal, portal.get_rect(center=r.center))
        if self.elma_yeri:
            self.ekran.blit(self.a.level(self.level, "item_fruit.png", (KARE, KARE)), self.kare(self.elma_yeri))
        self.yilan_ciz()

    def hud_ciz(self):
        logo = self.a.global_("logo_main.png", (185, 82))
        self.ekran.blit(logo, (54, 54))
        seviye_yazi = f"Seviye {self.level}"
        if self.oyun_modu == "zor":
            seviye_yazi += " Zor"
        oyun_suresi = self.sonuc_suresi if self.durum in ("kazandin", "kaybettin") and self.sonuc_suresi else time.time() - self.baslama
        bilgiler = [("icon_ranking.png", "Mevcut Seviye", seviye_yazi), ("icon_star.png", "Puan", str(self.puan)),
                    ("icon_clock.png", "Geçen Süre", sure_yaz(oyun_suresi)),
                    ("icon_apple.png", "Meyve Sayısı", f"{self.toplanan}/{self.hedef()}")]
        for i, (ikon, baslik, metin) in enumerate(bilgiler):
            x = int(338 + i * 225.56)
            panel = self.a.global_("ui_hud_panel.png", (215, 77))
            self.ekran.blit(panel, (x, 56))
            self.ekran.blit(self.a.global_(ikon, (30, 30)), (x + 16, 79))
            self.yazi_sol(baslik, self.hud_label_font, BEYAZ, (x + 54, 80))
            self.yazi_sol(metin, self.hud_value_font, BEYAZ, (x + 54, 103))
        self.yardim_ciz()

    def yardim_ciz(self):
        esc = self.a.global_("ui_keycap_esc.png")
        r_key = self.a.global_("ui_keycap_r.png")
        yazi1 = self.yardim_font.render("Menüye Dön", True, (230, 230, 235))
        yazi2 = self.yardim_font.render("Yeniden Başla", True, (230, 230, 235))
        toplam = esc.get_width() + 12 + yazi1.get_width() + 34 + r_key.get_width() + 12 + yazi2.get_width()
        x = ALAN.centerx - toplam // 2
        y = ALAN.bottom + 15
        orta = y + esc.get_height() // 2
        self.ekran.blit(esc, (x, y))
        x += esc.get_width() + 12
        self.ekran.blit(yazi1, yazi1.get_rect(midleft=(x, orta)))
        x += yazi1.get_width() + 34
        self.ekran.blit(r_key, (x, y))
        x += r_key.get_width() + 12
        self.ekran.blit(yazi2, yazi2.get_rect(midleft=(x, orta)))

    def yilan_ciz(self):
        if len(self.yilan) < 2:
            return

        head_img = self.a.global_("snake_head.png", (KARE, KARE))
        body_img = self.a.global_("snake_body_straight.png", (KARE, KARE))
        turn_img = self.a.global_("snake_body_turn.png", (KARE, KARE))
        tail_img = self.a.global_("snake_tail.png", (KARE, KARE))

        # Pre-pass: draw connecting lines between segment centers to fill junction gaps
        SNAKE_COL = (181, 73, 228)
        arm_w = int(KARE * 0.55)  # matches sprite arm thickness
        centers = [self.kare(p).center for p in self.yilan]
        for a, b in zip(centers, centers[1:]):
            pygame.draw.line(self.ekran, SNAKE_COL, a, b, arm_w)

        # base HEAD faces RIGHT, base TAIL points UP, base TURN connects RIGHT+DOWN
        HEAD_ROT = {(1, 0): 0, (-1, 0): 180, (0, -1): 90, (0, 1): 270}
        TAIL_ROT = {(0, -1): 0, (0, 1): 180, (1, 0): 270, (-1, 0): 90}
        TURN_ROT = {
            frozenset([(1, 0), (0, 1)]): 0,     # RIGHT + DOWN  (base)
            frozenset([(1, 0), (0, -1)]): 90,   # RIGHT + UP
            frozenset([(-1, 0), (0, -1)]): 180, # LEFT  + UP
            frozenset([(-1, 0), (0, 1)]): 270,  # LEFT  + DOWN
        }

        n = len(self.yilan)
        for i, pos in enumerate(self.yilan):
            rect = self.kare(pos)
            if i == 0:
                angle = HEAD_ROT.get(tuple(self.yon), 0)
                img = pygame.transform.rotate(head_img, angle)
            elif i == n - 1:
                dx = self.yilan[i - 1][0] - pos[0]
                dy = self.yilan[i - 1][1] - pos[1]
                angle = TAIL_ROT.get((dx, dy), 0)
                img = pygame.transform.rotate(tail_img, angle)
            else:
                d_next = (self.yilan[i - 1][0] - pos[0], self.yilan[i - 1][1] - pos[1])
                d_prev = (self.yilan[i + 1][0] - pos[0], self.yilan[i + 1][1] - pos[1])
                if d_next[0] == -d_prev[0] and d_next[1] == -d_prev[1]:
                    angle = 0 if d_next[0] != 0 else 90
                    img = pygame.transform.rotate(body_img, angle)
                else:
                    angle = TURN_ROT.get(frozenset([d_next, d_prev]), 0)
                    img = pygame.transform.rotate(turn_img, angle)
            self.ekran.blit(img, img.get_rect(center=rect.center))

    def sonuc_ciz(self):
        klasor = "Won" if self.durum == "kazandin" else "Lost"
        self.kutu((0, 0, W, H), 45)
        modal_adi = "ui_modal_bg_green.png" if klasor == "Won" else "ui_modal_bg_red.png"
        modal = self.a.al("Levels", klasor, modal_adi, boyut=(512, 476))
        r = modal.get_rect(center=(W // 2, H // 2))
        self.ekran.blit(modal, r)
        baslik = "KAZANDIN" if klasor == "Won" else "KAYBETTİN"
        self.yazi(baslik, self.sonuc_baslik_font, BEYAZ, (r.centerx, r.y + 40))
        yildiz = "icon_star_green.png" if klasor == "Won" else "icon_star_gray.png"
        self.ekran.blit(self.a.al("Levels", klasor, yildiz, boyut=(132, 48)),
                        (r.centerx - 66, r.y + 105))
        self.yazi(f"{self.puan} Puan", self.sonuc_skor_font, (45, 48, 55), (r.centerx, r.y + 185))
        sure = self.sonuc_suresi if self.sonuc_suresi else time.time() - self.baslama
        self.sonuc_stat_ciz(klasor, pygame.Rect(r.centerx - 208, r.y + 240, 198, 77),
                             "icon_clock.png", "Geçen Süre", sure_yaz(sure))
        self.sonuc_stat_ciz(klasor, pygame.Rect(r.centerx + 10, r.y + 240, 198, 77),
                             "icon_apple.png", "Meyve Sayısı", f"{self.toplanan}/{self.hedef()}")
        self.result_main = pygame.Rect(r.centerx - 208, r.y + 350, 198, 64)
        self.result_action = pygame.Rect(r.centerx + 10, r.y + 350, 198, 64)
        self.sonuc_buton_ciz(klasor, self.result_main, "btn_bg_gray.png", "btn_bg_dark_gray.png", "Ana Menü")
        btn = "btn_bg_pink.png" if klasor == "Won" else "btn_bg_red.png"
        ikon = "icon_arrow_right_white.png" if klasor == "Won" else "icon_retry_white.png"
        yazi = "Devam Et" if klasor == "Won" else "Tekrar"
        self.sonuc_buton_ciz(klasor, self.result_action, btn, ikon, yazi)

    def sonuc_stat_ciz(self, klasor, rect, ikon, baslik, deger):
        self.ekran.blit(self.a.al("Levels", klasor, "ui_panel_stats_light.png", boyut=rect.size), rect)
        self.ekran.blit(self.a.al("Levels", klasor, ikon, boyut=(30, 30)), (rect.x + 16, rect.y + 23))
        self.yazi_sol(baslik, self.kucuk, (78, 83, 91), (rect.x + 60, rect.y + 27))
        self.yazi_sol(deger, self.sonuc_stat_val_font, (45, 48, 55), (rect.x + 60, rect.y + 50))

    def sonuc_buton_ciz(self, klasor, rect, bg, ikon, metin):
        pos = pygame.mouse.get_pos()
        hover = rect.collidepoint(pos)
        
        draw_rect = rect.copy()
        if hover:
            draw_rect = draw_rect.inflate(8, 6)
            draw_rect.y -= 3
            
        self.ekran.blit(self.a.al("Levels", klasor, bg, boyut=draw_rect.size), draw_rect)
        
        if ikon == "btn_bg_dark_gray.png":
            # Left-aligned icon (Home)
            self.ekran.blit(self.a.al("Levels", klasor, ikon, boyut=(24, 24)), 
                            (draw_rect.x + 20, draw_rect.centery - 12))
            self.yazi(metin.upper(), self.sonuc_buton_font, BEYAZ, (draw_rect.centerx + 12, draw_rect.centery - 2))
        else:
            # Right-aligned icon (Arrow / Replay)
            self.ekran.blit(self.a.al("Levels", klasor, ikon, boyut=(24, 24)), 
                            (draw_rect.right - 20 - 24, draw_rect.centery - 12))
            self.yazi(metin.upper(), self.sonuc_buton_font, BEYAZ, (draw_rect.centerx - 12, draw_rect.centery - 2))

    def pause_ciz(self):
        self.kutu((0, 0, W, H), 130)
        modal = self.a.al("Settings", "ui_modal_bg.png", boyut=(680, 404))
        r = modal.get_rect(center=(W // 2, H // 2))
        self.ekran.blit(modal, r)

        self.yazi("DURAKLATILDI", self.ayarlar_baslik_font, BEYAZ,
                  (r.centerx, r.y + 47))

        self.pause_close_rect = pygame.Rect(r.right - 68, r.y + 17, 48, 48)
        close_rect = self.pause_close_rect.copy()
        if close_rect.collidepoint(pygame.mouse.get_pos()):
            close_rect = close_rect.inflate(6, 6)
        self.ekran.blit(
            self.a.al("Settings", "btn_bg_red_round.png", boyut=close_rect.size),
            close_rect
        )
        self.yazi("X", self.buton_font, BEYAZ, close_rect.center)

        mod = "Zorlayıcı Mod" if self.oyun_modu == "zor" else "Normal Mod"
        bilgi = f"{mod}   |   Seviye {self.level}   |   Skor {self.puan}"
        self.yazi(bilgi, self.font, (64, 66, 74), (r.centerx, r.y + 151))

        buton_y = r.y + 245
        self.pause_resume_rect = pygame.Rect(r.x + 38, buton_y, 180, 68)
        self.pause_settings_rect = pygame.Rect(r.x + 235, buton_y, 190, 68)
        self.pause_lobby_rect = pygame.Rect(r.x + 442, buton_y, 200, 68)
        self.pause_buton_ciz(
            self.pause_resume_rect, "btn_bg_pink.png", "icon_play.png", "DEVAM ET"
        )
        self.pause_buton_ciz(
            self.pause_settings_rect, "btn_bg_gray.png", "icon_settings.png", "AYARLAR"
        )
        self.pause_buton_ciz(
            self.pause_lobby_rect, "btn_bg_red.png", "icon_exit.png", "LOBİYE DÖN"
        )

    def pause_buton_ciz(self, rect, bg, ikon, metin):
        draw_rect = rect.copy()
        if rect.collidepoint(pygame.mouse.get_pos()):
            draw_rect = draw_rect.inflate(8, 6)

        self.ekran.blit(self.a.al("Main Menu", bg, boyut=draw_rect.size), draw_rect)
        yazi = self.buton_font.render(metin, True, BEYAZ)
        ikon_kaynak = self.a.al("Main Menu", ikon)
        ikon_h = int(yazi.get_height() * 0.8)
        ikon_w = round(ikon_kaynak.get_width() * ikon_h / ikon_kaynak.get_height())
        ikon_img = pygame.transform.smoothscale(ikon_kaynak, (ikon_w, ikon_h))

        gap = 12
        toplam = ikon_img.get_width() + gap + yazi.get_width()
        bas_x = draw_rect.centerx - toplam // 2
        ikon_y = draw_rect.centery - ikon_img.get_height() // 2
        yazi_y = draw_rect.centery - yazi.get_height() // 2
        self.ekran.blit(ikon_img, (bas_x, ikon_y))
        self.ekran.blit(yazi, (bas_x + ikon_img.get_width() + gap, yazi_y))

    def ayar_buton_ciz(self, rect, bg, metin, font=None):
        pos = pygame.mouse.get_pos()
        hover = rect.collidepoint(pos)
        
        draw_rect = rect.copy()
        if hover:
            draw_rect = draw_rect.inflate(8, 6)
            draw_rect.y -= 2
            
        f = font or self.buton_font
        self.ekran.blit(self.a.al("Settings", bg, boyut=draw_rect.size), draw_rect)
        self.yazi(metin, f, BEYAZ, draw_rect.center)

    def ayarlar_ciz(self):
        self.kutu((0, 0, W, H), 130)
        modal = self.a.al("Settings", "ui_modal_bg.png", boyut=(500, 300))
        r = modal.get_rect(center=(W // 2, H // 2))
        self.ekran.blit(modal, r)
        self.yazi("AYARLAR", self.ayarlar_baslik_font, BEYAZ, (r.centerx, r.y + 35))
        
        self.settings_close = pygame.Rect(r.right - 58, r.y + 12, 42, 42)
        pos = pygame.mouse.get_pos()
        close_hover = self.settings_close.collidepoint(pos)
        close_rect = self.settings_close.copy()
        if close_hover:
            close_rect = close_rect.inflate(6, 6)
            
        self.ekran.blit(self.a.al("Settings", "btn_bg_red_round.png", boyut=close_rect.size), close_rect)
        self.yazi("X", self.buton_font, BEYAZ, close_rect.center)
        
        self.yazi_sol("Oyun Sesleri", self.ayarlar_label_font, (64, 66, 74), (r.x + 48, r.y + 130))
        self.yazi_sol("Müzik", self.ayarlar_label_font, (64, 66, 74), (r.x + 48, r.y + 215))
        
        self.effects_toggle = pygame.Rect(r.right - 168, r.y + 104, 120, 52)
        self.music_toggle = pygame.Rect(r.right - 168, r.y + 189, 120, 52)
        
        self.ayar_buton_ciz(self.effects_toggle, "btn_bg_green.png" if self.efekt_acik else "btn_bg_red.png",
                            "AÇIK" if self.efekt_acik else "KAPALI", self.ayarlar_buton_font)
        self.ayar_buton_ciz(self.music_toggle, "btn_bg_green.png" if self.ses_acik else "btn_bg_red.png",
                            "AÇIK" if self.ses_acik else "KAPALI", self.ayarlar_buton_font)

    def cikis_ciz(self):
        self.kutu((0, 0, W, H), 105)
        modal = self.a.al("Quit", "ui_modal_bg.png", boyut=(430, 272))
        r = modal.get_rect(center=(W // 2, H // 2))
        self.ekran.blit(modal, r)
        self.yazi("ÇIKIŞ", self.baslik_font, BEYAZ, (W // 2, r.y + 34))
        self.yazi("Oyundan Çıkmak", self.font, (70, 70, 78), (W // 2, r.y + 98))
        self.yazi("istediğinize emin misiniz?", self.font, (70, 70, 78), (W // 2, r.y + 128))
        self.quit_yes = pygame.Rect(r.x + 58, r.y + 174, 145, 54)
        self.quit_no = pygame.Rect(r.x + 226, r.y + 174, 145, 54)
        self.cikis_buton_ciz(self.quit_yes, "btn_bg_green.png", "icon_check.png", "EVET")
        self.cikis_buton_ciz(self.quit_no, "btn_bg_red.png", "icon_cross_white.png", "HAYIR")

    def cikis_buton_ciz(self, rect, bg, ikon, metin):
        self.ekran.blit(self.a.al("Quit", bg, boyut=rect.size), rect)
        self.ekran.blit(self.a.al("Quit", ikon, boyut=(30, 30)), (rect.x + 14, rect.y + 12))
        self.yazi(metin, self.buton_font, BEYAZ, (rect.centerx + 18, rect.centery - 1))

    def buton_resimli(self, rect, bg, ikon, metin):
        pos = pygame.mouse.get_pos()
        hover = rect.collidepoint(pos)
        
        draw_rect = rect.copy()
        if hover:
            draw_rect = draw_rect.inflate(8, 6)
            draw_rect.y -= 3
            
        self.ekran.blit(self.a.al(*bg, boyut=draw_rect.size), draw_rect)
        if ikon:
            boy = min(30, draw_rect.h - 18)
            self.ekran.blit(self.a.al(*ikon, boyut=(boy, boy)), (draw_rect.x + 18, draw_rect.centery - boy // 2))
            x = draw_rect.centerx + 15
        else:
            x = draw_rect.centerx
        self.yazi(metin, self.buton_font, BEYAZ, (x, draw_rect.centery - 4))

    def ana_menu_buton_ciz(self, rect, bg, ikon, metin):
        pos = pygame.mouse.get_pos()
        hover = rect.collidepoint(pos)
        
        draw_rect = rect.copy()
        if hover:
            draw_rect = rect.inflate(12, 8)
            draw_rect.y -= 4
            
        self.ekran.blit(self.a.al("Main Menu", bg, boyut=draw_rect.size), draw_rect)
        yazi_img = self.menu_buton_font.render(metin, True, BEYAZ)
        ikon_kaynak = self.a.al("Main Menu", ikon)
        ikon_h = int(yazi_img.get_height() * 0.95)
        ikon_w = max(1, round(ikon_kaynak.get_width() * ikon_h / ikon_kaynak.get_height()))
        ikon_img = pygame.transform.smoothscale(ikon_kaynak, (ikon_w, ikon_h))
        gap = 12
        toplam = ikon_img.get_width() + gap + yazi_img.get_width()
        bas_x = draw_rect.centerx - toplam // 2
        ikon_x = bas_x
        yazi_x = bas_x + ikon_img.get_width() + gap
        
        offset_y = -5
        ikon_y = draw_rect.centery - ikon_img.get_height() // 2 + offset_y
        yazi_y = draw_rect.centery - yazi_img.get_height() // 2 + offset_y
        
        self.ekran.blit(ikon_img, (ikon_x, ikon_y))
        self.ekran.blit(yazi_img, (yazi_x, yazi_y))

    def mod_buton_ciz(self, rect, bg, metin, font=None):
        pos = pygame.mouse.get_pos()
        hover = rect.collidepoint(pos)
        
        draw_rect = rect.copy()
        if hover:
            draw_rect = draw_rect.inflate(8, 6)
            draw_rect.y -= 3
            
        f = font or self.mode_buton_font
        self.ekran.blit(self.a.al("Main Menu", bg, boyut=draw_rect.size), draw_rect)
        self.yazi(metin, f, BEYAZ, (draw_rect.centerx, draw_rect.centery - 4))

    def mod_rozet_ciz(self, metin, rect):
        rozet = self.a.al("Main Menu", "btn_bg_gray.png", boyut=rect.size)
        self.ekran.blit(rozet, rect)
        self.yazi(metin, self.mode_rozet_font, (48, 52, 60), rect.center)

    def kutu(self, rect, alpha):
        s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        s.fill((0, 0, 0, alpha))
        self.ekran.blit(s, rect[:2])

    def yazi(self, metin, font, renk, merkez):
        img = font.render(metin, True, renk)
        self.ekran.blit(img, img.get_rect(center=merkez))

    def yazi_sol(self, metin, font, renk, orta_sol):
        img = font.render(metin, True, renk)
        self.ekran.blit(img, img.get_rect(midleft=orta_sol))

    def calistir(self):
        self.ciz()
        pygame.display.flip()
        while True:
            degisti = self.olaylar() or self.guncelle()
            sure = int(time.time() - self.baslama)
            if self.durum == "oyun" and sure != self.son_sure:
                self.son_sure = sure
                degisti = True
            if degisti:
                self.ciz()
                pygame.display.flip()
            self.saat.tick(FPS)
