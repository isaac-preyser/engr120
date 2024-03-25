import machine
import network
import usocket as socket
import utime as time
import _thread
import json 
from poll import getValue

green_led = machine.Pin(16, machine.Pin.OUT) #green LED; represents fan
yellow_led = machine.Pin(17, machine.Pin.OUT) #yellow LED; represents shades
red_led = machine.Pin(18, machine.Pin.OUT) #red LED; represents heater

#set all LEDs to ON
green_led.value(1)
yellow_led.value(1)
red_led.value(1)

#global variables
target_temp = 30 #in C
TARGET_VOLTAGE = 3.1 #in V
doAuto = True #operate the device in automatic mode

# other global variables
tempInternal = getValue(2, 'T')
lightIntensity = getValue(3, 'V')
tempExternal = getValue(1, 'T')
green_led_state = green_led.value()
yellow_led_state = yellow_led.value()
red_led_state = red_led.value()
shadesOverride = False
fanOverride = False
heaterOverride = False



# Create a network connection
ssid = 'RPI_PICO_AP'       #Set access point name 
password = '12345678'      #Set your access point password
ap = network.WLAN(network.AP_IF)
ap.config(essid=ssid, password=password)
ap.active(True)            #activating



while ap.active() == False:
  pass
print('Connection is successful')
print(ap.ifconfig())

# Define HTTP response
def web_page():
    html = open('index.html', "r").read().replace('{EXTERNAL_TEMP}', str(getValue(1, 'T'))).replace('{INTERNAL_TEMP:}', str(getValue(2, 'T'))).replace('{LIGHT_VALUE}', str(getValue(3, 'V')))
    return html



def update():
    global tempInternal, lightIntensity, tempExternal, green_led_state, yellow_led_state, red_led_state, doAuto, shadesOverride, fanOverride, heaterOverride
    while True: 
        #update the global variables
        tempInternal = getValue(2, 'T')
        lightIntensity = getValue(3, 'V')
        tempExternal = getValue(1, 'T')
        green_led_state = green_led.value()
        yellow_led_state = yellow_led.value()
        red_led_state = red_led.value()

        print('auto:', doAuto)
        
        doLogic(doAuto)
        #wait for 5 seconds
        time.sleep(1.5)


def doLogic(toggle):
    global tempInternal, lightIntensity, tempExternal, green_led_state, yellow_led_state, red_led_state, doAuto, red_led, green_led, yellow_led
    #if auto mode is on, perform normal automatic logic. 
    if toggle:       
        if tempInternal < target_temp:
            red_led.value(1) # heat on
            green_led.value(0) # fan off
        else: 
            red_led.value(0) #heat off
            green_led.value(1) #fan on
        if lightIntensity > TARGET_VOLTAGE:
            yellow_led.value(0) #shades off, it is dark. 
        else:
            yellow_led.value(1) #shades on, it is bright.
    #if auto mode is off, perform manual logic.
    else:
        if heaterOverride:
            red_led.value(0) # heat off
        else:
            red_led.value(1) # heat on
        if fanOverride:
            green_led.value(0) # fan off
        else:
            green_led.value(1) # fan on
        if shadesOverride:
            yellow_led.value(0) #shades off
        else:
            yellow_led.value(1) #shades on
# Function to get the status of the IR emitter and redLED
# creates a JSON object and returns it as a string
def get_status():
    #json object !!!
    status = {
        "tempInternal": tempInternal, 
        "lightIntensity": lightIntensity,
        "tempExternal": tempExternal,
        "greenLED": green_led_state,
        "yellowLED": yellow_led_state,
        "redLED": red_led_state,
        "autoMode": doAuto,
        "shadesOverride": shadesOverride,
        "fanOverride": fanOverride,
        "heaterOverride": heaterOverride, 

        
    }
    return json.dumps(status)

# Start the ADC monitoring function in a separate thread
_thread.start_new_thread(update, ())

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

    if str(request).find("/autoMode") == 6:
        #parse the request: 
        #request = /updateAuto?auto=(true/false)
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
        #update the global variable
        doAuto = auto
        response = web_page()
        conn.send("HTTP/1.1 200 OK\n")
        conn.send("Content-Type: text/html\n")
        conn.send("Connection: close\n\n")
        conn.sendall(response)

    #handle the override requests
    if str(request).find("/override") == 6:
        #parse the request:
        #request = /override?device=(shades/fan/heater)&state=(on/off)
        print('handling override request')
        #find the index of the '=', and the '&'
        index = str(request).find("=")
        amp = str(request).find("&")
        #get the substring after the '='
        device = str(request)[index+1:amp]
        #truncate the string after the first '&'
        state = str(request)[amp+1:]

        #find the index of the '='
        index = str(state).find("=")
        #get the substring after the '='
        state = str(state)[index+1:]

        #truncate the string after the first space
        state = state[:state.find(' ')]
        print('device:', device)
        print('state:', state)
        
        if device == 'shades':
            #toggle the shades override
            shadesOverride = state == 'on'
            doAuto = False
        if device == 'fan':
            #toggle the fan override
            fanOverride = state == 'on'
            doAuto = False
        if device == 'heater':
            #toggle the heater override
            heaterOverride = state == 'on'
            doAuto = False
        
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
    time.sleep_ms(500)

