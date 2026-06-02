import random, time, pygame
from ayarlar import *

class Oyun:
    def __init__(self):
        # Pygame, pencere, fontlar ve gorseller burada hazirlaniyor.
        pygame.init(); pygame.display.set_caption("Snake Space"); pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN])
        self.ekran = pygame.display.set_mode((W, H), pygame.DOUBLEBUF)
        self.saat = pygame.time.Clock()
        self.font, self.kucuk = pygame.font.SysFont("arial", 22, bold=True), pygame.font.SysFont("arial", 17)
        self.buyuk = pygame.font.SysFont("arial", 58, bold=True)
        self.elma, self.kapi = resim("apple.png", (KARE, KARE)), resim("20251125compass.png", (KARE + 34, KARE + 34))
        self.menu_yilan, self.kafa_yon = resim("preview.png", (156, 132), True), self.kafa_hazirla()
        self.durum, self.level, self.puan, self.rekor = "menu", 1, 0, 0
        self.kazandi = False; self.baslama = time.time(); self.level_kur()
    def kafa_hazirla(self):
        # preview.png icinden yilan kafasini kesip dort yone cevirir.
        img = resim("preview.png", (156, 132), True)
        kafa = pygame.Surface((74, 92), pygame.SRCALPHA)
        kafa.blit(img, (0, 0), pygame.Rect(0, 18, 74, 92))
        kafa = pygame.transform.scale(kafa, (KARE + 16, KARE + 16))
        return {(1, 0): pygame.transform.rotate(kafa, -90), (0, -1): kafa,
                (-1, 0): pygame.transform.rotate(kafa, 90), (0, 1): pygame.transform.rotate(kafa, 180)}
    def yeni_oyun(self):
        # Skoru ve leveli sifirlayip oyunu bastan baslatir.
        self.level, self.puan, self.kazandi = 1, 0, False
        self.baslama = time.time(); self.level_kur(); self.durum = "oyun"
    def level_kur(self):
        # Her level basinda yilan, yon, elma, engel ve kapi bilgileri yenilenir.
        self.yilan = [(7, 10), (6, 10), (5, 10)]
        self.yon = self.sonraki = (1, 0)
        self.toplanan, self.kapi_acik = 0, False
        self.kapi_yeri = (SUTUN - 3, SATIR - 3)
        self.son_hareket = pygame.time.get_ticks()
        self.engeller = self.engel_uret()
        self.elma_yeri = None
        self.elma_uret()
    def hedef(self):
        # 1. level 3 elma; 2. level 5 elma; sonra her levelde 3 artar.
        return 3 if self.level == 1 else 5 + (self.level - 2) * 3
    def hiz(self):
        # Level arttikca bekleme suresi azalir, yani yilan hizlanir.
        return max(50, 105 - self.level * 6)
    def engel_uret(self):
        # Engeller level sayisina gore rastgele ama baslangic ve kapiya gelmeyecek sekilde uretilir.
        rnd, engel = random.Random(self.level * 50), set()
        yasak = set(self.yilan) | {self.kapi_yeri}
        while len(engel) < 3 + self.level * 4:
            yer = (rnd.randrange(2, SUTUN - 2), rnd.randrange(3, SATIR - 2))
            if yer not in yasak:
                engel.add(yer)
        if self.level >= 5:
            bos = rnd.randrange(7, SUTUN - 7)
            engel |= {(x, 5) for x in range(5, SUTUN - 5) if abs(x - bos) > 1}
        return engel
    def elma_uret(self):
        # Leveldeki elmalar bittiyse kapi acilir; bitmediyse bos bir kareye yeni elma gelir.
        if self.toplanan >= self.hedef():
            self.elma_yeri, self.kapi_acik = None, True
            return
        dolu = set(self.yilan) | self.engeller | {self.kapi_yeri}
        bos = [(x, y) for x in range(SUTUN) for y in range(SATIR) if (x, y) not in dolu]
        self.elma_yeri = random.choice(bos)
        self.elma_zamani = time.time()
    def olaylar(self):
        # Klavye ve pencere kapatma olaylari burada okunur.
        degisti = False
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if e.type == pygame.KEYDOWN:
                degisti = self.tus(e.key) or degisti
        return degisti
    def tus(self, t):
        # Menu/game over ekraninda oyunu baslatir; oyun sirasinda yon degistirir.
        if self.durum in ("menu", "bitti") and t in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_r):
            self.yeni_oyun()
            return True
        elif self.durum == "oyun":
            yonler = {pygame.K_w: (0, -1), pygame.K_UP: (0, -1), pygame.K_s: (0, 1),
                      pygame.K_DOWN: (0, 1), pygame.K_a: (-1, 0), pygame.K_LEFT: (-1, 0),
                      pygame.K_d: (1, 0), pygame.K_RIGHT: (1, 0)}
            if t in yonler and yonler[t] != (-self.yon[0], -self.yon[1]):
                self.sonraki = yonler[t]
                return True
            elif t == pygame.K_r:
                self.yeni_oyun()
                return True
            elif t == pygame.K_ESCAPE:
                self.durum = "menu"
                return True
        return False
    def guncelle(self):
        # Yilan belli araliklarla bir kare ilerler; elma, carpma ve kapi kontrolleri burada yapilir.
        if self.durum != "oyun" or pygame.time.get_ticks() - self.son_hareket < self.hiz():
            return False
        self.son_hareket, self.yon = pygame.time.get_ticks(), self.sonraki
        x, y = self.yilan[0]
        bas = (x + self.yon[0], y + self.yon[1])
        if self.carpti(bas):
            self.rekor = max(self.rekor, self.puan)
            self.durum = "bitti"
            return True
        self.yilan.insert(0, bas)
        self.elma_topla() if bas == self.elma_yeri else self.yilan.pop()
        if self.kapi_acik and bas == self.kapi_yeri:
            self.level += 1
            self.kazandi = self.level > SON_LEVEL
            self.durum = "bitti" if self.kazandi else "oyun"
            self.rekor = max(self.rekor, self.puan)
            if not self.kazandi:
                self.level_kur()
        return True
    def carpti(self, yer):
        # Duvara, engele veya kendi govdesine carpma kontrolu.
        x, y = yer
        return x < 0 or y < 0 or x >= SUTUN or y >= SATIR or yer in self.engeller or yer in self.yilan[:-1]
    def elma_topla(self):
        # Elma ne kadar hizli alinirsa puan o kadar yuksek olur.
        gecen = time.time() - self.elma_zamani
        self.puan += max(10, int(120 + self.level * 15 - gecen * (7 + self.level)))
        self.toplanan += 1
        self.elma_uret()
    def kare(self, yer):
        # Grid koordinatini ekrandaki piksel dikdortgenine cevirir.
        return pygame.Rect(ALAN.x + yer[0] * KARE, ALAN.y + yer[1] * KARE, KARE, KARE)
    def ciz(self):
        # Duruma gore menu, oyun veya game over ekrani cizilir.
        self.ekran.fill(KOYU)
        if self.durum == "menu":
            self.menu_ciz()
        else:
            self.oyun_ciz()
            if self.durum == "bitti":
                self.bitti_ciz()
    def menu_ciz(self):
        # Ana menu ekrani.
        self.yazi("SNAKE", self.buyuk, PEMBE, (W // 2 - 45, 215))
        self.yazi("SPACE", self.buyuk, SARI, (W // 2 - 45, 280))
        self.ekran.blit(self.menu_yilan, self.menu_yilan.get_rect(center=(W // 2 + 175, 255)))
        self.yazi("W A S D ile yon degistir, elmalari topla, kapiya gir.", self.kucuk, BEYAZ, (W // 2, 375))
        self.buton(pygame.Rect(W // 2 - 115, 480, 230, 56), "Oyuna Basla")
        self.yazi(f"En yuksek skor: {self.rekor}", self.kucuk, (205, 190, 230), (W // 2, 560))
    def oyun_ciz(self):
        # Harita, engeller, elma, kapi ve yilan burada cizilir.
        self.hud()
        pygame.draw.rect(self.ekran, (14, 13, 31), ALAN)
        pygame.draw.rect(self.ekran, MOR, ALAN, 2)
        for e in self.engeller:
            pygame.draw.rect(self.ekran, (68, 68, 96), self.kare(e).inflate(-4, -4))
        if self.kapi_acik:
            r = self.kare(self.kapi_yeri)
            self.ekran.blit(self.kapi, self.kapi.get_rect(center=r.center))
        if self.elma_yeri:
            self.ekran.blit(self.elma, self.kare(self.elma_yeri))
        self.yilan_ciz()
    def hud(self):
        # Ustteki level, puan, elma ve sure yazilari.
        yazilar = [f"Level {self.level}/{SON_LEVEL}", f"Puan {self.puan}",
                   f"Elma {self.toplanan}/{self.hedef()}", sure_yaz(time.time() - self.baslama)]
        for i, yazi in enumerate(yazilar):
            self.yazi(yazi, self.font, BEYAZ, (135 + i * 210, 62))
        self.yazi("ESC menu   R yeniden", self.kucuk, (210, 200, 230), (ALAN.right - 86, 105))
    def yilan_ciz(self):
        # Govde cizgiyle, kafa ise hazir yilan gorseliyle cizilir.
        n = [self.kare(p).center for p in self.yilan]
        if len(n) > 1:
            pygame.draw.lines(self.ekran, MAVI, False, n, KARE - 9)
        for p in n[1:]:
            pygame.draw.circle(self.ekran, (82, 180, 240), p, 7)
        kafa = self.kafa_yon.get(self.yon)
        self.ekran.blit(kafa, kafa.get_rect(center=n[0]))
    def bitti_ciz(self):
        # Kaybetme veya kazanma ekrani.
        pygame.draw.rect(self.ekran, (110, 28, 65), (310, 275, 380, 210), border_radius=12)
        self.yazi("Kazandin" if self.kazandi else "Kaybettin", self.font, BEYAZ, (W // 2, 325))
        self.yazi(f"Skor: {self.puan}", self.font, SARI, (W // 2, 375))
        self.buton(pygame.Rect(W // 2 - 105, H // 2 + 30, 210, 46), "Yeniden Basla")
    def buton(self, r, yazi):
        # Basit buton cizimi.
        pygame.draw.rect(self.ekran, (170, 60, 210), r, border_radius=12)
        pygame.draw.rect(self.ekran, PEMBE, r, 2, border_radius=12)
        self.yazi(yazi, self.font, BEYAZ, r.center)
    def yazi(self, metin, font, renk, merkez):
        # Metni verilen merkeze hizalayarak ekrana basar.
        img = font.render(metin, True, renk)
        self.ekran.blit(img, img.get_rect(center=merkez))
    def calistir(self):
        # Ana oyun dongusu: olaylari oku, oyunu guncelle, gerekiyorsa ekrani yeniden ciz.
        self.ciz()
        pygame.display.flip()
        son_sure = -1
        while True:
            degisti = self.olaylar() or self.guncelle()
            sure = int(time.time() - self.baslama)
            if self.durum == "oyun" and sure != son_sure:
                son_sure = sure
                degisti = True
            if degisti:
                self.ciz()
                pygame.display.flip()
            self.saat.tick(FPS)
