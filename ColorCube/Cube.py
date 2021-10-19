#Client
# Missing values (i.e. Pin numbers) are marked with //
from ble_advertising import advertising_payload
from netvars import setNetVar, getNetVar, initNet
from machine import Pin, PWM, Timer
from micropython import const
from time import sleep, time
import bluetooth, json, micropython, neopixel, random, struct

#BLE STUFF
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_FLAG_READ = const(0x0002)
_FLAG_WRITE_NO_RESPONSE = const(0x0004)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (
    bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_READ | _FLAG_NOTIFY,
)
_UART_RX = (
    bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_WRITE | _FLAG_WRITE_NO_RESPONSE,
)
_UART_SERVICE = (
    _UART_UUID,
    (_UART_TX, _UART_RX),
)


class BLESimplePeripheral:
    def __init__(self, ble, name="ColCube1"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services((_UART_SERVICE,))
        self._ble.gatts_set_buffer(self._handle_tx, 200)
        self._ble.gatts_set_buffer(self._handle_rx, 200)
        self._connections = set()
        self._write_callback = None
        self._payload = advertising_payload(name=name, services=[_UART_UUID])
        self._advertise()

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            print("New connection", conn_handle)
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            print("Disconnected", conn_handle)
            self._connections.remove(conn_handle)
            # Start advertising again to allow a new connection.
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            value = self._ble.gatts_read(value_handle)
            if value_handle == self._handle_rx and self._write_callback:
                self._write_callback(value)

    def send(self, data):
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._handle_tx, data)

    def is_connected(self):
        return len(self._connections) > 0

    def _advertise(self, interval_us=500000):
        print("Starting advertising")
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def on_write(self, callback):
        self._write_callback = callback
#BLE END
        
def set_LED_colors():
    global led_matrix, gameMap, COLORCUBE_DARK, COLORCUBE_WHITE, COLORCUBE_RED, COLORCUBE_BLUE
    for i in range(0,5):
        for j in range(0,5):
            for k in range(0,5):
                if led_matrix[i][j][k] != -1:
                    col_ID = gameMap[i][j][k]
                    if col_ID == -1:
                        set_pixels(COLORCUBE_DARK, led_matrix[i][j][k])
                    elif col_ID == 0:
                        set_pixels(COLORCUBE_WHITE, led_matrix[i][j][k])
                    elif col_ID == 1:
                        set_pixels(COLORCUBE_RED, led_matrix[i][j][k])
                    elif col_ID == 2:
                        set_pixels(COLORCUBE_BLUE, led_matrix[i][j][k])

# def set_cursor():
#     global cursor, led_matrix, COLORCUBE_GREEN
#     led_matrix[cursor[0]][cursor[1]][cursor[2]] = COLORCUBE_GREEN

def cursor_flash(self):
    global cursor_status, gameMap, led_matrix, COLORCUBE_GREEN, COLORCUBE_WHITE, COLORCUBE_RED, COLORCUBE_BLUE
    print(gameMap)
    print(cursor[0])
    print(cursor[1])
    print(cursor[2])
    if cursor_status:
        if gameMap[cursor[0]][cursor[1]][cursor[2]] != -1:
            set_pixels(COLORCUBE_GREEN, led_matrix[cursor[0]][cursor[1]][cursor[2]])
        cursor_status = False
    else:
        if gameMap[cursor[0]][cursor[1]][cursor[2]] == 0:
            set_pixels(COLORCUBE_WHITE, led_matrix[cursor[0]][cursor[1]][cursor[2]])
        elif gameMap[cursor[0]][cursor[1]][cursor[2]] == 1:
            set_pixels(COLORCUBE_RED, led_matrix[cursor[0]][cursor[1]][cursor[2]])
        elif gameMap[cursor[0]][cursor[1]][cursor[2]] == 2:
            set_pixels(COLORCUBE_BLUE, led_matrix[cursor[0]][cursor[1]][cursor[2]])
        cursor_status = True
        
def play_anim(anim_ID):
    global led_matrix, gameMap
    if anim_ID == 11: #boot
#         side_mids = [[2,2,0],[4,2,2],[2,4,2],[0,2,2],[2,0,2],[2,2,4]]
#         temp = []
#         for i in range(0,len(side_mids)):
#             for j in range(-1,3):
#                 newCoords = side_mids[i]
#                 if side_mids[i][0] != 0 and side_mids[i][0] != 4: 
#                     newCoords[0] = side_mids[i][0] + j
#                 elif side_mids[i][1] != 0 and side_mids[i][1] != 4:
#                     newCoords[1] = side_mids[i][1] + j
#                 elif side_mids[i][2] != 0 and side_mids[i][2] != 4:
#                     newCoords[2] = side_mids[i][2] + j
#                 temp.append(newCoords)
#
        pass
            
    elif anim_ID == 12: #shutdown
        pass        
    elif anim_ID == 13: #new game
        pass    
    elif anim_ID == 14: #win
        pass        
    elif anim_ID == 15: #loose
        pass
    elif anim_ID == 16: #draw
        pass
        
def restart_game():
    global gameMap, cursor
    gameMap = [[[0 for k in range(5)] for j in range(5)] for i in range(5)]
    
    write_map()
    set_LED_colors()
    
def boot():
    global gameMap
    try:
        data = open("data.json", "r+")
        gameMap = data.read()
        data.close()
        print("reading map")
    except:
        print("loading of map failed")
        print("creating new map file")
        try:
            data = open("data.json", "w")
            print("writing map again")
            data.write(json.dumps(gameMap))
            data.close()
        except:
            print("all failed")
    set_LED_colors()

def shutdown():
    write_map()
    gameMap = [[[-1 for k in range(5)] for j in range(5)] for i in range(5)]
    set_LED_colors()
    
def write_map():
    global gameMap
    try:
        data = open("data.json", "r+")
        data.write(json.dumps(gameMap))
        data.close()
        print("writing map")
    except:
        print("loading of map failed")
        print("creating new map file")
        try:
            data = open("data.json", "w")
            print("writing map again")
            data.write(json.dumps(gameMap))
            data.close()
        except:
            print("all failed")

def set_pixels(col_code,led_nr):
    if led_nr < 25:
        led_5x5_1[led_nr] = col_code        
    elif led_nr < 40:
        led_3x5_1[led_nr-25] = col_code
    elif led_nr < 49:
        led_3x3_1[led_nr-40] = col_code
    elif led_nr < 64:
        led_3x5_2[led_nr-49] = col_code
    elif led_nr < 73:
        led_3x3_2[led_nr-64] = col_code
    else: #led_nr < 98
        led_5x5_2[led_nr-73] = col_code
    

micropython.alloc_emergency_exception_buf(200)
#LEDs
#Overall there are 98 LEDs

led_5x5_1 = neopixel.NeoPixel(Pin(22), 25) #0-24
led_3x5_1 = neopixel.NeoPixel(Pin(12), 15) #25-39
led_3x3_1 = neopixel.NeoPixel(Pin(23), 9) #40-48
led_3x5_2 = neopixel.NeoPixel(Pin(26), 15) #49-63
led_3x3_2 = neopixel.NeoPixel(Pin(27), 9) #64-72
led_5x5_2 = neopixel.NeoPixel(Pin(21), 25) #73-97

all_led = []
led_matrix = [[[-1 for k in range(5)] for j in range(5)] for i in range(5)]


#Colors

COLORCUBE_DARK = (0,0,0) #standby mode, map-code = -1
COLORCUBE_RED = (255,0,0) #player 1, map-code = 1
COLORCUBE_GREEN = (0,255,0) #cursor,
COLORCUBE_BLUE = (0,0,255) #player 2, map-code = 2
COLORCUBE_YELLOW = (255,255,0) #impossible selection, 
COLORCUBE_WHITE = (255,255,255) #unoccupied, map-code = 0

#game related
gameMap = [[[0 for k in range(5)] for j in range(5)] for i in range(5)]
write_map()

#cursor
cursor = [2,2,0]
cursor_status= False
cursTimer = Timer(0)
cursTimer.init(period=500, mode=Timer.PERIODIC, callback=cursor_flash)

for i in range(0,98):
    all_led.append(i)
    
# for i in range(0,98):
#     if i < 25:
#         all_led.append(led_5x5_1[i])        
#     elif i < 40:
#         all_led.append(led_3x5_1[i-25])
#     elif i < 49:
#         all_led.append(led_3x3_1[i-40])
#     elif i < 64:
#         all_led.append(led_3x5_2[i-49])
#     elif i < 73:
#         all_led.append(led_3x3_2[i-64])
#     else: #i < 98
#         all_led.append(led_5x5_2[i-73])
        
         
for i in range (0,len(all_led)):
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
 
 

ble = bluetooth.BLE()
p = BLESimplePeripheral(ble)

while True:
    def on_rx(v):
        global gameMap, cursor, led_matrix
        print("RX", v)
        mess = json.loads(v)
        print(mess)
        print(type(mess))
        print(type(mess[0]))
        print(type(mess[3]))
        if type(mess[3]) == int: #map update
            gameMap[mess[0]][mess[1]][mess[2]] = mess[3]
            if mess[3] == 1:
                set_pixels(COLORCUBE_RED, led_matrix[mess[0]][mess[1]][mess[2]])
            elif mess[3] == 2:
                set_pixels(COLORCUBE_BLUE, led_matrix[mess[0]][mess[1]][mess[2]])
            write_map()
        elif mess[3] == "c":  #cursor update
            cursor[0] = mess[0]
            cursor[1] = mess[1]
            cursor[2] = mess[2]
        elif mess[3] == "r":  #restart game
            restart_game()
        elif mess[3] == "b":  #boot peripheral
            boot()
        elif mess[3] == "s":  #shutdown/standby peripheral
            shutdown()
#         elif mess[3] == "c2": #cursor flashing yellow
#             print(6)
        else:  #message[3] == "a"  #animation
            if mess[0] == 11: #boot
                play_anim(11)
            elif mess[0] == 12: #shutdown
                play_anim(12)
            elif mess[0] == 13: #new game
                play_anim(13)
            elif mess[0] == 14: #win
                play_anim(14)
            elif mess[0] == 15: #loose
                play_anim(15)
            elif mess[0] == 16: #draw
                play_anim(16)
        
#         if p.is_connected():
#             cursTimer.callback(cursor_flash) ##11
#         else:
#             cursTimer.callback(None)

    p.on_write(on_rx)

# i = 0
# while True:
#     if p.is_connected():
#         # Short burst of queued notifications.
#         for _ in range(3):
#             data = str(i) + "_"
#             print("TX", data)
#             
#             i += 1
#     time.sleep_ms(100)



