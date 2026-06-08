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


class Oyun:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 256)
        pygame.init()
        pygame.display.set_caption("Snake Space")
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN])
        self.ekran = pygame.display.set_mode((W, H), pygame.DOUBLEBUF)
        self.saat = pygame.time.Clock()
        self.a = Assetler()
        self.font = pygame.font.SysFont("arial", 22, bold=True)
        self.kucuk = pygame.font.SysFont("arial", 16)
        self.buyuk = pygame.font.SysFont("arial", 42, bold=True)
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
        self.ses_acik = True
        self.muzik_ses = 0.70
        self.kazandi = False
        self.gecis_basla = 0
        self.gecis_level = 1
        self.gecis_puan = None
        self.son_sure = -1
        self.sesleri_hazirla()
        self.level_kur()
        self.menu_muzigi_baslat()

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
        if self.ses_acik and self.ses_hazir and self.game_over_sesi:
            self.game_over_sesi.play()

    def level_gecis_sesi_cal(self):
        if self.ses_acik and self.ses_hazir and self.level_gecis_sesi:
            self.level_gecis_sesi.stop()
            self.level_gecis_sesi.set_volume(1)
            if self.menu_caliyor:
                pygame.mixer.music.set_volume(self.muzik_ses * 0.35)
            self.level_gecis_sesi.play()

    def muzik_sesi_degistir(self, miktar):
        self.muzik_ses = max(0, min(1, round(self.muzik_ses + miktar, 2)))
        if self.ses_hazir:
            pygame.mixer.music.set_volume(self.muzik_ses)

    def level_kur(self):
        self.yilan = [(7, 8), (6, 8), (5, 8)]
        self.yon = self.sonraki = (1, 0)
        self.toplanan = 0
        self.kapi_acik = False
        self.kapi_yeri = (SUTUN - 3, SATIR - 3)
        self.son_hareket = pygame.time.get_ticks()
        self.baslama = time.time()
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
        s.set_alpha(225)
        return s

    def hedef(self):
        return 3 if self.level == 1 else 5 + (self.level - 2) * 3

    def hiz(self):
        taban = 112 - self.level * 4
        if self.oyun_modu == "zor":
            taban -= 14
        return max(42, taban)

    def engel_uret(self):
        rnd = random.Random(self.level * 77)
        engel = set()
        guvenli_baslangic = {(x, y) for x in range(3, 12) for y in range(6, 11)}
        yasak = set(self.yilan) | guvenli_baslangic | {self.kapi_yeri}
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

    def elma_uret(self):
        if self.toplanan >= self.hedef():
            self.elma_yeri = None
            self.kapi_acik = True
            return
        dolu = set(self.yilan) | self.engeller | {self.kapi_yeri}
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
                self.region = self.region % 5 + 1
                return True
            if tus in (pygame.K_LEFT, pygame.K_a):
                self.region = 5 if self.region == 1 else self.region - 1
                return True
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
                self.durum = "level_menu"
                self.menu_muzigi_baslat()
                return True
            if tus == pygame.K_r:
                self.level_baslat(self.level, self.level_puan_baslangic)
                return True
        if self.durum in ("kazandin", "kaybettin") and tus in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_r):
            self.sonuc_devam()
            return True
        if tus == pygame.K_ESCAPE and self.durum in ("ayarlar", "cikis"):
            self.durum = "menu"
            self.menu_muzigi_baslat()
            return True
        return False

    def tikla(self, pos):
        if self.durum == "menu":
            if self.play_rect.collidepoint(pos):
                self.durum = "mod_menu"
                self.menu_muzigi_baslat()
            elif self.settings_rect.collidepoint(pos):
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
            if self.mode_back_rect.collidepoint(pos):
                self.durum = "menu"
                self.menu_muzigi_baslat()
                return True
        if self.durum == "level_menu":
            if self.next_region_rect.collidepoint(pos):
                self.region = self.region % 5 + 1
                return True
            for level, rect in self.level_rects:
                if rect.collidepoint(pos) and level <= self.acik_level:
                    puan = self.level_puan_baslangic if level == self.level else 0
                    self.gecis_baslat(level, puan)
                    return True
        if self.durum == "ayarlar":
            if self.settings_save.collidepoint(pos):
                self.ses_acik = not self.ses_acik
                if self.ses_acik:
                    self.menu_muzigi_baslat()
                else:
                    self.menu_muzigi_durdur()
                return True
            if self.volume_down.collidepoint(pos):
                self.muzik_sesi_degistir(-0.10)
                return True
            if self.volume_up.collidepoint(pos):
                self.muzik_sesi_degistir(0.10)
                return True
            if self.settings_close.collidepoint(pos):
                self.durum = "menu"
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
        elif self.durum == "ayarlar":
            self.menu_ciz()
            self.ayarlar_ciz()
        elif self.durum == "cikis":
            self.menu_ciz()
            self.cikis_ciz()
        else:
            self.oyun_ciz()
            self.sonuc_ciz()

    def menu_ciz(self):
        self.ekran.blit(self.a.al("Main Menu", "bg_main_menu.png", boyut=(W, H)), (0, 0))
        self.play_rect = pygame.Rect(W // 2 - 125, 500, 250, 72)
        self.settings_rect = pygame.Rect(W // 2 - 137, 580, 275, 72)
        self.exit_rect = pygame.Rect(W // 2 - 125, 660, 250, 72)
        self.buton_resimli(self.play_rect, ("Main Menu", "btn_bg_pink.png"), ("Main Menu", "icon_play.png"), "Oyuna Başla")
        self.buton_resimli(self.settings_rect, ("Main Menu", "btn_bg_gray.png"), ("Main Menu", "icon_settings.png"), "Ayarlar")
        self.buton_resimli(self.exit_rect, ("Main Menu", "btn_bg_red.png"), ("Main Menu", "icon_exit.png"), "Çıkış")

    def mod_menu_ciz(self):
        self.ekran.blit(self.a.al("Main Menu", "bg_main_menu.png", boyut=(W, H)), (0, 0))
        self.kutu((260, 115, 760, 485), 125)
        self.yazi("Oyun Modu", self.buyuk, BEYAZ, (W // 2, 180))
        self.hard_mode_rect = pygame.Rect(W // 2 - 285, 300, 250, 72)
        self.normal_mode_rect = pygame.Rect(W // 2 + 35, 300, 250, 72)
        self.mode_back_rect = pygame.Rect(W // 2 - 105, 510, 210, 58)
        self.buton_resimli(self.hard_mode_rect, ("Main Menu", "btn_bg_red.png"), None, "Zorlayıcı Mod")
        self.buton_resimli(self.normal_mode_rect, ("Main Menu", "btn_bg_pink.png"), None, "Normal Mod")
        self.yazi("Ölünce başa döner", self.kucuk, (230, 230, 240), self.hard_mode_rect.move(0, 55).center)
        self.yazi("Checkpoint açık", self.kucuk, (230, 230, 240), self.normal_mode_rect.move(0, 55).center)
        self.buton_resimli(self.mode_back_rect, ("Main Menu", "btn_bg_gray.png"), None, "Geri")

    def level_menu_ciz(self):
        self.ekran.blit(self.a.region(self.region, f"bg_level_menu_region_{self.region}.png", (W, H)), (0, 0))
        self.kutu((34, 28, 1212, 120), 105)
        self.ekran.blit(self.a.fixed("logo_main.png", (170, 75)), (55, 50))
        self.yazi(f"Bölge {self.region} / 5", self.buyuk, BEYAZ, (W // 2, 60))
        panel = self.a.region(self.region, f"ui_panel_region_{self.region}_info.png")
        panel_rect = panel.get_rect(topright=(W - 58, 50))
        self.ekran.blit(panel, panel_rect)
        baslik, aciklama = BOLGELER[self.region]
        self.yazi(baslik, self.font, (35, 35, 45), (panel_rect.centerx, panel_rect.y + 27))
        self.yazi(aciklama, self.kucuk, (55, 55, 65), (panel_rect.centerx, panel_rect.y + 55))
        self.level_rects = []
        basla = (self.region - 1) * 4 + 1
        for i in range(4):
            level = basla + i
            x = 250 + i * 235
            kilitli = level > self.acik_level
            gezegen = self.a.al(*self.gezegen_yolu(level, kilitli), boyut=(155, 155))
            rect = gezegen.get_rect(center=(x, 390))
            self.ekran.blit(gezegen, rect)
            self.level_rects.append((level, rect.inflate(20, 20)))
            acik = level <= self.acik_level
            etiket = self.a.fixed("ui_label_bg_active.png" if acik else "ui_label_bg.png", (150, 54))
            self.ekran.blit(etiket, etiket.get_rect(center=(x, 520)))
            self.yazi(f"Level {level}", self.font, BEYAZ if acik else (78, 78, 92), (x, 520))
        self.next_region_rect = pygame.Rect(W - 105, H // 2 - 36, 72, 72)
        self.ekran.blit(self.a.fixed("btn_bg_round_gray.png", (72, 72)), self.next_region_rect)
        self.ekran.blit(self.a.fixed("icon_arrow_right.png", (32, 28)), (W - 85, H // 2 - 14))
        self.yazi("ESC menü", self.kucuk, BEYAZ, (72, H - 36))

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
        self.ekran.blit(self.a.level(self.level, "bg_world.png", (W, H)), (0, 0))
        self.hud_ciz()
        self.ekran.blit(self.tahta, ALAN)
        pygame.draw.rect(self.ekran, (20, 20, 25), ALAN, 3)
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
        logo = self.a.global_("logo_main.png", (155, 68))
        self.ekran.blit(logo, (60, 34))
        seviye_yazi = f"Seviye {self.level}"
        if self.oyun_modu == "zor":
            seviye_yazi += " Zor"
        bilgiler = [("icon_ranking.png", seviye_yazi), ("icon_star.png", str(self.puan)),
                    ("icon_clock.png", sure_yaz(time.time() - self.baslama)),
                    ("icon_apple.png", f"{self.toplanan}/{self.hedef()}")]
        for i, (ikon, metin) in enumerate(bilgiler):
            x = 260 + i * 210
            panel = self.a.global_("ui_hud_panel.png", (190, 56))
            self.ekran.blit(panel, (x, 45))
            self.ekran.blit(self.a.global_(ikon, (30, 30)), (x + 16, 58))
            self.yazi(metin, self.kucuk, BEYAZ, (x + 106, 73))
        self.ekran.blit(self.a.global_("ui_keycap_esc.png"), (ALAN.x + 375, ALAN.bottom + 15))
        self.yazi("Menü", self.kucuk, BEYAZ, (ALAN.x + 455, ALAN.bottom + 31))
        self.ekran.blit(self.a.global_("ui_keycap_r.png"), (ALAN.x + 530, ALAN.bottom + 15))
        self.yazi("Yeniden", self.kucuk, BEYAZ, (ALAN.x + 610, ALAN.bottom + 31))

    def yilan_ciz(self):
        noktalar = [self.kare(p).center for p in self.yilan]
        govde, golge = (188, 72, 224), (115, 35, 145)
        kalinlik = KARE - 4
        for renk, kayma in ((golge, (3, 4)), (govde, (0, 0))):
            ciz = [(x + kayma[0], y + kayma[1]) for x, y in noktalar]
            for a, b in zip(ciz, ciz[1:]):
                pygame.draw.line(self.ekran, renk, a, b, kalinlik)
            for p in ciz:
                pygame.draw.circle(self.ekran, renk, p, kalinlik // 2)

        dx, dy = self.yon
        px, py = -dy, dx
        hx, hy = noktalar[0]
        goz = (hx + dx * 7 + px * 7, hy + dy * 7 + py * 7)
        pygame.draw.circle(self.ekran, (25, 25, 28), goz, 7)
        pygame.draw.circle(self.ekran, (245, 245, 245), (goz[0] - px * 2 - dx * 2, goz[1] - py * 2 - dy * 2), 2)
        dil_bas = (hx + dx * (KARE // 2 - 1), hy + dy * (KARE // 2 - 1))
        dil_uc = (hx + dx * (KARE // 2 + 13), hy + dy * (KARE // 2 + 13))
        pygame.draw.line(self.ekran, (238, 70, 72), dil_bas, dil_uc, 4)
        pygame.draw.line(self.ekran, (238, 70, 72), dil_uc, (dil_uc[0] + px * 6 - dx * 4, dil_uc[1] + py * 6 - dy * 4), 3)
        pygame.draw.line(self.ekran, (238, 70, 72), dil_uc, (dil_uc[0] - px * 6 - dx * 4, dil_uc[1] - py * 6 - dy * 4), 3)

    def sonuc_ciz(self):
        klasor = "Won" if self.durum == "kazandin" else "Lost"
        self.kutu((0, 0, W, H), 130)
        modal = self.a.al("Levels", klasor, "ui_modal_bg_green.png" if klasor == "Won" else "ui_modal_bg_red.png")
        r = modal.get_rect(center=(W // 2, H // 2))
        self.ekran.blit(modal, r)
        baslik_renk = (32, 115, 72) if klasor == "Won" else (165, 34, 54)
        self.yazi("Kazandın" if klasor == "Won" else "Kaybettin", self.buyuk, baslik_renk, (W // 2, r.y + 115))
        self.yazi(f"Skor: {self.puan}", self.font, (45, 45, 55), (W // 2, r.y + 178))
        self.result_main = pygame.Rect(W // 2 - 210, r.bottom - 92, 198, 64)
        self.result_action = pygame.Rect(W // 2 + 18, r.bottom - 92, 198, 64)
        self.buton_resimli(self.result_main, ("Levels", klasor, "btn_bg_gray.png"), None, "Level Menü")
        btn = "btn_bg_pink.png" if klasor == "Won" else "btn_bg_red.png"
        yazi = "Sonraki" if klasor == "Won" else "Tekrar"
        self.buton_resimli(self.result_action, ("Levels", klasor, btn), None, yazi)

    def ayarlar_ciz(self):
        self.kutu((0, 0, W, H), 130)
        modal = self.a.al("Settings", "ui_modal_bg.png")
        r = modal.get_rect(center=(W // 2, H // 2))
        self.ekran.blit(modal, r)
        self.yazi("Ayarlar", self.buyuk, (115, 42, 145), (W // 2, r.y + 92))
        self.yazi(f"Ses: {'Açık' if self.ses_acik else 'Kapalı'}", self.font, (55, 55, 65), (W // 2, r.y + 145))
        self.yazi(f"Müzik: %{int(self.muzik_ses * 100)}", self.font, (55, 55, 65), (W // 2, r.y + 195))
        self.volume_down = pygame.Rect(W // 2 - 190, r.y + 168, 64, 54)
        self.volume_up = pygame.Rect(W // 2 + 126, r.y + 168, 64, 54)
        self.settings_save = pygame.Rect(W // 2 - 165, r.bottom - 76, 150, 58)
        self.settings_close = pygame.Rect(W // 2 + 15, r.bottom - 76, 150, 58)
        self.buton_resimli(self.volume_down, ("Settings", "btn_bg_red.png"), None, "-")
        self.buton_resimli(self.volume_up, ("Settings", "btn_bg_green.png"), None, "+")
        self.buton_resimli(self.settings_save, ("Settings", "btn_bg_green.png"), None, "Değiştir")
        self.buton_resimli(self.settings_close, ("Settings", "btn_bg_red.png"), None, "Kapat")

    def cikis_ciz(self):
        self.kutu((0, 0, W, H), 130)
        modal = self.a.al("Quit", "ui_modal_bg.png")
        r = modal.get_rect(center=(W // 2, H // 2))
        self.ekran.blit(modal, r)
        self.yazi("Çıkmak istiyor musun?", self.buyuk, (45, 45, 55), (W // 2, r.y + 125))
        self.quit_yes = pygame.Rect(W // 2 - 220, r.bottom - 115, 200, 72)
        self.quit_no = pygame.Rect(W // 2 + 20, r.bottom - 115, 200, 72)
        self.buton_resimli(self.quit_yes, ("Quit", "btn_bg_green.png"), ("Quit", "icon_check.png"), "Evet")
        self.buton_resimli(self.quit_no, ("Quit", "btn_bg_red.png"), ("Quit", "icon_cross_white.png"), "Hayır")

    def buton_resimli(self, rect, bg, ikon, metin):
        self.ekran.blit(self.a.al(*bg, boyut=rect.size), rect)
        if ikon:
            self.ekran.blit(self.a.al(*ikon, boyut=(32, 32)), (rect.x + 25, rect.y + 20))
            x = rect.centerx + 18
        else:
            x = rect.centerx
        self.yazi(metin, self.font, BEYAZ, (x, rect.centery))

    def kutu(self, rect, alpha):
        s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        s.fill((0, 0, 0, alpha))
        self.ekran.blit(s, rect[:2])

    def yazi(self, metin, font, renk, merkez):
        img = font.render(metin, True, renk)
        self.ekran.blit(img, img.get_rect(center=merkez))

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
