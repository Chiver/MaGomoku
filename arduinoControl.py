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

MUX_SELECT_PINS = [7, 6, 5, 4]



VAL_DEFAULT = [0 ]
MUX_READ_VAL_TIME = [0]
MUX_VAL_ACCUMULATE = [0]


BoardMem = np.zeros(shape=(9,9), dtype="int")



TRESHOLD = [
    [(178, 183), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188), (180, 188)],
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
X_OFFSET = 0
Y_OFFSET = 0



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

ENABLE_PIN = 8

# flag to keep track of the number of times the callback
# was called. When == 2, exit program

x = 0
y = 0
exit_flag = 0
channel = 0
#y = 0


"""
Nothing = 0
WHITE = 1
BLACK = 2


"""

#pin, channel to x y pair

location_dict = {
    (0,0): (0,0),
    (1,0): (1,0),
    (2,0): (1,0),
    (3,0): (1,0)
}

    

def calc_xy(pin):
    global channel
    return location_dict[(pin, channel)]
    #return (0,0)


def read_val_callback(data):
    #date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[CB_TIME]))
    #x, y = calc_xy(data[CB_PIN])

    global MUX_READ_VAL_TIME 
    global MUX_VAL_ACCUMULATE

    MUX_READ_VAL_TIME[data[CB_PIN]] += 1
    MUX_VAL_ACCUMULATE[data[CB_PIN]] += data[CB_VALUE]

    #PRINT OUT INFO
    print(f"Pin: {data[CB_PIN]} Val: {data[CB_VALUE]}")



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
    

    

    

def reset(board, speed):
    global x
    global y
    print(f"x is {x}, y is {y}")
    step_relative(board, motorX, -x * 495, speed)
    step_relative(board, motorY, -y * 495, speed)
    x = 0
    y = 0

def stepX(board, num, speed):
    step_relative(board, motorX, num * 495, speed)

def stepY(board, num, speed):
    step_relative(board, motorY, num * 495, speed)


@app.route('/movepiece')
def move(x, y, speed):

    x = request.args.get('x', 0)  # Default to 0 if not provided
    y = request.args.get('y', 0)  # Default to 0 if not provided

    electroMagnet_on()

    stepX(board, x-1, speed)
    stepY(board, y, speed)
    stepX(board, 1, speed)

    electroMagnet_off()

    return jsonify({'x': x, 'y': y, 'message': 'Response from Flask with parameters!'})



def electroMagnet_on():
    board2.digital_write(ELECTROMAGNET, 1)

def electroMagnet_off():
    board2.digital_write(ELECTROMAGNET, 0)



# instantiate telemetrix
#board = telemetrix.Telemetrix(arduino_instance_id = 1)
board2 = telemetrix.Telemetrix(arduino_instance_id= 2)

board2.set_pin_mode_analog_input(0 , differential=0, callback=read_val_callback)
#board2.set_pin_mode_analog_input(1 , differential=0, callback=read_val_callback)
#board2.set_pin_mode_analog_input(2 , differential=3, callback=read_val_callback)

board2.set_pin_mode_digital_output(ELECTROMAGNET)

for select in MUX_SELECT_PINS:
    board2.set_pin_mode_digital_output(select)





def iterate():

    global BoardMem
    global MUX_VAL_ACCUMULATE
    global MUX_READ_VAL_TIME
   

    for i in range(5, 6):
        sel_0 = i & 1
        sel_1 = (i >>1) & 1
        sel_2 = (i >>2) & 1
        sel_3 = (i >>3) & 1

        board2.digital_write(MUX_SELECT_PINS[0], sel_0)
        board2.digital_write(MUX_SELECT_PINS[1], sel_1)
        board2.digital_write(MUX_SELECT_PINS[2], sel_2)
        board2.digital_write(MUX_SELECT_PINS[3], sel_3)


        print(f"Selecting {sel_0} {sel_1} {sel_2} {sel_3} ")

        board2.enable_analog_reporting(0)
        #board2.enable_analog_reporting(1)
        #board2.enable_analog_reporting(2)
        
        #board2.enable_analog_reporting(3)
        #board2.enable_analog_reporting(4)
        #board2.enable_analog_reporting(5)

        time.sleep(0.1)

        board2.disable_analog_reporting(0)
        #board2.disable_analog_reporting(1)
        #board2.disable_analog_reporting(2)
        #board2.disable_analog_reporting(3)
        #board2.disable_analog_reporting(4)
        #board2.disable_analog_reporting(5)

        
        #j = 0
        #x, y = iteration_to_sesnor(i, j)
        #print(f"x: {x}, y:{y}")

        
        for j in range(len(MUX_VAL_ACCUMULATE)):
            avg = round(MUX_READ_VAL_TIME[j] / MUX_READ_VAL_TIME[j])
            x, y = iteration_to_sesnor(i, j)
            black_upper, black_lower = TRESHOLD[x][y]
            prev = BoardMem[x][y]
            verifyCell(avg, prev, black_lower, black_upper)
            BoardMem[x][y] = avg
            print(f"x: {x}, y:{y}, avg:{avg}")
           
        #MUX_VAL_ACCUMULATE = VAL_DEFAULT
        #MUX_READ_VAL_TIME = VAL_DEFAULT

        time.sleep(5)


        
            
            
            


"""

0 stands for nothing ~200 in raw
1 stands for black ~176 in raw
2 stands for white ~174 in raw
webapp

Responsible for sending message to 
"""
def verifyCell(avg, prev, black_lower, black_upper):

    if prev == 0:
        pass

    elif avg > black_upper:
        if prev >= black_lower and prev <= black_upper:
            # nothing to black
            pass
        else:
            # nothing to white
            pass
    elif avg >= black_lower:
        if prev > black_upper:
            # black to nothing
            pass
        elif prev < black_lower:
            # nothing to white
            pass
    else:
        if prev > black_upper:
            # white  to nothing
            pass
        elif prev >= black_lower:
            # white to black
            pass
        







def iteration_to_sesnor(iteration, mux_num):
    if mux_num % 2 == 1:
        if iteration in range(0,9):
            if mux_num == 1:
                return (2, iteration)
            elif mux_num == 3:
                return (5, iteration)
            elif mux_num == 5:
                return (8, iteration)
        else:
            if mux_num == 1:
                return (1, iteration - 9)
            elif mux_num == 3:
                return (4, iteration - 9)
            elif mux_num == 5:
                return (7, iteration - 9)
    else:
        if iteration == 13:
            return (-1, -1)
        elif iteration in range(4, 13):
            if mux_num == 0:
                return (0, iteration - 4)
            elif mux_num == 2:
                return (3, iteration - 4)
            elif mux_num == 4:
                return (6, iteration - 4)
        else:
            if mux_num == 0:
                return (1, iteration + 5)
            elif mux_num == 2:
                return (4, iteration + 5)
            elif mux_num == 4:
                return (7, iteration + 5)
        
        


    





#motorX = board.set_pin_mode_stepper(interface=1, pin1=X_PULSE_PIN,
 #                                                pin2=X_DIRECTION_PIN)


#motorY = board.set_pin_mode_stepper(interface=1, pin1=Y_PULSE_PIN,
  #                                               pin2=Y_DIRECTION_PIN)

actionQ = [0,1,0,1]
distance = [3, 3, -3, -3]
actionIndex= 0







#app.run(port=5000)
while True:
    try:
        # start the main function
        """
        dir = int(input("next "))
        action = actionQ[actionIndex]
        dist = distance[actionIndex]0

        if action == 0:
            stepX(board, dist, 800)
        else:
            stepY(board,dist, 800)
        """
        
        #x, y = map(int, input("Enter input:").split())
        
        #move(x,y, 800) 

        iterate()

        
        
        #resetX(board)
    except KeyboardInterrupt:
        sys.exit(0)