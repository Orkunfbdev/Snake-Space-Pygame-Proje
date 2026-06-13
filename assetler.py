import sys
from pathlib import Path

import pygame


# PyInstaller ile açıldığında geçici klasörü, Python ile açıldığında proje klasörünü kullanır.
KOK = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
GUI = KOK / "SnakeSpaceGUI"


# Projedeki bütün görsellerin yüklenmesini ve önbelleğe alınmasını yönetir.
class Assetler:
    # Yüklenen görselleri bellekte tutarak aynı dosyanın tekrar yüklenmesini önler.
    def __init__(self):
        self.cache = {}

    # Verilen klasör yolundaki resmi yükler ve istenirse belirtilen boyuta getirir.
    def al(self, *parca, boyut=None):
        anahtar = (parca, boyut)
        if anahtar not in self.cache:
            yol = GUI.joinpath(*parca)
            img = pygame.image.load(str(yol)).convert_alpha()
            if boyut:
                img = pygame.transform.smoothscale(img, boyut)
            self.cache[anahtar] = img
        return self.cache[anahtar]

    # Seçili level klasöründen görsel getirir.
    def level(self, no, dosya, boyut=None):
        return self.al("Levels", f"Level {no}", dosya, boyut=boyut)

    # Seçili bölgenin level menüsü görselini getirir.
    def region(self, no, dosya, boyut=None):
        return self.al("Level Menus", f"Region {no}", dosya, boyut=boyut)

    # Bütün bölge menülerinde ortak kullanılan görselleri getirir.
    def fixed(self, dosya, boyut=None):
        return self.al("Level Menus", "Region Fixed", dosya, boyut=boyut)

    # Bütün oyun seviyelerinde ortak kullanılan görselleri getirir.
    def global_(self, dosya, boyut=None):
        return self.al("Levels", "Global", dosya, boyut=boyut)
