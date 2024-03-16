import machine
import network
import usocket as socket
import utime as time
import _thread
import json 

# Define the IR emitter and Red LED (in this code Red LED is sometimes called as buzzer) pins
ir_emitter_pin = machine.Pin(15, machine.Pin.OUT)
redLED_pin = machine.Pin(14, machine.Pin.OUT)
redLED_status = "On"

# Function to control the IR emitter
def control_ir_emitter(status):
    if status == "on":
        ir_emitter_pin.on()
    elif status == "off":
        ir_emitter_pin.off()

# Function to get the buzzer status
def get_redLED_status():
    return "On" if redLED_pin.value() == 1 else "Off"

# Function to periodically check the ADC value and control the redLED
def check_adc_and_control_redLED():
    global redLED_status  # Declare redLED_status as global
    adc = machine.ADC(26) 
    while True:
        adc_value = adc.read_u16()
        print("ADC Value:", adc_value)

        if adc_value > 1000: # the threshold value must be tuned based on test environment. Ambient light also has IR rays. 
            print("Receiver/Transmitter blocked, turning on the red LED")
            redLED_pin.on()
        else:
            print("Receiver/Transmitter not blocked, turning off the red LED")
            redLED_pin.off()

        redLED_status = get_redLED_status()  # Update redLED_status
        print("Red LED Status:", redLED_status)
        time.sleep(1)


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
    ir_emitter_status = get_ir_emitter_status()
    redLED_status = get_redLED_status()
    ir_emitter_color = "purple" if ir_emitter_status == "ON" else "black"
    buzzer_color = "red" if redLED_status == "On" else "gray"
    
    html = """<!DOCTYPE html>
<!--[if lt IE 7]>      <html class="no-js lt-ie9 lt-ie8 lt-ie7"> <![endif]-->
<!--[if IE 7]>         <html class="no-js lt-ie9 lt-ie8"> <![endif]-->
<!--[if IE 8]>         <html class="no-js lt-ie9"> <![endif]-->
<!--[if gt IE 8]>      <html class="no-js"> <!--<![endif]-->
<html>
    <head>
        <script>    
        //import everything over from scripts.js
        var weatherData = null; //global variable to store the weather data
var positionData = null; //global variable to store the position data
var publicToken = "pk.eyJ1IjoicHJleXNlciIsImEiOiJjbHRvenp2b3YwNTVqMmpwa3ZldmdzdzI5In0.xxdA2sVzYqcyU1kJPGek0Q" //for mapbox API

function getWeather(lat, long, callback) {
    var apiUrl = "https://api.pirateweather.net/forecast/8xb4Xw81stuOYY6R9OaUdLcwsbsRQzBa/"+lat+"%2C"+long+"?units=ca";
        fetch(apiUrl).then(response => {
            // weatherData = response.json();
            return response.json();
        }).then(data => {
            // Work with JSON data here
            weatherData = data; //store the data in the global variable
            document.getElementById("forecast").innerHTML = "It is currently "+ Math.round(weatherData.currently.temperature) + " degrees and " + weatherData.currently.summary +".";
            console.log(data);
            callback(); //call the callback function
        }).catch(err => {
            // Do something for an error here
            console.log("Error: " + err);
        });

    }

function init() {
    //get coordinates of user via geolocation
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            var lat = position.coords.latitude;
            var long = position.coords.longitude;
            console.log(lat);
            console.log(long);
            //TODO call getWeather with lat and long as parameters
            getWeather(lat, long, function() {
                //update the location on the DOM
                console.log("Data has been loaded");
                updateLocationByCoordinates(lat, long);
            });
        });
    } else {
        console.log("Geolocation is not supported by this browser.");
    }
}

function getLocation(){
    //grab the user input from the text box with id locationInput
    var location = document.getElementById("locationInput").value;
    //format string for URL
    location = location.replace(" ", "%20");


    //use the input to build the URL for the API
    //using mapbox API to get the latitude and longitude of the location

    
    
    var url = "https://api.mapbox.com/geocoding/v5/mapbox.places/" + location + ".json?proximity=ip&access_token=" + publicToken;

    //fetch the data from the API and store long and lat into globals 
    fetch(url).then(response => {
        return response.json();
    }).then(data => {
        // Work with JSON data here
        console.log(data);
        var lat = data.features[0].center[1];
        var long = data.features[0].center[0];
        console.log(lat);
        console.log(long);
        //call the weather function with the lat and long as parameters
        getWeather(lat, long);
        //update the location on the DOM
        document.getElementById("location").innerHTML = data.features[0].place_name;
    }).catch(err => {
        // Do something for an error here
        console.log("Error: " + err);
    });


}

function updateLocationByCoordinates(lat, long){
    //search for the location using lat and long via reverse geocoding
    //use the input to build the URL for the API
    //using mapbox API to get the latitude and longitude of the location

    var url = "https://api.mapbox.com/geocoding/v5/mapbox.places/" + long + "," + lat + ".json?proximity=ip&access_token=" + publicToken;

    //fetch the data from the API and update the location ID on the DOM
    fetch(url).then(response => {
        return response.json();
    }).then(data => {
        // Work with JSON data here
        positionData = data; //store the data in the global variable
        console.log(data);
        var location = data.features[1].place_name;
        console.log(location);
        document.getElementById("location").innerHTML = location;
    }).catch(err => {
        // Do something for an error here
        console.log("Error: " + err);
    });
}


//these functions toggle physical devices on the pi (server)
//these functions will send a request to the server to toggle the device
//ideally these should send PUT requests to update the state of the device
//maybe a JSON object with the device name and state

function updateStatus() {
            var xhr = new XMLHttpRequest();
            xhr.onreadystatechange = function() {
                if (xhr.readyState == 4 && xhr.status == 200) {
                    var data = JSON.parse(xhr.responseText);
                    document.getElementById("shadesButton").innerHTML = data.irEmitterStatus;
                    var irEmitterColor = data.irEmitterStatus === "ON" ? "purple" : "black";
                    document.getElementById("heaterButton").style.backgroundColor = irEmitterColor;
                    document.getElementById("RedLEDStatus").innerHTML = data.RedLEDStatus;
                    var buzzerColor = data.RedLEDStatus === "On" ? "red" : "gray";
                    document.getElementById("buzzerIndicator").style.backgroundColor = buzzerColor;
                }
            };
            xhr.open("GET", "/status", true);
            xhr.send();
        }
        setInterval(updateStatus, 1000); // Refresh every 1 second

function toggleShades() {
    //send request to the server to toggle the shades


}

function toggleHeating() {

}

function toggleCooling() {
    //send request to the server to toggle the cooling

} 

function setTemp(){
    //update the temperature set on the DOM
    var temp = document.getElementById("tempInput").value;
    document.getElementById("tempDisplay").innerHTML = temp;
}
        </script>
        <style>
            /* MVP.css v1.14 - https://github.com/andybrewer/mvp */

:root {
    --active-brightness: 0.85;
    --border-radius: 5px;
    --box-shadow: 2px 2px 10px;
    --color-accent: #118bee15;
    --color-bg: #fff;
    --color-bg-secondary: #e9e9e9;
    --color-link: #118bee;
    --color-secondary: #920de9;
    --color-secondary-accent: #920de90b;
    --color-shadow: #f4f4f4;
    --color-table: #118bee;
    --color-text: #000;
    --color-text-secondary: #999;
    --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
    --hover-brightness: 1.2;
    --justify-important: center;
    --justify-normal: left;
    --line-height: 1.5;
    --width-card: 285px;
    --width-card-medium: 460px;
    --width-card-wide: 800px;
    --width-content: 1080px;
}

@media (prefers-color-scheme: dark) {
    :root[color-mode="user"] {
        --color-accent: #0097fc4f;
        --color-bg: #333;
        --color-bg-secondary: #555;
        --color-link: #0097fc;
        --color-secondary: #e20de9;
        --color-secondary-accent: #e20de94f;
        --color-shadow: #bbbbbb20;
        --color-table: #0097fc;
        --color-text: #f7f7f7;
        --color-text-secondary: #aaa;
    }
}

html {
    scroll-behavior: smooth;
}

@media (prefers-reduced-motion: reduce) {
    html {
        scroll-behavior: auto;
    }
}

/* Layout */
article aside {
    background: var(--color-secondary-accent);
    border-left: 4px solid var(--color-secondary);
    padding: 0.01rem 0.8rem;
}

body {
    background: var(--color-bg);
    color: var(--color-text);
    font-family: var(--font-family);
    line-height: var(--line-height);
    margin: 0;
    overflow-x: hidden;
    padding: 0;
}

footer,
header,
main {
    margin: 0 auto;
    max-width: var(--width-content);
    padding: 3rem 1rem;
}

hr {
    background-color: var(--color-bg-secondary);
    border: none;
    height: 1px;
    margin: 4rem 0;
    width: 100%;
}

section {
    display: flex;
    flex-wrap: wrap;
    justify-content: var(--justify-important);
}

section img,
article img {
    max-width: 100%;
}

section pre {
    overflow: auto;
}

section aside {
    border: 1px solid var(--color-bg-secondary);
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow) var(--color-shadow);
    margin: 1rem;
    padding: 1.25rem;
    width: var(--width-card);
}

section aside:hover {
    box-shadow: var(--box-shadow) var(--color-bg-secondary);
}

[hidden] {
    display: none;
}

/* Headers */
article header,
div header,
main header {
    padding-top: 0;
}

header {
    text-align: var(--justify-important);
}

header a b,
header a em,
header a i,
header a strong {
    margin-left: 0.5rem;
    margin-right: 0.5rem;
}

header nav img {
    margin: 1rem 0;
}

section header {
    padding-top: 0;
    width: 100%;
}

/* Nav */
nav {
    align-items: center;
    display: flex;
    font-weight: bold;
    justify-content: space-between;
    margin-bottom: 7rem;
}

nav ul {
    list-style: none;
    padding: 0;
}

nav ul li {
    display: inline-block;
    margin: 0 0.5rem;
    position: relative;
    text-align: left;
}

/* Nav Dropdown */
nav ul li:hover ul {
    display: block;
}

nav ul li ul {
    background: var(--color-bg);
    border: 1px solid var(--color-bg-secondary);
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow) var(--color-shadow);
    display: none;
    height: auto;
    left: -2px;
    padding: .5rem 1rem;
    position: absolute;
    top: 1.7rem;
    white-space: nowrap;
    width: auto;
    z-index: 1;
}

nav ul li ul::before {
    /* fill gap above to make mousing over them easier */
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    top: -0.5rem;
    height: 0.5rem;
}

nav ul li ul li,
nav ul li ul li a {
    display: block;
}

/* Typography */
code,
samp {
    background-color: var(--color-accent);
    border-radius: var(--border-radius);
    color: var(--color-text);
    display: inline-block;
    margin: 0 0.1rem;
    padding: 0 0.5rem;
}

details {
    margin: 1.3rem 0;
}

details summary {
    font-weight: bold;
    cursor: pointer;
}

h1,
h2,
h3,
h4,
h5,
h6 {
    line-height: var(--line-height);
    text-wrap: balance;
}

mark {
    padding: 0.1rem;
}

ol li,
ul li {
    padding: 0.2rem 0;
}

p {
    margin: 0.75rem 0;
    padding: 0;
    width: 100%;
}

pre {
    margin: 1rem 0;
    max-width: var(--width-card-wide);
    padding: 1rem 0;
}

pre code,
pre samp {
    display: block;
    max-width: var(--width-card-wide);
    padding: 0.5rem 2rem;
    white-space: pre-wrap;
}

small {
    color: var(--color-text-secondary);
}

sup {
    background-color: var(--color-secondary);
    border-radius: var(--border-radius);
    color: var(--color-bg);
    font-size: xx-small;
    font-weight: bold;
    margin: 0.2rem;
    padding: 0.2rem 0.3rem;
    position: relative;
    top: -2px;
}

/* Links */
a {
    color: var(--color-link);
    display: inline-block;
    font-weight: bold;
    text-decoration: underline;
}

a:hover {
    filter: brightness(var(--hover-brightness));
}

a:active {
    filter: brightness(var(--active-brightness));
}

a b,
a em,
a i,
a strong,
button,
input[type="submit"] {
    border-radius: var(--border-radius);
    display: inline-block;
    font-size: medium;
    font-weight: bold;
    line-height: var(--line-height);
    margin: 0.5rem 0;
    padding: 1rem 2rem;
}

button,
input[type="submit"] {
    font-family: var(--font-family);
}

button:hover,
input[type="submit"]:hover {
    cursor: pointer;
    filter: brightness(var(--hover-brightness));
}

button:active,
input[type="submit"]:active {
    filter: brightness(var(--active-brightness));
}

a b,
a strong,
button,
input[type="submit"] {
    background-color: var(--color-link);
    border: 2px solid var(--color-link);
    color: var(--color-bg);
}

a em,
a i {
    border: 2px solid var(--color-link);
    border-radius: var(--border-radius);
    color: var(--color-link);
    display: inline-block;
    padding: 1rem 2rem;
}

article aside a {
    color: var(--color-secondary);
}

/* Images */
figure {
    margin: 0;
    padding: 0;
}

figure img {
    max-width: 100%;
}

figure figcaption {
    color: var(--color-text-secondary);
}

/* Forms */
button:disabled,
input:disabled {
    background: var(--color-bg-secondary);
    border-color: var(--color-bg-secondary);
    color: var(--color-text-secondary);
    cursor: not-allowed;
}

button[disabled]:hover,
input[type="submit"][disabled]:hover {
    filter: none;
}

form {
    border: 1px solid var(--color-bg-secondary);
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow) var(--color-shadow);
    display: block;
    max-width: var(--width-card-wide);
    min-width: var(--width-card);
    padding: 1.5rem;
    text-align: var(--justify-normal);
}

form header {
    margin: 1.5rem 0;
    padding: 1.5rem 0;
}

input,
label,
select,
textarea {
    display: block;
    font-size: inherit;
    max-width: var(--width-card-wide);
}

input[type="checkbox"],
input[type="radio"] {
    display: inline-block;
}

input[type="checkbox"]+label,
input[type="radio"]+label {
    display: inline-block;
    font-weight: normal;
    position: relative;
    top: 1px;
}

input[type="range"] {
    padding: 0.4rem 0;
}

input,
select,
textarea {
    border: 1px solid var(--color-bg-secondary);
    border-radius: var(--border-radius);
    margin-bottom: 1rem;
    padding: 0.4rem 0.8rem;
}

input[type="text"],
textarea {
    width: calc(100% - 1.6rem);
}

input[readonly],
textarea[readonly] {
    background-color: var(--color-bg-secondary);
}

label {
    font-weight: bold;
    margin-bottom: 0.2rem;
}

/* Popups */
dialog {
    border: 1px solid var(--color-bg-secondary);
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow) var(--color-shadow);
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 50%;
    z-index: 999;
}

/* Tables */
table {
    border: 1px solid var(--color-bg-secondary);
    border-radius: var(--border-radius);
    border-spacing: 0;
    display: inline-block;
    max-width: 100%;
    overflow-x: auto;
    padding: 0;
    white-space: nowrap;
}

table td,
table th,
table tr {
    padding: 0.4rem 0.8rem;
    text-align: var(--justify-important);
}

table thead {
    background-color: var(--color-table);
    border-collapse: collapse;
    border-radius: var(--border-radius);
    color: var(--color-bg);
    margin: 0;
    padding: 0;
}

table thead tr:first-child th:first-child {
    border-top-left-radius: var(--border-radius);
}

table thead tr:first-child th:last-child {
    border-top-right-radius: var(--border-radius);
}

table thead th:first-child,
table tr td:first-child {
    text-align: var(--justify-normal);
}

table tr:nth-child(even) {
    background-color: var(--color-accent);
}

/* Quotes */
blockquote {
    display: block;
    font-size: x-large;
    line-height: var(--line-height);
    margin: 1rem auto;
    max-width: var(--width-card-medium);
    padding: 1.5rem 1rem;
    text-align: var(--justify-important);
}

blockquote footer {
    color: var(--color-text-secondary);
    display: block;
    font-size: small;
    line-height: var(--line-height);
    padding: 1.5rem 0;
}

/* Scrollbars */
* {
    scrollbar-width: thin;
    scrollbar-color: rgb(202, 202, 232) auto;
}

*::-webkit-scrollbar {
    width: 5px;
    height: 5px;
}

*::-webkit-scrollbar-track {
    background: transparent;
}

*::-webkit-scrollbar-thumb {
    background-color: rgb(202, 202, 232);
    border-radius: 10px;
}

        </style>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <title>Bigweld's big website</title>
        <meta name="description" content="">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="">

    </head>
    
    <body onload="init()">
        <section id="header">
            <h1><a onclick="init()">Bigweld's Big Website</a></h1>
            
        </section>



        <section id="section-1">
            <aside>
                <h3>Current Conditions:</h3>
                <p id="forecast">Loading weather data...</p>

                <small id="location">Loading location data...</small> 
                
                <div style="flex:50%"><input type="text" id="locationInput" placeholder="Enter your location..."> </div>
                <div style="flex:50%"><button onclick="getLocation()">Get Weather</button></div>
            </aside>
            <aside>
                <h3>Sensor Readings:</h3>
                <table>
                    <tr>
                        <td>External Temperature:</td>
                        <td id="extTemp">Loading...</td>
                    </tr>
                    <tr>
                        <td>Internal Temperature:</td>
                        <td id="intTemp">Loading...</td>
                    </tr>
                    <tr>
                        <td>Light:</td>
                        <td id="light">Loading...</td>
                    </tr>
            </table>
            </aside>
            <aside>
                <h3>Control Panel:</h3>
                <button onclick="toggleShades()" id="shadesButton">Toggle Shades</button>
                <button onclick="toggleCooling()" id="fanButton">Toggle Fan</button>
                <button onclick="toggleHeating()" id="heaterButton">Toggle Heater</button>
                <input type="range" min="0" max="45" value="20" id="tempInput" oninput="setTemp()">
                <p>Set Temperature: <span id="tempDisplay">20</span>°C</p>
                <a href="temp.html">link (temp)</a>
            </aside>
        </section>

    </body>
</html>"""
    return html

# Function to get the IR emitter status
def get_ir_emitter_status():
    return "ON" if ir_emitter_pin.value() == 1 else "OFF"


# Function to get the status of the IR emitter and redLED
# creates a JSON object and returns it as a string
def get_status():
    status = {
        "irEmitterStatus": get_ir_emitter_status(),
        "RedLEDStatus": redLED_status,
    }
    return json.dumps(status)

# Start the ADC monitoring function in a separate thread
_thread.start_new_thread(check_adc_and_control_redLED, ())

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
        buzzer_on = request.find('/?redLED_pin=on') #buzzer is the red LED
        buzzer_off = request.find('/?redLED_pin=off')
        ir_emitter_on = request.find('/?ir_emitter_pin=on')
        ir_emitter_off = request.find('/?ir_emitter_pin=off')

    if buzzer_on == 6:
        print('BUZZER ON')
        redLED_pin.value(1)
    elif buzzer_off == 6:
        print('BUZZER OFF')
        redLED_pin.value(0)

    if ir_emitter_on == 6:
        print('IR EMITTER ON')
        control_ir_emitter("on")
    elif ir_emitter_off == 6:
        print('IR EMITTER OFF')
        control_ir_emitter("off")

    if request.find("/status") == 6:
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

