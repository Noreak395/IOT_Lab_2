# ==============================
# Add LCD Library to Task 1 code
# ==============================
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

# Library ADDITION
from machine import SoftI2C
from machine_i2c_lcd import I2cLcd

# ==============================
# Set the Show state to False
# ==============================

show_distance = False
show_temperature = False

# ==============================
# Add LCD SETUP
# ==============================

I2C_ADDR = 0x27

i2c = SoftI2C(
    sda=Pin(21),
    scl=Pin(22),
    freq=400000
)

lcd = I2cLcd(
    i2c,
    I2C_ADDR,
    2,
    16
)

lcd.clear()


### Display the text -> IoT Class on the first row
lcd.move_to(0, 0)
lcd.putstr("IoT Class")


### Display the text -> Lab 2 & Task 2 on the second Row
lcd.move_to(0, 1)
lcd.putstr("Lab 2 & Task 2")

time.sleep(2)

lcd.clear()

# ==============================
# Add a function to clear the ROW
# ==============================

def clear_lcd_row(row):

    lcd.move_to(0, row)

    # 16 spaces clear the entire row
    lcd.putstr("                ")

# ==============================
# Add a function to display the Temperature
# ==============================

def display_temperature(temperature):

    
    ### write a code to display the Temperature if the Temperature is
    ### None display "Temp Error"  and if not display the
    ### Temperature Reading on the Second Row of the LCD
    clear_lcd_row(1)
    lcd.move_to(0, 1)

    if temperature is None:
        lcd.putstr("Temp Error")
    else:
        lcd.putstr("Temp: {} C".format(temperature))

# ==============================
# Add a function to display the Distance
# ==============================

def display_distance(distance):

    
    ### write a code to display the distance if the distance is
    ### None display "Distance Error"  and if not display the
    ### Ultrasonic Distance on the First Row of the LCD
    clear_lcd_row(0)
    lcd.move_to(0, 0)

    if distance is None:
        lcd.putstr("Distance Error")
    else:
        lcd.putstr("Distance: {:.1f}cm".format(distance))
        
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

def create_webpage(
    temperature,
    humidity,
    distance,
    show_distance,
    show_temperature
):

    if temperature is None:
        temperature_text = "Sensor error"
    else:
        temperature_text = (
            str(temperature) + " &deg;C"
        )

    if humidity is None:
        humidity_text = "Sensor error"
    else:
        humidity_text = (
            str(humidity) + " %"
        )

    if distance is None:
        distance_text = "Out of range"
    else:
        distance_text = (
            "{:.1f} cm".format(distance)
        )

    # TASK 3 ADDITION
    if show_distance:
        distance_button_text = "Hide Distance"
        distance_button_class = "hide-button"
    else:
        distance_button_text = "Show Distance"
        distance_button_class = "show-button"

    # TASK 3 ADDITION
    if show_temperature:
        temperature_button_text = (
            "Hide Temperature"
        )

        temperature_button_class = (
            "hide-button"
        )

    else:
        temperature_button_text = (
            "Show Temperature"
        )

        temperature_button_class = (
            "show-button"
        )

    html = """
<!DOCTYPE html>
<html>

<head>
    <title>ESP32 Sensor Monitoring</title>

    <meta name="viewport"
          content="width=device-width,
                   initial-scale=1">

    <meta http-equiv="refresh"
          content="2; URL=/">

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
            width: 60%;
            margin: 30px auto;
            padding: 40px;
            border-radius: 20px;

            box-shadow:
                0 2px 8px
                rgba(0, 0, 0, 0.2);
        }

        .value {
            color: blue;
            font-size: 36px;
            font-weight: bold;
        }

        button {
            border: none;
            color: white;
            padding: 15px 30px;
            margin: 10px;
            border-radius: 8px;
            font-size: 20px;
            cursor: pointer;
        }

        .show-button {
            background-color: blue;
        }

        .hide-button {
            background-color: red;
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
    </div>

    <div class="card">
         <h2>HC-SR04 Sensor</h2>
         <p>Distance</p>
         <p class="value">DISTANCE_VALUE</p>
    </div>


    <!-- TASK 3 ADDITION -->

    <div class="card">

        <h2>LCD Control</h2>

        <a href="/?distance=toggle">
            <button class="DISTANCE_BUTTON_CLASS">
                DISTANCE_BUTTON_TEXT
            </button>
        </a>

        <a href="/?temperature=toggle">
            <button class="TEMPERATURE_BUTTON_CLASS">
                TEMPERATURE_BUTTON_TEXT
            </button>
        </a>

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

    # TASK 2 ADDITION
    html = html.replace(
        "DISTANCE_BUTTON_TEXT",
        distance_button_text
    )

    html = html.replace(
        "TEMPERATURE_BUTTON_TEXT",
        temperature_button_text
    )

    html = html.replace(
        "DISTANCE_BUTTON_CLASS",
        distance_button_class
    )

    html = html.replace(
        "TEMPERATURE_BUTTON_CLASS",
        temperature_button_class
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

        # Receive and decode browser request
        request = client.recv(1024).decode()

        print("Request received")

        # Read sensors
        temperature, humidity = humidity = read_dht11()
        
        ### call the dht reading function
        distance = read_distance() ### call the ultrasonic distance reading function

        print("Temperature:", temperature)
        print("Humidity:", humidity)
        print("Distance:", distance)


        
        # TASK 2: DISTANCE BUTTON
        

        if "/?distance=toggle" in request:

            show_distance = not show_distance

            if show_distance:

                # Display the current distance on the LCD
                display_distance(distance)

                print("Distance shown on LCD")

            else:

                # Clear LCD line 1
                # Remember: LCD row numbering starts from 0
                clear_lcd_row(0)

                print("Distance hidden")


    
        # TASK 2: TEMPERATURE BUTTON

        elif "/?temperature=toggle" in request:

            show_temperature = not show_temperature

            if show_temperature:

                # Display the current temperature on the LCD
                display_temperature(temperature)

                print("Temperature shown on LCD")

            else:

                # Clear LCD line 2
                # Remember: LCD row numbering starts from 0
                clear_lcd_row(1)

                print("Temperature hidden")


        # Update the values while they are shown
        if show_distance:
            display_distance(distance)

        if show_temperature:
            display_temperature(temperature)


        # Create webpage
        webpage = create_webpage(
            temperature,
            humidity,
            distance,
            show_distance,
            show_temperature
        )
        
        ###  call the function create the webpage


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