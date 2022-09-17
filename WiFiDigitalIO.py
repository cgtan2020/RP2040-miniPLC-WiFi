# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT


import time
import adafruit_requests as requests
import adafruit_espatcontrol_socket as socket
import adafruit_espatcontrol
from machine import UART, Pin, PWM

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise
# Debug Level
# Change the Debug Flag if you have issues with AT commands
debugflag = True

#configure output pin
# output pin
Output = []
Output.append(Pin(18, Pin.OUT))
Output.append(Pin(19, Pin.OUT))
Output.append(Pin(20, Pin.OUT))
Output.append(Pin(21, Pin.OUT))
Output.append(Pin(26, Pin.OUT))
Output.append(Pin(27, Pin.OUT))
Output.append(Pin(24, Pin.OUT))
Output.append(Pin(25, Pin.OUT))


Input = []
Input.append(Pin(6, Pin.IN))
Input.append(Pin(7, Pin.IN))
Input.append(Pin(12, Pin.IN))
Input.append(Pin(13, Pin.IN))
Input.append(Pin(14, Pin.IN))
Input.append(Pin(15, Pin.IN))
Input.append(Pin(16, Pin.IN))
Input.append(Pin(17, Pin.IN))


uart = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))

print("ESP AT commands")
# For Boards that do not have an rtspin like challenger_rp2040_wifi set rtspin to False.
esp = adafruit_espatcontrol.ESP_ATcontrol(
    uart, 115200,  debug=debugflag
)


first_pass = True
connect_to_server = False
data_receive = bytearray(b'')


while True:
    try:
        if first_pass:
            
            # secrets dictionary must contain 'ssid' and 'password' at a minimum
#             print("Connecting...")
#             b_reset = esp.soft_reset()
#             print("Softreset")
#            print(b_reset)
            esp.connect(secrets)
            print("Connected to AT software version ", esp.version)
            print("IP address ", esp.local_ip)
            # start to connect to server
            connect_to_server = esp.socket_connect("TCP","192.168.0.22",8083)
            while (connect_to_server == False):
                connect_to_server = esp.socket_connect("TCP","192.168.0.22",8083)
            first_pass = False
        data_receive = esp.socket_receive(50) # 50 milisecond timeout
        #print(data_receive)
        # Process the data receive from Server
        # This is a digital IO module
        # @SO,xx,* xx is the bit of the IO, value 00 to FF
        # reply will be the input state of the IO @SO,ii,*
        LCmydata = data_receive.decode()
        mySO = chr(0x53) + chr(0x4F)
        if len(LCmydata) == 6:
            pos3 = LCmydata.find(mySO)
            if pos3 == 1:
                print("Got SO")
                print(LCmydata)
                value = ((LCmydata[3:5]))
                print(value)
                #convert value to integer
                intvalue = (int(value, 16))
                print(intvalue)
                #set the output status
                # output pin
                #Output = []
                
                Output[0].value(intvalue & 0x01)
                Output[1].value((intvalue & 0x02) >> 1)
                Output[2].value((intvalue & 0x04) >> 2)
                Output[3].value((intvalue & 0x08) >> 3)
                Output[4].value((intvalue & 0x10) >> 4)
                Output[5].value((intvalue & 0x20) >> 5)
                Output[6].value((intvalue & 0x40) >> 6)
                Output[7].value((intvalue & 0x80) >> 7)
                
                inputvalue = ( Input[0].value() + (Input[1].value() << 1) + (Input[2].value() << 2) + (Input[3].value() << 3) + (Input[4].value() << 4) + (Input[5].value() << 5) + (Input[6].value() << 6) + (Input[7].value() << 7) )
                print(inputvalue)
                
                inverted_value = (~inputvalue ) & 0xFF 
                inputvaluehexstr = "0x%0.2X" % inverted_value
                print("inverted value")
                print(inputvaluehexstr)
                
                
                # reply to the command
                str2sent = "@SO,OK*\r\n"
                esp.socket_send(str2sent)

        
        
        
        #time.sleep(0.001)
    except (ValueError, RuntimeError, adafruit_espatcontrol.OKError) as e:
        print("Failed to get data, retrying\n", e)
        print("Resetting ESP module")
        #esp.hard_reset()
        continue

