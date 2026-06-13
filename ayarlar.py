import pygame

# Ekran, oyun alanı ve seviye sınırları.
W, H, FPS = 1280, 800, 120
KARE, SUTUN, SATIR, SON_LEVEL = 32, 34, 16, 20
ALAN = pygame.Rect((W - SUTUN * KARE) // 2, 176, SUTUN * KARE, SATIR * KARE)

# Arayüzde ortak kullanılan renkler.
BEYAZ = (245, 240, 255)
KOYU = (10, 8, 25)
PEMBE = (218, 77, 239)
MOR = (95, 45, 145)
SARI = (255, 220, 80)
GOLGE = (0, 0, 0, 150)


# Saniyeyi ekranda gösterilen dakika:saniye biçimine çevirir.
def sure_yaz(saniye):
    saniye = int(saniye)
    return f"{saniye // 60:02d}:{saniye % 60:02d}"
