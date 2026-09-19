import network
import socket
import time
import dht

from machine import Pin, time_pulse_us
# ==============================
# wifi setup
# ==============================

ssid = "Robotic WIFI"
password = "rbtWIFI@2025"

# ==============================
# Sensor Pin Setup
# ==============================

# DHT11 data pin
DHT_PIN = 4
dht_sensor = dht.DHT11(Pin(DHT_PIN))

# HC-SR04 pins
trig = Pin(27, Pin.OUT)
echo = Pin(26, Pin.IN)

# ==============================
# Read distance from the ultrasonic
# ==============================


def read_distance():
    try:
        # set Trigger to off for 2us
        trig.value(0)
        time.sleep_us(2)

        # set Trigger to on for 10us
        trig.value(1)
        time.sleep_us(10)
        
        
        # set Trigger to off again
        trig.value(0)

        # Measure the ECHO pulse
        duration = time_pulse_us(echo, 1, 30000)

        # make a codition if the duration less than 0 return None
        if duration < 0:
            return None

        # Convert time to distance in centimetres with the formular d = v*t/2
        distance = (duration * 0.0343) / 2
        return distance

    except Exception as error:
        print("Ultrasonic error:", error)
        return None

# ==============================
# read temperature and humidity Function
# ==============================

def read_dht11():
    try:
    # Call the object from the dht library 
        dht_sensor.measure()
        

        temperature = dht_sensor.temperature()  # °C
        humidity = dht_sensor.humidity()        # %

        return temperature, humidity

    except Exception as error:
        print("DHT11 error:", error)
        return None, None
# ==============================
# Create a webpage Function
# ==============================
def create_webpage(temperature, humidity, distance):

    if temperature is None:
        temperature_text = "Sensor error"
    else:
        temperature_text = str(temperature) + " &deg;C"

    if humidity is None:
        humidity_text = "Sensor error"
    else:
        humidity_text = str(humidity) + " %"

    if distance is None:
        distance_text = "Out of range"
    else:
        distance_text = "{:.1f} cm".format(distance)

    html = """
<!DOCTYPE html>
<html>

<head>
    <title>ESP32 Sensor Monitoring</title>

    <meta name="viewport"
          content="width=device-width, initial-scale=1">

    <meta http-equiv="refresh" content="2">

    <style>
        body {
            font-family: Arial;
            text-align: center;
            background-color: #f2f2f2;
            margin: 0;
            padding: 20px;
        }

        h1 {
            color: black;
        }

        .card {
            background-color: white;
            width: 60% ;
            margin: 30px auto;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }

        .value {
            color: blue;
            font-size: 36px;
            font-weight: bold;
        }
    </style>
</head>

<body>

    <h1>ESP Sensor Monitoring</h1>

    <div class="card">
         <h2>DHT11 Sensor</h2>
         <p>Temperature</p>
         <p class="value">TEMPERATURE_VALUE</p>
         <p>Humidity</p>
         <p class="value">HUMIDITY_VALUE</p>
         
         ##complete this part by using the class card and display the temerature and humidity--
    </div>

    <div class="card">
         <h2>HC-SR04 Sensor</h2>
         <p>Distance</p>
         <p class="value">DISTANCE_VALUE</p>
         
         ##Complete this part by using the class card and distance from the ultrasonic sensor---
    </div>

  
</body>

</html>
"""

    html = html.replace(
        "TEMPERATURE_VALUE",
        temperature_text
    )

    html = html.replace(
        "HUMIDITY_VALUE",
        humidity_text
    )

    html = html.replace(
        "DISTANCE_VALUE",
        distance_text
    )

    return html

# ==============================
# Connect to wifi setup
# ==============================

wifi = network.WLAN(network.STA_IF)
wifi.active(True)

if not wifi.isconnected():
    print("Connecting to Wi-Fi...")
    wifi.connect(ssid, password)

    while not wifi.isconnected():
        print(".", end="")
        time.sleep(1)

ip = wifi.ifconfig()[0]

print()
print("Wi-Fi connected!")
print("ESP32 IP address:", ip)
print("Open this address in your browser:")
print("http://" + ip)


# ==============================
# START WEB SERVER
# ==============================

address = socket.getaddrinfo(
    "0.0.0.0",
    80
)[0][-1]

server = socket.socket()

server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server.bind(address)
server.listen(1)

print("Web server is running...")

# ==============================
# Main
# ==============================

while True:

    client = None

    try:
        client, client_address = server.accept()

        print("Browser connected:", client_address)

        # Receive browser request
        request = client.recv(1024)
        print("Request received")

        # Read sensors
        temperature, humidity = read_dht11()
        distance = read_distance()

        print("Temperature:", temperature)
        print("Humidity:", humidity)
        print("Distance:", distance)

        # Create webpage
        webpage = create_webpage(temperature, humidity, distance)

        # Send HTTP response
        client.send("HTTP/1.1 200 OK\r\n")
        client.send("Content-Type: text/html\r\n")
        client.send("Connection: close\r\n")
        client.send("\r\n")
        client.sendall(webpage)

    except Exception as error:
        print("Server error:", error)

    finally:
        if client is not None:
            client.close()

