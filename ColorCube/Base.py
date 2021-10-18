#Server
from ble_advertising import decode_services, decode_name
from netvars import setNetVar, getNetVar, initNet
from machine import ADC, Pin, PWM
from micropython import const
from time import sleep, sleep_ms, time
import bluetooth, config, json, micropython, random, re, struct

# def IRQ_button(pin):
#     start_time = time()
#     while not pin.value():
#         pass
#     time_diff = time() - start_time
#     
#     if time_diff <= 3:
#         print("short press")
#         send_selection()
#         #normal press - selection
#     elif time_diff <= 5:
#         print("long press")
#         shutdown()
#         #long press - shutdown
#     elif time_diff >= 6:
#         print("longest press")
#         req_anim(13)
#         sleep(5)
#         reset_game()
#         #longest press - reset game

def shutdown():
    global standby_mode
    if standby_mode:
        standby_mode = False
        req_anim(11)
        sleep(5)
        bt_send([-1,-1,-1,"b"])
    else:
        req_anim(12)
        sleep(5)
        standby_mode = True
        bt_send([-1,-1,-1,"s"])

def reset_game():
    global gameMap
    gameMap = [[[0 for k in range(5)] for j in range(5)] for i in range(5)]
    bt_send([-1,-1,-1,"r"])
    write_map()

def send_cursor():
    global cursor
    bt_send(cursor)

def req_anim(anim_ID):
    #boot = 11, shutdown = 12, new game = 13, win = 14, loose = 15, draw =16
    bt_send([anim_ID,-1,-1, "a"])

def send_selection():
    global cursor, gameMap
    xCurs = cursor[0]
    yCurs = cursor[1]
    zCurs = cursor[2]
    if gameMap[xCurs][yCurs][zCurs] != 0:
        bt_send([-1,-1,-1,"c2"])
    else:
        global move_count, key, player_ID
        gameMap[xCurs][yCurs][zCurs] = player_ID
        #bt_send([xCurs,yCurs,zCurs,player_ID])
        move_count +=1
        #dirs to check x +-, y +-, z+-
        for i in range(-1,2):
            for j in range(-1,2):
                for k in range(-1,2):
                    xTest = min(4, max(0, xCurs + i))
                    yTest = min(4, max(0, yCurs + j))
                    zTest = min(4, max(0,zCurs + k))
                    neighbor = gameMap[xTest][yTest][zTest]
                    if not neighbor in [-1, 0, player_ID]:
                        gameMap[xTest][yTest][zTest] = player_ID
                        bt_send([xTest,yTest,zTest,player_ID])
        bt_send([xCurs,yCurs,zCurs,player_ID])
        write_map()
        netStr = str(xCurs)+str(yCurs)+str(zCurs)+str(player_ID)
        setNetVar(key, netStr)
                        
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
    
#Space holder for BLE crap
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_IRQ_GATTS_READ_REQUEST = const(4)
_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)
_IRQ_PERIPHERAL_CONNECT = const(7)
_IRQ_PERIPHERAL_DISCONNECT = const(8)
_IRQ_GATTC_SERVICE_RESULT = const(9)
_IRQ_GATTC_SERVICE_DONE = const(10)
_IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
_IRQ_GATTC_CHARACTERISTIC_DONE = const(12)
_IRQ_GATTC_DESCRIPTOR_RESULT = const(13)
_IRQ_GATTC_DESCRIPTOR_DONE = const(14)
_IRQ_GATTC_READ_RESULT = const(15)
_IRQ_GATTC_READ_DONE = const(16)
_IRQ_GATTC_WRITE_DONE = const(17)
_IRQ_GATTC_NOTIFY = const(18)
_IRQ_GATTC_INDICATE = const(19)

_ADV_IND = const(0x00)
_ADV_DIRECT_IND = const(0x01)
_ADV_SCAN_IND = const(0x02)
_ADV_NONCONN_IND = const(0x03)

_UART_SERVICE_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_RX_CHAR_UUID = bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX_CHAR_UUID = bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")

class BLESimpleCentral:
    def __init__(self, ble):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        #self.ble.gatts_set_buffer(self.tx, 200, True)
        #self.ble.gatts_set_buffer(self.rx, 200, True)
        self._reset()

    def _reset(self):
        # Cached name and address from a successful scan.
        self._name = None
        self._addr_type = None
        self._addr = None

        # Callbacks for completion of various operations.
        # These reset back to None after being invoked.
        self._scan_callback = None
        self._conn_callback = None
        self._read_callback = None

        # Persistent callback for when new data is notified from the device.
        self._notify_callback = None

        # Connected device.
        self._conn_handle = None
        self._start_handle = None
        self._end_handle = None
        self._tx_handle = None
        self._rx_handle = None

    def _irq(self, event, data):
        if event == _IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data
            if adv_type in (_ADV_IND, _ADV_DIRECT_IND) and _UART_SERVICE_UUID in decode_services(
                adv_data
            ):
                # Found a potential device, remember it and stop scanning.
                self._addr_type = addr_type
                self._addr = bytes(
                    addr
                )  # Note: addr buffer is owned by caller so need to copy it.
                self._name = decode_name(adv_data) or "?"
                self._ble.gap_scan(None)

        elif event == _IRQ_SCAN_DONE:
            if self._scan_callback:
                if self._addr:
                    # Found a device during the scan (and the scan was explicitly stopped).
                    self._scan_callback(self._addr_type, self._addr, self._name)
                    self._scan_callback = None
                else:
                    # Scan timed out.
                    self._scan_callback(None, None, None)

        elif event == _IRQ_PERIPHERAL_CONNECT:
            # Connect successful.
            conn_handle, addr_type, addr = data
            if addr_type == self._addr_type and addr == self._addr:
                self._conn_handle = conn_handle
                self._ble.gattc_discover_services(self._conn_handle)

        elif event == _IRQ_PERIPHERAL_DISCONNECT:
            # Disconnect (either initiated by us or the remote end).
            conn_handle, _, _ = data
            if conn_handle == self._conn_handle:
                # If it was initiated by us, it'll already be reset.
                self._reset()

        elif event == _IRQ_GATTC_SERVICE_RESULT:
            # Connected device returned a service.
            conn_handle, start_handle, end_handle, uuid = data
            print("service", data)
            if conn_handle == self._conn_handle and uuid == _UART_SERVICE_UUID:
                self._start_handle, self._end_handle = start_handle, end_handle

        elif event == _IRQ_GATTC_SERVICE_DONE:
            # Service query complete.
            if self._start_handle and self._end_handle:
                self._ble.gattc_discover_characteristics(
                    self._conn_handle, self._start_handle, self._end_handle
                )
            else:
                print("Failed to find uart service.")

        elif event == _IRQ_GATTC_CHARACTERISTIC_RESULT:
            # Connected device returned a characteristic.
            conn_handle, def_handle, value_handle, properties, uuid = data
            if conn_handle == self._conn_handle and uuid == _UART_RX_CHAR_UUID:
                self._rx_handle = value_handle
            if conn_handle == self._conn_handle and uuid == _UART_TX_CHAR_UUID:
                self._tx_handle = value_handle

        elif event == _IRQ_GATTC_CHARACTERISTIC_DONE:
            # Characteristic query complete.
            if self._tx_handle is not None and self._rx_handle is not None:
                # We've finished connecting and discovering device, fire the connect callback.
                if self._conn_callback:
                    self._conn_callback()
            else:
                print("Failed to find uart rx characteristic.")

        elif event == _IRQ_GATTC_WRITE_DONE:
            conn_handle, value_handle, status = data
            print("TX complete")

        elif event == _IRQ_GATTC_NOTIFY:
            conn_handle, value_handle, notify_data = data
            if conn_handle == self._conn_handle and value_handle == self._tx_handle:
                if self._notify_callback:
                    self._notify_callback(notify_data)

    # Returns true if we've successfully connected and discovered characteristics.
    def is_connected(self):
        return (
            self._conn_handle is not None
            and self._tx_handle is not None
            and self._rx_handle is not None
        )

    # Find a device advertising the environmental sensor service.
    def scan(self, callback=None):
        self._addr_type = None
        self._addr = None
        self._scan_callback = callback
        self._ble.gap_scan(2000, 30000, 30000)

    # Connect to the specified device (otherwise use cached address from a scan).
    def connect(self, addr_type=None, addr=None, callback=None):
        self._addr_type = addr_type or self._addr_type
        self._addr = addr or self._addr
        self._conn_callback = callback
        if self._addr_type is None or self._addr is None:
            return False
        self._ble.gap_connect(self._addr_type, self._addr)
        return True

    # Disconnect from current device.
    def disconnect(self):
        if not self._conn_handle:
            return
        self._ble.gap_disconnect(self._conn_handle)
        self._reset()

    # Send data over the UART
    def write(self, v, response=False):
        if not self.is_connected():
            return
        self._ble.gattc_write(self._conn_handle, self._rx_handle, v, 1 if response else 0)

    # Set handler for when data is received over the UART.
    def on_notify(self, callback):
        self._notify_callback = callback

def bt_send(message):
    ble = bluetooth.BLE()
    central = BLESimpleCentral(ble)
    not_found = False

    def on_scan(addr_type, addr, name):
        if addr_type is not None:
            print("Found peripheral:", addr_type, addr, name)
            if name == "ColCube1":  ##TODO
                try:
                    central.connect()
                except:
                    print("retry bt connection")
                    sleep(0.2)
            else:
                print("Not the Cube we are looking for.")
        else:
            nonlocal not_found
            not_found = True
            print("No peripheral found.")

    central.scan(callback=on_scan)

    # Wait for connection...
    while not central.is_connected():
        sleep_ms(100)
        if not_found:
            return

    print("Connected")

    def on_rx(v):
        pass
        #print("RX", v)

    central.on_notify(on_rx)

    with_response = False

    while central.is_connected():
        #try:
        v = json.dumps(message)
        print("TX", v)
            #print("v length:" + str(len(v)))
            #if len(v) > 9:
            #    for i in range(1,29):
            #        minVal = (i-1) * 16
            #        maxVal = i * 16
            #        central.write(v[minVal:maxVal])
            #else:
            #   central.write(v)
        central.write(v)
        #central.disconnect()
        central._ble.gap_disconnect(central._conn_handle)
        central._reset()
        sleep_ms(200)
        #except:
        #    print("TX failed")
        #sleep_ms(400 if with_response else 30)

    print("Disconnected")
    sleep(0.2)
# BLE END

#system control
standby_mode = False

#controls
button = Pin(4, Pin.IN, Pin.PULL_UP)  #not pressed value = 1, pressed = 0
#button.irq(trigger=Pin.IRQ_FALLING, handler=IRQ_button)
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
setNetVar(key, "0002")  ##TODO ??

#game variables
own_turn = False
player_ID = 1
cursor = [-1,-1,-1, "c"]
gameMap = [[[0 for k in range(5)] for j in range(5)] for i in range(5)]
move_count = 0

req_anim(11)
sleep(5)
try:
    data = open("data.json", "r+")
    gameMap = json.loads(data.read())
    data.close()
    bt_send([-1,-1,-1,"b"])
    print("loading map")
except:
    print("loading of map failed")
    print("creating map file")
    try:
        data = open("data.json", "w")
        data.write(json.dumps(gameMap))
        data.close()
        bt_send([-1,-1,-1,"r"])
    except:
        print("all failed")

while True:
    if own_turn:
        #gameloop
        while own_turn and move_count < 97:
            if not button.value():
                start_time = time()
                while not button.value():
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
                    req_anim(13)
                    sleep(5)
                    reset_game()
                    #longest press - reset game
                    
            if cursor[0] == -1 or cursor[1] ==-1 or cursor[2] == -1:
                cursor = [3,3,0]
            #send to cube
            x = joystick_x.read()-2048 #move zeropoint to 0,0
            y = joystick_y.read()-2048
            print("XXXX : " + str(x) + " - " + str(joystick_x.read())) ##TODO
            print("YYYY : " + str(y) + " - " + str(joystick_y.read())) ##TODO
        
            if x > 150 or y > 150:
                if abs(x)-abs(y) >= 0:
                    if active_side == 1:
                        if cursor[0] == 0:
                            cursor[2] +=1
                            active_side = 4
                            
                        else:
                            cursor[0] -=1
                            
                            #left
                            
                    elif active_side == 2:
                        if cursor[2] == 0:
                            cursor[0] +=1
                            active_side = 1
                            
                        else:
                            cursor[2] -=1
                            
                            #left
                            
                    elif active_side == 3:
                        if cursor[0] == 0:
                            cursor[1] -=1
                            active_side = 4
                            
                        else:
                            cursor[0] -=1
                            
                            #left
                            
                    elif active_side == 4:
                        if cursor[2] == 4:
                            cursor[0] +=1
                            active_side = 6
                            
                        else:
                            cursor[2] +=1
                            
                            #left
                    
                    elif active_side == 5:
                        if cursor[0] == 0:
                            cursor[1] +=1
                            active_side = 4
                            
                        else:
                            cursor[0] -=1
                            
                            #left
                            
                    elif active_side == 6:
                        if cursor[0] == 4:
                            cursor[2] -=1
                            active_side = 2
                            
                        else:
                            cursor[0] +=1
                            
                            #left
                            
                else:
                    if active_side == 1:
                        if cursor[1] == 4:
                            cursor[2] +=1
                            active_side = 3
                            
                        else:
                            cursor[1] += 1
                            
                            #up
                            
                    elif active_side == 2:
                        if cursor[1] == 4:
                            cursor[0] -=1
                            active_side = 3
                            
                        else:
                            cursor[1] += 1
                            
                            #up
                            
                    elif active_side == 3:
                        if cursor[2] == 4:
                            cursor[1] -=1
                            active_side = 6
                            
                        else:
                            cursor[2] += 1
                            
                            #up
                            
                    elif active_side == 4:
                        if cursor[1] == 4:
                            cursor[0] +=1
                            active_side = 3
                            
                        else:
                            cursor[1] += 1
                            
                            #up
                            
                    elif active_side == 5:
                        if cursor[2] == 0:
                            cursor[1] +=1
                            active_side = 1
                            
                        else:
                            cursor[2] -= 1
                            
                            #up
                              
                    elif active_side == 6:
                        if cursor[1] == 0:
                            cursor[2] -=1
                            active_side = 5
                            
                        else:
                            cursor[1] -= 1
                            
                            #up
                send_cursor()
                
            elif x < -150 or y < -150:
                if abs(x)-abs(y) >= 0:
                    if active_side == 1:
                        if cursor[0] == 4:
                            cursor[2] +=1
                            active_side = 2
                            
                        else:
                            cursor[0] +=1
                            
                            #right
                            
                    elif active_side == 2:
                        if cursor[2] == 4:
                            cursor[0] -=1
                            active_side = 6
                            
                        else:
                            cursor[2] +=1
                            
                            #right
                            
                    elif active_side == 3:
                        if cursor[0] == 4:
                            cursor[1] -=1
                            active_side = 2
                            
                        else:
                            cursor[0] +=1
                            
                            #right
                            
                    elif active_side == 4:
                        if cursor[2] == 0:
                            cursor[0] +=1
                            active_side = 1
                            
                        else:
                            cursor[2] -=1
                            
                            #right
                    
                    elif active_side == 5:
                        if cursor[0] == 0:
                            cursor[1] +=1
                            active_side = 4
                            
                        else:
                            cursor[0] -=1
                            
                            #right
                                                
                    elif active_side == 6:
                        if cursor[0] == 0:
                            cursor[2] -=1
                            active_side = 4
                            
                        else:
                            cursor[0] -=1
                            
                            #right
                    
                else:
                    if active_side == 1:
                        if cursor[1] == 0:
                            cursor[2] +=1
                            active_side = 5
                            
                        else:
                            cursor[1] -=1
                            
                            #down
                    
                    elif active_side == 2:
                        if cursor[1] == 0:
                            cursor[0] -=1
                            active_side = 5
                            
                        else:
                            cursor[1] -=1
                            
                            #down
                            
                    elif active_side == 3:
                        if cursor[2] == 0:
                            cursor[1] -=1
                            active_side = 1
                            
                        else:
                            cursor[2] -=1
                            
                            #down
                            
                    elif active_side == 4:
                        if cursor[1] == 0:
                            cursor[0] +=1
                            active_side = 5
                            
                        else:
                            cursor[1] -=1
                            
                            #down
                            
                    elif active_side == 5:
                        if cursor[2] == 4:
                            cursor[1] +=1
                            active_side = 6
                            
                        else:
                            cursor[2] +=1
                            
                            #down
                    
                    elif active_side == 6:
                        if cursor[1] == 4:
                            cursor[2] -=1
                            active_side = 3
                            
                        else:
                            cursor[1] +=1
                            
                            #down
                send_cursor()
            sleep(0.5)
        
    elif move_count >= 97:
        score=[0,0,0]
        for i in range(0,5):
            for j in range(0,5):
                for k in range(0,5):
                    score[gameMap[i][j][k]] +=1
        
        if score[1] > score[2]: #win player 1
            req_anim(14)  ##TODO for player 2; switch anims
            sleep(5)
            req_anim(13)
            sleep(5)
            reset_game()
        elif score[2] > score[1]: #win player 2
            req_anim(15)  ##TODO for player 2; switch anims
            sleep(5)
            req_anim(13)
            sleep(5)
            reset_game()
        else: #draw
            req_anim(16)  
            sleep(5)
            req_anim(13)
            sleep(5)
            reset_game()
    
    else:
        gameVar = getNetVar("ColorCube_GameVar")
        if re.match(re.compile("...2"),gameVar): #change for other player ##TODO
            own_turn = True
            if move_count > 0:
                move_x = int(gameVar[0])
                move_y = int(gameVar[1])
                move_z = int(gameVar[2])
                opp_ID = int(gameVar[3])
                gameMap[move_x][move_y][move_z] = opp_ID
                bt_send([move_x,move_y,move_z,opp_ID])
                for i in range(-1,2):
                    for j in range(-1,2):
                        for k in range(-1,2):
                            xTest = min(4, max(0, move_x + i))
                            yTest = min(4, max(0, move_y + j))
                            zTest = min(4, max(0,move_z + k))
                            neighbor = gameMap[xTest][yTest][zTest] 
                            if not neighbor in [-1, 0, opp_ID]:
                                gameMap[xTest][yTest][zTest] = opp_ID
                                bt_send([xTest, yTest, zTest, opp_ID])
                write_map()               
                move_count += 1
        else:

            sleep(1)   #set to 150 := 2.5 minutes ##TODO
