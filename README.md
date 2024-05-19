# AIoT SmartHome
An AIoT smart home project using various sensors to control home functions and intergrated with AI modules that aim to help people with disability via voice recognition and gesture recognition. This project is part of the course Computer Engineering Project.

## Description

## Components
- 1 Yolo:Bit or 1 micro:bit
- 1 GPIO Expansion board for the Yolo:Bit or the micro:bit
- 1 Temperature and Humidity sensor
- 1 Light sensor
- 1 PIR sensor
- 1 IR receiver
- 1 16x2 LCD
- 1 RC Servo motor
- 1 Mini fan
- 1 IR remote control

## MQTT Topics

|    Topics   |        Description       |
| ----------- | ------------------------ |
|      V1     | Temperature              |
|      V2     | Humidity                 |
|      V3     | Light level              |
|      V10    | LED control              |
|      V11    | LED colors               |
|      V12    | Fan control              |
|      V13    | AI response (dashboard)  |
|      V14    | AI response (Gemini API) |
|      V15    | AI command               |
|      V16    | Voice recognition output |

## Demonstration
### Basic features
- Showing data from sensors:
  
  **From LCD Display**
  
  ![lcd_display](/img/lcd_display.jfif)
  
  **From IoT dashboard**
  
  ![dashboard_display](/img/dashboard_display.jpg)

To be updated...
### IoT Dashboard
Currently using the built-in dashboard from OhStem, might switch to Adafruit IO or a custom built IoT web dashboard in the future.
![iot_dashboard](/img/iot_dashboard.jpg)
### Voice Recognition
To be updated...
### Gesture Control
To be updated...
