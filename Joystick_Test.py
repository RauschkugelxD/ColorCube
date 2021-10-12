from machine import Pin, ADC
from time import sleep_ms

x_joystick = ADC(Pin(34, Pin.IN))
y_joystick = ADC(Pin(35, Pin.IN))
x_joystick.atten(ADC.ATTN_11DB)
y_joystick.atten(ADC.ATTN_11DB) # attenuation=Dämpfung: wird zu 11db Ratio gesetzt

button = Pin(25, Pin.IN, Pin.PULL_UP)


while True:
    x_val = x_joystick.read()
    y_val = y_joystick.read()
    print("Current position:{},{}".format(x_val, y_val))
    
    
    print("button value: ", button.value())
    
    sleep_ms(300)



# myButton = Pin(3, Pin.IN, Pin.PULL_DOWN)
# myLEDs = Pin(2, Pin.OUT)
# 
# while True:
#     if myButton.value():
#         myLEDs.on()
#         print(myButton.value())
#         print("Button is pressed")
#         
#     else:
#         myLEDs.off()
#         print(myButton.value())
#         print("Button is NOT pressed")
#         