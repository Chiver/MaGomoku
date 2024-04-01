"""
 Copyright (c) 2022 Alan Yorinks All rights reserved.

 This program is free software; you can redistribute it and/or
 modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
 Version 3 as published by the Free Software Foundation; either
 or (at your option) any later version.
 This library is distributed in the hope that it will be useful,f
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 General Public License for more details.

 You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
 along with this library; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
import sys
import time
import numpy as np
from flask import Flask, jsonify, request

app = Flask(__name__)


import requests
from telemetrix import telemetrix

"""
Run a motor to a relative position.

Motor used to test is a NEMA-17 size - 200 steps/rev, 12V 350mA.
And the driver is a TB6600 4A 9-42V Nema 17 Stepper Motor Driver.

The driver was connected as follows:
VCC 12 VDC
GND Power supply ground
ENA- Not connected
ENA+ Not connected
DIR- ESP32 GND
DIR+ GPIO Pin 23 ESP32
PUL- ESP32 GND
PUL+ GPIO Pin 22 ESP32
A-, A+ Coil 1 stepper motor
B-, B+ Coil 2 stepper motor

"""
"""
const int StepX = 2;
const int DirX = 5;
const int StepY = 3;
const int DirY = 6;
const int StepZ = 4;
const int DirZ = 7;

"""

MUX_SELECT_PINS = [0, 1, 2, 3]



mem = np.zeros(shape=(9,9), dtype="float")


TRESHOLD = [
    [(173, 177), (169, 173), (174, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188)],
    [(180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188)],
    [(180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188)],
    [(180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188)],
    [(180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188)],
    [(180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188)],
    [(180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188)],
    [(180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188)],
    [(180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188)],
]


def serial_board():
    print("    +-------------------+")
    for i in range(9):
        print(' ', 9 - i, "| ", end='')
        for j in range(9):
            c = mem[i][j]
            print(c, end=' ')
        print('|')
    print("    +-------------------+")
    print("      a b c d e f g h i")

#PIN_MODE setting
    
CB_PIN_MODE = 0
CB_PIN = 1
CB_VALUE = 2
CB_TIME = 3

# x y offset from feeding point to grid 0 0 
X_OFFSET = 495
Y_OFFSET = 495



#ELECTRO

"""
board.digital_write(DIGITAL_PIN, 1)
board.digital_write(DIGITAL_PIN, 0)
"""

ELECTROMAGNET = 3

# GPIO Pins 
X_PULSE_PIN = 2
X_DIRECTION_PIN = 5

Y_PULSE_PIN = 3
Y_DIRECTION_PIN = 6


Z_PULSE_PIN = 4
Z_DIRECTION_PIN = 7

ENABLE_PIN = 8

# flag to keep track of the number of times the callback
# was called. When == 2, exit program

x = 0
y = 0
exit_flag = 0
channel = 0
initFlag = False
#y = 0


"""
Nothing = 0
WHITE = 1
BLACK = 2


"""

#pin, channel to x y pair

location_dict = {
    (0,0): (8,2),
    (1,0): (8,1),
    (2,0): (8,0),
}


def helper():
    board2.enable_analog_reporting(0)
    time.sleep(.1)
    board2.disable_analog_reporting(0)

def updateBoard(x_loc, y_loc, value):
    """
    if value >= BLACK_THRESHOLD[x_loc][y_loc]:
        mem[x_loc][y_loc] = 2
    elif value >= WHITE_THRESHOLD[x_loc][y_loc]:
        mem[x_loc][y_loc] = 1
    else:
        mem[x_loc][y_loc] = 0
    """
    global is_update_ready
    global update_coordination

    is_update_ready = True
    update_coordination = (x_loc, y_loc)
    

def calc_xy(pin):
    global channel
    return location_dict[(pin, channel)]
    #return (0,0)


def read_val_callback(data):
    global initFlag

    if initFlag:
        x, y = calc_xy(data[CB_PIN])
        updateBoard(x,y,data[CB_VALUE])
        #serial_board()
        print(f"Pin: {data[CB_PIN]} Val: {data[CB_VALUE]}")

    if data[CB_PIN] == 2:
        initFlag = True




def the_callback(data):
    global exit_flag
    date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[2]))
    print(f'Motor {data[1]} relative  motion completed at: {date}.')
    exit_flag += 1

def current_position_callback(data):
    print(f'current_position_callback returns {data[2]}\n')

def target_position_callback(data):
    print(f'target_position_callback returns {data[2]}')

def step_relative(the_board:telemetrix, motor_num, target, speed):

    global exit_flag

    #the_board.stepper_enable_outputs(motor_num)
    
    # create an accelstepper instance for a TB6600 motor driver
    # if you are using a micro stepper controller board:
    # pin1 = pulse pin, pin2 = direction
    
    the_board.stepper_set_current_position(motor_num, 0)
    # set the max speed and acceleration
    the_board.stepper_set_max_speed(motor_num, 999)
    the_board.stepper_move_to(motor_num, target)
    if target <=0:
        speed = -speed
    the_board.stepper_set_speed(motor_num, speed)

    the_board.stepper_get_current_position(motor_num, current_position_callback)
    the_board.stepper_get_target_position(motor_num, target_position_callback)

    board.stepper_run_speed_to_position(motor_num, the_callback)


    print('Running Motor')
    

    # keep application running
    while exit_flag == 0:
        try:
            time.sleep(.2)
        except KeyboardInterrupt:
            board.shutdown()
            sys.exit(0)
    exit_flag = 0
    

def reset(board, x, y, speed):
    
    stepX(board, -1, speed, 0)
    step_relative(board, motorY, -y * 495 - Y_OFFSET, speed)
    step_relative(board, motorX, (-x+1) * 495 - X_OFFSET, speed)
    x = 0
    y = 0

def stepX(board, num, speed, offset):
    step_relative(board, motorX, num * 495 + offset , speed)

def stepY(board, num, speed, offset):
    step_relative(board, motorY, num * 495 + offset, speed)


is_update_ready = False 
update_coordination = (-1, -1)

@app.route("/check_update_piece")
def check_update():
    global is_update_ready
    global update_coordination
    a, b = is_update_ready, update_coordination
    is_update_ready = False
    update_coordination = (-1,-1)

    return jsonify({'is_Ready': a, 'x': b[0], 'y': b[1]})
    
@app.route('/move_piece')
def move():

    x = request.args.get('x', 0)  # Default to 0 if not provided
    y = request.args.get('y', 0)  # Default to 0 if not provided
    x, y = int(x) * 2, int(y) * 2

    x, y = y,x
    speed = 800
    electroMagnet_on()

    stepX(board, x-1, speed, X_OFFSET)
    stepY(board, y , speed, Y_OFFSET)
    stepX(board, 1, speed, 0)

    electroMagnet_off()

    time.sleep(0.5)

    reset(board, x, y, 800)

    return jsonify({'x': x, 'y': y, 'message': 'Response from Flask with parameters!'})



def moveLocal(x, y):

    speed = 800

    x, y = int(x) , int(y)

    x*=2
    y*=2

    speed = 800
    electroMagnet_on()

    print(f"x is {x}, y is {y}")

    stepX(board, x-1, speed)
    stepY(board, y, speed)
    stepX(board, 1, speed)

    electroMagnet_off()





def electroMagnet_on():
    board2.digital_write(ELECTROMAGNET, 1)

def electroMagnet_off():
    board2.digital_write(ELECTROMAGNET, 0)

    



# instantiate telemetrix
board = telemetrix.Telemetrix(arduino_instance_id = 1)
board2 = telemetrix.Telemetrix(arduino_instance_id= 2)

board2.set_pin_mode_analog_input(0 , differential=16, callback=read_val_callback)
board2.set_pin_mode_analog_input(1 , differential=5, callback=read_val_callback)
board2.set_pin_mode_analog_input(2 , differential=15, callback=read_val_callback)



board2.set_pin_mode_digital_output(ELECTROMAGNET)










motorX = board.set_pin_mode_stepper(interface=1, pin1=X_PULSE_PIN,
                                                 pin2=X_DIRECTION_PIN)


motorY = board.set_pin_mode_stepper(interface=1, pin1=Y_PULSE_PIN,
                                                 pin2=Y_DIRECTION_PIN)

motorZ = board.set_pin_mode_stepper(interface=1, pin1=Z_PULSE_PIN,
                                                 pin2=Z_DIRECTION_PIN)



app.run(port=5000)

"""





"""
    
