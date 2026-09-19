# ==============================
# Import the library
# ==============================

import network
import socket
import time

from machine import Pin, PWM

# ==============================
# Wifi Setting
# ==============================

ssid = "Robotic WIFI"
password = "rbtWIFI@2025"

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
    
# ==============================
# Create a Webpage
# ==============================

def create_webpage(angle):

    html = """
<!DOCTYPE html>

<html>

<head>

    <title>ESP32 Servo Control</title>

    <meta name="viewport"
          content="width=device-width,
                   initial-scale=1">

    <style>

        body {
            font-family: Arial;
            text-align: center;
            background-color: #f2f2f2;
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
        }

        input[type="range"] {
            width: 280px;
            margin-top: 20px;
        }

    </style>

</head>

<body>

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

</body>

</html>
"""

    html = html.replace(
        "SERVO_ANGLE",
        str(angle)
    )

    return html

# ==============================
# WIFI Connection
# ==============================

# CONNECT TO WIFI

wifi = network.WLAN(
    network.STA_IF
)

wifi.active(True)

if not wifi.isconnected():

    print("Connecting to Wi-Fi...")

    wifi.connect(
        ssid,
        password
    )

    while not wifi.isconnected():
        print(".", end="")
        time.sleep(1)


ip = wifi.ifconfig()[0]

print()
print("Wi-Fi connected!")
print("ESP32 IP address:", ip)
print("Open this address:")
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
# Initial the servo position
# ==============================

# INITIAL SERVO POSITION

move_servo(90)

# ==============================
# Main
# ==============================

while True:

    client = None

    try:
        client, client_address = (
            server.accept()
        )

        request = client.recv(1024)
        request = request.decode()

        request_line = request.split(
            "\r\n"
        )[0]

        print("Request:", request_line)
  
        # RECEIVE SLIDER ANGLE
 

        if "GET /servo?angle=" in request_line:

            try:
                start = request_line.find("angle=") + len("angle=")
                end = request_line.find(" ", start)
                angle_text = request_line[start:end]
                servo_angle = int(angle_text)
                move_servo(servo_angle)

                client.send(
                    "HTTP/1.1 204 No Content\r\n"
                )

                client.send(
                    "Connection: close\r\n"
                )

                client.send("\r\n")

            except Exception as error:
                print(
                    "Servo control error:",
                    error
                )

        # SEND MAIN WEBPAGE


        else:

            webpage = create_webpage(
                servo_angle
            )

            client.send(
                "HTTP/1.1 200 OK\r\n"
            )

            client.send(
                "Content-Type: text/html\r\n"
            )

            client.send(
                "Connection: close\r\n"
            )

            client.send("\r\n")

            client.sendall(webpage)


    except Exception as error:

        print(
            "Server error:",
            error
        )


    finally:

        if client is not None:
            client.close()