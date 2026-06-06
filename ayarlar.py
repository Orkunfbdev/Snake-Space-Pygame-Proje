import pygame

W, H, FPS = 1280, 800, 120
KARE, SUTUN, SATIR, SON_LEVEL = 32, 28, 16, 20
ALAN = pygame.Rect((W - SUTUN * KARE) // 2, 200, SUTUN * KARE, SATIR * KARE)

BEYAZ = (245, 240, 255)
KOYU = (10, 8, 25)
PEMBE = (218, 77, 239)
MOR = (95, 45, 145)
SARI = (255, 220, 80)
GOLGE = (0, 0, 0, 150)


def sure_yaz(saniye):
    saniye = int(saniye)
    return f"{saniye // 60:02d}:{saniye % 60:02d}"
