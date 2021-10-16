#Server
from netvars import setNetVar, getNetVar, initNet
from machine import ADC, Pin, PWM
from time import sleep, time
import bluetooth, config, json, re

def IRQ_button(pin):
    start_time = time()
    while not pin.value():
        pass
    time_diff = time() - start_time
    
    if time_diff <= 3:
        print("short press")
        send_selection()
        #normal press - selection
    elif time_diff <= 5:
        print("long press")
        shutdown()
        #long press - shutdown
    elif time_diff >= 6:
        print("longest press")
        reset_game()
        #longest press - reset game

def shutdown():
    global standby_mode
    if standby_mode:
        standby_mode = False
        send_game()
    else:
        standby_mode = True
        send_game()

def reset_game():
    global gameMap
    gameMap = [[[0 for k in range(5)] for j in range(5)] for i in range(5)]
    send_game()

def send_cursor():
    global cursor
    print(cursor[0])
    print(cursor[1])
    print(cursor[2])

def send_selection():
    global cursor, gameMap
    xCurs = cursor[0]
    yCurs = cursor[1]
    zCurs = cursor[2]
    
    if gameMap[xCurs][yCurs][zCurs] != 0:
        #yellow flashing
        pass
    else:
        gameMap[xCurs][yCurs][zCurs] = player_ID
        #dirs to check x +-, y +-, z+-
        for i in range(-1,2):
            for j in range(-1,2):
                for k in range(-1,2):
                    neighbor = gameMap[min(4, max(0, xCurs + i))][min(4, max(0,yCurs + j))][min(4, max(0,zCurs + k))]
                    if not neighbor in [-1, 0, player_ID]:
                        gameMap[min(4, max(0, xCurs + i))][min(4, max(0,yCurs + j))][min(4, max(0,zCurs + k))] = player_ID
        send_game()
                        

def send_game():
    global standby_mode
    if standby_mode:
        darkMap = [[[-1 for k in range(5)] for j in range(5)] for i in range(5)]
        #send dark map
    else:
        #send game Map
        pass
    
#Space holder for BLE crap




#

#system control
standby_mode = False

#controls
button = Pin(4, Pin.IN, Pin.PULL_UP)  #not pressed value = 1, pressed = 0
button.irq(trigger=Pin.IRQ_FALLING, handler=IRQ_button)
joystick_x = ADC(Pin(35)) #left_max x = 4095, right_max x = 0, Nullpunkt bei [1900,2300]; joystick physically flipped -> cable leave on the right, model name on the top left (upside down)
joystick_x.atten(ADC.ATTN_11DB)
joystick_y = ADC(Pin(34)) #top_max y = 4095, down_max y = 0, Nullpunk bei [1900, 2300]
joystick_y.atten(ADC.ATTN_11DB)
joystick_button = Pin(25,Pin.IN, Pin.PULL_UP)
active_side = 1

#wifi
ssid = config.ssid
password = config.pw #change for other player ##TODO
initNet(ssid, password)

#server variable
key = "ColorCube_GameVar" 
setNetVar(key, 4031)  ##TODO

#game variables
own_turn = False
player_ID = 1
cursor = [-1,-1,-1]
gameMap = [[[0 for k in range(5)] for j in range(5)] for i in range(5)]

try:
    data = open("data.json", "r+")
    gameMap = json.loads(data.read())
    data.close()
    print("loading map")
except:
    print("loading of map failed")
    print("creating map file")
    try:
        data = open("data.json", "w")
        data.write(json.dumps(gameMap))
        data.close()
    except:
        print("all failed")

send_game()

while True:
    if own_turn:
        #gameloop
        while own_turn:
            if cursor[0] == -1 or cursor[1] ==-1 or cursor[2] == -1:
                cursor = [3,3,0]
            #send to cube
            x = joystick_x.read()-2048 #move zeropoint to 0,0
            y = joystick_y.read()-2048
            print("XXXX : " + str(x) + " - " + str(joystick_x.read()))
            print("YYYY : " + str(y) + " - " + str(joystick_y.read()))
            #sleep(0.3)
            #continue
        
            if x > 150 or y > 150:
                if abs(x)-abs(y) >= 0:
                    if active_side == 1:
                        if cursor[0] == 0:
                            cursor[2] +=1
                            active_side = 4
                            send_cursor()
                        else:
                            cursor[0] -=1
                            send_cursor()
                            #left
                            
                    elif active_side == 2:
                        if cursor[2] == 0:
                            cursor[0] +=1
                            active_side = 1
                            send_cursor()
                        else:
                            cursor[2] -=1
                            send_cursor()
                            #left
                            
                    elif active_side == 3:
                        if cursor[0] == 0:
                            cursor[1] -=1
                            active_side = 4
                            send_cursor()
                        else:
                            cursor[0] -=1
                            send_cursor()
                            #left
                            
                    elif active_side == 4:
                        if cursor[2] == 4:
                            cursor[0] +=1
                            active_side = 6
                            send_cursor()
                        else:
                            cursor[2] +=1
                            send_cursor()
                            #left
                    
                    elif active_side == 5:
                        if cursor[0] == 0:
                            cursor[1] +=1
                            active_side = 4
                            send_cursor()
                        else:
                            cursor[0] -=1
                            send_cursor()
                            #left
                            
                    elif active_side == 6:
                        if cursor[0] == 4:
                            cursor[2] -=1
                            active_side = 2
                            send_cursor()
                        else:
                            cursor[0] +=1
                            send_cursor()
                            #left
                            
                else:
                    if active_side == 1:
                        if cursor[1] == 4:
                            cursor[2] +=1
                            active_side = 3
                            send_cursor()
                        else:
                            cursor[1] += 1
                            send_cursor()
                            #up
                            
                    elif active_side == 2:
                        if cursor[1] == 4:
                            cursor[0] -=1
                            active_side = 3
                            send_cursor()
                        else:
                            cursor[1] += 1
                            send_cursor()
                            #up
                            
                    elif active_side == 3:
                        if cursor[2] == 4:
                            cursor[1] -=1
                            active_side = 6
                            send_cursor()
                        else:
                            cursor[2] += 1
                            send_cursor()
                            #up
                            
                    elif active_side == 4:
                        if cursor[1] == 4:
                            cursor[0] +=1
                            active_side = 3
                            send_cursor()
                        else:
                            cursor[1] += 1
                            send_cursor()
                            #up
                            
                    elif active_side == 5:
                        if cursor[2] == 0:
                            cursor[1] +=1
                            active_side = 1
                            send_cursor()
                        else:
                            cursor[2] -= 1
                            send_cursor()
                            #up
                              
                    elif active_side == 6:
                        if cursor[1] == 0:
                            cursor[2] -=1
                            active_side = 5
                            send_cursor()
                        else:
                            cursor[1] -= 1
                            send_cursor()
                            #up
                        
            elif x < -150 or y < -150:
                if abs(x)-abs(y) >= 0:
                    if active_side == 1:
                        if cursor[0] == 4:
                            cursor[2] +=1
                            active_side = 2
                            send_cursor()
                        else:
                            cursor[0] +=1
                            send_cursor()
                            #right
                            
                    elif active_side == 2:
                        if cursor[2] == 4:
                            cursor[0] -=1
                            active_side = 6
                            send_cursor()
                        else:
                            cursor[2] +=1
                            send_cursor()
                            #right
                            
                    elif active_side == 3:
                        if cursor[0] == 4:
                            cursor[1] -=1
                            active_side = 2
                            send_cursor()
                        else:
                            cursor[0] +=1
                            send_cursor()
                            #right
                            
                    elif active_side == 4:
                        if cursor[2] == 0:
                            cursor[0] +=1
                            active_side = 1
                            send_cursor()
                        else:
                            cursor[2] -=1
                            send_cursor()
                            #right
                    
                    elif active_side == 5:
                        if cursor[0] == 0:
                            cursor[1] +=1
                            active_side = 4
                            send_cursor()
                        else:
                            cursor[0] -=1
                            send_cursor()
                            #right
                                                
                    elif active_side == 6:
                        if cursor[0] == 0:
                            cursor[2] -=1
                            active_side = 4
                            send_cursor()
                        else:
                            cursor[0] -=1
                            send_cursor()
                            #right
                    
                else:
                    if active_side == 1:
                        if cursor[1] == 0:
                            cursor[2] +=1
                            active_side = 5
                            send_cursor()
                        else:
                            cursor[1] -=1
                            send_cursor()
                            #down
                    
                    elif active_side == 2:
                        if cursor[1] == 0:
                            cursor[0] -=1
                            active_side = 5
                            send_cursor()
                        else:
                            cursor[1] -=1
                            send_cursor()
                            #down
                            
                    elif active_side == 3:
                        if cursor[2] == 0:
                            cursor[1] -=1
                            active_side = 1
                            send_cursor()
                        else:
                            cursor[2] -=1
                            send_cursor()
                            #down
                            
                    elif active_side == 4:
                        if cursor[1] == 0:
                            cursor[0] +=1
                            active_side = 5
                            send_cursor()
                        else:
                            cursor[1] -=1
                            send_cursor()
                            #down
                            
                    elif active_side == 5:
                        if cursor[2] == 4:
                            cursor[1] +=1
                            active_side = 6
                            send_cursor()
                        else:
                            cursor[2] +=1
                            send_cursor()
                            #down
                    
                    elif active_side == 6:
                        if cursor[1] == 4:
                            cursor[2] -=1
                            active_side = 3
                            send_cursor()
                        else:
                            cursor[1] +=1
                            send_cursor()
                            #down
            sleep(0.5)
            
    else:
        gameVar = getNetVar("ColorCube_GameVar")
        if re.match(re.compile("...1"),gameVar): #change for other player ##TODO
            own_turn = True        
        else:

            sleep(1)   #set to 150 := 2.5 minutes ##TODO
