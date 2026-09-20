# LAB2: IoT Webserver with LED, Sensors, LCD, and Servo Control

## 1. Project Overview

This project is an ESP32-based IoT system developed using MicroPython. It combines a webserver, sensors, an LCD display, and a servo motor.

The web interface allows the user to:

* View temperature and humidity from the DHT11 sensor.
* View distance from the HC-SR04 ultrasonic sensor.
* Display temperature and distance on the LCD.
* Control the servo motor using a web slider from 0 to 180 degrees.
* Send custom text from the web browser to the LCD.
* Scroll text longer than 16 characters across the LCD.

## 2. Hardware
The components used in this project are:

* ESP32 Dev Board
* DHT11 Temperature and Humidity Sensor
* HC-SR04 Ultrasonic Sensor
* 16x2 LCD with I2C Backpack
* SG90 Servo Motor
* Breadboard
* Jumper Wires
* USB Cable
* Laptop with Thonny
* Wi-Fi

## 3. Wiring
### Pin Configuration

| Component    | ESP32 Pin |
| ------------ | --------- |
| DHT11 Data   | GPIO 4    |
| HC-SR04 Trig | GPIO 27   |
| HC-SR04 Echo | GPIO 26   |
| LCD SDA      | GPIO 21   |
| LCD SCL      | GPIO 22   |
| Servo Signal | GPIO 13   |

The LCD I2C address used in this project is `0x27`.

## 4. Software Setup
### Requirements

* ESP32 with MicroPython
* Thonny
* `main.py`
* `machine_i2c_lcd.py`
* Wi-Fi connection

### Setup Steps
1. Connect the ESP32 to the computer using USB.
2. Open the project in Thonny.
3. Upload `main.py` to the ESP32.
4. Upload `machine_i2c_lcd.py` to the ESP32.
5. Connect all hardware according to the wiring configuration.
6. Enter the Wi-Fi name and password in `main.py`.
7. Run the program.

The ESP32 will display its IP address in the Thonny console.

Open the displayed IP address in a web browser connected to the same Wi-Fi network.

## 5. Web Dashboard
The web dashboard displays the sensor readings and provides controls for the LCD and servo.

### Sensor Monitoring
The webpage displays:

* Temperature
* Humidity
* Distance

The webpage refreshes automatically to update the sensor readings.

![Web Dashboard](images/webpage.png)

### LCD Temperature
Click the **Show Temperature** button to display the temperature on the second line of the LCD.

Example:

```text
Temp: 27 C
```

Click the button again to hide the temperature.

![LCD Temperature](images/lcd-temperature.jpg)

### LCD Distance

Click the **Show Distance** button to display the ultrasonic distance on the first line of the LCD.

Example:

```text
Distance: 24.5cm
```

Click the button again to hide the distance.

![LCD Distance](images/lcd-distance.jpg)

### Servo Control
The webpage contains a slider with a range from **0 to 180 degrees**.
Moving the slider changes the angle of the SG90 servo.
The selected servo angle is also displayed on the webpage.

### Custom Text to LCD
The webpage contains a textbox and a **Send** button.

To send text to the LCD:

1. Enter text into the textbox.
2. Click **Send**.
3. The ESP32 receives the message.
4. The message is displayed on the LCD.

If the message is longer than 16 characters, it scrolls across the LCD.

## 6. Demonstration Video
The demonstration video shows the completed IoT system.
The demonstration includes:

* Live temperature readings.
* Live humidity readings.
* Live distance readings.
* Temperature displayed on the LCD.
* Distance displayed on the LCD.
* Servo controlled using the web slider.
* Custom text sent from the browser to the LCD.
* Long text scrolling across the LCD.

### Video

[Demonstration Video](https://youtube.com/shorts/AsPFrTOfDrY?si=1ypEa97JbAhKUjPN)

(https://youtube.com/shorts/89xMoLI5JnI?si=omO4xazwVasmRHI6)
---

## 7. Project Files

| File                 | Description                           |
| -------------------- | ------------------------------------- |
| `main.py`            | Complete ESP32 IoT webserver program  |
| `machine_i2c_lcd.py` | LCD helper library                    |
| `README.md`          | Project documentation                 |
| `images/`            | Project screenshots and wiring photos |
| `video/`             | Demonstration video                   |
