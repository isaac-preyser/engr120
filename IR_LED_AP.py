import machine
import network
import usocket as socket
import utime as time
import _thread
import json 
from poll import getValue

green_led = machine.Pin(16, machine.Pin.OUT) #green LED
yellow_led = machine.Pin(17, machine.Pin.OUT) #yellow LED
red_led = machine.Pin(18, machine.Pin.OUT) #red LED

#set all LEDs to ON
green_led.value(1)
yellow_led.value(1)
red_led.value(1)

#global variables
target_temp = 25 #in C
TARGET_VOLTAGE = 3.1 #in V
doAuto = True #operate the device in automatic mode

# other global variables
tempInternal = getValue(2, 'T')
lightIntensity = getValue(3, 'V')
tempExternal = getValue(1, 'T')
green_led_state = green_led.value()
yellow_led_state = yellow_led.value()
red_led_state = red_led.value()


# Create a network connection
ssid = 'RPI_PICO_AP'       #Set access point name 
password = '12345678'      #Set your access point password
ap = network.WLAN(network.AP_IF)
ap.config(essid=ssid, password=password)
ap.active(True)            #activating
#output the MAC address of the AP
mac = ap.config('mac').hex
print('MAC address:', mac)



while ap.active() == False:
  pass
print('Connection is successful')
print(ap.ifconfig())

# Define HTTP response
def web_page():
    #replace EXTERNAL_TEMP with the value of the external temperature (temp of therm1)
    #replace INTERNAL_TEMP with the value of the internal temperature (temp of therm2)
    #replace SHADES_RAISED with the value of the shades (0 or 1)
    html = open('index.html').read().replace('{EXTERNAL_TEMP}', str(getValue(1, 'T'))).replace('{INTERNAL_TEMP:}', str(getValue(2, 'T'))).replace('{LIGHT_VALUE}', str(getValue(3, 'V')))
    return html


def do_logic():
    if tempInternal < target_temp:
        green_led.value(1)
        red_led.value(0)
    else:  
        green_led.value(0)
        red_led.value(1)

    if lightIntensity > TARGET_VOLTAGE:
        #it's dark, turn on the lights
        yellow_led.value(1)
    else:
        #it's bright, turn off the lights
        yellow_led.value(0)


# Function to get the status of the IR emitter and redLED
# creates a JSON object and returns it as a string
def get_status():
    #update the global variables
    tempInternal = getValue(2, 'T')
    lightIntensity = getValue(3, 'V')
    tempExternal = getValue(1, 'T')
    green_led_state = green_led.value()
    yellow_led_state = yellow_led.value()
    red_led_state = red_led.value()
    
    if doAuto:
        do_logic()
    
    

    #json object !!!
    status = {
        "tempInternal": tempInternal, 
        "lightIntensity": lightIntensity,
        "tempExternal": tempExternal,
        "greenLED": green_led_state,
        "yellowLED": yellow_led_state,
        "redLED": red_led_state,
        "autoMode": doAuto
        
    }
    return json.dumps(status)

# Start the ADC monitoring function in a separate thread
_thread.start_new_thread(get_status, ())

# Create a socket server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    if request:
        request = str(request)
        print('Content = %s' % request)
        
    if str(request).find("/updateTemp") == 6:
        #parse the request: 
        #request = /updateTemp?temp=(some number)
        print('handling updateTemp request')
        #find the index of the '='
        index = str(request).find("=")
        #get the substring after the '='
        temp = str(request)[index+1:]
        #truncate the string after the first space
        temp = temp[:temp.find(' ')]
        print('temp:', temp)
        #convert the substring to an integer
        temp = int(temp)
        #set the global variable to the new temperature
        target_temp = temp
        response = web_page()
        conn.send("HTTP/1.1 200 OK\n")
        conn.send("Content-Type: text/html\n")
        conn.send("Connection: close\n\n")
        conn.sendall(response)

    if str(request).find("/updateAuto") == 6:
        #parse the request: 
        #request = /updateAuto?auto=(some number)
        print('handling updateAuto request')
        #find the index of the '='
        index = str(request).find("=")
        #get the substring after the '='
        auto = str(request)[index+1:]
        #truncate the string after the first space
        auto = auto[:auto.find(' ')]
        print('auto:', auto)
        #convert the substring to an boolean
        auto = int(auto == 'true')
        #set the global variable to the new temperature
        doAuto = auto
        response = web_page()
        conn.send("HTTP/1.1 200 OK\n")
        conn.send("Content-Type: text/html\n")
        conn.send("Connection: close\n\n")
        conn.sendall(response)

    if request.find("/status") == 6:
        print('handling status request')
        response = get_status()
        conn.send("HTTP/1.1 200 OK\n")
        conn.send("Content-Type: application/json\n")
        conn.send("Connection: close\n\n")
        conn.sendall(response)
    else:
        response = web_page()
        conn.send("HTTP/1.1 200 OK\n")
        conn.send("Content-Type: text/html\n")
        conn.send("Connection: close\n\n")
        conn.sendall(response)
    conn.close()

