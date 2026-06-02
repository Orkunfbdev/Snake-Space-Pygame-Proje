import sys
from pathlib import Path
import pygame
KOK = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))

# Pencere, FPS ve oyun alaninin grid ayarlari.
W, H, FPS = 1000, 760, 120
KARE, SUTUN, SATIR, SON_LEVEL = 30, 30, 20, 10
ALAN = pygame.Rect(50, 120, SUTUN * KARE, SATIR * KARE)

# Oyunda kullanilan temel renkler.
BEYAZ, KOYU, MOR = (245, 240, 255), (8, 7, 18), (95, 36, 150)
PEMBE, SARI, MAVI = (224, 75, 240), (255, 216, 92), (48, 150, 225)

# Resmi yukler, gerekirse boyutlandirir. renk_sil=True ise ilk pikseli arka plan rengi sayar.
def resim(ad, boyut=None, renk_sil=False):
    img = pygame.image.load(str(KOK / ad))
    if renk_sil: img = img.convert(); img.set_colorkey(img.get_at((0, 0)))
    img = img.convert_alpha()
    return pygame.transform.scale(img, boyut) if boyut else img

# Saniyeyi 00:00 formatinda yazar.
def sure_yaz(s):
    s = int(s); return f"{s // 60:02d}:{s % 60:02d}"
