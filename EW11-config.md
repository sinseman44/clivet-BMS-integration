
# Elfin EW11A Configuration

![EW11A](png/Elfin-EW11.png)

The Elfin-EW11 provides RS485 interface to Wi-Fi connectivity. The Elfin-EW11 integrate TCP/IP controller, memory, high-speed serial port and integrates a fully developed TCP/IP network stack and mbed OS.<br />
Elfin-EW11 also support remotely configure, monitor with IOTService. <br />
The Elfin-EW11 using highly integrated hardware and software platform, it has been optimized for all kinds of applications in the industrial control, smart grid, personal medical application and remote control that have lower data rates, and transmit or receive data on an infrequent basis.<br />

## Characteristics
* Support 802.11bgn Wireless Standard
* Support TCP/UDP/Telnet /Modbus TCP Protocol
* Support RS232/RS485 to Wi-Fi Conversion, Serial Speed Up to 230400 bps
* Support STA/AP/AP+STA Mode
* Support SmartLink V8 Smart Config (Provide APP)
* Support Easy Configuration Through Web Interface or PC IOTService Tool
* Support Security Protocol Such As TLS/AES/DES3
* Support Webpage OTA Wirelss Upgrade
* Support Internal PCB Antenna

## First use

* Connect to dongle wifi
* Go to the web interface 10.10.100.254
* Default Login: __admin__ and default password: __admin__
* Change settings to connect to your wifi network

## STA Mode

Product can be set as a wireless STA and AP as well. And logically, it supports two wireless interfaces, one is used as STA and the other is AP.<br />
Other STA devices can join into the wireless network through AP interface. So the it can provide flexible networking method and network topology.<br />

Connect the device to your Wifi before configuring it.<br />

![STA](png/EW11_wifi_conf.png)

## RS485 Configuration

By default, the Koolnova controller's Modbus serial communication is as follows:
* Baudrate: 9600
* Stopbits: 1
* Sizebyte: 8
* Parity: Even

Set the protocol settings to __Modbus__. The flow control settings to __disable__ and the cli settings to __disable__.<br />

![serial](png/EW11_serial_conf.png)

## TCP Configuration

To create a Modbus TCP server, choose for the protocol: __TCP Server__ and choose a local port to communicate with Home Assistant (default: __502__ for Modbus TCP).<br />
The timeout settings (unit second) must be ___greater than 30 seconds___ because the integration values ​​refresh is configured to 30 seconds.<br />
The keep alive settings (Heartbeat, unit second) must be minimum the double of the timeout value.

![tcp](png/EW11_tcp_server_conf.png)
