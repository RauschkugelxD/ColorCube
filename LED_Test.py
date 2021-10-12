import machine, neopixel
import time

number_led = 25

np1 = neopixel.NeoPixel(machine.Pin(4), number_led)
np2 = neopixel.NeoPixel(machine.Pin(5), number_led)
np3 = neopixel.NeoPixel(machine.Pin(18), number_led)
np4 = neopixel.NeoPixel(machine.Pin(19), number_led)
np5 = neopixel.NeoPixel(machine.Pin(21), number_led)
np6 = neopixel.NeoPixel(machine.Pin(23), number_led)

np1.fill((255,0,0))
np1.write()
time.sleep(1)

#np2.fill((255,0,0))
#np2.write()
#time.sleep(1)

#np3.fill((255,0,0))
#np3.write()
#time.sleep(1)

#np4.fill((255,0,0))
#np4.write()
#time.sleep(1)

#np5.fill((255,0,0))
#np5.write()
#time.sleep(1)


#np6.fill((255,0,0))
#np6.write()
#time.sleep(1)
np2.fill((0,0,0))
np2.write()
np3.fill((0,0,0))
np3.write()
np4.fill((0,0,0))
np4.write()
np5.fill((0,0,0))
np5.write()
np6.fill((0,0,0))
np6.write()