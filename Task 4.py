import network
import socket
import time

from machine import Pin, SoftI2C
from machine_i2c_lcd import I2cLcd

# WIFI SETTINGS

ssid = "Robotic WIFI"
password = "rbtWIFI@2025"

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
    
##Display the text on the LCD
    
def display_message(message):
    lcd.clear()
    
    if len(message) <= 16:
        lcd.putstr(message)
    
    else:
        lcd.scroll_text(message)
    
# CREATE WEBPAGE

def create_webpage():

    html = """
<!DOCTYPE html>

<html>

<head>

    <title>ESP32 LCD Control</title>

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

        input[type="text"] {
            width: 260px;
            padding: 12px;
            font-size: 16px;
            border: 1px solid #cccccc;
            border-radius: 6px;
            margin-bottom: 15px;
        }

        button {
            background-color: #0066cc;
            border: none;
            color: white;
            padding: 12px 24px;
            border-radius: 6px;
            font-size: 16px;
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

    return html


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

# MAIN PROGRAM
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


      
        # RECEIVE CUSTOM TEXT
     

        if "GET /message?text=" in request_line:

            start = request_line.find("text=") + len("text=")

            end = request_line.find(" ", start)

            encoded_message = request_line[start:end]

            message = url_decode(encoded_message)

            print("Message:", message)

            # Respond before scrolling
            client.send(
                "HTTP/1.1 204 No Content\r\n"
            )

            client.send(
                "Connection: close\r\n"
            )

            client.send("\r\n")

            client.close()
            client = None

            # Display or scroll the message
            display_message(message)


    
        # SEND WEBPAGE
    

        else:

            webpage = create_webpage()

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
