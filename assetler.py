import sys
from pathlib import Path

import pygame


KOK = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
GUI = KOK / "SnakeSpaceGUI"


class Assetler:
    def __init__(self):
        self.cache = {}

    def al(self, *parca, boyut=None):
        anahtar = (parca, boyut)
        if anahtar not in self.cache:
            yol = GUI.joinpath(*parca)
            img = pygame.image.load(str(yol)).convert_alpha()
            if boyut:
                img = pygame.transform.smoothscale(img, boyut)
            self.cache[anahtar] = img
        return self.cache[anahtar]

    def level(self, no, dosya, boyut=None):
        return self.al("Levels", f"Level {no}", dosya, boyut=boyut)

    def region(self, no, dosya, boyut=None):
        return self.al("Level Menus", f"Region {no}", dosya, boyut=boyut)

    def fixed(self, dosya, boyut=None):
        return self.al("Level Menus", "Region Fixed", dosya, boyut=boyut)

    def global_(self, dosya, boyut=None):
        return self.al("Levels", "Global", dosya, boyut=boyut)
