"""
Copyright 2024 MaGomoku Team 
Members: 
1. Shuailin Pan
2. Sizhe Chen 
3. Zipiao Wan

Explanation: 
- `board`: control of gantry system (x,y motors)
- `board2`: control of electromagnet and pcb board of hall effect sensors 
"""

from flask import Flask, jsonify, request
import requests
from multiprocessing import Process, Event
from telemetrix import telemetrix
import atexit
import time 
import numpy as np
import sys

""" ************************* GLOBAL VARIABLES ************************* """
app = Flask(__name__)
stop_event = Event()

#PIN_MODE setting
CB_PIN_MODE = 0
CB_PIN = 1
CB_VALUE = 2
CB_TIME = 3

# GANTRY: x y offset from feeding point to grid 0 0 
X_OFFSET = 1
Y_OFFSET = 1
# flag to keep track of the number of times the callback was called. When == 2, exit program
x = 0
y = 0
exit_flag = 0
channel = 0

# ELECTRO MAGNET 
ELECTROMAGNET = 3

# GPIO Pins 
X_PULSE_PIN = 2
X_DIRECTION_PIN = 5

Y_PULSE_PIN = 3
Y_DIRECTION_PIN = 6


# SENSOR: mux related 
MUX_SELECT_PINS = [7, 6, 5, 4]
VAL_DEFAULT = [0, 0]
ENABLE_PIN = 8
# pin 5 4 3 2
MUX_READ_VAL_TIME = [0, 0]
MUX_VAL_ACCUMULATE = [0, 0]
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
BoardMem = np.zeros(shape=(9,9), dtype="int")

# API 
DJANGO_ENDPOINT_URL = 'http://localhost:8000/physical_placement_action'
F_EMPTY = "EMPTY"
F_BLACK = "BLACK"
F_WHITE = "WHITE"


# pretty print 3 digit 2d array
def serial_board(BoardMem, dim):
    print("    +" + "-" * 46 + "+")
    max_widths = [max(len(str(c)) for c in col) for col in zip(*BoardMem)]
    for i in range(dim):
        print(' ', dim - i -1, "| ", end='')
        for j in range(dim):
            c = BoardMem[j][i]
            # Calculate the spacing needed based on maximum width of each column
            spaces_needed = max_widths[j] - len(str(c))
            print(' ' * spaces_needed, c, end=' ')
        print('|')
    print("    +" + "-" * 46 + "+")
    print("        " + "    ".join(str(i) for i in range(dim)))

""" ************************* FLASK API ENDPOINTS ************************* """

@app.route('/move_piece')
def move():
    """
    API for moving pieces via gantry system 
    """
    x = request.args.get('x', 0)  # Default to 0 if not provided
    y = request.args.get('y', 0)  # Default to 0 if not provided
    a, b = int(x) * 2, int(y) * 2
    speed = 800  

    # electroMagnet_on()
    
    print(f"{a}, {b}")
    stepX(board, a-1, speed, 495)
    stepY(board, b, speed, 495)
    stepX(board, 1, speed, 0)
    time.sleep(0.2)
    stepY(board, -b, speed, -495)
    stepX(board, -1, speed, 0)
    stepX(board, -a+1, speed, -495)

    # electroMagnet_off()

    

    return jsonify({'x': x, 'y': y, 'message': 'Response from Flask with parameters!'})

""" ************************* BOARD 1 GANTRY ************************* """

def stepX(board, num, speed, offset):

    step_relative(board, motorX, num * 495 + offset, speed)


def stepY(board, num, speed, offset):
 
    step_relative(board, motorY, num * 495 + offset, speed)


# step the stepper motor for a relative distance from its current position
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


# motor call back function 
def the_callback(data):
    global exit_flag
    date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[2]))
    print(f'Motor {data[1]} relative  motion completed at: {date}.')
    exit_flag += 1


#call back that print out the current position 
def current_position_callback(data):
    print(f'current_position_callback returns {data[2]}\n')


#call back that print out the target position
def target_position_callback(data):
    print(f'target_position_callback returns {data[2]}')


def reset(board, speed):
    global x
    global y
    print(f"x is {x}, y is {y}")
    step_relative(board, motorX, -x * 495 - 495, speed)
    step_relative(board, motorY, -y * 495 - 495, speed)
    x = 0
    y = 0

""" ************************* BOARD 2 SENSOR & ELECTROMAGNET ************************* """

def fire_placement_event(prev, curr, x, y): 
    """
    Fire placement events of black and white pieces 
    """
    # Define the parameters for the GET request
    params = {
        'prev': prev,
        'curr': curr,
        'x': x,
        'y': y
    }
    # Make the GET request
    response = requests.get(DJANGO_ENDPOINT_URL, params=params)

    # Print the response text (or do something else with it)
    print(f"Called django endpoint to fire placement event: \n{response.text}")


def verifyCell(avg, prev, black_lower, black_upper, x, y):
    """
    0 stands for nothing ~ in raw
    1 stands for black ~ in raw
    2 stands for white ~ in raw
    Responsible for sending message to webapp
    """
    if prev == 0:
        return
    elif avg > black_upper:
        if prev >= black_lower and prev <= black_upper:
            # nothing to black
            fire_placement_event(F_EMPTY, F_BLACK, x, y) 
            return
        else:
            # nothing to white
            fire_placement_event(F_EMPTY, F_WHITE, x, y) 
            return 
    elif avg >= black_lower:
        if prev > black_upper:
            # black to nothing
            fire_placement_event(F_BLACK, F_EMPTY, x, y) 
            return
        elif prev < black_lower:
            # TODO: nothing to white (black to white??)
            fire_placement_event(F_BLACK, F_WHITE, x, y) 
            return 
    else:
        if prev > black_upper:
            # white to nothing
            fire_placement_event(F_WHITE, F_EMPTY, x, y) 
            return 
        elif prev >= black_lower:
            # white to black
            fire_placement_event(F_WHITE, F_BLACK, x, y) 
            return 


# transform mux select vals and output pin num to (x,y)
def iteration_to_sesnor(iteration, mux_num):
    if mux_num % 2 == 1:
        if iteration in range(0,6):
            if mux_num == 1:
                return (2, iteration)
            elif mux_num == 3:
                return (5, iteration)
            elif mux_num == 5:
                return (8, iteration)
        elif iteration in range(9, 14):
            if mux_num == 1:
                return (1, iteration - 9)
            elif mux_num == 3:
                return (4, iteration - 9)
            elif mux_num == 5:
                return (7, iteration - 9)
        else:
            return (-1, -1)
    else:
        if iteration == 13:
            return (-1, -1)
        elif iteration in range(4, 10):
            if mux_num == 0:
                return (0, iteration - 4)
            elif mux_num == 2:
                return (3, iteration - 4)
            elif mux_num == 4:
                return (6, iteration - 4)
        elif iteration in range(0,1):
            if mux_num == 0:
                return (1, iteration + 5)
            elif mux_num == 2:
                return (4, iteration + 5)
            elif mux_num == 4:
                return (7, iteration + 5)
        else:
            return (-1, -1)


def check_board_val(board2):
    global BoardMem
    global MUX_VAL_ACCUMULATE
    global MUX_READ_VAL_TIME

    for i in [4]:
        
        board2.digital_write(ENABLE_PIN, 0)
        time.sleep(0.5)
        sel_0 = i & 1
        sel_1 = (i >>1) & 1
        sel_2 = (i >>2) & 1
        sel_3 = (i >>3) & 1

        board2.digital_write(MUX_SELECT_PINS[0], sel_0)
        board2.digital_write(MUX_SELECT_PINS[1], sel_1)
        board2.digital_write(MUX_SELECT_PINS[2], sel_2)
        board2.digital_write(MUX_SELECT_PINS[3], sel_3)
        time.sleep(0.5)
        #print(f"Selecting {sel_0} {sel_1} {sel_2} {sel_3} ")
        board2.enable_analog_reporting(0)
        board2.enable_analog_reporting(1)
        time.sleep(0.5)
        board2.disable_analog_reporting(0)
        board2.disable_analog_reporting(1)
        
        for j in range(len(MUX_VAL_ACCUMULATE)):
            # get the average val
            avg = round(MUX_VAL_ACCUMULATE[j] / MUX_READ_VAL_TIME[j])
            # get the x, y position given iteration and pin 
            x, y = iteration_to_sesnor(i, j)
            if x != -1:
                # get threshold
                black_upper, black_lower = TRESHOLD[x][y]
                # get previous val
                prev = BoardMem[x][y]
                # given threshold, prev and average, send change to webapp
                #verifyCell(avg, prev, black_lower, black_upper, x, y)
                # update
                BoardMem[x][y] = avg
                # print out
                #print(f"x: {x}, y:{y}, avg:{avg}, mux valL {MUX_VAL_ACCUMULATE[j]}")

        # reset counter vals   
        MUX_VAL_ACCUMULATE = [0, 0]
        MUX_READ_VAL_TIME = [0, 0]
        
        board2.digital_write(ENABLE_PIN, 1)
        time.sleep(0.5)
    serial_board(BoardMem, 9)

    

# CALLED IN NEW PROCESS: main function to check censors 
def check_sensor(stop_event):
    pass
    # Initialize sensor arduino board
    #board2 = telemetrix.Telemetrix(arduino_instance_id=2)
    #board2.set_pin_mode_analog_input(0 , differential=0, callback=read_val_callback)
    #board2.set_pin_mode_analog_input(1 , differential=0, callback=read_val_callback)

    #board2.disable_analog_reporting(0)
    #board2.disable_analog_reporting(1)
    #while not stop_event.is_set():
       # print("Calling check_board_val() to check sensor events") 
       # check_board_val(board2)
       # time.sleep(0.5)  # Sleep to simulate sensor checking delay


def stop_process():
    stop_event.set()
    sensor_process.join()
    print(f"Shutting down process: {sensor_process.pid}") 


def read_val_callback(data):
    #date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[CB_TIME]))
    #x, y = calc_xy(data[CB_PIN])

    global MUX_READ_VAL_TIME 
    global MUX_VAL_ACCUMULATE

    #Store val to compute the averafe
    MUX_READ_VAL_TIME[data[CB_PIN]] += 1
    MUX_VAL_ACCUMULATE[data[CB_PIN]] += data[CB_VALUE]

    #PRINT OUT INFO
    #print(f"Pin: {data[CB_PIN]} Val: {data[CB_VALUE]}")


# Turn on electro magnet 
def electroMagnet_on():
    board2.digital_write(ELECTROMAGNET, 1)


# Turn off electro magnet 
def electroMagnet_off():
    board2.digital_write(ELECTROMAGNET, 0)



""" ************************* MAIN FUNCTION ************************* """

if __name__ == '__main__':

    # Initialize gantry arduino board 
    board = telemetrix.Telemetrix(arduino_instance_id=1)
    motorY = board.set_pin_mode_stepper(interface=1, pin1=X_PULSE_PIN, pin2=X_DIRECTION_PIN)
    motorX = board.set_pin_mode_stepper(interface=1, pin1=Y_PULSE_PIN, pin2=Y_DIRECTION_PIN)

    

    # Initialize sensor checking process 
    sensor_process = Process(target=check_sensor, args=(stop_event,))
    sensor_process.start()
    print(f"Sensor checking process spawned: {sensor_process.pid}")
    atexit.register(stop_process)

    # Initialize flask process 
    app.run(port=5000)
    