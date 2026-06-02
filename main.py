import sys, pygame
from oyun import Oyun

# Oyunu olusturur ve normal calistirma/test calistirmasini ayirir.
o = Oyun()
if "--smoke-test" in sys.argv: o.ciz(); pygame.display.flip(); pygame.quit()
else: o.calistir()
