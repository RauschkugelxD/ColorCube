#Client
# Missing values (i.e. Pin numbers) are marked with //
from netvars import setNetVar, getNetVar, initNet
from machine import Pin, PWM
from micropython import const
from time import sleep, time
import bluetooth, neopixel


#LEDs
#Overall there are 98 LEDs

led_5x5_1 = neopixel.NeoPixel(machine.Pin(//), 25) #0-24
led_3x5_1 = neopixel.NeoPixel(machine.Pin(//), 15) #25-39
led_3x3_1 = neopixel.NeoPixel(machine.Pin(//), 9) #40-48
led_3x5_2 = neopixel.NeoPixel(machine.Pin(//), 15) #49-63
led_3x3_2 = neopixel.NeoPixel(machine.Pin(//), 9) #64-72
led_5x5_2 = neopixel.NeoPixel(machine.Pin(//), 25) #73-97

#Color Constants

COLORCUBE_DARK = const((0,0,0)) #standby mode, map-code = -1
COLORCUBE_RED = const((255,0,0)) #player 1, map-code = 1
COLORCUBE_GREEN = const((0,255,0)) #cursor,
COLORCUBE_BLUE = const((0,0,255)) #player 2, map-code = 2
COLORCUBE_YELLOW = const((255,255,0)) #impossible selection, 
COLORCUBE_WHITE = const((255,255,255)) #unoccupied, map-code = 0


all_led = []
#initialize matrix
led_matrix = [[[0 for k in range(5)] for j in range(5)] for i in range(5)]

for i in range(0,98):
    if i < 25:
        all_led.append(led_5x5_1[i])        
    elif i < 40:
        all_led.append(led_3x5_1[i])
    elif i < 49:
        all_led.append(led_3x3_1[i])
    elif i < 64:
        all_led.append(led_3x5_2[i])
    elif i < 73:
        all_led.append(led_3x3_2[i])
    else: #i < 98
        all_led.append(led_5x5_2[i])
        
        
        
for i in range (0,len(all_led())):
    #5x5_1 physically starts at the coordinates (0,4,0) going to (4,4,0) -> (4,3,0) to (0,3,0) -> (0,2,0) to (4,2,0) > (4,1,0) to (0,1,0) -> (0,0,0) to (4,0,0)
    if i < 25:
        if i < 5:
            led_matrix[i][4][0] = all_led[i]
        elif i < 10:
            led_matrix[9-i][3][0] = all_led[i]
        elif i < 15:
            led_matrix[i%5][2][0] = all_led[i]
        elif i < 20:
            led_matrix[19-i][1][0] = all_led[i]
        else: #i<25
            led_matrix[i%5][0][0] = all_led[i]
    
    elif i < 40:
        #3x5_1 physically starts at the coordinates (4,4,1) to (4,0,1) -> (4,0,2) to (4,4,2) -> (4,4,3) to (4,0,3)
        if i < 30:
            led_matrix[4][29-i][1] = all_led[i]
        elif i < 35:
            led_matrix[4][i%5][2] = all_led[i]
        else: #i <40
            led_matrix[4][39-i][3] = all_led[i]
    
    elif i < 49:
        #3x3_1 physically starts at the coordinates (1,4,3) to (3,4,3) -> (3,4,2) to (1,4,2) -> (1,4,1) to (3,4,1)
        if i < 43:
            led_matrix[(i+1)%4][4][3] = all_led[i]
        elif i < 46:
            led_matrix[46-i][4][2] = all_led[i]
        else: #i < 49
            led_matrix[(i+3)%4][4][1] = all_led[i]
    
    elif i < 64:
        #3x5_2 physically starts at the coordinates (0,0,3) to (0,4,3) -> (0,4,2) to (0,0,2) -> (0,0,1) to (0,4,1)
        if i < 54:
            led_matrix[0][(i+1)%5][3] = all_led[i]
        elif i < 59:
            led_matrix[0][58-i][2] = all_led[i]            
        else: #i<64
            led_matrix[0][(i+1)%5][2] = all_led[i]
            
    elif i < 73:
        #3x3_2 physically starts at the coordinates (1,0,1) to (1,0,3) -> (2,0,3) to (2,0,1) -> (3,0,1) to (3,0,3)
        if i < 67:
            led_matrix[1][0][(i+1)%4] = all_led[i]
        elif i < 70:
            led_matrix[2][0][70-i] = all_led[i]
        else: #i<73
            led_matrix[3][0][(i-1)%4] = all_led[i]
    
    else: #i< 98
        #5x5_2 physically starts at the coordinates (0,4,4) going to (4,4,4) -> (4,3,4) to (0,3,4) -> (0,2,4) to (4,2,4) > (4,1,4) to (0,1,4) -> (0,0,4) to (4,0,4)
        if i < 78:
            led_matrix[(i+2)%5][4][4] = all_led[i]
        elif i < 83:
            led_matrix[82-i][3][4] = all_led[i]
        elif i < 88:
            led_matrix[(i+2)%5][2][4] = all_led[i]
        elif i < 93:
            led_matrix[92-i][1][4] = all_led[i]
        else: #i<98
            led_matrix[(i+2)%5][0][4] = all_led[i]
            




def startup_anim():
    for