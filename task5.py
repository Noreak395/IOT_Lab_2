import network
import socket
import time
import dht

from machine import Pin, time_pulse_us
# Library ADDITION
from machine import SoftI2C
from machine_i2c_lcd import I2cLcd
from machine import Pin, PWM

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

#TASK4 display text
# LCD SETUP
I2C_ADDR = 0x27 ## Add the LCD Address

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
### Display the "IoT LAB" on the first row
lcd.putstr("IoT LAB")

### Display the "Task 2" on the second row
lcd.move_to(0, 1)
lcd.putstr("Task 2")

time.sleep(2)

lcd.clear()

show_distance = False
show_temperature = False

# ==============================
# Initial the servo position
# ==============================



### DECODE TEXT FROM URL

def url_decode(text):

    result = bytearray()
    index = 0

    while index < len(text):

        if text[index] == "+":

            # Convert + to a space
            result.append(32)
            index += 1

        elif text[index] == "%":

            try:
                hex_value = text[
                    index + 1:index + 3
                ]

                result.append(
                    int(hex_value, 16)
                )

                index += 3

            except:
                index += 1

        else:

            result.extend(
                text[index].encode()
            )

            index += 1

    try:
        return result.decode("utf-8")

    except:
        return str(result)
    
def display_message(message):
    lcd.clear()
    
    if len(message) <= 16:
        lcd.putstr(message)
    
    else:
        lcd.scroll_text(message)

#TASK1&2 display temp & hum
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
        
#TASK3 servo
# ==============================
# Servo Setup
# ==============================

servo = PWM(Pin(13), freq=50) ## add the pin that you use with the 50hz frequency

servo_angle = 90  ## set servo angle to 90 degree

# ==============================
# Create a move servo angle function
# ==============================

def move_servo(angle):

    # Keep the angle between 0 and 180 degrees
    if angle < 0:
        angle = 0

    if angle > 180:
        angle = 180


    # Servo PWM duty range
    duty_min = 26
    duty_max = 128

    # Convert angle 0-180 degrees servo duty
    duty = int(
        duty_min
        + (angle / 180)
        * (duty_max - duty_min)
    )


    # Send the calculated duty to the servo
    servo.duty(duty)


    print("Servo angle:", angle)
    print("PWM duty:", duty)

# INITIAL SERVO POSITION
move_servo(90)
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

def create_webpage(
    temperature,
    humidity,
    distance,
    show_distance,
    show_temperature,
    angle
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
        .angle {
            color: blue;
            font-size: 32px;
            font-weight: bold;
                
        .value {
            color: blue;
            font-size: 36px;
            font-weight: bold;
        }
        
        input[type="range"] {
            width: 280px;
            margin-top: 20px;
        }
        
        input[type="text"] {
            width: 260px;
            padding: 12px;
            font-size: 16px;
            border: 1px solid #cccccc;
            border-radius: 6px;
            margin-bottom: 15px;
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
        
        button:hover {
            background-color: #0052a3;
        }
        
        #status {
            color: #28a745;
            margin-top: 15px;
            font-weight: bold;
        }
        
        .show-button {
            background-color: blue;
        }

        .hide-button {
            background-color: red;
        }
    </style>
    <script>

        function sendMessage() {

            var message =
                document.getElementById(
                    "message"
                ).value;

            if (message == "") {

                document.getElementById(
                    "status"
                ).innerHTML =
                    "Please enter a message.";

                return;
            }

            fetch(
                "/message?text=" +
                encodeURIComponent(message)
            );

            document.getElementById(
                "status"
            ).innerHTML =
                "Message sent to LCD";
        }

    </script>
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
    <h1>ESP32 Servo Control</h1>

    <div class="card">

        <h2>Servo angle</h2>

        <p class="angle" id="angle-value">  </p>
        <input
            type="range"
            min="0"
            max="180"
            value="SERVO_ANGLE"

            oninput="
                document.getElementById(
                    'angle-value'
                ).innerHTML = this.value
            "

            onchange="
                fetch(
                    '/servo?angle=' + this.value
                )
            "
        >

        <p>
            Move the slider to control the servo.
        </p>

    </div>

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
    
    <h1>LCD Control</h1>
    
    <div class="card">
        <h2>Send Text to LCD</h2>
        <input
            type="text"
            id="message"
            placeholder="Enter your message"
            maxlength="32"
        >
        
        <br>
        <button onclick="sendMessage()">
            Send
        </button>

        <p id="status"></p>

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
    
    html = html.replace(
        "SERVO_ANGLE",
        str(angle)
    )

    return html

#main code
while True:

    client = None

    try:

        # Wait for browser connection
        client, client_address = server.accept()

        print("Browser connected:", client_address)

        # Receive browser request
        request = client.recv(1024).decode()

        request_line = request.split("\r\n")[0]

        print("Request:", request_line)


        # Read sensors
        temperature, humidity = read_dht11()
        distance = read_distance()

        print("Temperature:", temperature)
        print("Humidity:", humidity)
        print("Distance:", distance)


        # ==================================================
        # 1. DISTANCE BUTTON
        # ==================================================

        if "GET /?distance=toggle" in request_line:

            show_distance = not show_distance

            if show_distance:
                print("Distance shown on LCD")

            else:
                clear_lcd_row(0)
                print("Distance hidden")


            # Update LCD if enabled
            if show_distance:
                display_distance(distance)

            if show_temperature:
                display_temperature(temperature)


            # Send ONE response
            client.send(
                "HTTP/1.1 204 No Content\r\n"
                "Connection: close\r\n"
                "\r\n"
            )


        # ==================================================
        # 2. TEMPERATURE BUTTON
        # ==================================================

        elif "GET /?temperature=toggle" in request_line:

            show_temperature = not show_temperature

            if show_temperature:
                print("Temperature shown on LCD")

            else:
                clear_lcd_row(1)
                print("Temperature hidden")


            # Update LCD if enabled
            if show_distance:
                display_distance(distance)

            if show_temperature:
                display_temperature(temperature)


            # Send ONE response
            client.send(
                "HTTP/1.1 204 No Content\r\n"
                "Connection: close\r\n"
                "\r\n"
            )


        # ==================================================
        # 3. SERVO CONTROL
        # ==================================================

        elif "GET /servo?angle=" in request_line:

            try:

                start = request_line.find("angle=") + len("angle=")

                end = request_line.find(" ", start)

                angle_text = request_line[start:end]

                servo_angle = int(angle_text)

                move_servo(servo_angle)


                print("Servo angle received:", servo_angle)


                # Send ONE response
                client.send(
                    "HTTP/1.1 204 No Content\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                )


            except Exception as error:

                print(
                    "Servo control error:",
                    error
                )

                client.send(
                    "HTTP/1.1 400 Bad Request\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                )


        # ==================================================
        # 4. CUSTOM LCD MESSAGE
        # ==================================================

        elif "GET /message?text=" in request_line:

            start = request_line.find("text=") + len("text=")

            end = request_line.find(" ", start)

            encoded_message = request_line[start:end]

            message = url_decode(encoded_message)

            print("Message:", message)


            # Display message
            display_message(message)


            # Send ONE response
            client.send(
                "HTTP/1.1 204 No Content\r\n"
                "Connection: close\r\n"
                "\r\n"
            )


        # ==================================================
        # 5. MAIN WEBPAGE
        # ==================================================

        elif "GET / HTTP/1.1" in request_line:

            # Update LCD values
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
                show_temperature,
                servo_angle
            )


            # Send webpage
            client.send(
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html\r\n"
                "Connection: close\r\n"
                "\r\n"
            )

            client.sendall(webpage)

        else:

            print("Unknown request:", request_line)

            client.send(
                "HTTP/1.1 404 Not Found\r\n"
                "Connection: close\r\n"
                "\r\n"
            )


    except Exception as error:

        print(
            "Server error:",
            error
        )


    finally:

        if client is not None:

            client.close()
            client = None