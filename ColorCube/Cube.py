#Client
# Missing values (i.e. Pin numbers) are marked with //
from ble_advertising import advertising_payload
from netvars import setNetVar, getNetVar, initNet
from machine import Pin, PWM
from micropython import const
from time import sleep, time
import bluetooth, neopixel, random, struct

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
    def __init__(self, ble, name="ColorCube_1"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services((_UART_SERVICE,))
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

def demo():
    ble = bluetooth.BLE()
    p = BLESimplePeripheral(ble)

    def on_rx(v):
        print("RX", v)

    p.on_write(on_rx)

    i = 0
    while True:
        if p.is_connected():
            # Short burst of queued notifications.
            for _ in range(3):
                data = str(i) + "_"
                print("TX", data)
                p.send("piemel")
                i += 1
        time.sleep_ms(100)

#BLE END


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