import sys, pygame
from oyun import Oyun

# Oyun nesnesini oluşturur.
o = Oyun()

# EXE kontrolünde yalnızca bir kare çizer; normal açılışta ana döngüyü başlatır.
if "--smoke-test" in sys.argv: o.ciz(); pygame.display.flip(); pygame.quit()
else: o.calistir()
